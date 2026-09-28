<script setup>
import { computed, onBeforeMount, ref } from "vue"
import axios from "axios"
import Cookies from "js-cookie"

import { useUserInfoStore } from "../stores/user_info_store"

const userInfoStore = useUserInfoStore()

const applications = ref([])
const tournaments = ref([])
const teams = ref([])
const statistics = ref({})

const filters = ref({
    team_id: "",
    tournament_id: "",
    submitted_by_id: "",
    status: "",
    created_at_from: "",
    created_at_to: ""
})
const members = ref([])
const newTournamentId = ref("")

const applicationToEdit = ref({})

const teamsById = computed(() => {
    const result = {}

    teams.value.forEach(team => {
        result[team.id] = team
    })

    return result
})

const tournamentsById = computed(() => {
    const result = {}

    tournaments.value.forEach(tournament => {
        result[tournament.id] = tournament
    })

    return result
})

onBeforeMount(async () => {
    axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken")

    await userInfoStore.fetchUserInfo()
    await onLoadClick()
})

async function onLoadClick() {
    const applicationsResponse = await axios.get("/api/applications/", {
        params: filters.value
    })

    applications.value = applicationsResponse.data

    const tournamentsResponse = await axios.get("/api/tournaments/")
    tournaments.value = tournamentsResponse.data

    const teamsResponse = await axios.get("/api/teams/")
    teams.value = teamsResponse.data

    if (userInfoStore.userInfo.is_admin) {
        const membersResponse = await axios.get("/api/userprofiles/")
        members.value = membersResponse.data

        const statsResponse = await axios.get("/api/applications/stats/", {
            params: filters.value
        })

        statistics.value = statsResponse.data
    }
}

async function onCreateClick() {
    await axios.post("/api/applications/", {
        team: userInfoStore.userInfo.team_id,
        tournament: newTournamentId.value
    })

    newTournamentId.value = ""

    await onLoadClick()
}

async function onRemoveClick(application) {
    await axios.delete(
        `/api/applications/${application.id}/`
    )

    await onLoadClick()
}

function onApplicationEditClick(application) {
    applicationToEdit.value = {
        ...application
    }
}

async function onUpdateApplication() {
    await axios.put(
        `/api/applications/${applicationToEdit.value.id}/`,
        {
            team: applicationToEdit.value.team,
            tournament: applicationToEdit.value.tournament
        }
    )

    await onLoadClick()
}

async function onApproveClick(application) {
    await axios.post(
        `/api/applications/${application.id}/approve/`
    )

    await onLoadClick()
}

async function onRejectClick(application) {
    await axios.post(
        `/api/applications/${application.id}/reject/`
    )

    await onLoadClick()
}

function statusName(status) {
    if (status === "pending") {
        return "На рассмотрении"
    }

    if (status === "approved") {
        return "Подтверждена"
    }

    if (status === "rejected") {
        return "Отклонена"
    }

    return status
}
async function onResetFilters() {
    filters.value = {
        team_id: "",
        tournament_id: "",
        submitted_by_id: "",
        status: "",
        created_at_from: "",
        created_at_to: ""
    }

    await onLoadClick()
}
</script>

<template>
    <div class="p-2">

        <div
            v-if="
                userInfoStore.userInfo.is_captain &&
                !userInfoStore.userInfo.is_admin
            "
            class="row g-2 mb-2"
        >
            <div class="col">
                <div class="form-floating">
                    <select
                        id="applicationTournament"
                        v-model="newTournamentId"
                        class="form-select"
                    >
                        <option value="">
                            Выберите турнир
                        </option>

                        <option
                            v-for="tournament in tournaments"
                            :key="tournament.id"
                            :value="tournament.id"
                        >
                            {{ tournament.name }}
                        </option>
                    </select>

                    <label for="applicationTournament">
                        Турнир
                    </label>
                </div>
            </div>

            <div class="col-auto">
                <button
                    class="btn btn-primary"
                    :disabled="!newTournamentId"
                    @click="onCreateClick"
                >
                    Подать заявку
                </button>
            </div>
        </div>
        <div
            v-if="userInfoStore.userInfo.is_admin"
            class="card mb-3"
        >
            <div class="card-body">
                <h5 class="card-title mb-3">
                    Фильтрация заявок
                </h5>

                <div class="row g-2 mb-2">
                    <div class="col-md-4">
                        <label class="form-label">
                            Команда
                        </label>

                        <select
                            v-model="filters.team_id"
                            class="form-select"
                        >
                            <option value="">
                                Все команды
                            </option>

                            <option
                                v-for="team in teams"
                                :key="team.id"
                                :value="team.id"
                            >
                                {{ team.name }}
                            </option>
                        </select>
                    </div>

                    <div class="col-md-4">
                        <label class="form-label">
                            Турнир
                        </label>

                        <select
                            v-model="filters.tournament_id"
                            class="form-select"
                        >
                            <option value="">
                                Все турниры
                            </option>

                            <option
                                v-for="tournament in tournaments"
                                :key="tournament.id"
                                :value="tournament.id"
                            >
                                {{ tournament.name }}
                            </option>
                        </select>
                    </div>

                    <div class="col-md-4">
                        <label class="form-label">
                            Заявку подал
                        </label>

                        <select
                            v-model="filters.submitted_by_id"
                            class="form-select"
                        >
                            <option value="">
                                Все участники
                            </option>

                            <option
                                v-for="member in members"
                                :key="member.id"
                                :value="member.id"
                            >
                                {{ member.nickname }}
                            </option>
                        </select>
                    </div>
                </div>

                <div class="row g-2 mb-2">
                    <div class="col-md-4">
                        <label class="form-label">
                            Статус
                        </label>

                        <select
                            v-model="filters.status"
                            class="form-select"
                        >
                            <option value="">
                                Все статусы
                            </option>

                            <option value="pending">
                                На рассмотрении
                            </option>

                            <option value="approved">
                                Подтверждена
                            </option>

                            <option value="rejected">
                                Отклонена
                            </option>
                        </select>
                    </div>

                    <div class="col-md-4">
                        <label class="form-label">
                            Дата подачи от
                        </label>

                        <input
                            v-model="filters.created_at_from"
                            type="date"
                            class="form-control"
                        >
                    </div>

                    <div class="col-md-4">
                        <label class="form-label">
                            Дата подачи до
                        </label>

                        <input
                            v-model="filters.created_at_to"
                            type="date"
                            class="form-control"
                        >
                    </div>
                </div>

                <div class="d-flex gap-2">
                    <button
                        class="btn btn-primary"
                        @click="onLoadClick"
                    >
                        Применить фильтры
                    </button>

                    <button
                        class="btn btn-secondary"
                        @click="onResetFilters"
                    >
                        Сбросить
                    </button>
                </div>
            </div>
        </div>
        <div
            v-if="userInfoStore.userInfo.is_admin"
            class="row g-2 mb-3"
        >
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            Количество заявок
                        </h5>

                        <p class="card-text">
                            {{ statistics.total ?? 0 }}
                        </p>
                    </div>
                </div>
            </div>

            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            На рассмотрении
                        </h5>

                        <p class="card-text">
                            {{ statistics.pending ?? 0 }}
                        </p>
                    </div>
                </div>
            </div>

            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            Подтверждено
                        </h5>

                        <p class="card-text">
                            {{ statistics.approved ?? 0 }}
                        </p>
                    </div>
                </div>
            </div>

            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            Отклонено
                        </h5>

                        <p class="card-text">
                            {{ statistics.rejected ?? 0 }}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <div>
            <div
                v-for="application in applications"
                :key="application.id"
                class="application-item"
            >
                <div>
                    <div>
                        <strong>Команда:</strong>
                        {{ teamsById[application.team]?.name }}
                    </div>

                    <div>
                        <strong>Турнир:</strong>
                        {{ tournamentsById[application.tournament]?.name }}
                    </div>

                    <div>
                        <strong>Статус:</strong>
                        {{ statusName(application.status) }}
                    </div>

                    <div>
                        <strong>Дата подачи:</strong>
                        {{ application.created_at }}
                    </div>
                </div>

                <div
                    v-if="userInfoStore.userInfo.is_admin"
                    class="d-flex gap-2 align-items-center"
                >
                    <button
                        class="btn btn-primary"
                        :disabled="application.status !== 'pending'"
                        @click="onApproveClick(application)"
                    >
                        Подтвердить
                    </button>

                    <button
                        class="btn btn-warning"
                        :disabled="application.status !== 'pending'"
                        @click="onRejectClick(application)"
                    >
                        Отклонить
                    </button>

                    <button
                        class="btn btn-success"
                        data-bs-toggle="modal"
                        data-bs-target="#editApplicationModal"
                        @click="onApplicationEditClick(application)"
                    >
                        <i class="bi bi-pen-fill"></i>
                    </button>

                    <button
                        class="btn btn-danger"
                        @click="onRemoveClick(application)"
                    >
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            </div>
        </div>

        <div
            v-if="userInfoStore.userInfo.is_admin"
            id="editApplicationModal"
            class="modal fade"
            tabindex="-1"
        >
            <div class="modal-dialog">
                <div class="modal-content">

                    <div class="modal-header">
                        <h1 class="modal-title fs-5">
                            Редактировать заявку
                        </h1>

                        <button
                            type="button"
                            class="btn-close"
                            data-bs-dismiss="modal"
                        ></button>
                    </div>

                    <div class="modal-body">

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <select
                                        id="editApplicationTeam"
                                        v-model="applicationToEdit.team"
                                        class="form-select"
                                    >
                                        <option
                                            v-for="team in teams"
                                            :key="team.id"
                                            :value="team.id"
                                        >
                                            {{ team.name }}
                                        </option>
                                    </select>

                                    <label for="editApplicationTeam">
                                        Команда
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <select
                                        id="editApplicationTournament"
                                        v-model="applicationToEdit.tournament"
                                        class="form-select"
                                    >
                                        <option
                                            v-for="tournament in tournaments"
                                            :key="tournament.id"
                                            :value="tournament.id"
                                        >
                                            {{ tournament.name }}
                                        </option>
                                    </select>

                                    <label for="editApplicationTournament">
                                        Турнир
                                    </label>
                                </div>
                            </div>
                        </div>

                    </div>

                    <div class="modal-footer">
                        <button
                            type="button"
                            class="btn btn-secondary"
                            data-bs-dismiss="modal"
                        >
                            Закрыть
                        </button>

                        <button
                            type="button"
                            class="btn btn-primary"
                            data-bs-dismiss="modal"
                            @click="onUpdateApplication"
                        >
                            Сохранить
                        </button>
                    </div>

                </div>
            </div>
        </div>

    </div>
</template>

<style scoped>
.application-item {
    padding: 0.5rem;
    margin: 0.5rem 0;
    border: 1px solid silver;
    border-radius: 8px;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 8px;
    justify-content: space-between;
}
</style>