import pytest
from swingtime.models import EventType, Event, Occurrence

from datetime import datetime
from django.utils import timezone


def make_dt(*args):
    return timezone.make_aware(datetime(*args))

@pytest.fixture
def work_type():
    #2
    return EventType.objects.create(abbr='work', label='Work')

@pytest.fixture
def play_type():
    #1
    return EventType.objects.create(abbr='play', label='Play')


@pytest.fixture
def occurence(work_type):
    e = Event.objects.create(event_type=work_type, title='event')
    return Occurrence.objects.create(
        event=e,
        start_time=make_dt(2018, 3, 18, 16, 00), 
        end_time=make_dt(2018, 3, 18, 16, 45)
    )


@pytest.fixture
def events(play_type, work_type):
    e = Event.objects.create(event_type=play_type, title='bravo')
    Occurrence.objects.create(
        event=e,
        start_time=make_dt(2008, 12, 11, 16, 00), 
        end_time=make_dt(2008, 12, 11, 16, 45)
    )

    e = Event.objects.create(event_type=work_type,  title='echo')
    Occurrence.objects.create(
        event=e,
        start_time=make_dt(2008, 12, 11, 17, 15), 
        end_time=make_dt(2008, 12, 11, 18, 00)
    )

    e = Event.objects.create(event_type=play_type, title='charlie')
    Occurrence.objects.create(
        event=e,
        start_time=make_dt(2008, 12, 11, 16, 15), 
        end_time=make_dt(2008, 12, 11, 17, 00)
    )

    e = Event.objects.create(event_type=work_type, title='foxtrot')
    Occurrence.objects.create(
        event=e,
        start_time=make_dt(2008, 12, 11, 16, 00), 
        end_time=make_dt(2008, 12, 11, 16, 45)
    )

    e = Event.objects.create(event_type=play_type, title='alpha')
    Occurrence.objects.create(
        event=e,
        start_time=make_dt(2008, 12, 11, 15, 30), 
        end_time=make_dt(2008, 12, 11, 17, 45)
    )

    e = Event.objects.create(event_type=work_type, title='zelda')
    Occurrence.objects.create(
        event=e,
        start_time=make_dt(2008, 12, 11, 15, 15), 
        end_time=make_dt(2008, 12, 11, 15, 45)
    )

    e = Event.objects.create(event_type=play_type, title='delta')
    Occurrence.objects.create(
        event=e,
        start_time=make_dt(2008, 12, 11, 16, 30), 
        end_time=make_dt(2008, 12, 11, 17, 15)
    )

    return Event.objects.all()
