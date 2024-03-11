import datetime
import logging
import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import util

logger = logging.getLogger(__name__)


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        verbose_name=_("owner"),
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=128, verbose_name=_("name"))
    color = models.CharField(max_length=6, default=util.color)
    url = models.URLField(blank=True, verbose_name=_("Optional link"))
    memo = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    duration = models.IntegerField(verbose_name=_("duration"), default=0)

    class Meta:
        ordering = ("name",)
        unique_together = [["owner", "name"]]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("pomodoro:project-detail", kwargs={"pk": self.pk})

    def timedelta(self):
        return datetime.timedelta(seconds=self.duration)

    timedelta.admin_order_field = "duration"

    def refresh(self, lookback=90):
        limit = timezone.now() - datetime.timedelta(days=lookback)
        duration = datetime.timedelta()
        for pomodoro in Pomodoro.objects.filter(
            start__gte=limit,
            owner=self.owner,
            project=self,
        ):
            duration += pomodoro.end - pomodoro.start
        self.duration = duration.total_seconds()
        self.save(update_fields=("duration",))


class Pomodoro(models.Model):
    start = models.DateTimeField(default=timezone.now, verbose_name=_("start time"))
    end = models.DateTimeField(default=timezone.now, verbose_name=_("end time"))

    title = models.CharField(max_length=128, verbose_name=_("title"))
    category = models.CharField(max_length=32, blank=True, verbose_name=_("category"))
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        verbose_name=_("owner"),
        on_delete=models.CASCADE,
    )
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)

    url = models.URLField(blank=True, help_text="Optional link")
    memo = models.TextField(blank=True)

    @property
    def duration(self):
        return self.end - self.start

    duration.fget.short_description = _("duration")

    def __str__(self):
        return f"{self.start}:{self.title}"

    def get_absolute_url(self):
        return reverse("pomodoro:pomodoro-detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ("-start",)


class Favorite(models.Model):
    duration = models.IntegerField(verbose_name=_("duration"))
    title = models.CharField(max_length=128, verbose_name=_("title"))
    category = models.CharField(max_length=32, blank=True, verbose_name=_("category"))
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        verbose_name=_("owner"),
        on_delete=models.CASCADE,
    )
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)
    icon = models.ImageField(upload_to=util._upload_to_path, blank=True)
    count = models.PositiveIntegerField(default=0)
    url = models.URLField(blank=True)

    pomodoro_set = models.ManyToManyField(
        Pomodoro,
        through="FavoritePomodoro",
        through_fields=("favorite", "pomodoro"),
    )

    class Meta:
        ordering = ("-count",)

    def get_absolute_url(self):
        return reverse("pomodoro:favorite-detail", kwargs={"pk": self.pk})

    def refresh(self, lookback=90):
        search = timezone.now() - datetime.timedelta(days=lookback)
        self.count = self.pomodoro_set.filter(end__gte=search).count()
        self.save(update_fields=("count",))

    def timedelta(self):
        return datetime.timedelta(minutes=self.duration)

    def start(self, ts):
        pomodoro = Pomodoro.objects.create(
            title=self.title,
            category=self.category,
            project=self.project,
            owner=self.owner,
            start=ts,
            end=ts + datetime.timedelta(minutes=self.duration),
            url=self.url,
        )
        self.pomodoro_set.add(pomodoro)
        return pomodoro


class Share(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        verbose_name=_("owner"),
        on_delete=models.CASCADE,
    )
    last_accessed = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse("pomodoro:share-calendar", kwargs={"pk": self.pk})


class FavoritePomodoro(models.Model):
    favorite = models.ForeignKey(Favorite, on_delete=models.CASCADE)
    pomodoro = models.ForeignKey(Pomodoro, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
