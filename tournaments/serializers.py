from rest_framework import serializers

from tournaments.models import (
    Tournament,
    Discipline,
    Organizer,
    Team,
    UserProfile,
    TournamentApplication
)


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = "__all__"


class OrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizer
        fields = "__all__"


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        exclude = ("otp_key",)

    def validate(self, attrs):

        if self.instance is not None:
            team = attrs.get(
                "team",
                self.instance.team
            )

            role = attrs.get(
                "role",
                self.instance.role
            )

            is_captain = attrs.get(
                "is_captain",
                self.instance.is_captain
            )
        else:
            team = attrs.get("team")
            role = attrs.get(
                "role",
                UserProfile.Role.PLAYER
            )
            is_captain = attrs.get(
                "is_captain",
                False
            )

        if is_captain:

            if role != UserProfile.Role.PLAYER:
                raise serializers.ValidationError(
                    "Капитаном может быть только участник"
                )

            if team is None:
                raise serializers.ValidationError(
                    "Капитан должен состоять в команде"
                )

            captain = UserProfile.objects.filter(
                team=team,
                is_captain=True
            )

            if self.instance is not None:
                captain = captain.exclude(
                    id=self.instance.id
                )

            if captain.exists():
                raise serializers.ValidationError(
                    "В команде уже есть капитан"
                )

        return attrs


class TournamentSerializer(serializers.ModelSerializer):
    discipline = DisciplineSerializer(read_only=True)

    discipline_id = serializers.PrimaryKeyRelatedField(
        queryset=Discipline.objects.all(),
        source="discipline",
        write_only=True
    )

    class Meta:
        model = Tournament
        fields = "__all__"


class TournamentApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = TournamentApplication
        fields = "__all__"

        read_only_fields = (
            "submitted_by",
            "status",
            "created_at"
        )


class OTPSerializer(serializers.Serializer):
    key = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()