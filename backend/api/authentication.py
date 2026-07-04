"""Session authentication without CSRF enforcement.

The whole site is same-origin and calls JSON endpoints via fetch. We want
`request.user` populated from the session (so logged-in players are detected)
but without CSRF tokens on every POST. This class does exactly that.
"""
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSession(SessionAuthentication):
    def enforce_csrf(self, request):
        return
