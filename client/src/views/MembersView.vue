<script setup>
import { ref, onBeforeMount, computed } from "vue"
import axios from "axios"
import Cookies from "js-cookie"
import { useUserInfoStore } from "../stores/user_info_store"

const userInfoStore = useUserInfoStore()
const members = ref([])
const statistics = ref({})
const teams = ref([])

const teamsById = computed(() => {
    const map = {}

    teams.value.forEach(team => {
        map[team.id] = team
    })

    return map
})

const filters = ref({
    nickname: "",
    real_name: "",
    role: "",
    game_role: "",
    rating_min: "",
    rating_max: "",
    email: "",
    team_id: ""
})

const newMemberNickname = ref("")
const newMemberRealName = ref("")
const newMemberRole = ref("player")
const newMemberGameRole = ref("")
const newMemberRating = ref("")
const newMemberEmail = ref("")
const newMemberUser = ref("")
const newMemberTeam = ref("")
const newMemberIsCaptain = ref(false)
const newMemberPicture = ref(null)
const pictureInput = ref(null)

const memberToEdit = ref({})
const editMemberPicture = ref(null)
const editPictureInput = ref(null)
const pictureToShow = ref("")

onBeforeMount(async () => {
    axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken")
    await userInfoStore.fetchUserInfo()
    await onLoadClick()
})

async function onLoadClick() {
    if (userInfoStore.userInfo.is_admin) {
        const response = await axios.get("/api/userprofiles/", {
            params: filters.value
        })
        members.value = response.data

        const teamsResponse = await axios.get("/api/teams/")
        teams.value = teamsResponse.data

        const statsResponse = await axios.get("/api/userprofiles/stats/")
        statistics.value = statsResponse.data
    } else {
        const response = await axios.get("/api/userprofiles/")
        members.value = response.data

        const teamsResponse = await axios.get("/api/teams/")
        teams.value = teamsResponse.data
    }
}

async function onResetFilters() {
    filters.value = {
        nickname: "",
        real_name: "",
        role: "",
        game_role: "",
        rating_min: "",
        rating_max: "",
        email: "",
        team_id: ""
    }
    await onLoadClick()
}

function onPictureChange(event) {
    newMemberPicture.value = event.target.files[0] || null
}

async function onCreateClick() {
    const formData = new FormData()
    formData.append("nickname", newMemberNickname.value)
    formData.append("real_name", newMemberRealName.value)
    formData.append("role", newMemberRole.value)
    formData.append("game_role", newMemberGameRole.value)
    formData.append("rating", newMemberRating.value)
    formData.append("email", newMemberEmail.value)
    formData.append("user", newMemberUser.value)
    formData.append("team", newMemberTeam.value)
    formData.append("is_captain", newMemberIsCaptain.value)

    if (newMemberPicture.value) {
        formData.append("picture", newMemberPicture.value)
    }

    await axios.post("/api/userprofiles/", formData)

    newMemberNickname.value = ""
    newMemberRealName.value = ""
    newMemberRole.value = "player"
    newMemberGameRole.value = ""
    newMemberRating.value = ""
    newMemberEmail.value = ""
    newMemberUser.value = ""
    newMemberTeam.value = ""
    newMemberIsCaptain.value = false
    newMemberPicture.value = null

    if (pictureInput.value) {
        pictureInput.value.value = ""
    }

    await onLoadClick()
}

async function onRemoveClick(member) {
    await axios.delete(`/api/userprofiles/${member.id}/`)
    await onLoadClick()
}

function onMemberEditClick(member) {
    memberToEdit.value = { ...member }
    editMemberPicture.value = null

    if (editPictureInput.value) {
        editPictureInput.value.value = ""
    }
}

function onEditPictureChange(event) {
    editMemberPicture.value = event.target.files[0] || null
}

async function onUpdateMember() {
    const formData = new FormData()
    formData.append("nickname", memberToEdit.value.nickname)
    formData.append("real_name", memberToEdit.value.real_name)
    formData.append("role", memberToEdit.value.role)
    formData.append("game_role", memberToEdit.value.game_role || "")
    formData.append("rating", memberToEdit.value.rating ?? "")
    formData.append("email", memberToEdit.value.email || "")
    formData.append("user", memberToEdit.value.user)
    formData.append("team", memberToEdit.value.team ?? "")
    formData.append("is_captain", memberToEdit.value.is_captain)

    if (editMemberPicture.value) {
        formData.append("picture", editMemberPicture.value)
    }

    await axios.put(
        `/api/userprofiles/${memberToEdit.value.id}/`,
        formData
    )

    editMemberPicture.value = null

    if (editPictureInput.value) {
        editPictureInput.value.value = ""
    }

    await onLoadClick()
}
</script>

<template>
    <div class="p-2">
        <template v-if="userInfoStore.userInfo.is_admin">
            <div class="row g-2 mb-2">
                <div class="col">
                    <div class="form-floating">
                        <input
                            id="memberNickname"
                            v-model="newMemberNickname"
                            type="text"
                            class="form-control"
                            placeholder="Никнейм"
                        >
                        <label for="memberNickname">Никнейм</label>
                    </div>
                </div>
                <div class="col">
                    <div class="form-floating">
                        <input
                            id="memberRealName"
                            v-model="newMemberRealName"
                            type="text"
                            class="form-control"
                            placeholder="Настоящее имя"
                        >
                        <label for="memberRealName">Настоящее имя</label>
                    </div>
                </div>
                <div class="col">
                    <div class="form-floating">
                        <select
                            id="memberRole"
                            v-model="newMemberRole"
                            class="form-select"
                        >
                            <option value="player">Игрок</option>
                            <option value="admin">Администратор</option>
                        </select>
                        <label for="memberRole">Роль</label>
                    </div>
                </div>
            </div>

            <div class="row g-2 mb-2">
                <div class="col">
                    <div class="form-floating">
                        <input
                            id="memberGameRole"
                            v-model="newMemberGameRole"
                            type="text"
                            class="form-control"
                            placeholder="Игровая роль"
                        >
                        <label for="memberGameRole">Игровая роль</label>
                    </div>
                </div>
                <div class="col">
                    <div class="form-floating">
                        <input
                            id="memberRating"
                            v-model="newMemberRating"
                            type="number"
                            step="any"
                            class="form-control"
                            placeholder="Рейтинг"
                        >
                        <label for="memberRating">Рейтинг</label>
                    </div>
                </div>
                <div class="col">
                    <div class="form-floating">
                        <input
                            id="memberEmail"
                            v-model="newMemberEmail"
                            type="email"
                            class="form-control"
                            placeholder="Контактная почта"
                        >
                        <label for="memberEmail">Контактная почта</label>
                    </div>
                </div>
            </div>

            <div class="row g-2 mb-2">
                <div class="col">
                    <div class="form-floating">
                        <input
                            id="memberUser"
                            v-model="newMemberUser"
                            type="number"
                            class="form-control"
                            placeholder="ID пользователя"
                        >
                        <label for="memberUser">ID пользователя</label>
                    </div>
                </div>
                <div class="col">
                    <div class="form-floating">
                        <select
                            id="memberTeam"
                            v-model="newMemberTeam"
                            class="form-select"
                        >
                            <option value="">Без команды</option>
                            <option
                                v-for="team in teams"
                                :key="team.id"
                                :value="team.id"
                            >
                                {{ team.name }}
                            </option>
                        </select>
                        <label for="memberTeam">Команда</label>
                    </div>
                </div>
                <div class="col">
                    <div class="form-check mt-3">
                        <input
                            id="memberIsCaptain"
                            v-model="newMemberIsCaptain"
                            class="form-check-input"
                            type="checkbox"
                        >

                        <label
                            class="form-check-label"
                            for="memberIsCaptain"
                        >
                            Капитан команды
                        </label>
                    </div>
                </div>
                <div class="col">
                    <div class="form-floating">
                        <input
                            id="memberPicture"
                            ref="pictureInput"
                            type="file"
                            class="form-control"
                            accept="image/*"
                            @change="onPictureChange"
                        >
                        <label for="memberPicture">Аватар участника</label>
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
                    <h5 class="card-title mb-3">Фильтрация участников</h5>

                    <div class="row g-2 mb-2">
                        <div class="col-md-4">
                            <label class="form-label">Никнейм</label>
                            <input
                                v-model="filters.nickname"
                                type="text"
                                class="form-control"
                                placeholder="Поиск по никнейму"
                            >
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Настоящее имя</label>
                            <input
                                v-model="filters.real_name"
                                type="text"
                                class="form-control"
                                placeholder="Поиск по имени"
                            >
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Роль</label>
                            <select v-model="filters.role" class="form-select">
                                <option value="">Все роли</option>
                                <option value="player">Игрок</option>
                                <option value="admin">Администратор</option>
                            </select>
                        </div>
                    </div>

                    <div class="row g-2 mb-2">
                        <div class="col-md-4">
                            <label class="form-label">Игровая роль</label>
                            <input
                                v-model="filters.game_role"
                                type="text"
                                class="form-control"
                                placeholder="Поиск по игровой роли"
                            >
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Рейтинг от</label>
                            <input
                                v-model="filters.rating_min"
                                type="number"
                                step="any"
                                class="form-control"
                            >
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Рейтинг до</label>
                            <input
                                v-model="filters.rating_max"
                                type="number"
                                step="any"
                                class="form-control"
                            >
                        </div>
                    </div>

                    <div class="row g-2 mb-3">
                        <div class="col-md-6">
                            <label class="form-label">Контактная почта</label>
                            <input
                                v-model="filters.email"
                                type="text"
                                class="form-control"
                                placeholder="Поиск по почте"
                            >
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Команда</label>
                            <select v-model="filters.team_id" class="form-select">
                                <option value="">Все команды</option>
                                <option
                                    v-for="team in teams"
                                    :key="team.id"
                                    :value="team.id"
                                >
                                    {{ team.name }}
                                </option>
                            </select>
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

            <div class="row g-2 mb-3">
                <div class="col">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Количество участников</h5>
                            <p class="card-text">{{ statistics.total ?? 0 }}</p>
                        </div>
                    </div>
                </div>
                <div class="col">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Количество игроков</h5>
                            <p class="card-text">{{ statistics.total_players ?? 0 }}</p>
                        </div>
                    </div>
                </div>
                <div class="col">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Количество администраторов</h5>
                            <p class="card-text">{{ statistics.total_admins ?? 0 }}</p>
                        </div>
                    </div>
                </div>
                <div class="col">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Средний рейтинг</h5>
                            <p class="card-text">
                                {{ statistics.average_rating != null
                                    ? statistics.average_rating.toFixed(2)
                                    : 0 }}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </template>

        <h4 v-if="!userInfoStore.userInfo.is_admin" class="mb-3">
            {{ userInfoStore.userInfo.team_id ? "Моя команда" : "Мои данные" }}
        </h4>

        <div
            v-for="member in members"
            :key="member.id"
            class="member-item"
        >
            <div class="d-flex align-items-center gap-3">
                <img
                    v-if="member.picture"
                    :src="member.picture"
                    width="60"
                    height="60"
                    style="object-fit: cover; cursor: pointer;"
                    data-bs-toggle="modal"
                    data-bs-target="#pictureModal"
                    @click="pictureToShow = member.picture"
                >

                <div>
                    <div class="fw-bold">{{ member.nickname }}</div>

                    <template v-if="!userInfoStore.userInfo.is_admin">
                        <div>Настоящее имя: {{ member.real_name }}</div>
                        <div>Игровая роль: {{ member.game_role || "Не указана" }}</div>
                        <div>Рейтинг: {{ member.rating ?? "Не указан" }}</div>
                        <div>Почта: {{ member.email || "Не указана" }}</div>
                        <div>
                            Команда:
                            {{ teamsById[member.team]?.name || "Не назначена" }}
                        </div>
                        <div>
                            Статус:
                            {{ member.is_captain ? "Капитан" : "Участник" }}
                        </div>
                    </template>
                </div>
            </div>

            <button
                v-if="userInfoStore.userInfo.is_admin"
                class="btn btn-success"
                data-bs-toggle="modal"
                data-bs-target="#editMemberModal"
                @click="onMemberEditClick(member)"
            >
                <i class="bi bi-pen-fill"></i>
            </button>

            <button
                v-if="userInfoStore.userInfo.is_admin"
                class="btn btn-danger"
                @click="onRemoveClick(member)"
            >
                <i class="bi bi-x"></i>
            </button>
        </div>

        <div
            v-if="userInfoStore.userInfo.is_admin"
            id="editMemberModal"
            class="modal fade"
            tabindex="-1"
        >
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h1 class="modal-title fs-5">Редактировать участника</h1>
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
                                        id="editMemberNickname"
                                        v-model="memberToEdit.nickname"
                                        type="text"
                                        class="form-control"
                                        placeholder="Никнейм"
                                    >
                                    <label for="editMemberNickname">Никнейм</label>
                                </div>
                            </div>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <input
                                        id="editMemberRealName"
                                        v-model="memberToEdit.real_name"
                                        type="text"
                                        class="form-control"
                                        placeholder="Настоящее имя"
                                    >
                                    <label for="editMemberRealName">Настоящее имя</label>
                                </div>
                            </div>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <select
                                        id="editMemberRole"
                                        v-model="memberToEdit.role"
                                        class="form-select"
                                    >
                                        <option value="player">Игрок</option>
                                        <option value="admin">Администратор</option>
                                    </select>
                                    <label for="editMemberRole">Роль</label>
                                </div>
                            </div>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <input
                                        id="editMemberGameRole"
                                        v-model="memberToEdit.game_role"
                                        type="text"
                                        class="form-control"
                                        placeholder="Игровая роль"
                                    >
                                    <label for="editMemberGameRole">Игровая роль</label>
                                </div>
                            </div>
                            <div class="col">
                                <div class="form-floating">
                                    <input
                                        id="editMemberRating"
                                        v-model="memberToEdit.rating"
                                        type="number"
                                        step="any"
                                        class="form-control"
                                        placeholder="Рейтинг"
                                    >
                                    <label for="editMemberRating">Рейтинг</label>
                                </div>
                            </div>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <input
                                        id="editMemberEmail"
                                        v-model="memberToEdit.email"
                                        type="email"
                                        class="form-control"
                                        placeholder="Контактная почта"
                                    >
                                    <label for="editMemberEmail">Контактная почта</label>
                                </div>
                            </div>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <select
                                        id="editMemberTeam"
                                        v-model="memberToEdit.team"
                                        class="form-select"
                                    >
                                        <option :value="null">Без команды</option>
                                        <option
                                            v-for="team in teams"
                                            :key="team.id"
                                            :value="team.id"
                                        >
                                            {{ team.name }}
                                        </option>
                                    </select>
                                    <label for="editMemberTeam">Команда</label>
                                </div>
                            </div>
                        </div>
                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-check">
                                    <input
                                        id="editMemberIsCaptain"
                                        v-model="memberToEdit.is_captain"
                                        class="form-check-input"
                                        type="checkbox"
                                    >
                                    <label
                                        class="form-check-label"
                                        for="editMemberIsCaptain"
                                    >
                                        Капитан команды
                                    </label>
                                </div>
                            </div>
                        </div>
                        <div class="row g-2 mb-2">
                            <div class="col">
                                <label class="form-label">
                                    Изменить аватар участника
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
                            @click="onUpdateMember"
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
.member-item {
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