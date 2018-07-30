from django.db import models
from ilot.core.models import AuditedModel

class ActorInferedType(AuditedModel):
    """
    Roles of actors on elements
    """
    context = models.ForeignKey('core.Moderation', related_name='meta_typed', blank=True, null=True, editable=False, db_constraint=False, on_delete=models.CASCADE)
    actor = models.ForeignKey('core.Moderation', related_name='meta_types', blank=True, null=True, editable=False, db_constraint=False, on_delete=models.CASCADE)
    type = models.ForeignKey('rules.Type', related_name='typed_meta', blank=True, null=True, editable=False, db_constraint=False, on_delete=models.CASCADE)
    event = models.ForeignKey('core.Moderation', related_name='meta_typing', blank=True, null=True, editable=False, db_constraint=False, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('context', 'actor', 'type', 'event')


class ActorNotification(AuditedModel):
    """
    Notifications to roles by element
    """
    context = models.ForeignKey(ActorInferedType, related_name='notifs', editable=False, db_constraint=False, on_delete=models.CASCADE)
    rule = models.ForeignKey('grammar.Notification', related_name='nrules', blank=True, null=True, editable=False, db_constraint=False, on_delete=models.CASCADE)
    event = models.ForeignKey('core.Moderation', related_name='notifs', blank=True, null=True, editable=False, db_constraint=False, on_delete=models.CASCADE)
    request = models.ForeignKey('webhooks.WebhookRequest', related_name='notifications', blank=True, null=True, verbose_name="Webhook request", on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        """
        In order to be finally saved, if the notif has webhook,
        let's parse and save it for async send
        This should not change afterwards
        If the requets fails we may retry it ...
        """
        if self.rule.webhook:
            self.request = self.rule.webhook.parse(self.context.actor, self.context.event, self.rule)

        super(ActorNotification, self).save(*args, **kwargs)

        self.notify()

        if self.request:
            self.request.dispatch()


    def get_notif_message(self):
        from ilot.grammar.models import parse_message
        return parse_message(self.rule.for_target, self.event, target=self.context.actor)

    def notify(self):

        from ilot.manager import OnlineManager
        online_manager = OnlineManager.get_instance()

        message = self.get_notif_message()

        if not message:
            message = 'DONE '
        #'akey': self.context.akey,
        data = {
            'target': self.context.actor_id,
            'text': message,
            'todo':self.rule.todo,
        }
        print('Sending notfication to ', data)
        online_manager.notify(self.context.actor_id, data)
