import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class PollQuerySet(models.QuerySet):
    def public(self):
        return self.filter(pub_date__lte=timezone.now())


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    visible = models.NullBooleanField()
    created_by = models.ForeignKey(User, default=0)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.question

    def get_absolute_url(self):
        return reverse('polls:results', args=(self.id,))

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date < now

    #TODO: pub_date ??
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'
    
    def num_voters(self):
        '''Return the number of people who voted on this poll.'''
        return Vote.objects.filter(choice__poll=self).count()

    num_voters.short_description = 'Number of voters'

    objects = PollQuerySet.as_manager()


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.choice_text

    class Meta:
        unique_together = ('poll', 'choice_text')


class Vote(models.Model):
    choice = models.ForeignKey(Choice)
    user = models.ForeignKey(User)

    def __unicode__(self):  # Python 3: def __str__(self):
        return u'{0}: {1} ({2})'.format(
                self.choice.poll.question,
                self.choice.choice_text,
                str(self.user),
                )
    class Meta:
        unique_together = ('choice', 'user')

