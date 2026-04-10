"""Authentication views — login, logout, and current-user info."""

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class LoginView(APIView):
    """Authenticate a user and return an auth token."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "")

        if not username or not password:
            return Response(
                {"error": "Both username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)
        if user is None:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.pk,
            "username": user.username,
        })


class LogoutView(APIView):
    """Delete the user's auth token to log them out."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out."})


class CurrentUserView(APIView):
    """Return profile info for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "user_id": user.pk,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        })
