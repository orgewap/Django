from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.test import APIClient
from model_bakery import baker

from tournaments.models import Discipline, Organizer, Team, Tournament, UserProfile, TournamentApplication


class DisciplineViewsetTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_superuser(
            username="admin",
            password="admin"
        )

        self.client.login(
            username="admin",
            password="admin"
        )

    def test_get_list(self):
        discipline = baker.make("tournaments.Discipline")

        r = self.client.get("/api/disciplines/")
        data = r.json()

        assert discipline.name == data[0]["name"]
        assert discipline.id == data[0]["id"]
        assert len(data) == 1

    def test_create_discipline(self):
        r = self.client.post("/api/disciplines/", {
            "name": "Counter-Strike 2",
            "genre": "Шутер",
            "description": "Командная дисциплина"
        })

        new_discipline_id = r.json()["id"]

        disciplines = Discipline.objects.all()
        assert len(disciplines) == 1

        new_discipline = Discipline.objects.filter(
            id=new_discipline_id
        ).first()

        assert new_discipline.name == "Counter-Strike 2"
        assert new_discipline.genre == "Шутер"
        assert new_discipline.description == "Командная дисциплина"

    def test_delete_discipline(self):
        disciplines = baker.make(
            "tournaments.Discipline",
            10
        )

        r = self.client.get("/api/disciplines/")
        data = r.json()

        assert len(data) == 10

        discipline_id_to_delete = disciplines[3].id

        self.client.delete(
            f"/api/disciplines/{discipline_id_to_delete}/"
        )

        r = self.client.get("/api/disciplines/")
        data = r.json()

        assert len(data) == 9

        assert discipline_id_to_delete not in [
            i["id"] for i in data
        ]

    def test_update_discipline(self):
        discipline = baker.make(
            "tournaments.Discipline"
        )

        cache.set(
            f"otp_good_{self.user.pk}",
            True,
            timeout=300
        )

        r = self.client.get(
            f"/api/disciplines/{discipline.id}/"
        )

        data = r.json()

        assert data["name"] == discipline.name

        r = self.client.put(
            f"/api/disciplines/{discipline.id}/",
            {
                "name": "Dota 2",
                "genre": "MOBA",
                "description": "Командная дисциплина"
            }
        )

        assert r.status_code == 200

        r = self.client.get(
            f"/api/disciplines/{discipline.id}/"
        )

        data = r.json()

        assert data["name"] == "Dota 2"
        assert data["genre"] == "MOBA"

        discipline.refresh_from_db()

        assert data["name"] == discipline.name
class OrganizerViewsetTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_superuser(
            username="admin",
            password="admin"
        )

        self.client.login(
            username="admin",
            password="admin"
        )

    def test_get_list(self):
        organizer = baker.make("tournaments.Organizer")

        r = self.client.get("/api/organizers/")
        data = r.json()

        assert organizer.name == data[0]["name"]
        assert organizer.id == data[0]["id"]
        assert len(data) == 1

    def test_create_organizer(self):
        r = self.client.post("/api/organizers/", {
            "name": "ESL",
            "email": "esl@example.com",
            "social_media": "https://example.com/esl"
        })

        new_organizer_id = r.json()["id"]

        organizers = Organizer.objects.all()
        assert len(organizers) == 1

        new_organizer = Organizer.objects.filter(
            id=new_organizer_id
        ).first()

        assert new_organizer.name == "ESL"
        assert new_organizer.email == "esl@example.com"
        assert new_organizer.social_media == "https://example.com/esl"

    def test_delete_organizer(self):
        organizers = baker.make(
            "tournaments.Organizer",
            10
        )

        r = self.client.get("/api/organizers/")
        data = r.json()

        assert len(data) == 10

        organizer_id_to_delete = organizers[3].id

        self.client.delete(
            f"/api/organizers/{organizer_id_to_delete}/"
        )

        r = self.client.get("/api/organizers/")
        data = r.json()

        assert len(data) == 9

        assert organizer_id_to_delete not in [
            i["id"] for i in data
        ]

    def test_update_organizer(self):
        organizer = baker.make(
            "tournaments.Organizer"
        )

        cache.set(
            f"otp_good_{self.user.pk}",
            True,
            timeout=300
        )

        r = self.client.put(
            f"/api/organizers/{organizer.id}/",
            {
                "name": "BLAST",
                "email": "blast@example.com",
                "social_media": "https://example.com/blast"
            }
        )

        assert r.status_code == 200

        organizer.refresh_from_db()

        assert organizer.name == "BLAST"
        assert organizer.email == "blast@example.com"
        assert organizer.social_media == "https://example.com/blast"
class TeamViewsetTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_superuser(
            username="admin",
            password="admin"
        )

        self.client.login(
            username="admin",
            password="admin"
        )

    def test_get_list(self):
        team = baker.make("tournaments.Team")

        r = self.client.get("/api/teams/")
        data = r.json()

        assert team.name == data[0]["name"]
        assert team.id == data[0]["id"]
        assert len(data) == 1

    def test_create_team(self):
        r = self.client.post("/api/teams/", {
            "name": "NAVI",
            "country": "Украина",
            "founded_year": 2009
        })

        new_team_id = r.json()["id"]

        teams = Team.objects.all()
        assert len(teams) == 1

        new_team = Team.objects.filter(
            id=new_team_id
        ).first()

        assert new_team.name == "NAVI"
        assert new_team.country == "Украина"
        assert new_team.founded_year == 2009

    def test_delete_team(self):
        teams = baker.make(
            "tournaments.Team",
            10
        )

        r = self.client.get("/api/teams/")
        data = r.json()

        assert len(data) == 10

        team_id_to_delete = teams[3].id

        self.client.delete(
            f"/api/teams/{team_id_to_delete}/"
        )

        r = self.client.get("/api/teams/")
        data = r.json()

        assert len(data) == 9

        assert team_id_to_delete not in [
            i["id"] for i in data
        ]

    def test_update_team(self):
        team = baker.make(
            "tournaments.Team"
        )

        cache.set(
            f"otp_good_{self.user.pk}",
            True,
            timeout=300
        )

        r = self.client.put(
            f"/api/teams/{team.id}/",
            {
                "name": "Team Spirit",
                "country": "Россия",
                "founded_year": 2015
            }
        )

        assert r.status_code == 200

        team.refresh_from_db()

        assert team.name == "Team Spirit"
        assert team.country == "Россия"
        assert team.founded_year == 2015
class TournamentViewsetTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_superuser(
            username="admin",
            password="admin"
        )

        self.client.login(
            username="admin",
            password="admin"
        )

        self.discipline = baker.make(
            "tournaments.Discipline"
        )

        self.organizer = baker.make(
            "tournaments.Organizer"
        )

    def test_get_list(self):
        tournament = baker.make(
            "tournaments.Tournament",
            discipline=self.discipline,
            organizer=self.organizer
        )

        r = self.client.get("/api/tournaments/")
        data = r.json()

        assert tournament.name == data[0]["name"]
        assert tournament.id == data[0]["id"]
        assert len(data) == 1

    def test_create_tournament(self):
        r = self.client.post("/api/tournaments/", {
            "name": "Cyber Masters",
            "discipline_id": self.discipline.id,
            "organizer": self.organizer.id,
            "start_date": "2026-10-01",
            "end_date": "2026-10-05",
            "prize_pool": "100000.00"
        })

        new_tournament_id = r.json()["id"]

        tournaments = Tournament.objects.all()
        assert len(tournaments) == 1

        new_tournament = Tournament.objects.filter(
            id=new_tournament_id
        ).first()

        assert new_tournament.name == "Cyber Masters"
        assert new_tournament.discipline == self.discipline
        assert new_tournament.organizer == self.organizer
        assert str(new_tournament.start_date) == "2026-10-01"
        assert str(new_tournament.end_date) == "2026-10-05"

    def test_delete_tournament(self):
        tournaments = baker.make(
            "tournaments.Tournament",
            10,
            discipline=self.discipline,
            organizer=self.organizer
        )

        r = self.client.get("/api/tournaments/")
        data = r.json()

        assert len(data) == 10

        tournament_id_to_delete = tournaments[3].id

        self.client.delete(
            f"/api/tournaments/{tournament_id_to_delete}/"
        )

        r = self.client.get("/api/tournaments/")
        data = r.json()

        assert len(data) == 9

        assert tournament_id_to_delete not in [
            i["id"] for i in data
        ]

    def test_update_tournament(self):
        tournament = baker.make(
            "tournaments.Tournament",
            discipline=self.discipline,
            organizer=self.organizer
        )

        cache.set(
            f"otp_good_{self.user.pk}",
            True,
            timeout=300
        )

        r = self.client.put(
            f"/api/tournaments/{tournament.id}/",
            {
                "name": "Updated Tournament",
                "discipline_id": self.discipline.id,
                "organizer": self.organizer.id,
                "start_date": "2026-11-01",
                "end_date": "2026-11-10",
                "prize_pool": "200000.00"
            }
        )

        assert r.status_code == 200

        tournament.refresh_from_db()

        assert tournament.name == "Updated Tournament"
        assert tournament.discipline == self.discipline
        assert tournament.organizer == self.organizer
        assert str(tournament.start_date) == "2026-11-01"
        assert str(tournament.end_date) == "2026-11-10"
class UserProfileViewsetTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_superuser(
            username="admin",
            password="admin"
        )

        self.client.login(
            username="admin",
            password="admin"
        )

    def test_get_list(self):
        account = User.objects.create_user(
            username="player1",
            password="player1"
        )

        profile = baker.make(
            "tournaments.UserProfile",
            user=account,
            role=UserProfile.Role.PLAYER,
            is_captain=False
        )

        r = self.client.get("/api/userprofiles/")
        data = r.json()

        assert profile.nickname == data[0]["nickname"]
        assert profile.id == data[0]["id"]
        assert len(data) == 1

    def test_create_userprofile(self):
        account = User.objects.create_user(
            username="player1",
            password="player1"
        )

        r = self.client.post("/api/userprofiles/", {
            "user": account.id,
            "nickname": "PlayerOne",
            "real_name": "Иван Иванов",
            "role": "player",
            "game_role": "AWP",
            "rating": 1500,
            "email": "player@example.com",
            "is_captain": False
        })

        assert r.status_code == 201

        new_profile_id = r.json()["id"]

        profiles = UserProfile.objects.all()
        assert len(profiles) == 1

        new_profile = UserProfile.objects.filter(
            id=new_profile_id
        ).first()

        assert new_profile.nickname == "PlayerOne"
        assert new_profile.real_name == "Иван Иванов"
        assert new_profile.role == UserProfile.Role.PLAYER
        assert new_profile.game_role == "AWP"
        assert new_profile.rating == 1500
        assert new_profile.user == account

    def test_delete_userprofile(self):
        profiles = baker.make(
            "tournaments.UserProfile",
            10,
            role=UserProfile.Role.PLAYER,
            is_captain=False
        )

        r = self.client.get("/api/userprofiles/")
        data = r.json()

        assert len(data) == 10

        profile_id_to_delete = profiles[3].id

        self.client.delete(
            f"/api/userprofiles/{profile_id_to_delete}/"
        )

        r = self.client.get("/api/userprofiles/")
        data = r.json()

        assert len(data) == 9

        assert profile_id_to_delete not in [
            i["id"] for i in data
        ]

    def test_update_userprofile(self):
        account = User.objects.create_user(
            username="player1",
            password="player1"
        )

        profile = baker.make(
            "tournaments.UserProfile",
            user=account,
            role=UserProfile.Role.PLAYER,
            is_captain=False,
            team=None
        )

        cache.set(
            f"otp_good_{self.user.pk}",
            True,
            timeout=300
        )

        r = self.client.put(
            f"/api/userprofiles/{profile.id}/",
            {
                "user": account.id,
                "nickname": "UpdatedPlayer",
                "real_name": "Пётр Петров",
                "role": "player",
                "game_role": "Support",
                "rating": 1700,
                "email": "updated@example.com",
                "is_captain": False
            }
        )

        assert r.status_code == 200

        profile.refresh_from_db()

        assert profile.nickname == "UpdatedPlayer"
        assert profile.real_name == "Пётр Петров"
        assert profile.game_role == "Support"
        assert profile.rating == 1700
        assert profile.email == "updated@example.com"
class TournamentApplicationViewsetTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_superuser(
            username="admin",
            password="admin"
        )

        self.client.login(
            username="admin",
            password="admin"
        )

        self.team = baker.make(
            "tournaments.Team"
        )

        self.tournament = baker.make(
            "tournaments.Tournament",
            status=Tournament.Status.REGISTRATION
        )

        self.captain_user = User.objects.create_user(
            username="captain",
            password="captain"
        )

        self.captain = baker.make(
            "tournaments.UserProfile",
            user=self.captain_user,
            team=self.team,
            role=UserProfile.Role.PLAYER,
            is_captain=True
        )

        baker.make(
            "tournaments.UserProfile",
            4,
            team=self.team,
            role=UserProfile.Role.PLAYER,
            is_captain=False
        )

    def test_get_list(self):
        application = baker.make(
            "tournaments.TournamentApplication",
            team=self.team,
            tournament=self.tournament,
            submitted_by=self.captain
        )

        r = self.client.get("/api/applications/")
        data = r.json()

        assert application.id == data[0]["id"]
        assert len(data) == 1

    def test_create_application(self):
        self.client.logout()

        self.client.login(
            username="captain",
            password="captain"
        )

        r = self.client.post("/api/applications/", {
            "team": self.team.id,
            "tournament": self.tournament.id
        })

        assert r.status_code == 201

        new_application_id = r.json()["id"]

        applications = TournamentApplication.objects.all()
        assert len(applications) == 1

        application = TournamentApplication.objects.filter(
            id=new_application_id
        ).first()

        assert application.team == self.team
        assert application.tournament == self.tournament
        assert application.submitted_by == self.captain
        assert application.status == TournamentApplication.Status.PENDING

    def test_delete_application(self):
        application = baker.make(
            "tournaments.TournamentApplication",
            team=self.team,
            tournament=self.tournament,
            submitted_by=self.captain
        )

        r = self.client.get("/api/applications/")
        data = r.json()

        assert len(data) == 1

        self.client.delete(
            f"/api/applications/{application.id}/"
        )

        r = self.client.get("/api/applications/")
        data = r.json()

        assert len(data) == 0

    def test_update_application(self):
        application = baker.make(
            "tournaments.TournamentApplication",
            team=self.team,
            tournament=self.tournament,
            submitted_by=self.captain
        )

        new_tournament = baker.make(
            "tournaments.Tournament",
            status=Tournament.Status.REGISTRATION
        )

        cache.set(
            f"otp_good_{self.admin.pk}",
            True,
            timeout=300
        )

        r = self.client.put(
            f"/api/applications/{application.id}/",
            {
                "team": self.team.id,
                "tournament": new_tournament.id
            }
        )

        assert r.status_code == 200

        application.refresh_from_db()

        assert application.team == self.team
        assert application.tournament == new_tournament