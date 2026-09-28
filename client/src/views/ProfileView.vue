<script setup>
import { computed, onBeforeMount, ref } from "vue"
import axios from "axios"

const profile = ref(null)
const team = ref(null)
const members = ref([])
const tournaments = ref([])

const teammates = computed(() => {
    if (!profile.value) {
        return []
    }

    return members.value.filter(
        member => member.id !== profile.value.id
    )
})

onBeforeMount(async () => {
    await onLoadClick()
})

async function onLoadClick() {
    const profileResponse = await axios.get(
        "/api/userprofiles/me/"
    )

    profile.value = profileResponse.data

    if (!profile.value.team) {
        return
    }

    const teamResponse = await axios.get(
        `/api/teams/${profile.value.team}/`
    )

    team.value = teamResponse.data

    const membersResponse = await axios.get(
        "/api/userprofiles/",
        {
            params: {
                team_id: profile.value.team
            }
        }
    )

    members.value = membersResponse.data

    const tournamentsResponse = await axios.get(
        "/api/tournaments/",
        {
            params: {
                team_id: profile.value.team
            }
        }
    )

    tournaments.value = tournamentsResponse.data
}

function roleName(role) {
    if (role === "player") {
        return "Игрок"
    }

    if (role === "admin") {
        return "Администратор"
    }

    return role
}
</script>

<template>
    <div class="p-2">

        <div
            v-if="profile"
            class="card mb-3"
        >
            <div class="card-body">
                <div class="d-flex align-items-center gap-3">
                    <img
                        v-if="profile.picture"
                        :src="profile.picture"
                        width="100"
                        height="100"
                        style="object-fit: cover;"
                    >

                    <div>
                        <h5 class="card-title">
                            {{ profile.nickname }}
                        </h5>

                        <div>
                            <strong>Имя:</strong>
                            {{ profile.real_name }}
                        </div>

                        <div>
                            <strong>Роль:</strong>
                            {{ roleName(profile.role) }}
                        </div>

                        <div v-if="profile.game_role">
                            <strong>Игровая роль:</strong>
                            {{ profile.game_role }}
                        </div>

                        <div v-if="profile.rating !== null">
                            <strong>Рейтинг:</strong>
                            {{ profile.rating }}
                        </div>

                        <div v-if="profile.email">
                            <strong>Почта:</strong>
                            {{ profile.email }}
                        </div>

                        <div v-if="profile.is_captain">
                            <strong>Капитан команды</strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div
            v-if="team"
            class="card mb-3"
        >
            <div class="card-body">
                <h5 class="card-title">
                    Моя команда
                </h5>

                <div class="d-flex align-items-center gap-3">
                    <img
                        v-if="team.picture"
                        :src="team.picture"
                        width="80"
                        height="80"
                        style="object-fit: cover;"
                    >

                    <div>
                        <div>
                            <strong>Название:</strong>
                            {{ team.name }}
                        </div>

                        <div>
                            <strong>Страна:</strong>
                            {{ team.country }}
                        </div>

                        <div>
                            <strong>Год основания:</strong>
                            {{ team.founded_year }}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div
            v-if="team"
            class="card mb-3"
        >
            <div class="card-body">
                <h5 class="card-title">
                    Мои товарищи по команде
                </h5>

                <div
                    v-for="member in teammates"
                    :key="member.id"
                    class="profile-item"
                >
                    <div class="d-flex align-items-center gap-3">
                        <img
                            v-if="member.picture"
                            :src="member.picture"
                            width="50"
                            height="50"
                            style="object-fit: cover;"
                        >

                        <div>
                            <div>
                                <strong>{{ member.nickname }}</strong>
                            </div>

                            <div>
                                {{ member.real_name }}
                            </div>

                            <div v-if="member.game_role">
                                {{ member.game_role }}
                            </div>

                            <div v-if="member.is_captain">
                                Капитан
                            </div>
                        </div>
                    </div>
                </div>

                <div v-if="teammates.length === 0">
                    Товарищей по команде нет
                </div>
            </div>
        </div>

        <div
            v-if="team"
            class="card mb-3"
        >
            <div class="card-body">
                <h5 class="card-title">
                    Турниры моей команды
                </h5>

                <div
                    v-for="tournament in tournaments"
                    :key="tournament.id"
                    class="profile-item"
                >
                    <div class="d-flex align-items-center gap-3">
                        <img
                            v-if="tournament.picture"
                            :src="tournament.picture"
                            width="60"
                            height="60"
                            style="object-fit: cover;"
                        >

                        <div>
                            <strong>
                                {{ tournament.name }}
                            </strong>
                        </div>
                    </div>
                </div>

                <div v-if="tournaments.length === 0">
                    Подтверждённых турниров пока нет
                </div>
            </div>
        </div>

        <div
            v-if="profile && !profile.team"
            class="alert alert-secondary"
        >
            Пользователь пока не состоит в команде
        </div>

    </div>
</template>

<style scoped>
.profile-item {
    padding: 0.5rem;
    margin: 0.5rem 0;
    border: 1px solid silver;
    border-radius: 8px;
}
</style>