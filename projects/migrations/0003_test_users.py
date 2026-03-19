import io
import os
import random
import uuid
from django.db import migrations
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

AVATAR_SIZE = 256
AVATAR_FONT_SIZE = 140
AVATAR_TEXT_OFFSET_Y = 8
AVATAR_TEXT_COLOR = (255, 255, 255)
AVATAR_BACKGROUND_COLORS = [
    (76, 110, 219),  # синий
    (45, 156, 219),  # голубой
    (39, 174, 96),  # зелёный
    (111, 66, 193),  # фиолетовый
    (240, 138, 93),  # оранжевый
    (52, 73, 94),  # тёмный
]


def generate_avatar_for_user(user):
    letter = (user.name or "U").strip()[:1].upper()
    bg_color = random.choice(AVATAR_BACKGROUND_COLORS)
    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color=bg_color)
    draw = ImageDraw.Draw(image)

    system_fonts = [
        "C:/Windows/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttf",
    ]
    font = None
    for path in system_fonts:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, AVATAR_FONT_SIZE)
                break
            except OSError:
                continue

    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (AVATAR_SIZE - text_width) / 2
    text_y = (AVATAR_SIZE - text_height) / 2 - AVATAR_TEXT_OFFSET_Y
    draw.text((text_x, text_y), letter, font=font, fill=AVATAR_TEXT_COLOR)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    file_name = f"avatar_{uuid.uuid4().hex}.png"
    user.avatar.save(file_name, ContentFile(buffer.read()), save=False)
    user.save()


def create_test_data(apps, schema_editor):
    User = apps.get_model("users", "User")
    Project = apps.get_model("projects", "Project")

    users_data = [
        {
            "email": "leonova@pochta.ru",
            "name": "Мария",
            "surname": "Леонова",
            "phone": "+79161112233",
            "github_url": "https://github.com/leonova",
            "about": "Backend-разработчик, увлекаюсь машинным обучением и созданием API.",
        },
        {
            "email": "batman@pochta.ru",
            "name": "Эдуард",
            "surname": "Дёмин",
            "phone": "+79262223344",
            "github_url": "https://github.com/batman",
            "about": "Fullstack разработчик, люблю игры и frontend. В свободное время пишу на React.",
        },
        {
            "email": "bird@pochta.ru",
            "name": "Эльвира",
            "surname": "Дятлова",
            "phone": "+79363334455",
            "github_url": "https://github.com/bird",
            "about": "Data scientist, аналитик данных, строю дашборды и модели.",
        },
        {
            "email": "usmanova@pochta.ru",
            "name": "Алсу",
            "surname": "Усманова",
            "phone": "+79464445566",
            "github_url": "https://github.com/usmanova",
            "about": "Мобильный разработчик (iOS/Android), создаю полезные приложения.",
        },
        {
            "email": "taras@pochta.ru",
            "name": "Тарас",
            "surname": "Бульба",
            "phone": "+79565556677",
            "github_url": "https://github.com/taras",
            "about": "DevOps инженер, автоматизация, контейнеризация, люблю козаков и байки.",
        },
    ]

    password = make_password("password123")

    users = []
    for data in users_data:
        user = User.objects.create(
            email=data["email"],
            name=data["name"],
            surname=data["surname"],
            phone=data["phone"],
            github_url=data["github_url"],
            about=data["about"],
            password=password,
        )
        generate_avatar_for_user(user)
        users.append(user)

    projects_info = [
        # Мария
        (
            "AI Chat Bot",
            "Интеллектуальный чат-бот на основе нейросетей для поддержки пользователей.",
            users[0],
            "open",
        ),
        (
            "Task Manager API",
            "REST API для управления задачами с JWT-аутентификацией.",
            users[0],
            "open",
        ),
        (
            "Data Visualizer",
            "Веб-сервис для визуализации данных в реальном времени.",
            users[0],
            "closed",
        ),
        # Эдуард
        (
            "Superhero Game",
            "Браузерная игра про супергероев с использованием Canvas.",
            users[1],
            "open",
        ),
        (
            "Weather App",
            "Приложение для прогноза погоды с интеграцией OpenWeatherMap.",
            users[1],
            "open",
        ),
        (
            "Crypto Tracker",
            "Отслеживание курсов криптовалют с графиками.",
            users[1],
            "open",
        ),
        # Эльвира
        (
            "E-commerce Platform",
            "Платформа для интернет-магазинов с корзиной и оплатой.",
            users[2],
            "open",
        ),
        (
            "Blog Engine",
            "Движок для блога с поддержкой Markdown и комментариями.",
            users[2],
            "closed",
        ),
        ("Portfolio Site", "Генератор портфолио для разработчиков.", users[2], "open"),
        # Алсу
        (
            "Mobile App for Fitness",
            "Приложение для отслеживания тренировок и питания.",
            users[3],
            "open",
        ),
        (
            "Recipe Finder",
            "Поиск рецептов по ингредиентам с фильтрами.",
            users[3],
            "open",
        ),
        (
            "Event Planner",
            "Планировщик мероприятий с напоминаниями.",
            users[3],
            "closed",
        ),
        # Тарас
        (
            "Online Code Editor",
            "Редактор кода в браузере с подсветкой синтаксиса.",
            users[4],
            "open",
        ),
        (
            "File Converter",
            "Конвертер изображений и документов онлайн.",
            users[4],
            "open",
        ),
        (
            "Chat App",
            "Чат с комнатами и личными сообщениями на WebSockets.",
            users[4],
            "open",
        ),
    ]

    projects = []
    for name, desc, owner, status in projects_info:
        project = Project.objects.create(
            name=name,
            description=desc,
            owner=owner,
            github_url=f'https://github.com/{owner.github_url.split("/")[-1]}/{name.replace(" ", "").lower()}',
            status=status,
        )
        projects.append(project)

    Project.objects.filter(name="AI Chat Bot", owner=users[0]).first().participants.add(
        users[1], users[2]
    )
    Project.objects.filter(
        name="Superhero Game", owner=users[1]
    ).first().participants.add(users[4], users[3])
    Project.objects.filter(
        name="E-commerce Platform", owner=users[2]
    ).first().participants.add(users[0], users[4])
    Project.objects.filter(
        name="Mobile App for Fitness", owner=users[3]
    ).first().participants.add(users[1], users[2])
    Project.objects.filter(
        name="Online Code Editor", owner=users[4]
    ).first().participants.add(users[0], users[3])

    # Избранное
    # Мария
    users[0].favorites.add(
        Project.objects.get(name="Superhero Game", owner=users[1]),
        Project.objects.get(name="E-commerce Platform", owner=users[2]),
        Project.objects.get(name="Chat App", owner=users[4]),
    )
    # Эдуард
    users[1].favorites.add(
        Project.objects.get(name="AI Chat Bot", owner=users[0]),
        Project.objects.get(name="Mobile App for Fitness", owner=users[3]),
        Project.objects.get(name="File Converter", owner=users[4]),
    )
    # Эльвира
    users[2].favorites.add(
        Project.objects.get(name="Task Manager API", owner=users[0]),
        Project.objects.get(name="Crypto Tracker", owner=users[1]),
        Project.objects.get(name="Event Planner", owner=users[3]),
    )
    # Алсу
    users[3].favorites.add(
        Project.objects.get(name="Data Visualizer", owner=users[0]),
        Project.objects.get(name="Blog Engine", owner=users[2]),
        Project.objects.get(name="Online Code Editor", owner=users[4]),
    )
    # Тарас
    users[4].favorites.add(
        Project.objects.get(name="Weather App", owner=users[1]),
        Project.objects.get(name="Portfolio Site", owner=users[2]),
        Project.objects.get(name="Recipe Finder", owner=users[3]),
    )


def remove_test_data(apps, schema_editor):
    User = apps.get_model("users", "User")
    emails = [
        "leonova@pochta.ru",
        "batman@pochta.ru",
        "bird@pochta.ru",
        "usmanova@pochta.ru",
        "taras@pochta.ru",
    ]
    User.objects.filter(email__in=emails).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
        ("projects", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(create_test_data),
    ]
