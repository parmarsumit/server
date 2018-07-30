from ilot.core.models import AuditedModel, Item
from django.db.models.manager import Manager
from django.db import models
from django.db.models import CharField, TextField, ForeignKey
from ilot.scenarios.avatar import Player
from ilot.core.parsers.api_json import load_json
METHOD = (
    ('GET', 'GET/SUB'),
    ('POST', 'POST/PUB')
)

class ScenarioManager(Manager):
    players = {}
    steps = {}

    authorizations = {}

class Avatar(AuditedModel):
    name = CharField(max_length=200, unique=True)
    identity = TextField()
    description = TextField()

    def __str__(self):
        return str(self.name)

    def get_player(self):
        if not self.id in Scenario.objects.players:
            Scenario.objects.players[self.id] = Player(load_json(self.identity))
        return Scenario.objects.players[self.id]

class Step(AuditedModel):
    name = CharField(max_length=200, unique=True)
    description = TextField()

    avatar = ForeignKey(Avatar, on_delete=models.PROTECT)

    next = ForeignKey('self', related_name='following', null=True, blank=True, on_delete=models.PROTECT)

    action = ForeignKey('rules.Action', null=True, blank=True, on_delete=models.PROTECT)
    data = TextField()

    method = CharField(max_length=6, default=METHOD[0][0], choices=METHOD)

    def get_url(self, action=None):
        if not action and self.ruid:
            return self.ruid

        url = 'https://localhost:9999/'+self.ruid+'/'
        if action:
            url += action.name+'/'

        return url

    def get_refering_url(self):
        return self.rurl

    def __str__(self):
        return str(self.name)

    def run(self, prev):
        print('\n------- ', self.name,' \n')
        Scenario.objects.steps[self.id] = prev

        player = self.avatar.get_player()
        url = prev.get_url(self.action)

        refering_url = prev.get_refering_url()

        print('From:', refering_url)
        print('To:', self.method, url)
        print('\n')

        from ilot.core.manager import AppManager

        self.current_ref_time = AppManager.get_ref_time()

        if self.method == 'GET':
            player.get(refering_url, url, load_json(self.data), self.done)
        elif self.method == 'POST':
            player.post(refering_url, url, load_json(self.data), self.done)
        else:
            raise

    def done(self, uid, url):

        # what are the produced webhooks ?
        if self.action.authorize and self.method == 'POST':
            # get last one
            from ilot.models import Authorization
            sublink = Authorization.objects.all().order_by('-ref_time')[0].get_url()
            player = self.avatar.get_player()
            return player.get(url, sublink, {}, self.done)

        self.ruid = uid
        self.rurl = url

        if self.next:
            return self.next.run(self)
        else:
            return


class Scenario(AuditedModel):
    name = CharField(max_length=200, unique=True)
    description = TextField()
    interface = ForeignKey('ilot.Interface', related_name='scenarios', null=True, blank=True, on_delete=models.PROTECT)
    entry_url = CharField(max_length=2048, null=True, blank=True)
    start = ForeignKey(Step, null=True, blank=True, on_delete=models.PROTECT)

    objects = ScenarioManager()

    def __str__(self):
        return str(self.name)

    def get_url(self, action=None):
        if not self.entry_url and self.interface:
            url = 'https://'+self.interface.cname+':9999/'
        else:
            url = self.entry_url
        return url

    def run(self):
        Scenario.objects.steps[self.id] = self
        self.ruid = None
        self.rurl = self.get_url()
        self.start.run(self)

    def done(self, uid, url):
        print('DONE !', uid, url)

    def get_refering_url(self):
        return ''

    def get_steps(self):
        self.start.followings.all()
