
from django.contrib import admin

from tournaments.models import Discipline, Organizer, Tournament, Team, UserProfile, TournamentApplication


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'genre', 'description']


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'social_media']


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'discipline', 'organizer', 'start_date', 'end_date', 'prize_pool']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'country', 'founded_year']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'nickname', 'real_name', 'role', 'game_role', 'rating', 'email', 'team']


@admin.register(TournamentApplication)
class TournamentApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'team', 'tournament', 'submitted_by', 'status', 'created_at']