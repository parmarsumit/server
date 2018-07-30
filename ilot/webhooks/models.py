
from ilot.core.models import AuditedModel, Item, DataPath
from ilot.core.models import request_switch, Translation, Moderation
from django.db.models.fields import CharField, BooleanField, EmailField, IntegerField, TextField
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db import models
from django.conf import settings

METHOD = (
    ('GET', 'GET'),
    ('POST', 'POST')
)
MIMETYPES = (
    ('application/json', 'JSON'),
    ('application/x-www-form-urlencoded', 'WWW'),
)

from django.template.base import Template
from django.template.context import Context


from ilot.async import AsyncDispatcher


class Webhook(AuditedModel):
    """
    Webhook request to be executed when notification raised
    """
    name = CharField(max_length=128, unique=True)
    description = CharField(max_length=1024)
    url = TextField(verbose_name='Url template')
    method = CharField(max_length=128, choices=METHOD)
    basic_auth = CharField(max_length=256, verbose_name='Basic Auth', blank=True, null=True)
    content_type = CharField(max_length=128, verbose_name='Content-Type:',  choices=MIMETYPES)
    headers = TextField(verbose_name='Request headers template', blank=True, null=True)
    body = TextField(verbose_name='Request body template', blank=True, null=True)

    #forward = ForeignKey('rules.Action', blank=True, null=True, )

    def __str__(self):
        return str(self.name)

    def parse(self, akey, origin, notification=None, authorization=None):

        event = origin

        #print('E', event.id, 'B', event.behavior)

        template_args = {}
        template_args['settings'] = request_switch.interface.get_settings()
        template_args['application'] = request_switch.organization
        template_args['DEBUG'] = settings.DEBUG
        template_args['origin'] = event
        template_args['node'] = event.related
        template_args['authorization'] = authorization
        template_args['actor'] = Item.objects.get_at_id(akey)

        if authorization:
            template_args['url'] = authorization.get_url()
        else:
            # generate a authorization to index on event
            from ilot.models import Authorization
            authorization = Authorization(organization=request_switch.organization, akey=akey, origin=event.id, action='index')
            authorization.save()
            template_args['url'] = authorization.get_url()

        #print('WEBHOOK ', event.id,' user ', akey,' url', template_args['url'])

        if settings.DEBUG:
            print('WEBHOOK URL', template_args['url'])

        if notification:
            context = Context(template_args)
            template_args['title'] = Template(notification.title).render(context)
            template_args['message'] = Template(notification.message).render(context)

        context = Context(template_args)
        parsed_url = Template(self.url).render(context)
        if self.basic_auth:
            parsed_auth = Template(self.basic_auth).render(context)
        else:
            parsed_auth = ''
        parsed_headers = Template(self.headers).render(context)
        parsed_body = Template(self.body).render(context)

        request = WebhookRequest(method=self.method,
                                   content_type=self.content_type,
                                   url=parsed_url,
                                   basic_auth=parsed_auth,
                                   headers=parsed_headers,
                                   content=parsed_body)
        request.save()

        return request



def send_request(request):
    """
    Wrapper method to async request execution
    """
    request.send()


class WebhookRequest(AuditedModel):
    """
    Parsed webhooks queue
    """
    # should nto be null
    # webhook = ForeignKey('webhooks.Webhook', blank=True, null=True)

    # event = ForeignKey('core.Moderation', blank=True, null=True)
    # context = ForeignKey('meta.ActorInferedType', blank=True, null=True)
    # action = ForeignKey('rules.Action', blank=True, null=True)

    method = TextField(verbose_name='Method')
    content_type = TextField(verbose_name='Content-Type')
    url = TextField(verbose_name='Url')
    basic_auth = TextField(verbose_name='Basic Auth', blank=True, null=True)
    headers = TextField(verbose_name='Headers', blank=True, null=True)
    content = TextField(verbose_name='Body')
    done = BooleanField(default=False)
    response = TextField(verbose_name='Response', blank=True, null=True)
    response_code = TextField(verbose_name='Response code', blank=True, null=True)


    def dispatch(self):
        AsyncDispatcher.get_instance().spawn(self.id, send_request, [self])


    def send(self):

        # TODO
        # better encrypted handling of auth keys

        # create a raw http request
        import requests
        from requests import Session, Request
        from requests.auth import HTTPBasicAuth
        s = Session()

        headers_as_dict = {}
        if self.headers:
            for line in self.headers.split('\n'):
                headers_as_dict[line.split(':')[0]] = line.split(':')[1]


        req = requests.Request(self.method,
                               self.url,
                               headers=headers_as_dict,
                               data=self.content)

        if self.basic_auth:
            credentials = self.basic_auth.split(':')
            req.auth = HTTPBasicAuth(credentials[0], credentials[1])

        prepped = req.prepare()
        prepped.headers['Content-Type'] = self.content_type

        verify = True
        if settings.DEBUG:
            print('{}\n{}\n{}\n\n{}'.format(
                '-----------START-----------',
                prepped.method + ' ' + prepped.url,
                '\n'.join('{}: {}'.format(k, v) for k, v in prepped.headers.items()),
                prepped.body,
                '-----------END-----------',
            ))
            verify = False
        else:
            try:
                resp = s.send(prepped, verify=verify)

                print(resp)
                print(resp.text)
            except:
                traceback.print_exc()

            self.response = resp.text
            self.response_code = resp.status_code
            self.done = True

            self.save()

        # parse and push to WS
