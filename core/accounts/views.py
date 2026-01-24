from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, LoginSerializer
from core.utils.message import Message
from commons.permissions import IsSuperAdmin, IsPlatformAdmin


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        operation_description="Register a new user",
        tags=["Auth"],
        responses={
            201: openapi.Response('User created successfully', UserSerializer),
            400: 'Bad Request'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': Message(resource="User").created_success(),
                'data': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'message': Message(resource="User").created_failed(),
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """
    User login endpoint.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_description="Login endpoint",
        tags=["Auth"],
        request_body=LoginSerializer,
        responses={
            200: openapi.Response('Login successful'),
            400: 'Bad Request',
            401: 'Unauthorized'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': Message.login_success(),
                'data': {
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'message': Message.login_failed(),
            'errors': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(generics.GenericAPIView):
    """
    User logout endpoint.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout endpoint",
        tags=["Auth"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Refresh token to blacklist'
                )
            }
        ),
        responses={
            200: openapi.Response('Logout successful'),
            401: 'Unauthorized'
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({
                'message': Message.logout()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': Message.logout(),
                'error': str(e)
            }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """
    Endpoint for Admins to list all users with filtering.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsPlatformAdmin]

    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    @swagger_auto_schema(
        operation_description="List all users (Admin only). Filter by role using ?role=...",
        tags=["Accounts"],
        manual_parameters=[
            openapi.Parameter('role', openapi.IN_QUERY, description="Filter by user role", type=openapi.TYPE_STRING)
        ],
        responses={
            200: UserSerializer(many=True),
            403: 'Forbidden'
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
