from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from ilot.core.models import AuditedModel
from ilot.core.parsers.api_json import load_json

class Container(AuditedModel):
    """
    A container is a node of a cluster
    """
    name = models.CharField(max_length=255)
    ip = models.GenericIPAddressField(protocol='both', default="127.0.0.1")
    capacity = models.IntegerField(default=1)

    enabled = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    def get_processes(self, status=None):
        if status == None:
            return Process.objects.filter(container=self).exclude(status='stopped')
        else:
            return Process.objects.filter(container=self, status=status)

    def get_next_available_port(self):
        # gether all it's container ports
        processes = Process.objects.filter(status__in=('configured', 'started')).order_by('-port')
        if processes.count():
            if processes[0].port+1 > 9999:
                processes[0].port = 9000
        else:
            return 9000
        return processes[0].port+1

class Service(AuditedModel):
    container = models.ForeignKey(Container, related_name='services', on_delete=models.PROTECT)
    interface = models.OneToOneField('ilot.Interface', related_name='service', on_delete=models.PROTECT)
    path =  models.CharField(max_length=512)

    settings = models.TextField(default="{}")

    enabled =  models.BooleanField(default=True)

    def __str__(self):
        return str(self.interface.cname)

    def get_data(self):
        return load_json(self.settings)

    def get_configured_processes(self):
        return Process.objects.filter(service=self, status='configured')


class Process(AuditedModel):
    """
    A process is a program running on a machine
    """
    container = models.ForeignKey(Container, related_name='processes', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='processes', on_delete=models.PROTECT, null=True)
    port = models.IntegerField()
    status = models.CharField(max_length=128, default='unknown')
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return str(self.container.ip)+':'+str(self.port)

class Frontend(AuditedModel):
    """
    A Public Frontend for a cluster
    """
    container = models.ForeignKey(Container, related_name='frontends', on_delete=models.PROTECT)
    ip = models.GenericIPAddressField(protocol='both')
    port = models.IntegerField(default=80)

    def __str__(self):
        return 'A '+str(self.ip)+' '+str(self.container)+':'+str(self.port)

    class Meta:
        unique_together = ('ip', 'port', 'container')
