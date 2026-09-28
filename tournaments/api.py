import pyotp
import openpyxl

from django.http import HttpResponse
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from tournaments.permissions import OTPRequired, IsAdmin
from rest_framework.exceptions import PermissionDenied, ValidationError

from tournaments.serializers import OTPSerializer, LoginSerializer, TournamentApplicationSerializer

from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Count, Sum, Avg, Q

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from tournaments.models import (
    Tournament,
    Discipline,
    Organizer,
    Team,
    UserProfile,
    TournamentApplication
)

from tournaments.serializers import (
    TournamentSerializer,
    DisciplineSerializer,
    OrganizerSerializer,
    TeamSerializer,
    UserProfileSerializer
)



class DisciplineViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):

    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        name = self.request.query_params.get("name")
        genre = self.request.query_params.get("genre")
        description = self.request.query_params.get("description")
        if name:
            queryset = queryset.filter(name__icontains=name)

        if genre:
            queryset = queryset.filter(genre__icontains=genre)

        if description:
            queryset = queryset.filter(description__icontains=description)

        return queryset

    def get_permissions(self):
        permissions = [IsAuthenticated()]

        if self.action not in ["list", "retrieve"]:
            permissions.append(IsAdmin())

        if self.action in ["update", "partial_update"]:
            permissions.append(OTPRequired())

        return permissions

    @action(detail=False, methods=["GET"])
    def stats(self, request):
        statistics = self.get_queryset().aggregate(
            total=Count("id"),
            total_genres=Count("genre", distinct=True)
        )

        return Response(statistics)

class OrganizerViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):

    queryset = Organizer.objects.all()
    serializer_class = OrganizerSerializer


    def get_queryset(self):
        queryset = super().get_queryset()

        name = self.request.query_params.get("name")
        email = self.request.query_params.get("email")
        social_media = self.request.query_params.get("social_media")

        if name:
            queryset = queryset.filter(name__icontains=name)

        if email:
            queryset = queryset.filter(email__icontains=email)

        if social_media:
            queryset = queryset.filter(social_media__icontains=social_media)

        return queryset

    def get_permissions(self):
        permissions = [IsAuthenticated()]

        if self.action not in ["list", "retrieve"]:
            permissions.append(IsAdmin())

        if self.action in ["update", "partial_update"]:
            permissions.append(OTPRequired())

        return permissions
    
    @action(detail=False, methods=["GET"])
    def stats(self, request):
        statistics = self.get_queryset().aggregate(
            total=Count("id"),
            total_emails=Count("email", distinct=True)
        )

        return Response(statistics)


class TournamentViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):

    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permissions = [IsAuthenticated()]

        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "stats",
            "export_excel"
        ]:
            permissions.append(IsAdmin())

        if self.action in ["update", "partial_update"]:
            permissions.append(OTPRequired())

        return permissions
    
    
    def get_queryset(self):
        queryset = super().get_queryset()

        name = self.request.query_params.get("name")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        prize_pool_min = self.request.query_params.get("prize_pool_min")
        prize_pool_max = self.request.query_params.get("prize_pool_max")
        discipline_id = self.request.query_params.get("discipline_id")
        organizer_id = self.request.query_params.get("organizer_id")
        status = self.request.query_params.get("status")
        team_id = self.request.query_params.get("team_id")

        if name:
            queryset = queryset.filter(name__icontains=name)

        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)

        if prize_pool_min:
            queryset = queryset.filter(prize_pool__gte=prize_pool_min)

        if prize_pool_max:
            queryset = queryset.filter(prize_pool__lte=prize_pool_max)

        if discipline_id:
            queryset = queryset.filter(discipline_id=discipline_id)

        if organizer_id:
            queryset = queryset.filter(organizer_id=organizer_id)
        if status:
            queryset = queryset.filter(status=status)

        if team_id:
            queryset = queryset.filter(
                applications__team_id=team_id,
                applications__status=TournamentApplication.Status.APPROVED
            ).distinct()

        return queryset

    @action(detail=False, methods=["GET"])
    def stats(self, request):
        queryset = self.get_queryset()

        statistics = queryset.aggregate(
            total=Count("id"),
            total_prize_pool=Sum("prize_pool"),
            average_prize_pool=Avg("prize_pool")
        )

        return Response(statistics)


    @action(
        detail=False,
        methods=["GET"],
        url_path="export-excel"
    )
    def export_excel(self, request, *args, **kwargs):

        queryset = self.get_queryset()

        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        worksheet.title = "Турниры"

        worksheet.append([
            "ID",
            "Название",
            "Дата начала",
            "Дата окончания",
            "Призовой фонд",
            "Дисциплина",
            "Организатор"
        ])

        for tournament in queryset:
            worksheet.append([
                tournament.id,
                tournament.name,
                str(tournament.start_date) if tournament.start_date else "",
                str(tournament.end_date) if tournament.end_date else "",
                float(tournament.prize_pool) if tournament.prize_pool is not None else None,
                tournament.discipline.name if tournament.discipline else "",
                tournament.organizer.name if tournament.organizer else ""
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response["Content-Disposition"] = (
            'attachment; filename="tournaments.xlsx"'
        )

        workbook.save(response)

        return response

class TeamViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):

    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        name = self.request.query_params.get("name")
        country = self.request.query_params.get("country")
        founded_year_min = self.request.query_params.get("founded_year_min")
        founded_year_max = self.request.query_params.get("founded_year_max")

        if name:
            queryset = queryset.filter(name__icontains=name)

        if country:
            queryset = queryset.filter(country__icontains=country)

        if founded_year_min:
            queryset = queryset.filter(
                founded_year__gte=founded_year_min
            )

        if founded_year_max:
            queryset = queryset.filter(
                founded_year__lte=founded_year_max
            )

        return queryset

    
    def get_permissions(self):
        permissions = [IsAuthenticated()]

        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "stats"
        ]:
            permissions.append(IsAdmin())

        if self.action in ["update", "partial_update"]:
            permissions.append(OTPRequired())

        return permissions

    @action(detail=False, methods=["GET"])
    def stats(self, request):
        statistics = self.get_queryset().aggregate(
            total=Count("id"),
            total_countries=Count("country", distinct=True),
            average_founded_year=Avg("founded_year")
        )

        return Response(statistics)


class UserProfileViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_superuser:
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                raise PermissionDenied(
                    "Профиль пользователя не найден"
                )

            if profile.role == UserProfile.Role.PLAYER:

                if profile.team_id:
                    queryset = queryset.filter(
                        team_id=profile.team_id
                    )
                else:
                    queryset = queryset.filter(
                        user=user
                    )

            elif profile.role != UserProfile.Role.ADMIN:
                raise PermissionDenied(
                    "Доступ к участникам запрещён"
                )

        nickname = self.request.query_params.get("nickname")
        real_name = self.request.query_params.get("real_name")
        role = self.request.query_params.get("role")
        game_role = self.request.query_params.get("game_role")
        rating_min = self.request.query_params.get("rating_min")
        rating_max = self.request.query_params.get("rating_max")
        email = self.request.query_params.get("email")
        team_id = self.request.query_params.get("team_id")

        if nickname:
            queryset = queryset.filter(
                nickname__icontains=nickname
            )

        if real_name:
            queryset = queryset.filter(
                real_name__icontains=real_name
            )

        if role:
            queryset = queryset.filter(role=role)

        if game_role:
            queryset = queryset.filter(
                game_role__icontains=game_role
            )

        if rating_min:
            queryset = queryset.filter(
                rating__gte=rating_min
            )

        if rating_max:
            queryset = queryset.filter(
                rating__lte=rating_max
            )

        if email:
            queryset = queryset.filter(
                email__icontains=email
            )

        if team_id:
            queryset = queryset.filter(team_id=team_id)

        return queryset

    
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]

        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "stats"
        ]:
            permissions = [
                IsAuthenticated(),
                IsAdmin()
            ]

            if self.action in ["update", "partial_update"]:
                permissions.append(OTPRequired())

            return permissions

        return super().get_permissions()

    @action(
        detail=False,
        url_path="check-login",
        methods=["GET"],
        permission_classes=[]
    )
    def get_check_login(self, request, *args, **kwargs):
        return Response({
            "is_authenticated": request.user.is_authenticated
        })

    @action(
        detail=False,
        url_path="info",
        methods=["GET"],
        permission_classes=[]
    )
    def info(self, request, *args, **kwargs):

        auth_user = request.user

        is_auth = auth_user.is_authenticated

        data = {
            "is_authenticated": is_auth,
            "is_superuser": (
                bool(auth_user.is_superuser)
                if is_auth else False
            ),
            "username": (
                auth_user.username
                if is_auth else None
            )
        }

        role = None

        
        is_captain = False
        team_id = None

        if is_auth:
            try:
                profile = auth_user.profile
                role = profile.role
                team_id = profile.team_id
                is_captain = profile.is_captain

            except UserProfile.DoesNotExist:
                role = None

        is_admin = bool(
            (is_auth and auth_user.is_superuser)
            or role == UserProfile.Role.ADMIN
        )

        data.update({
            "role": role,
            "is_admin": is_admin,
            "is_captain": is_captain,
            "team_id": team_id
        })

        return Response(data)
   
    @action(
        detail=False,
        url_path="me",
        methods=["GET"],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({
                "detail": "Профиль пользователя не найден"
            }, status=404)

        serializer = self.get_serializer(profile)

        return Response(serializer.data)
    
    @action(
        detail=False,
        url_path="login",
        methods=["POST"],
        serializer_class=LoginSerializer,
        permission_classes=[]
    )
    def user_login(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            return Response({
                "success": True
            })

        return Response({
            "success": False
        }, status=400)
    @action(
        detail=False,
        url_path="logout",
        methods=["POST"],
        permission_classes=[IsAuthenticated]
        )
    def user_logout(self, request, *args, **kwargs):
        logout(request)

        return Response({
                "success": True
        })


    @action(
    detail=False,
    url_path="otp-setup",
    methods=["GET"],
    permission_classes=[IsAuthenticated, IsAdmin]
)
    def otp_setup(self, request, *args, **kwargs):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({
                "detail": "Профиль пользователя не найден"
            }, status=404)

        if not profile.otp_key:
            profile.otp_key = pyotp.random_base32()
            profile.save(update_fields=["otp_key"])

        totp = pyotp.TOTP(profile.otp_key)

        url = totp.provisioning_uri(
            name=request.user.username,
            issuer_name="Киберспортивные турниры"
        )

        return Response({
            "url": url
        })
    
    @action(
        detail=False,
        url_path="otp-login",
        methods=["POST"],
        serializer_class=OTPSerializer,
        permission_classes=[IsAuthenticated]
    )
    
    def otp_login(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({
                "success": False,
                "detail": "Профиль пользователя не найден"
            }, status=400)

        if not profile.otp_key:
            return Response({
                "success": False,
                "detail": "Ключ OTP не настроен"
            }, status=400)

        totp = pyotp.TOTP(profile.otp_key)

        success = totp.verify(
            serializer.validated_data["key"]
        )

        if success:
            cache.set(
                f"otp_good_{request.user.pk}",
                True,
                timeout=300
            )

        return Response({
            "success": success
        })


    @action(
        detail=False,
        url_path="otp-status",
        methods=["GET"],
        permission_classes=[IsAuthenticated]
    )
    def otp_status(self, request, *args, **kwargs):
        return Response({
            "otp_good": bool(
                cache.get(
                    f"otp_good_{request.user.pk}",
                    False
                )
            )
        })
    
    @action(detail=False, methods=["GET"])
    def stats(self, request):
        statistics = self.get_queryset().aggregate(
            total=Count("id"),
            total_players=Count(
                "id",
                filter=Q(role="player")
            ),
            total_admins=Count(
                "id",
                filter=Q(role="admin")
            ),
            average_rating=Avg("rating")
        )

        return Response(statistics)


class TournamentApplicationViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):

    queryset = TournamentApplication.objects.all()
    serializer_class = TournamentApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permissions = [IsAuthenticated()]

        if self.action in [
            "update",
            "partial_update",
            "destroy",
            "approve",
            "reject",
            "stats"
        ]:
            permissions.append(IsAdmin())

        if self.action in [
            "update",
            "partial_update",
            "approve",
            "reject"
        ]:
            permissions.append(OTPRequired())

        return permissions

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_superuser:
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                raise PermissionDenied(
                    "Профиль пользователя не найден"
                )

            if profile.role == UserProfile.Role.ADMIN:
                pass

            elif (
                profile.role == UserProfile.Role.PLAYER
                and profile.team_id
                and profile.is_captain
            ):
                queryset = queryset.filter(
                    submitted_by=profile
                )

            else:
                raise PermissionDenied(
                    "Просмотр заявок доступен только капитану команды"
                )

        team_id = self.request.query_params.get("team_id")
        tournament_id = self.request.query_params.get("tournament_id")
        submitted_by_id = self.request.query_params.get("submitted_by_id")
        status = self.request.query_params.get("status")
        created_at_from = self.request.query_params.get("created_at_from")
        created_at_to = self.request.query_params.get("created_at_to")

        if team_id:
            queryset = queryset.filter(team_id=team_id)

        if tournament_id:
            queryset = queryset.filter(
                tournament_id=tournament_id
            )

        if submitted_by_id:
            queryset = queryset.filter(
                submitted_by_id=submitted_by_id
            )

        if status:
            queryset = queryset.filter(status=status)

        if created_at_from:
            queryset = queryset.filter(
                created_at__date__gte=created_at_from
            )

        if created_at_to:
            queryset = queryset.filter(
                created_at__date__lte=created_at_to
            )

        return queryset

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_superuser:
            raise PermissionDenied(
                "Заявки подаются только капитанами команд"
            )

        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            raise PermissionDenied(
                "Профиль пользователя не найден"
            )

        if profile.role != UserProfile.Role.PLAYER:
            raise PermissionDenied(
                "Заявки подаются только капитанами команд"
            )

        team = serializer.validated_data["team"]
        tournament = serializer.validated_data["tournament"]

        if (
            profile.team_id != team.id
            or not profile.is_captain
        ):
            raise PermissionDenied(
                "Вы не являетесь капитаном этой команды"
            )

        players_count = UserProfile.objects.filter(
            team=team,
            role=UserProfile.Role.PLAYER
        ).count()

        if players_count < 5:
            raise ValidationError({
                "team": "Для регистрации необходимо минимум 5 игроков"
            })

        if tournament.status != Tournament.Status.REGISTRATION:
            raise ValidationError({
                "tournament": "Регистрация на этот турнир закрыта"
            })

        existing_application = TournamentApplication.objects.filter(
            team=team,
            tournament=tournament,
            status__in=[
                TournamentApplication.Status.PENDING,
                TournamentApplication.Status.APPROVED
            ]
        ).exists()

        if existing_application:
            raise ValidationError({
                "team": "У команды уже есть действующая заявка на этот турнир"
            })

        serializer.save(
            submitted_by=profile
        )

    @action(
        detail=True,
        methods=["POST"],
        url_path="approve"
    )
    def approve(self, request, pk=None):

        application = self.get_object()

        if application.status != TournamentApplication.Status.PENDING:
            raise ValidationError({
                "status": "Заявка уже рассмотрена"
            })

        players_count = UserProfile.objects.filter(
            team=application.team,
            role=UserProfile.Role.PLAYER
        ).count()

        if players_count < 5:
            raise ValidationError({
                "team": "В команде должно быть минимум 5 игроков"
            })

        if application.tournament.status == Tournament.Status.FINISHED:
            raise ValidationError({
                "tournament": "Турнир уже завершён"
            })

        application.status = TournamentApplication.Status.APPROVED

        application.save(
            update_fields=["status"]
        )

        return Response(
            self.get_serializer(application).data
        )
    
    @action(
        detail=True,
        methods=["POST"],
        url_path="reject"
    )
    def reject(self, request, pk=None):

        application = self.get_object()

        if application.status != TournamentApplication.Status.PENDING:
            raise ValidationError({
                "status": "Заявка уже рассмотрена"
            })

        application.status = TournamentApplication.Status.REJECTED

        application.save(
            update_fields=["status"]
        )

        return Response(
            self.get_serializer(application).data
        )
    @action(detail=False, methods=["GET"])
    def stats(self, request):
        statistics = self.get_queryset().aggregate(
            total=Count("id"),
            pending=Count(
                "id",
                filter=Q(status=TournamentApplication.Status.PENDING)
            ),
            approved=Count(
                "id",
                filter=Q(status=TournamentApplication.Status.APPROVED)
            ),
            rejected=Count(
                "id",
                filter=Q(status=TournamentApplication.Status.REJECTED)
            )
        )

        return Response(statistics)