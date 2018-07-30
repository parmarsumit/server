# -*- coding: utf-8 -*-
import re

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation

from ilot.core.utils.compatibility import unicode3

import logging
logger = logging.getLogger(__name__)

URLS_WITHOUT_LANGUAGE_REDIRECT = getattr(settings, 'URLS_WITHOUT_LANGUAGE_REDIRECT', ())

def get_default_locale(locale_code=None):
    """Returns default locale depending on settings.LANGUAGE_CODE merged with
    best match from settings.LANGUAGES
    Returns: locale_code
    """
    if not locale_code:
        locale_code = settings.LANGUAGE_CODE
    locales = dict(settings.LANGUAGES).keys()

    # first try if there is an exact locale
    if locale_code in locales:
        return locale_code

    # otherwise split the locale code if possible, so iso3
    locale_code = locale_code.split("-")[0]
    if not locale_code in locales:
        return settings.LANGUAGE_CODE
    return locale_code

class MultilingualURLMiddleware(object):
    '''
    See http://ilian.i-n-i.org/locale-redirects-for-multilingual-sites-with-django-cms/
    '''
    cached_locale_regexp = None

    def get_supported_locales(self):
        return settings.LANGUAGES

    def has_lang_prefix(self, path):

        if not self.cached_locale_regexp:
            self.cached_locale_regexp = re.compile(r"^/(%s)/.*" % "|".join([re.escape(l) for l in self.get_supported_locales()]))

        check = self.cached_locale_regexp.match(path)

        if check is not None:
            return check.group(1)
        else:
            return False


    def get_language_from_request(self, request):

        changed = False
        prefix = self.has_lang_prefix(request.path_info)
        if prefix:
            request.path = "/" + "/".join(request.path.split("/")[2:])
            request.path_info = request.path
            t = prefix
            if t in self.get_supported_locales():
                lang = t
                if hasattr(request, "session") and request.session.get("django_locale", None) != lang:
                    request.session["django_locale"] = lang
                changed = True
        else:
            lang = translation.get_language_from_request(request)

        if not changed:
            if hasattr(request, "session"):
                lang = request.session.get("django_locale", None)
                if lang in self.get_supported_locales() and lang is not None:
                    return lang

            elif "django_locale" in request.COOKIES.keys():
                lang = request.COOKIES.get("django_locale", None)
                if lang in self.get_supported_locales() and lang is not None:
                    return lang

            if not lang:
                lang = translation.get_language_from_request(request)

        return lang

    def process_request(self, request):
        path = unicode3(request.path)

        if not path in URLS_WITHOUT_LANGUAGE_REDIRECT and \
           not path.startswith(settings.MEDIA_URL) and \
           not path.startswith(settings.STATIC_URL):



            # Parent will rewrite the path to remove the locale if found
            # get_full_path() so we include any query string
            original_path = request.get_full_path()

            request_locale = self.get_language_from_request(request)
            request.LANGUAGE_CODE = request_locale
            translation.activate(request_locale)

            # manage to remove the locale root and patch with host path
            for no_redirect_url in URLS_WITHOUT_LANGUAGE_REDIRECT:
                if original_path.startswith(no_redirect_url):
                    # Path matched, no need for auth
                    logger.debug('Requested path %s in URLS_WITHOUT_LANGUAGE_REDIRECT, '
                                 'skipping locale enforcement' % original_path)
                    return None

            # at this point we redirect to the locale url
            # only if get or head requests methods
            if request.method not in ('GET', 'HEAD'):
                return

            #
            locale = getattr(request, 'LANGUAGE_CODE', None)

            # Missing trailing slash
            if original_path == ('/%s' % locale):
                return HttpResponseRedirect('/%s/' % locale)
            else:
                # Missing trailing slash with query string
                if original_path.startswith('/%s?' % locale):
                    return HttpResponseRedirect('/%s/?%s' % (locale, request.META.get('QUERY_STRING', '')))

                #
                if not original_path.startswith('/%s/' % locale):
                    return HttpResponseRedirect('/%s%s?%s' % (locale, request.path, request.META.get('QUERY_STRING', '')))
                #else:
                #    return HttpResponseRedirect('/%s%s' % (locale, request.path))
