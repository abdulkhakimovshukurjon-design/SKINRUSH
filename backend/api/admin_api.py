"""Custom admin panel API (replaces the built-in Django admin UI).

All endpoints are session-authenticated and restricted to staff users.
The admin front-end (admin/index.html) is a thin client that calls these.
"""
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import Case, CaseItem, Drop


class CsrfExemptSession(SessionAuthentication):
    """Session auth without CSRF enforcement (same-origin JSON admin)."""

    def enforce_csrf(self, request):
        return


def _case_row(c):
    return {
        "id": c.id,
        "name": c.name,
        "price": c.price,
        "image": c.image,
        "openings": c.openings,
        "items_count": getattr(c, "n_items", None),
        "is_new": c.is_new,
    }


# ---------- auth ----------
@api_view(["GET"])
@authentication_classes([CsrfExemptSession])
@permission_classes([AllowAny])
def admin_me(request):
    u = request.user
    if u.is_authenticated and u.is_staff:
        return Response({"authenticated": True, "username": u.username})
    return Response({"authenticated": False})


@api_view(["POST"])
@authentication_classes([CsrfExemptSession])
@permission_classes([AllowAny])
def admin_login(request):
    user = authenticate(
        request,
        username=(request.data.get("username") or "").strip(),
        password=request.data.get("password") or "",
    )
    if user is None or not user.is_staff:
        return Response({"error": "Login yoki parol noto'g'ri"}, status=400)
    login(request._request, user)
    return Response({"authenticated": True, "username": user.username})


@api_view(["POST"])
@authentication_classes([CsrfExemptSession])
@permission_classes([AllowAny])
def admin_logout(request):
    logout(request._request)
    return Response({"authenticated": False})


# ---------- data ----------
@api_view(["GET"])
@authentication_classes([CsrfExemptSession])
@permission_classes([IsAdminUser])
def admin_stats(request):
    return Response({
        "cases": Case.objects.count(),
        "skins": CaseItem.objects.values("name").distinct().count(),
        "items": CaseItem.objects.count(),
        "drops": Drop.objects.count(),
    })


@api_view(["GET"])
@authentication_classes([CsrfExemptSession])
@permission_classes([IsAdminUser])
def admin_cases(request):
    q = (request.query_params.get("q") or "").strip()
    qs = Case.objects.annotate(n_items=Count("items")).order_by("sort_order", "price")
    if q:
        qs = qs.filter(name__icontains=q)
    return Response([_case_row(c) for c in qs])


@api_view(["GET"])
@authentication_classes([CsrfExemptSession])
@permission_classes([IsAdminUser])
def admin_case_detail(request, pk):
    case = Case.objects.filter(pk=pk).annotate(n_items=Count("items")).first()
    if case is None:
        return Response({"error": "Topilmadi"}, status=404)
    items = [
        {
            "id": it.id, "name": it.name, "weapon": it.weapon, "finish": it.finish,
            "wear": it.wear, "chance": it.chance, "price": it.price,
            "rarity": it.rarity, "color": it.color, "image": it.image,
        }
        for it in case.items.all().order_by("chance")
    ]
    return Response({"case": _case_row(case), "items": items})
