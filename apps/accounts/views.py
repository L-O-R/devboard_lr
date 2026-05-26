from rest_framework.views import APIView
from rest_framework.permissions import AllowAny , IsAuthenticated 
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


from.serializers import (
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer
)


def set_auth_cookie(response, token):
    print(response)
    response.set_cookie(
        key = settings.AUTH_COOKIE_NAME,
        value = token,
        httponly = settings.AUTH_COOKIE_HTTPONLY,
        secure = settings.AUTH_COOKIE_SECURE,
        samesite = settings.AUTH_COOKIE_SAMESITE,
        max_age = settings.AUTH_COOKIE_MAX_AGE,
    )
    return response



class RegisterVIEW(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        seri = RegisterSerializer(data = request.data)

        if seri.is_valid():
            user = seri.save()
            token, _ = Token.objects.get_or_create(user = user)

            response = Response({
                'message': 'Registeration Successfull!',
                'user': UserProfileSerializer.data
            }, status = status.HTTP_201_CREATED),

            return set_auth_cookie(response, token.key)
        
        return Response(seri.errors, status=status.HTTP_400_BAD_REQUEST)
    


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        seri = LoginSerializer(
            data = request.data,
            context = {'request': request}
        )

        if seri.is_valid():
            user = seri.validated_data['user']
            token, _ = Token.objects.get_or_create(user = user)

            response = Response(
                {
                    'message': 'Login Successfully',
                    'user': UserProfileSerializer(user).data
                }, status=status.HTTP_200_OK
            )

            return set_auth_cookie(response, token.key) 
        return Response(
                seri.errors, status=status.HTTP_400_BAD_REQUEST
        ) 



class LogoutView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()

        response = Response(
            {
                'message': "Logout was successfull"
            },
            status=status.HTTP_200_OK
        )

        response.delete_cookie(settings.AUTH_COOKIE_NAME)

        return response


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        seri = UserProfileSerializer(request.user)
        return Response(seri.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        seri = UserProfileSerializer(
            request.user,
            data = request.data,
            partial = True
        )
        if seri.is_valid():
            seri.save()
            return Response(seri.data, status=status.HTTP_200_OK)
        
        return Response(seri.errors , status = status.HTTP_400_BAD_REQUEST)
    