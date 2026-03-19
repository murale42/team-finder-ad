from django import forms
from projects.models import Project
from team_finder.validators import validate_github_url


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "GitHub",
            "status": "Статус проекта",
        }

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url"))
