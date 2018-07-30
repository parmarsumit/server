from django.core.management.base import BaseCommand
from django.template import loader, Context

import os
import uuid

try:
    from urllib.parse import quote
except:
    from urllib import quote

class Command(BaseCommand):
    help = 'Update the server config for this domain folder'

    def add_arguments(self, parser):
        parser.add_argument('container', nargs=1, type=str, default='localhost')
        parser.add_argument('cname', nargs=1, type=str, default='localhost')

    def handle(self, *args, **options):
        from django.conf import settings
        from ilot.cloud.models import Container, Service, Process
        from ilot.models import Interface

        container = options['container'][0]
        cname = options['cname'][0]

        # create the service if not exists
        try:
            container = Container.objects.get(name=container)
        except Container.DoesNotExist:
            container = Container(name=container)
            container.save()

        # find out the corresponding interface
        try:
            interface = Interface.objects.get(cname=cname)
        except Interface.DoesNotExist:
            print('The provided cname does not correspond to an existing interface')
            return

        # check for an existsing service
        try:
            service = Service.objects.get(interface=interface)
        except Service.DoesNotExist:
            service = Service(interface=interface)
        service.path = os.getcwd()
        service.cname = cname
        service.container = container
        service.enabled = True
        service.save()

        if settings.DEBUG:
            return

        # build nginx config
        container_path = settings.SERVER_ROOT

        os.system('mkdir -p '+container_path+'/media')
        os.system('mkdir -p '+container_path+'/media/CACHE')
        os.system('mkdir -p '+container_path+'/conf')
        os.system('mkdir -p '+container_path+'/logs')
        os.system('mkdir -p '+container_path+'/env')

        import ilot
        lib_path = os.path.dirname(os.path.dirname(ilot.__file__))

        container_nginx_tpl = lib_path+'/config/nginx.template.txt'
        container_circus_tpl = lib_path+'/config/circusd.template.txt'
        container_install_tpl = lib_path+'/config/install.template.txt.sh'

        if not os.path.exists(settings.SERVER_ROOT+'/conf/certificate.'+service.id+'.pem'):
            os.system('openssl req -new -x509 -days 365 -nodes -out '+settings.SERVER_ROOT+'/conf/certificate.'+service.id+'.pem -keyout '+settings.SERVER_ROOT+'/conf/key.'+service.id+'.pem -subj "/C=FR/ST=ARA/L=Lyon/O=ILOT/OU=DEV/CN='+cname+'"')

        if not os.path.exists(settings.SERVER_ROOT+'/conf/dhparam.pem'):
            os.system('openssl dhparam -out '+settings.SERVER_ROOT+'/conf/dhparam.pem 2048')

        # migrate, collect static and preload rules
        os.system('mkdir -p media')
        os.system('mkdir -p media/CACHE')
        os.system('mkdir -p theme')
        os.system('mkdir -p build')

        #os.system('export DJANGO_SETTINGS_MODULE=ilot.settings;ilot migrate')
        #os.system('export DJANGO_SETTINGS_MODULE=ilot.settings;ilot update')
        os.system('export DJANGO_SETTINGS_MODULE=ilot.settings;ilot collectstatic --noinput')

        processes = container.get_processes('configured').filter(service=service).order_by('-port')

        num_processes = container.capacity

        if processes.count() > num_processes:
            for i in range(processes.count() - num_processes):
               processes[container.capacity+i-1].delete()

        elif processes.count() < num_processes:
            for i in range(num_processes - processes.count()):
                process = Process(container=container,
                                  status='configured',
                                  enabled=False)
                process.service = service
                process.port = max(9100, container.get_next_available_port())
                process.save()
        else:
            for process in processes:
                process.port = max(9100, container.get_next_available_port())
                process.save()

        services = Service.objects.filter(enabled=True)

        context = Context({'container_path':settings.SERVER_ROOT,
                           'container':container,
                           'service':service,
                           'services':services})

        from django.template.base import Template

        # create domain nginx file
        nginx_config_file = container_path+'/conf/nginx.conf'
        nginx_template = Template(open(container_nginx_tpl, 'r').read())
        open(nginx_config_file, 'w').write(nginx_template.render(context))

        # rebuild circus file
        circus_config_file = container_path+'/conf/circus.conf'
        circus_template = Template(open(container_circus_tpl, 'r').read())
        open(circus_config_file, 'w').write(circus_template.render(context))

        # rebuild install file
        update_file = container_path+'/update.sh'
        install_template = Template(open(container_install_tpl, 'r').read())
        open(update_file, 'w').write(install_template.render(context))

        # generate github keys for hooks
        ssh_key_path = container_path+'/conf/github.'+interface.id+'.key'
        ssh_pub_path = container_path+'/conf/github.'+interface.id+'.key.pub'
        secret_file_path = container_path+'/conf/github.'+interface.id+'.id'

        if not os.path.exists(secret_file_path):
            # generate ssh key and secret
            secret = str(uuid.uuid4())
            open(secret_file_path, 'w').write(secret)

        if not os.path.exists(ssh_key_path):
            cmd = "ssh-keygen -f "+ssh_key_path+" -t rsa -N ''"
            os.system(cmd)

        #
        print('WEBHOOK:', 'https://'+cname+'/')
        print('SECRET:', open(secret_file_path, 'r').read())
        print('KEY:')
        print(open(ssh_pub_path, 'r').read())

        commandline = open('./configure.sh', 'w')
        commandline.write('ilot configure '+container.name+' '+cname)
        commandline.close()
