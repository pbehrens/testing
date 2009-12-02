from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from managers import SpotManager, ScheduleManager
import datetime

OFFSET_CHOICES = [
    (i, (datetime.datetime(*datetime.datetime.now().timetuple()[:3]) + datetime.timedelta(seconds=i)).strftime('%I:%M%p')) 
    for i in range(0, 24*60*60, 30*60)
]

class Spot(models.Model):
    objects = SpotManager()
    DAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    REPEAT_CHOICES = (
        (0, 'Weekly'),
        (1, '1st day of month'),
        (2, '2nd day of month'),
        (3, '3rd day of month'),
        (4, '4th day of month'),
        (5, '5th day of month'),
        (6, '6th day of month'),
        (7, 'Never'),
    )
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    repeat_every = models.IntegerField(choices=REPEAT_CHOICES)
    offset = models.PositiveIntegerField(choices=OFFSET_CHOICES)                  #offset from 12:00AM in seconds
    dj = models.ForeignKey('DJ')
    show = models.ForeignKey('Show')
    schedule = models.ForeignKey('Schedule')

    def to_datetime(self):
        when = datetime.datetime.now()
        when = datetime.datetime(year=when.year, month=when.month, day=when.day, hour=0, minute=0)
        when = when - datetime.timedelta(days=when.weekday()) + datetime.timedelta(days=self.day_of_week)
        when = when + datetime.timedelta(seconds=self.offset)
        return when

    def __unicode__(self):
        when = self.to_datetime()
        return '%s / %s / %s' % (when.strftime('%I:%M%p'), dict(self.REPEAT_CHOICES)[self.repeat_every], when.strftime('%a')) 


class Show(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    special_program = models.BooleanField()
    active = models.BooleanField()
    date_added = models.DateTimeField()
    image = models.ImageField(upload_to="usr/shows")
    blurb = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    schedule = models.ManyToManyField("Schedule", through=Spot)

    def __unicode__(self): 
        return "%s" % self.name

    def get_spots(self, schedule=None):
        try:
            if schedule is None:
                schedule = Schedule.objects.get_current_schedule()
            return Spot.objects.filter(schedule=schedule, show=self)
        except Schedule.DoesNotExist, e:
            return None
        except Schedule.MultipleObjectsReturned, e:
            return None 

class Schedule(models.Model):
    objects = ScheduleManager()
    start_date = models.DateField()
    end_date = models.DateField()

    def get_edit_view(self):
        return mark_safe(u'<a href="%s" title="edit schedule">Edit Spots</a>' % reverse('admin:existing_schedule', kwargs={'schedule_pk':self.pk}))
    get_edit_view.allow_tags = True

    def __unicode__(self):
        return u'%s until %s' % (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d'))

class DJ(models.Model):
    display_name = models.CharField(max_length=255)
    user = models.OneToOneField(User)
    slug = models.SlugField(unique=True)
    summary = models.TextField()
    description = models.TextField()

    def get_absolute_url(self):
        reversed = reverse('dj-detail', kwargs={
            'dj_slug':self.slug,
        })
        return reversed


    def __unicode__(self):
        if self.display_name:
            return self.display_name
        else:
            return '%s %s' % (self.user.firstname, self.user.lastname[0])

