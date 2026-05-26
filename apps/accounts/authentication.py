from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class CookieAuthentication(TokenAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get(settings.AUTH_COOKIE_NAME)

        if token:
            return self.authenticate_credentials(token)
        
        return super().authenticate(request)
    