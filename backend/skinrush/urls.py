"""Root URL configuration for SKINRUSH.

Besides the API, Django also serves the static front-end (index.html, styles,
app.js, images) so the whole site runs from one backend on one origin. That
keeps the session cookie working for the per-user state endpoints.
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve as static_serve

FRONTEND_DIR = settings.FRONTEND_DIR


def index(request):
    return static_serve(request, "index.html", document_root=FRONTEND_DIR)


def admin_panel(request):
    # Custom admin single-page app. Auth is enforced by the /api/admin/* endpoints.
    return static_serve(request, "admin/index.html", document_root=FRONTEND_DIR)


urlpatterns = [
    # Custom admin panel (our own UI) — reached only via this URL, no link on the site.
    path("adminpanel/", admin_panel, name="adminpanel"),
    # Built-in Django admin kept as a hidden fallback only.
    path("django-admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("", index, name="index"),
    # Any other path is a front-end asset (styles.css, app.js, images/...).
    re_path(r"^(?P<path>.+)$", static_serve, {"document_root": FRONTEND_DIR}),
]
