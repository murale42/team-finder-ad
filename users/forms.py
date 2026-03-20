from django import forms
from django.contrib.auth import authenticate

from team_finder.constants import USER_NAME_MAX_LENGTH, USER_SURNAME_MAX_LENGTH
from team_finder.validators import validate_github_url
from users.models import User


# Регистрация пользователя
class RegisterForm(forms.Form):

    name = forms.CharField(max_length=USER_NAME_MAX_LENGTH, label="Имя")
    surname = forms.CharField(max_length=USER_SURNAME_MAX_LENGTH, label="Фамилия")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

    def save(self):
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            name=self.cleaned_data["name"],
            surname=self.cleaned_data["surname"],
        )


# Авторизация пользователя
class LoginForm(forms.Form):

    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            user = authenticate(email=email.lower(), password=password)
            if not user:
                raise forms.ValidationError("Неверный email или пароль")
            cleaned["user"] = user
        return cleaned


# Редактирование профиля
class UserProfileForm(forms.ModelForm):

    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/*"}),
    )

    class Meta:
        model = User
        fields = ["avatar", "name", "surname", "about", "phone", "github_url"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
            "avatar": "Аватар",
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return None
        if phone.startswith("8"):
            phone = "+7" + phone[1:]
        if not (phone.startswith("+7") and len(phone) == 12 and phone[1:].isdigit()):
            raise forms.ValidationError(
                "Номер должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
            )
        qs = User.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "Этот номер телефона уже зарегистрирован на платформе!"
            )
        return phone

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url"))
