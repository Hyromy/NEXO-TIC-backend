from django.db.transaction import atomic
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.api.decorators import require_fields
from apps.mail.mails import welcome

from utils.randomizer import generate_password
from utils.validator import is_email

class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

class MyTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

@api_view(['POST'])
@permission_classes([AllowAny])
@require_fields([
    ('username', str),
    ('email', str),
])
def signup(request: Request) -> Response:
    data = request.data

    if not is_email(data['email']):
        return Response(
            {"error": "Invalid email address."},
            status = status.HTTP_400_BAD_REQUEST
        )

    try:
        if User.objects.filter(username = data['username'], email = data['email']).exists():
            raise Exception("User already exists.")

        tmp_pass = generate_password(use_upper = True, use_numbers = True)
        with atomic():
            user = User.objects.create_user(
                username = data['username'],
                email = data['email'],
                password = tmp_pass
            )
    
            welcome(
                user = user,
                tmp_pass = tmp_pass
            )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status = status.HTTP_400_BAD_REQUEST
        )
    
    else:
        return Response(
            {"ok": True},
            status = status.HTTP_201_CREATED
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_fields(("refresh", str))
def logout(request: Request) -> Response:
    try:
        refresh_token = request.data.get("refresh")        
        if not refresh_token:
            raise Exception("Refresh token is required")

        token = RefreshToken(refresh_token)
        token.blacklist()
    
    except:
        return Response(
            {"error": "Invalid token"},
            status = status.HTTP_400_BAD_REQUEST
        )
    
    else:
        return Response(
            {"ok": True},
            status = status.HTTP_200_OK
        )
