from django.http.response import HttpResponse
from ilot.cloud.models import Service
from django.conf import settings
import os
import subprocess
import uuid

class GithubDeployMiddleware(object):
    def process_request(self, request):
        if 'HTTP_X_HUB_SIGNATURE' in request.META:
            interface = request_switch.interface
            git_folder = interface.service.path
            secret_file_path = settings.APP_ROOT+'/conf/github.'+interface.id+'.id'
            ssh_key_path = settings.APP_ROOT+'/conf/github.'+interface.id+'.key'
            secret = open(secret_file_path, 'r').read()
            # build hmac with repo secret
            import hashlib
            import hmac
            signature = 'sha1=' + hmac.new(secret.encode('utf-8'), request.body, hashlib.sha1).hexdigest()
            if signature == request.META.get('HTTP_X_HUB_SIGNATURE'):
                cmd = "ssh-agent bash -c 'ssh-add "+ssh_key_path+"; cd "+git_folder+"; git pull '"
                try:
                    output = subprocess.check_output(cmd, shell=True)
                    print(output)
                    # collect static
                    cmd = "cd "+git_folder+';source '+settings.APP_ROOT+'/env/bin/activate;ilot collectstatic --noinput'
                    output = subprocess.check_output(cmd, shell=True)
                    print(output)
                except subprocess.CalledProcessError:
                    return handler500(request)
            return HttpResponse('THX!')
            #setattr(request, '_dont_enforce_csrf_checks', True)
        return None

    def process_response( self, request, response ):
        return response
