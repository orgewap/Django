
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from faker import Faker

from uuid import uuid4
import random

from tournaments.models import (
    Discipline,
    Organizer,
    Team,
    Tournament,
    UserProfile
)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "--members-only",
            action="store_true"
        )


    def handle(self, *args, **options):
        fake = Faker(["ru_RU"])

        if not options["members_only"]:
            self.generate_main_data(fake)

        self.generate_members(fake)


    def generate_main_data(self, fake):

        disciplines = []

        for _ in range(1000):
            discipline = Discipline.objects.create(
                name=fake.word().capitalize(),
                genre=fake.word(),
                description=fake.sentence()
            )

            disciplines.append(discipline)

        organizers = []

        for _ in range(1000):
            organizer = Organizer.objects.create(
                name=fake.company(),
                email=fake.email(),
                social_media=fake.url()
            )

            organizers.append(organizer)

        for _ in range(1000):
            Team.objects.create(
                name=fake.company(),
                country=fake.country(),
                founded_year=fake.random_int(
                    min=2000,
                    max=2026
                )
            )

        for _ in range(1000):
            Tournament.objects.create(
                name=fake.company() + " Cup",
                start_date=fake.date_between(
                    start_date="-1y",
                    end_date="+1y"
                ),
                prize_pool=fake.random_int(
                    min=10000,
                    max=1000000
                ),
                discipline=fake.random_element(
                    elements=disciplines
                ),
                organizer=fake.random_element(
                    elements=organizers
                )
            )


    def generate_members(self, fake):

        User = get_user_model()

        current_count = UserProfile.objects.count()
        members_to_create = max(0, 1000 - current_count)

        team_ids = list(
            Team.objects.values_list("id", flat=True)
        )

        game_roles = [
            "Снайпер",
            "Стрелок",
            "Поддержка",
            "Саппорт",
            "Керри"
        ]

        for _ in range(members_to_create):

            unique_id = uuid4().hex

            with transaction.atomic():

                user = User.objects.create_user(
                    username=f"generated_{unique_id}",
                    password=None
                )

                UserProfile.objects.create(
                    user=user,
                    nickname=f"player_{unique_id[:12]}",
                    real_name=fake.name(),
                    role="player",
                    game_role=random.choice(game_roles),
                    rating=round(
                        random.uniform(1.0, 10.0),
                        2
                    ),
                    email=fake.email(),
                    team_id=(
                        random.choice(team_ids)
                        if team_ids else None
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Создано участников: {members_to_create}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Всего профилей: {UserProfile.objects.count()}"
            )
        )