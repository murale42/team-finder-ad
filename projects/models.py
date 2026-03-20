from django.conf import settings
from django.db import models

from team_finder.constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_CHOICES,
    PROJECT_STATUS_MAX_LENGTH,
    PROJECT_STATUS_OPEN,
)


class Project(models.Model):
    name = models.CharField(
        max_length=PROJECT_NAME_MAX_LENGTH,
        verbose_name="Название проекта",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="owned_projects",
        on_delete=models.CASCADE,
        verbose_name="Владелец",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    github_url = models.URLField(
        blank=True,
        verbose_name="GitHub",
    )
    status = models.CharField(
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=PROJECT_STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
        verbose_name="Статус проекта",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники",
    )
    interested_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="favorites",
        blank=True,
        verbose_name="Заинтересованные пользователи",
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
