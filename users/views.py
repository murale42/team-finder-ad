from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, DetailView, UpdateView
from django.views import View
from users.forms import LoginForm, RegisterForm, UserProfileForm
from users.models import User


# Регистрация пользователя
class RegisterView(FormView):
    template_name = "users/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


# Авторизация пользователя
class LoginView(FormView):
    template_name = "users/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        login(self.request, form.cleaned_data["user"])
        return super().form_valid(form)


# Выход из системы
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("projects:list")


# Профиль пользователя
class UserDetailView(DetailView):
    model = User
    template_name = "users/user-details.html"
    context_object_name = "user"
    pk_url_kwarg = "user_id"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("owned_projects__participants")


# Редактирование профиля
class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/edit_profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("users:detail", kwargs={"user_id": self.object.pk})


# Смена пароля
class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = "users/change_password.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("users:detail")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("users:detail", kwargs={"user_id": self.request.user.pk})


# Список пользователей
class ParticipantsListView(ListView):
    model = User
    template_name = "users/participants.html"
    context_object_name = "participants"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        active_filter = self.request.GET.get("filter")

        if self.request.user.is_authenticated and active_filter:
            if active_filter == "owners-of-favorite-projects":
                queryset = User.objects.filter(
                    owned_projects__in=self.request.user.favorites.all()
                )
            elif active_filter == "owners-of-participating-projects":
                queryset = User.objects.filter(
                    owned_projects__in=self.request.user.participated_projects.all()
                )
            elif active_filter == "interested-in-my-projects":
                queryset = User.objects.filter(favorites__owner=self.request.user)
            elif active_filter == "participants-of-my-projects":
                queryset = User.objects.filter(
                    participated_projects__owner=self.request.user
                )
            else:
                active_filter = None

        return queryset.distinct().order_by("-date_joined")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_filter"] = self.request.GET.get("filter")
        context["active_skill"] = context["active_filter"]
        return context
