from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Organisation
from .serializers import UserSerializer, RegisterSerializer, OrganisationSerializer
from django.contrib.auth import authenticate
from django.db.models import Q

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "status": "success",
            "message": "Registration successful",
            "data": {
                "accessToken": str(refresh.access_token),
                "user": UserSerializer(user).data
            }
        }, status=status.HTTP_201_CREATED)

    def handle_exception(self, exc):
        if isinstance(exc, ValueError):
            return Response({
                "status": "Bad request",
                "message": "Registration unsuccessful",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)


class LoginView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": str(refresh.access_token),
                    "user": UserSerializer(user).data
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user_id = self.kwargs['userId']

        try:
            # Check if the user is querying their own profile
            if str(user_id) == str(request.user.userId):
                user = request.user
            else:
                # Query to check if the user is in the same organization
                user = User.objects.filter(
                    Q(userId=user_id) & Q(organisations__users=request.user)
                ).distinct().get()

            serializer = self.get_serializer(user)
            return Response({
                "status": "success",
                "message": "User profile fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise NotFound("User not found or not in the same organization.")
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrganisationDetailView(generics.RetrieveAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.request.user not in instance.users.all():  # Correctly accessing the related manager
            raise NotFound("Organisation not found.")
        serializer = self.get_serializer(instance)
        return Response({
            "status": "success",
            "message": "Organisation details fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class OrganisationCreateView(generics.ListCreateAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.organisations.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "message": "Organisations fetched successfully",
            "data": {
                "organisations": serializer.data
            }
        }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        organisation = serializer.save()
        organisation.users.add(self.request.user)
        return organisation

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            "status": "success",
            "message": "Organisation created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrganisationSerializer
        return super().get_serializer_class()


class AddUserToOrganisationView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        org_id = self.kwargs['pk']
        organisation = get_object_or_404(Organisation, orgId=org_id)
        user_id = request.data.get('userId')
        user = get_object_or_404(User, userId=user_id)

        organisation.users.add(user)
        return Response({
            "status": "success",
            "message": "User added to organisation successfully"
        }, status=status.HTTP_200_OK)
