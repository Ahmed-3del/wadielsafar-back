from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from apps.users.serializers import UserSerializer


def _set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=str(refresh_token),
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        path=settings.REFRESH_TOKEN_COOKIE_PATH,
        httponly=True,
        secure=True,
        samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
    )


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data

        response = Response({"access": str(tokens["access"])}, status=status.HTTP_200_OK)
        _set_refresh_cookie(response, tokens["refresh"])
        return response


class RefreshView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        if not refresh_token:
            return Response(
                {"detail": "Refresh cookie missing."}, status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response(
                {"detail": "Refresh token invalid or expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = serializer.validated_data
        response = Response({"access": str(tokens["access"])}, status=status.HTTP_200_OK)

        # ROTATE_REFRESH_TOKENS=True means a new refresh comes back on every
        # call — re-issue the cookie so it stays in sync with the server.
        if "refresh" in tokens:
            _set_refresh_cookie(response, tokens["refresh"])
        return response


class LogoutView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(
            key=settings.REFRESH_TOKEN_COOKIE_NAME,
            path=settings.REFRESH_TOKEN_COOKIE_PATH,
            samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
        )
        return response


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)
