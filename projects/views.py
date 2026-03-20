from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from projects.forms import ProjectForm
from projects.models import Project
from team_finder.constants import PROJECTS_PER_PAGE, PROJECT_STATUS_OPEN, PROJECT_STATUS_CLOSED


# Список проектов
class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = PROJECTS_PER_PAGE

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("owner")
            .prefetch_related("participants")
            .order_by("-created_at")
        )


# Детали проекта
class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project-details.html"
    context_object_name = "project"
    pk_url_kwarg = "project_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        owner_in_participants = project.participants.filter(pk=project.owner_id).exists()
        participants = list(project.participants.all())
        if not owner_in_participants:
            participants.append(project.owner)
        participants_count = project.participants.count() + (0 if owner_in_participants else 1)
        context["project_participants"] = participants
        context["participants_count"] = participants_count

        return context


# Создание проекта
class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.save()
        project.participants.add(self.request.user)
        return redirect("projects:detail", project_id=project.pk)


# Редактирование проекта
class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"
    pk_url_kwarg = "project_id"

    def test_func(self):
        project = self.get_object()
        return project.owner_id == self.request.user.id

    def handle_no_permission(self):
        return HttpResponseForbidden("Только владелец может редактировать этот проект")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        context["project"] = self.object
        return context

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"project_id": self.object.pk})


# Закрытие проекта
@method_decorator(require_POST, name="dispatch")
class ProjectCompleteView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if project.owner_id != request.user.id or project.status != PROJECT_STATUS_OPEN:
            return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

        project.status = PROJECT_STATUS_CLOSED
        project.save(update_fields=["status"])
        return JsonResponse({"status": "ok", "project_status": PROJECT_STATUS_CLOSED})


# Присоединение / выход из проекта
@method_decorator(require_POST, name="dispatch")
class ToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        user = request.user

        if project.owner_id == user.id or project.status == PROJECT_STATUS_CLOSED:
            return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)

        if project.participants.filter(pk=user.id).exists():
            project.participants.remove(user)
            participant = False
        else:
            project.participants.add(user)
            participant = True

        return JsonResponse({"status": "ok", "participant": participant})


# Добавление / удаление проекта из избранного
@method_decorator(require_POST, name="dispatch")
class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        user = request.user

        if user.favorites.filter(pk=project.id).exists():
            user.favorites.remove(project)
            favorited = False
        else:
            user.favorites.add(project)
            favorited = True

        return JsonResponse({"status": "ok", "favorited": favorited})


# Список избранных проектов текущего пользователя
class FavoritesListView(LoginRequiredMixin, ListView):
    template_name = "projects/favorite_projects.html"
    context_object_name = "projects"
    paginate_by = PROJECTS_PER_PAGE

    def get_queryset(self):
        return (
            self.request.user.favorites.select_related("owner")
            .prefetch_related("participants")
            .all()
        )
