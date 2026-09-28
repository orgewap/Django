<script setup>
import { ref, onBeforeMount } from "vue"
import axios from "axios"
import Cookies from "js-cookie"
import { useUserInfoStore } from "../stores/user_info_store"

const userInfoStore = useUserInfoStore()
const teams = ref([])
const statistics = ref({})

const filters = ref({
    name: "",
    country: "",
    founded_year_min: "",
    founded_year_max: ""
})

const newTeamName = ref("")
const newTeamCountry = ref("")
const newTeamFoundedYear = ref("")
const newTeamPicture = ref(null)
const pictureInput = ref(null)

const teamToEdit = ref({})
const editTeamPicture = ref(null)
const editPictureInput = ref(null)
const pictureToShow = ref("")

onBeforeMount(async () => {
    axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken")
    await userInfoStore.fetchUserInfo()
    await onLoadClick()
})

async function onLoadClick() {
    const response = await axios.get("/api/teams/", {
        params: filters.value
    })

    teams.value = response.data

    if (userInfoStore.userInfo.is_admin) {
        const statsResponse = await axios.get("/api/teams/stats/")
        statistics.value = statsResponse.data
    }
}

async function onResetFilters() {
    filters.value = {
        name: "",
        country: "",
        founded_year_min: "",
        founded_year_max: ""
    }
    await onLoadClick()
}

function onPictureChange(event) {
    newTeamPicture.value = event.target.files[0] || null
}

async function onCreateClick() {
    const formData = new FormData()
    formData.append("name", newTeamName.value)
    formData.append("country", newTeamCountry.value)
    formData.append("founded_year", newTeamFoundedYear.value)

    if (newTeamPicture.value) {
        formData.append("picture", newTeamPicture.value)
    }

    await axios.post("/api/teams/", formData)

    newTeamName.value = ""
    newTeamCountry.value = ""
    newTeamFoundedYear.value = ""
    newTeamPicture.value = null

    if (pictureInput.value) {
        pictureInput.value.value = ""
    }

    await onLoadClick()
}

async function onRemoveClick(team) {
    await axios.delete(`/api/teams/${team.id}/`)
    await onLoadClick()
}

function onTeamEditClick(team) {
    teamToEdit.value = { ...team }
    editTeamPicture.value = null

    if (editPictureInput.value) {
        editPictureInput.value.value = ""
    }
}

function onEditPictureChange(event) {
    editTeamPicture.value = event.target.files[0] || null
}

async function onUpdateTeam() {
    const formData = new FormData()
    formData.append("name", teamToEdit.value.name)
    formData.append("country", teamToEdit.value.country)
    formData.append("founded_year", teamToEdit.value.founded_year)

    if (editTeamPicture.value) {
        formData.append("picture", editTeamPicture.value)
    }

    await axios.put(
        `/api/teams/${teamToEdit.value.id}/`,
        formData
    )

    editTeamPicture.value = null

    if (editPictureInput.value) {
        editPictureInput.value.value = ""
    }

    await onLoadClick()
}
</script>

<template>
    <div class="p-2">
        <div v-if="userInfoStore.userInfo.is_admin" class="row g-2 mb-2">
            <div class="col">
                <div class="form-floating">
                    <input
                        id="teamName"
                        v-model="newTeamName"
                        type="text"
                        class="form-control"
                        placeholder="Название"
                    >
                    <label for="teamName">Название</label>
                </div>
            </div>
            <div class="col">
                <div class="form-floating">
                    <input
                        id="teamCountry"
                        v-model="newTeamCountry"
                        type="text"
                        class="form-control"
                        placeholder="Страна"
                    >
                    <label for="teamCountry">Страна</label>
                </div>
            </div>
            <div class="col">
                <div class="form-floating">
                    <input
                        id="teamFoundedYear"
                        v-model="newTeamFoundedYear"
                        type="number"
                        class="form-control"
                        placeholder="Год основания"
                        min="1"
                    >
                    <label for="teamFoundedYear">Год основания</label>
                </div>
            </div>
        </div>

        <div v-if="userInfoStore.userInfo.is_admin" class="row g-2 mb-2">
            <div class="col">
                <div class="form-floating">
                    <input
                        id="teamPicture"
                        ref="pictureInput"
                        type="file"
                        class="form-control"
                        accept="image/*"
                        @change="onPictureChange"
                    >
                    <label for="teamPicture">Логотип команды</label>
                </div>
            </div>
            <div class="col-auto">
                <button class="btn btn-primary" @click="onCreateClick">
                    Добавить
                </button>
            </div>
        </div>

        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title mb-3">Фильтрация команд</h5>

                <div class="row g-2 mb-2">
                    <div class="col-md-6">
                        <label class="form-label">Название</label>
                        <input
                            v-model="filters.name"
                            type="text"
                            class="form-control"
                            placeholder="Поиск по названию"
                        >
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Страна</label>
                        <input
                            v-model="filters.country"
                            type="text"
                            class="form-control"
                            placeholder="Поиск по стране"
                        >
                    </div>
                </div>

                <div class="row g-2 mb-3">
                    <div class="col-md-6">
                        <label class="form-label">Год основания от</label>
                        <input
                            v-model="filters.founded_year_min"
                            type="number"
                            class="form-control"
                            min="1"
                        >
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Год основания до</label>
                        <input
                            v-model="filters.founded_year_max"
                            type="number"
                            class="form-control"
                            min="1"
                        >
                    </div>
                </div>

                <div class="d-flex gap-2">
                    <button class="btn btn-primary" @click="onLoadClick">
                        Применить фильтры
                    </button>
                    <button class="btn btn-secondary" @click="onResetFilters">
                        Сбросить
                    </button>
                </div>
            </div>
        </div>

        <div v-if="userInfoStore.userInfo.is_admin" class="row g-2 mb-3">
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Количество команд</h5>
                        <p class="card-text">{{ statistics.total ?? 0 }}</p>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Количество стран</h5>
                        <p class="card-text">{{ statistics.total_countries ?? 0 }}</p>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Средний год основания</h5>
                        <p class="card-text">
                            {{ statistics.average_founded_year != null
                                ? statistics.average_founded_year.toFixed(0)
                                : 0 }}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <div>
            <div
                v-for="team in teams"
                :key="team.id"
                class="team-item"
            >
                <div class="d-flex align-items-center gap-3">
                    <img
                        v-if="team.picture"
                        :src="team.picture"
                        width="60"
                        height="60"
                        style="object-fit: cover; cursor: pointer;"
                        data-bs-toggle="modal"
                        data-bs-target="#pictureModal"
                        @click="pictureToShow = team.picture"
                    >
                    <div>{{ team.name }}</div>
                </div>

                <button
                    v-if="userInfoStore.userInfo.is_admin"
                    class="btn btn-success"
                    data-bs-toggle="modal"
                    data-bs-target="#editTeamModal"
                    @click="onTeamEditClick(team)"
                >
                    <i class="bi bi-pen-fill"></i>
                </button>

                <button
                    v-if="userInfoStore.userInfo.is_admin"
                    class="btn btn-danger"
                    @click="onRemoveClick(team)"
                >
                    <i class="bi bi-x"></i>
                </button>
            </div>
        </div>

        <div
            v-if="userInfoStore.userInfo.is_admin"
            id="editTeamModal"
            class="modal fade"
            tabindex="-1"
        >
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h1 class="modal-title fs-5">Редактировать команду</h1>
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
                                    <input
                                        id="editTeamName"
                                        v-model="teamToEdit.name"
                                        type="text"
                                        class="form-control"
                                        placeholder="Название"
                                    >
                                    <label for="editTeamName">Название</label>
                                </div>
                            </div>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <input
                                        id="editTeamCountry"
                                        v-model="teamToEdit.country"
                                        type="text"
                                        class="form-control"
                                        placeholder="Страна"
                                    >
                                    <label for="editTeamCountry">Страна</label>
                                </div>
                            </div>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <input
                                        id="editTeamFoundedYear"
                                        v-model="teamToEdit.founded_year"
                                        type="number"
                                        class="form-control"
                                        placeholder="Год основания"
                                        min="1"
                                    >
                                    <label for="editTeamFoundedYear">Год основания</label>
                                </div>
                            </div>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <label class="form-label">
                                    Изменить логотип команды
                                </label>
                                <input
                                    ref="editPictureInput"
                                    type="file"
                                    class="form-control"
                                    accept="image/*"
                                    @change="onEditPictureChange"
                                >
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
                            @click="onUpdateTeam"
                        >
                            Сохранить
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div id="pictureModal" class="modal fade" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Просмотр изображения</h5>
                        <button
                            type="button"
                            class="btn-close"
                            data-bs-dismiss="modal"
                        ></button>
                    </div>
                    <div class="modal-body text-center">
                        <img :src="pictureToShow" class="img-fluid">
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.team-item {
    padding: 0.5rem;
    margin: 0.5rem 0;
    border: 1px solid silver;
    border-radius: 8px;
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 8px;
    justify-content: space-between;
}
</style>