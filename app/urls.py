"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from tournaments import views
from tournaments.api import (
    TournamentViewset,
    DisciplineViewset,
    OrganizerViewset,
    TeamViewset,
    UserProfileViewset,
    TournamentApplicationViewset
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register("tournaments", TournamentViewset, basename="tournaments")
router.register("disciplines", DisciplineViewset, basename="disciplines")
router.register("organizers", OrganizerViewset, basename="organizers")
router.register("teams", TeamViewset, basename="teams")
router.register("userprofiles", UserProfileViewset, basename="userprofiles")
router.register("applications", TournamentApplicationViewset, basename="applications")

urlpatterns = [

    path("api-auth/", include("rest_framework.urls")),
    path('admin/', admin.site.urls),
    path('', views.ShowTournamentsView.as_view()),
    path('api/', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)