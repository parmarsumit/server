# start
import os
from posix import mkdir

from tornado import websocket
import tornado.httpserver
import tornado.ioloop
from tornado.options import options, define
import tornado.web
import tornado.wsgi
import os
#
import sys

os.environ.setdefault("CERT_FILE", '.certificate.pem')
os.environ.setdefault("KEY_FILE", '.key.pem')
os.environ.setdefault("DJANGO_ENV", 'production')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ilot.settings")

def main():

    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    sys.path.append(os.getcwd())

    #
    import django
    django.setup()

    #
    from django.conf import settings

    serve()

def serve(ip='127.0.0.1', port=8080):
    #
    import django
    django.setup()

    from django.conf import settings
    from django.utils.translation import activate
    activate(settings.LANGUAGE_CODE)

    #
    try:
        define('port', type=int, default=port)
    except:
        pass
    try:
        define('ip', type=str, default=ip)
    except:
        pass

    tornado.options.parse_command_line()

    import django.core.handlers.wsgi
    wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())

    from ilot.socket import OnlineSocket

    # start the app
    if settings.DEBUG:
        tornado_app = tornado.web.Application([
              (r'/static/app/(.*)', StaticFileHandler, {'path': settings.APP_ROOT+'/build/app/' }),
              (r'/static/contracts/(.*)', StaticFileHandler, {'path': settings.APP_ROOT+'/build/contracts/' }),
              (r'/static/(.*)', StaticFileHandler, {'path': settings.STATIC_ROOT }),
              (r'/media/(.*)', StaticFileHandler, {'path': settings.MEDIA_ROOT }),
              (r'/io.ws', OnlineSocket),
              (r'/io.js', AppView),
              (r'/io/', IndexView),
              #(r'/(.*)', StaticFileSwitcher, {'path': 'www/' }),
              (r'(.*)', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
            ])
    else:
        tornado_app = tornado.web.Application([
              (r'/static/(.*)', StaticFileHandler, {'path': settings.STATIC_ROOT }),
              (r'/media/(.*)', StaticFileHandler, {'path': settings.MEDIA_ROOT }),
              (r'/io.ws', OnlineSocket),
              (r'/io.js', AppView),
              (r'/io/', IndexView),
              #(r'/(.*)', StaticFileSwitcher, {'path': 'www/' }),
              (r'(.*)', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
            ])
    # openssl req -new -x509 -days 365 -nodes -out conf/certificate.pem -keyout conf/key.pem
    #if settings.SECURE_SSL_REDIRECT:
    from ilot.core.manager import AppManager

    ssl_cert = os.path.normpath(os.path.realpath(os.environ['CERT_FILE']))
    ssl_key = os.path.normpath(os.path.realpath(os.environ['KEY_FILE']))

    if not os.path.exists(ssl_cert):
        os.system('openssl req -new -x509 -days 365 -nodes -out '+ssl_cert+' -keyout '+ssl_key+' -subj "/C=FR/ST=ARA/L=Lyon/O=ILOT/OU=DEV/CN='+options.ip+'"')

    SSL_CERTS = {
        "certfile": ssl_cert,
        "keyfile": ssl_key,
        }
    server = tornado.httpserver.HTTPServer(tornado_app, ssl_options=SSL_CERTS)

    def stop():
        print('STOPPED ...')
        from ilot.manager import OnlineManager
        OnlineManager.get_instance().stop()

    import signal
    import sys

    def signal_term_handler(signal, frame):
        print('got signal ', signal)
        stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_term_handler)
    signal.signal(signal.SIGHUP, signal_term_handler)

    print('SERVING AT https://'+options.ip+':'+str(options.port)+'/')
    try:
        server.listen(options.port, address=options.ip)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print('STOPPING ...')
        stop()

domains = {}

from tornado.web import RequestHandler
class IndexView(RequestHandler):
    def get(self):
        return self.render("templates/blank.html")

from tornado.web import RequestHandler
class AppView(RequestHandler):
    def get(self):
        return self.render("static/ws.js")

from tornado.web import StaticFileHandler
class StaticFileSwitcher(StaticFileHandler):
    """
    Switching root files depending on hostname application setup
    """
    def initialize(self, path, default_filename=None):
        self.base_root = path
        self.default_filename = default_filename

    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache, no-store, must-revalidate, max-age=0")

    def get(self, path, include_body=True):
        # switching root
        cname = self.request.host.split(':')[0]

        from ilot.cloud.models import Service

        try:
            if cname in domains:
                app = domains[cname]
            else:
                app = Service.objects.get(interface__cname=cname)
                domains[cname] = app
            self.root = os.path.join(app.path, self.base_root)
        except Service.DoesNotExist:
            from django.conf import settings
            self.root = os.path.join(settings.APP_ROOT, self.base_root)

        return super(StaticFileSwitcher, self).get(path, include_body)


if __name__ == "__main__":
    # starts the tornado server
    main()
