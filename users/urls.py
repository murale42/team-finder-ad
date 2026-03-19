from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("list/", views.ParticipantsListView.as_view(), name="list"),
    path("edit-profile/", views.EditProfileView.as_view(), name="edit_profile"),
    path(
        "change-password/", views.ChangePasswordView.as_view(), name="change_password"
    ),
    path("<int:user_id>/", views.UserDetailView.as_view(), name="detail"),
]
