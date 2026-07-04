"""Telegram-based player registration & login.

The Telegram Login Widget sends signed user data; we verify the signature with
the bot token (HMAC-SHA256), then create/refresh a Player and log them into a
Django session. Set these env vars on the server:

    TELEGRAM_BOT_TOKEN     – from @BotFather
    TELEGRAM_BOT_USERNAME  – the bot's @username (no @), used by the widget
"""
import hashlib
import hmac
import os
import time

from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .authentication import CsrfExemptSession
from .models import Player


def _token():
    return os.environ.get("TELEGRAM_BOT_TOKEN", "")


def _username():
    return os.environ.get("TELEGRAM_BOT_USERNAME", "")


def verify_telegram(data):
    """Validate the Login Widget payload against the bot token."""
    token = _token()
    if not token:
        return False
    received = data.get("hash", "")
    pairs = sorted(f"{k}={data[k]}" for k in data if k != "hash")
    check_string = "\n".join(pairs)
    secret = hashlib.sha256(token.encode()).digest()
    calc = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, received):
        return False
    # reject data older than 24h
    try:
        if time.time() - int(data.get("auth_date", 0)) > 86400:
            return False
    except (TypeError, ValueError):
        return False
    return True


def player_payload(p):
    return {
        "authenticated": True,
        "name": p.display_name,
        "username": p.username,
        "photo": p.photo_url,
        "balance": p.balance,
        "coins_purchased": p.coins_purchased,
        "telegram_id": p.telegram_id,
    }


def current_player(request):
    """The logged-in Player for a request (None for anonymous / staff-only)."""
    user = getattr(request, "user", None)
    if not (user and user.is_authenticated):
        return None
    try:
        return user.player
    except Player.DoesNotExist:
        return None


# ---------- endpoints ----------
@api_view(["GET"])
@authentication_classes([CsrfExemptSession])
@permission_classes([AllowAny])
def auth_config(request):
    """Tells the front-end whether Telegram login is configured (bot username)."""
    return Response({"provider": "telegram", "bot": _username(),
                     "enabled": bool(_token() and _username())})


@api_view(["GET"])
@authentication_classes([CsrfExemptSession])
@permission_classes([AllowAny])
def auth_me(request):
    p = current_player(request)
    return Response(player_payload(p) if p else {"authenticated": False})


@api_view(["POST"])
@authentication_classes([CsrfExemptSession])
@permission_classes([AllowAny])
def telegram_login(request):
    data = {k: str(v) for k, v in request.data.items()}
    if not verify_telegram(data):
        return Response({"error": "Telegram tekshiruvi muvaffaqiyatsiz"}, status=400)

    tg_id = int(data["id"])
    player, _ = Player.objects.get_or_create(telegram_id=tg_id)
    player.username = data.get("username", "")
    player.first_name = data.get("first_name", "")
    player.photo_url = data.get("photo_url", "")
    if player.user is None:
        user, _ = User.objects.get_or_create(username=f"tg_{tg_id}")
        player.user = user
    player.save()

    user = player.user
    user.backend = "django.contrib.auth.backends.ModelBackend"
    login(request._request, user)
    return Response(player_payload(player))


@api_view(["POST"])
@authentication_classes([CsrfExemptSession])
@permission_classes([AllowAny])
def auth_logout(request):
    logout(request._request)
    return Response({"authenticated": False})
