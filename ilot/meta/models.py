from django.db import models
from ilot.core.models import AuditedModel
from ilot.core.parsers.api_json import dump_json

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
        from ilot.meta.models import MessageQueue
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
        # print('Sending notfication to ', data)
        online_manager.notify(self.context.actor_id, data)

        # pushing notifications to database
        processes_to_notify = MessageQueue.objects.filter(actor_id=self.context.actor_id).exclude(process_id=online_manager.get_process_id()).values_list('process_id', flat=True).distinct()
        for process_id in processes_to_notify:
            m = MessageQueue(process_id=process_id,
                             actor_id=self.context.actor_id,
                             event_id=self.event.id,
                             message=dump_json(data))
            m.save()



class MessageQueue(AuditedModel):
    process_id = models.CharField(max_length=36)
    actor_id = models.CharField(max_length=36)
    event_id = models.CharField(max_length=36, blank=True, null=True)

    message = models.TextField(blank=True, null=True)
