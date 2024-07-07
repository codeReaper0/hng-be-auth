from django.urls import path
from .views import RegisterView, LoginView, UserProfileView, AddUserToOrganisationView, OrganisationDetailView, OrganisationCreateView

urlpatterns = [
    path('auth/register', RegisterView.as_view()),
    path('auth/login', LoginView.as_view()),
    path('api/users/<uuid:userId>', UserProfileView.as_view()),
    path('api/organisations', OrganisationCreateView.as_view()),
    path('api/organisations/<uuid:pk>', OrganisationDetailView.as_view()),
    path('api/organisations/<uuid:pk>/users',
         AddUserToOrganisationView.as_view()),
]
