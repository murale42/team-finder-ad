from django import forms
from team_finder.constants import GITHUB_DOMAIN, GITHUB_URL_ERROR


def validate_github_url(url: str | None) -> str:
    normalized_url = (url or "").strip()
    if not normalized_url:
        return ""
    if GITHUB_DOMAIN not in normalized_url.lower():
        raise forms.ValidationError(GITHUB_URL_ERROR)
    return normalized_url
