import io
import os
import random
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import (
    USER_NAME_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
    AVATAR_SIZE,
    AVATAR_FONT_SIZE,
    AVATAR_TEXT_OFFSET_Y,
    AVATAR_TEXT_COLOR,
    AVATAR_BACKGROUND_COLORS,
)
from .managers import UserManager


# Пользователь
class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        unique=True,
        verbose_name="Email",
    )

    name = models.CharField(
        max_length=USER_NAME_MAX_LENGTH,
        verbose_name="Имя",
    )

    surname = models.CharField(
        max_length=USER_SURNAME_MAX_LENGTH,
        verbose_name="Фамилия",
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        verbose_name="Аватар",
    )

    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Телефон",
    )

    github_url = models.URLField(
        blank=True,
        verbose_name="GitHub",
    )

    about = models.TextField(
        blank=True,
        validators=[MaxLengthValidator(USER_ABOUT_MAX_LENGTH)],
        verbose_name="О себе",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name="Администратор",
    )

    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата регистрации",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self._generate_default_avatar()

        super().save(*args, **kwargs)

    def _generate_default_avatar(self):
        letter = (self.name or "U").strip()[:1].upper()

        bg_color = random.choice(AVATAR_BACKGROUND_COLORS)

        image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color=bg_color)
        draw = ImageDraw.Draw(image)

        font = None
        font_path = (
            settings.BASE_DIR
            / "static"
            / "fonts"
            / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
        )

        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(str(font_path), AVATAR_FONT_SIZE)
            except OSError:
                font = None

        if font is None:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x = (AVATAR_SIZE - text_width) / 2
        text_y = (AVATAR_SIZE - text_height) / 2 - AVATAR_TEXT_OFFSET_Y

        draw.text(
            (text_x, text_y),
            letter,
            font=font,
            fill=AVATAR_TEXT_COLOR,
        )

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        file_name = f"avatar_{uuid.uuid4().hex}.png"
        self.avatar.save(file_name, ContentFile(buffer.read()), save=False)
