from django.db import models
from django.conf import settings

class Discipline(models.Model):
    name = models.TextField("Название")
    genre = models.TextField("Жанр", blank=True)
    description = models.TextField("Описание", blank=True)
    picture = models.ImageField("Изображение", null=True, blank=True, upload_to="disciplines")
    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"

    def __str__(self):
        return self.name

class Organizer(models.Model):
    name = models.TextField("Название")
    email = models.EmailField("Электронная почта")
    social_media = models.TextField("Социальные сети")
    picture = models.ImageField("Логотип организатора", null=True, blank=True, upload_to="organizers")
    class Meta:
        verbose_name = "Организатор"
        verbose_name_plural = "Организаторы"

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.TextField("Название")
    country = models.TextField("Страна")
    founded_year = models.PositiveIntegerField("Год основания")

    picture = models.ImageField(
        "Логотип команды",
        null=True,
        blank=True,
        upload_to="teams"
    )

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"

    def __str__(self):
        return self.name

class Tournament(models.Model):
    
    class Status(models.TextChoices):
        REGISTRATION = "registration", "Регистрация открыта"
        CLOSED = "closed", "Регистрация закрыта"
        ONGOING = "ongoing", "Проводится"
        FINISHED = "finished", "Завершён"

    status = models.CharField(
        "Статус турнира",
        max_length=16,
        choices=Status.choices,
        default=Status.REGISTRATION
    )
    name = models.TextField("Название")
    start_date = models.DateField("Дата начала", null=True, blank=True)
    end_date = models.DateField("Дата окончания", null=True, blank=True)
    prize_pool = models.DecimalField(
        "Призовой фонд",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True
    )
    picture = models.ImageField("Изображение", null=True, blank=True, upload_to="tournaments")
   
    discipline = models.ForeignKey(
        "Discipline",
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Дисциплина"
    )

    organizer = models.ForeignKey(
        "Organizer",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Организатор"
    )

    class Meta:
        verbose_name = "Турнир"
        verbose_name_plural = "Турниры"

    def __str__(self):
        return self.name

class UserProfile(models.Model):

    class Role(models.TextChoices):
        PLAYER = "player", "Игрок"
        ADMIN = "admin", "Администратор"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Аккаунт"
    )

    nickname = models.TextField("Никнейм")
    real_name = models.TextField("Настоящее имя")

    role = models.CharField(
        "Роль",
        max_length=16,
        choices=Role.choices,
        default=Role.PLAYER
    )

    game_role = models.TextField("Игровая роль", blank=True)
    rating = models.FloatField("Рейтинг", null=True, blank=True)
    email = models.EmailField("Контактная почта", blank=True)
    picture = models.ImageField("Аватар", null=True, blank=True, upload_to="users")

    otp_key = models.CharField(
        "Ключ двухфакторной аутентификации",
        max_length=32,
        blank=True
    )

    team = models.ForeignKey(
        "Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Команда"
    )
    is_captain = models.BooleanField(
        "Капитан команды",
        default=False
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return self.nickname

class TournamentApplication(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "На рассмотрении"
        APPROVED = "approved", "Подтверждена"
        REJECTED = "rejected", "Отклонена"

    team = models.ForeignKey(
        "Team",
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Команда"
    )

    tournament = models.ForeignKey(
        "Tournament",
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Турнир"
    )

    submitted_by = models.ForeignKey(
        "UserProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_applications",
        verbose_name="Заявку подал"
    )

    status = models.CharField(
        "Статус заявки",
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(
        "Дата подачи",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Заявка на турнир"
        verbose_name_plural = "Заявки на турниры"

    def __str__(self):
        return f"{self.team} — {self.tournament}"