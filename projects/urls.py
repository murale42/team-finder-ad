from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("list/", views.ProjectListView.as_view(), name="list"),
    path("favorites/", views.FavoritesListView.as_view(), name="favorites"),
    path("create-project/", views.ProjectCreateView.as_view(), name="create"),
    path("<int:project_id>/edit/", views.ProjectUpdateView.as_view(), name="edit"),
    path(
        "<int:project_id>/complete/",
        views.ProjectCompleteView.as_view(),
        name="complete",
    ),
    path(
        "<int:project_id>/toggle-participate/",
        views.ToggleParticipateView.as_view(),
        name="toggle_participate",
    ),
    path(
        "<int:project_id>/toggle-favorite/",
        views.ToggleFavoriteView.as_view(),
        name="toggle_favorite",
    ),
    path("<int:project_id>/", views.ProjectDetailView.as_view(), name="detail"),
]
