from datetime import datetime, date, timedelta
from dateutil import rrule

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from .conf import swingtime_settings

__all__ = (
    'EventType',
    'BaseEvent',
    'BaseOccurrence',
)


class EventType(models.Model):
    '''
    Simple ``Event`` classifcation.
    '''
    abbr = models.CharField(_('abbreviation'), max_length=4, unique=True)
    label = models.CharField(_('label'), max_length=50)

    class Meta:
        verbose_name = _('event type')
        verbose_name_plural = _('event types')

    def __str__(self):
        return self.label


class BaseEvent(models.Model):
    '''
    Base container model for general metadata.
    '''
    title = models.CharField(_('title'), max_length=32)
    description = models.CharField(_('description'), max_length=100)
    event_type = models.ForeignKey(
        EventType,
        verbose_name=_('event type'),
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ('title', )
        abstract = True

    occurrence_class = None

    def __str__(self):
        return self.title

    def get_occurrence_class(self):
        return self.occurrence_class

    def add_occurrences(self, start_time, end_time, **rrule_params):
        '''
        Add one or more occurences to the event using a comparable API to
        ``dateutil.rrule``.

        If ``rrule_params`` does not contain a ``freq``, one will be defaulted
        to ``rrule.DAILY``.

        Because ``rrule.rrule`` returns an iterator that can essentially be
        unbounded, we need to slightly alter the expected behavior here in order
        to enforce a finite number of occurrence creation.

        If both ``count`` and ``until`` entries are missing from ``rrule_params``,
        only a single ``Occurrence`` instance will be created using the exact
        ``start_time`` and ``end_time`` values.
        '''
        count = rrule_params.get('count')
        until = rrule_params.get('until')
        if not (count or until):
            self.occurrence_set.create(start_time=start_time, end_time=end_time)
        else:
            rrule_params.setdefault('freq', rrule.DAILY)
            delta = end_time - start_time
            occurrences = []
            Occurrence = self.get_occurrence_class()
            for ev in rrule.rrule(dtstart=start_time, **rrule_params):
                occurrences.append(Occurrence(start_time=ev, end_time=ev + delta, event=self))
            self.occurrence_set.bulk_create(occurrences)

    def upcoming_occurrences(self):
        '''
        Return all occurrences that are set to start on or after the current
        time.
        '''
        return self.occurrence_set.filter(start_time__gte=datetime.now())

    def next_occurrence(self):
        '''
        Return the single occurrence set to start on or after the current time
        if available, otherwise ``None``.
        '''
        upcoming = self.upcoming_occurrences()
        return upcoming[0] if upcoming else None


class OccurrenceManager(models.Manager):

    def daily_occurrences(self, dt=None, event=None):
        '''
        Returns a queryset of for instances that have any overlap with a
        particular day.

        * ``dt`` may be either a datetime.datetime, datetime.date object, or
          ``None``. If ``None``, default to the current day.

        * ``event`` can be an ``Event`` instance for further filtering.
        '''
        dt = dt or datetime.now()
        start = datetime(dt.year, dt.month, dt.day)
        end = start.replace(hour=23, minute=59, second=59)
        qs = self.filter(
            models.Q(
                start_time__gte=start,
                start_time__lte=end,
            ) |
            models.Q(
                end_time__gte=start,
                end_time__lte=end,
            ) |
            models.Q(
                start_time__lt=start,
                end_time__gt=end
            )
        )

        return qs.filter(event=event) if event else qs


class BaseOccurrence(models.Model):
    '''
    Represents the start end time for a specific occurrence of an event
    object.
    '''
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))

    class Meta:
        verbose_name = _('occurrence')
        verbose_name_plural = _('occurrences')
        ordering = ('start_time', 'end_time')
        base_manager_name = 'objects'
        abstract = True

    def __str__(self):
        return u'{}: {}'.format(self.title, self.start_time.isoformat())

    def __lt__(self, other):
        return self.start_time < other.start_time

    @property
    def title(self):
        return self.event.title

    @property
    def event_type(self):
        return self.event.event_type
