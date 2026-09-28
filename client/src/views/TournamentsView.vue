
<script setup>
import { ref, onBeforeMount } from "vue"
import axios from "axios"
import Cookies from "js-cookie"
import { useUserInfoStore } from "../stores/user_info_store"

const userInfoStore = useUserInfoStore()
const tournaments = ref([])
const disciplines = ref([])
const organizers = ref([])
const statistics = ref({})

const filters = ref({
    name: "",
    start_date: "",
    end_date: "",
    prize_pool_min: "",
    prize_pool_max: "",
    discipline_id: "",
    organizer_id: "",
    status: ""
    
})

const newTournamentName = ref("")
const newTournamentStartDate = ref("")
const newTournamentEndDate = ref("")
const newTournamentPrizePool = ref("")
const newTournamentDiscipline = ref("")
const newTournamentStatus = ref("registration")
const newTournamentOrganizer = ref("")
const newTournamentPicture = ref(null)
const pictureInput = ref(null)

const tournamentToEdit = ref({})
const editTournamentPicture = ref(null)
const editPictureInput = ref(null)
const pictureToShow = ref("")

onBeforeMount(async () => {
    axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken")
    await userInfoStore.fetchUserInfo()
    await onLoadClick()
})

async function onLoadClick() {
    const response = await axios.get("/api/tournaments/", {
        params: filters.value
    })
    tournaments.value = response.data

    const disciplinesResponse = await axios.get("/api/disciplines/")
    disciplines.value = disciplinesResponse.data

    const organizersResponse = await axios.get("/api/organizers/")
    organizers.value = organizersResponse.data

    if (userInfoStore.userInfo.is_admin) {
        const statsResponse = await axios.get("/api/tournaments/stats/")
        statistics.value = statsResponse.data
    }
}

async function onResetFilters() {
    filters.value = {
        name: "",
        start_date: "",
        end_date: "",
        prize_pool_min: "",
        prize_pool_max: "",
        discipline_id: "",
        organizer_id: "",
        status: ""
    }
    await onLoadClick()
}

function onPictureChange(event) {
    newTournamentPicture.value = event.target.files[0] || null
}

async function onCreateClick() {
    const formData = new FormData()
    formData.append("name", newTournamentName.value)
    formData.append("start_date", newTournamentStartDate.value)
    formData.append("end_date", newTournamentEndDate.value)
    formData.append("prize_pool", newTournamentPrizePool.value)
    formData.append("discipline_id", newTournamentDiscipline.value)
    formData.append("organizer", newTournamentOrganizer.value)
    formData.append("status", newTournamentStatus.value)

    if (newTournamentPicture.value) {
        formData.append("picture", newTournamentPicture.value)
    }

    await axios.post("/api/tournaments/", formData)

    newTournamentName.value = ""
    newTournamentStartDate.value = ""
    newTournamentEndDate.value = ""
    newTournamentPrizePool.value = ""
    newTournamentDiscipline.value = ""
    newTournamentOrganizer.value = ""
    newTournamentPicture.value = null
    newTournamentStatus.value = "registration"

    if (pictureInput.value) {
        pictureInput.value.value = ""
    }

    await onLoadClick()
}

async function onRemoveClick(tournament) {
    await axios.delete(`/api/tournaments/${tournament.id}/`)
    await onLoadClick()
}

function onTournamentEditClick(tournament) {
    tournamentToEdit.value = {
        ...tournament,
        discipline_id: tournament.discipline?.id ?? "",
        organizer: tournament.organizer ?? ""
    }

    editTournamentPicture.value = null

    if (editPictureInput.value) {
        editPictureInput.value.value = ""
    }
}

function onEditPictureChange(event) {
    editTournamentPicture.value = event.target.files[0] || null
}

async function onUpdateTournament() {
    const formData = new FormData()
    formData.append("name", tournamentToEdit.value.name)
    formData.append("start_date", tournamentToEdit.value.start_date || "")
    formData.append("end_date", tournamentToEdit.value.end_date || "")
    formData.append("prize_pool", tournamentToEdit.value.prize_pool ?? "")
    formData.append("discipline_id", tournamentToEdit.value.discipline_id)
    formData.append("organizer", tournamentToEdit.value.organizer || "")
    formData.append("status", tournamentToEdit.value.status)

    if (editTournamentPicture.value) {
        formData.append("picture", editTournamentPicture.value)
    }

    await axios.put(
        `/api/tournaments/${tournamentToEdit.value.id}/`,
        formData
    )

    editTournamentPicture.value = null

    if (editPictureInput.value) {
        editPictureInput.value.value = ""
    }

    await onLoadClick()
}


async function onApplyClick(tournament) {
    try {
        await axios.post("/api/applications/", {
            team: userInfoStore.userInfo.team_id,
            tournament: tournament.id
        })

        alert("Заявка отправлена на рассмотрение")
    } catch (error) {
        const data = error.response?.data

        alert(
            Array.isArray(data?.team) ? data.team[0] :
            Array.isArray(data?.tournament) ? data.tournament[0] :
            data?.team ||
            data?.tournament ||
            data?.detail ||
            "Не удалось отправить заявку"
        )
    }
}
</script>

<template>
    <div class="p-2">
        <div v-if="userInfoStore.userInfo.is_admin" class="row g-2 mb-2">
            <div class="col">
                <div class="form-floating">
                    <input
                        id="tournamentName"
                        v-model="newTournamentName"
                        type="text"
                        class="form-control"
                        placeholder="Название"
                    >
                    <label for="tournamentName">Название</label>
                </div>
            </div>
            <div class="col-auto">
                <div class="form-floating">
                    <select
                        id="tournamentDiscipline"
                        v-model="newTournamentDiscipline"
                        class="form-select"
                    >
                        <option value="">Выберите дисциплину</option>
                        <option
                            v-for="discipline in disciplines"
                            :key="discipline.id"
                            :value="discipline.id"
                        >
                            {{ discipline.name }}
                        </option>
                    </select>
                    <label for="tournamentDiscipline">Дисциплина</label>
                </div>
            </div>
            <div class="col-auto">
                <div class="form-floating">
                    <select
                        id="tournamentOrganizer"
                        v-model="newTournamentOrganizer"
                        class="form-select"
                    >
                        <option value="">Выберите организатора</option>
                        <option
                            v-for="organizer in organizers"
                            :key="organizer.id"
                            :value="organizer.id"
                        >
                            {{ organizer.name }}
                        </option>
                    </select>
                    <label for="tournamentOrganizer">Организатор</label>
                </div>
            </div>
            <div class="col-auto">
                <div class="form-floating">
                    <select
                        id="tournamentStatus"
                        v-model="newTournamentStatus"
                        class="form-select"
                    >
                        <option value="registration">Регистрация открыта</option>
                        <option value="closed">Регистрация закрыта</option>
                        <option value="ongoing">Проводится</option>
                        <option value="finished">Завершён</option>
                    </select>
                    <label for="tournamentStatus">Статус</label>
                </div>
            </div>

        </div>
        <div v-if="userInfoStore.userInfo.is_admin" class="row g-2 mb-2">
            <div class="col">
                <div class="form-floating">
                    <input
                        id="tournamentStartDate"
                        v-model="newTournamentStartDate"
                        type="date"
                        class="form-control"
                    >
                    <label for="tournamentStartDate">Дата начала</label>
                </div>
            </div>
            <div class="col">
                <div class="form-floating">
                    <input
                        id="tournamentEndDate"
                        v-model="newTournamentEndDate"
                        type="date"
                        class="form-control"
                    >
                    <label for="tournamentEndDate">Дата окончания</label>
                </div>
            </div>
            <div class="col">
                <div class="form-floating">
                    <input
                        id="tournamentPrizePool"
                        v-model="newTournamentPrizePool"
                        type="number"
                        class="form-control"
                        placeholder="Призовой фонд"
                    >
                    <label for="tournamentPrizePool">Призовой фонд</label>
                </div>
            </div>
        </div>

        <div v-if="userInfoStore.userInfo.is_admin" class="row g-2 mb-2">
            <div class="col">
                <div class="form-floating">
                    <input
                        id="tournamentPicture"
                        ref="pictureInput"
                        type="file"
                        class="form-control"
                        accept="image/*"
                        @change="onPictureChange"
                    >
                    <label for="tournamentPicture">Афиша турнира</label>
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
                <h5 class="card-title mb-3">Фильтрация турниров</h5>

                <div class="row g-2 mb-2">

                    <div class="col-md-4">
                        <label class="form-label">Название</label>
                        <input
                            v-model="filters.name"
                            type="text"
                            class="form-control"
                            placeholder="Поиск по названию"
                        >
                    </div>

                    <div class="col-md-4">
                        <label class="form-label">Дисциплина</label>
                        <select v-model="filters.discipline_id" class="form-select">
                            <option value="">Все дисциплины</option>
                            <option
                                v-for="discipline in disciplines"
                                :key="discipline.id"
                                :value="discipline.id"
                            >
                                {{ discipline.name }}
                            </option>
                        </select>
                    </div>

                    <div class="col-md-4">
                        <label class="form-label">Организатор</label>
                        <select v-model="filters.organizer_id" class="form-select">
                            <option value="">Все организаторы</option>
                            <option
                                v-for="organizer in organizers"
                                :key="organizer.id"
                                :value="organizer.id"
                            >
                                {{ organizer.name }}
                            </option>
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Статус</label>
                        <select v-model="filters.status" class="form-select">
                            <option value="">Все статусы</option>
                            <option value="registration">Регистрация открыта</option>
                            <option value="closed">Регистрация закрыта</option>
                            <option value="ongoing">Проводится</option>
                            <option value="finished">Завершён</option>
                        </select>
                    </div>
                </div>
                <div class="row g-2 mb-2">
                    <div class="col-md-6">
                        <label class="form-label">Дата начала от</label>
                        <input
                            v-model="filters.start_date"
                            type="date"
                            class="form-control"
                        >
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Дата окончания до</label>
                        <input
                            v-model="filters.end_date"
                            type="date"
                            class="form-control"
                        >
                    </div>
                </div>

                <div class="row g-2 mb-3">
                    <div class="col-md-6">
                        <label class="form-label">Призовой фонд от</label>
                        <input
                            v-model="filters.prize_pool_min"
                            type="number"
                            class="form-control"
                            min="0"
                            step="0.01"
                        >
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Призовой фонд до</label>
                        <input
                            v-model="filters.prize_pool_max"
                            type="number"
                            class="form-control"
                            min="0"
                            step="0.01"
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

                <div v-if="userInfoStore.userInfo.is_admin" class="mt-2">
                    <a
                        href="/api/tournaments/export-excel/"
                        class="btn btn-success"
                    >
                        Скачать Excel
                    </a>
                </div>
            </div>
        </div>

        <div v-if="userInfoStore.userInfo.is_admin" class="row g-2 mb-3">
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Количество турниров</h5>
                        <p class="card-text">{{ statistics.total ?? 0 }}</p>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Общий призовой фонд</h5>
                        <p class="card-text">{{ statistics.total_prize_pool ?? 0 }}</p>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Средний призовой фонд</h5>
                        <p class="card-text">
                            {{ statistics.average_prize_pool?.toFixed(2) ?? 0 }}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <div>
            <div
                v-for="tournament in tournaments"
                :key="tournament.id"
                class="tournament-item"
            >
                <div class="d-flex align-items-center gap-3">
                    <img
                        v-if="tournament.picture"
                        :src="tournament.picture"
                        width="60"
                        height="60"
                        style="object-fit: cover; cursor: pointer;"
                        data-bs-toggle="modal"
                        data-bs-target="#pictureModal"
                        @click="pictureToShow = tournament.picture"
                    >
                    <div>{{ tournament.name }}</div>
                </div>

                <button
                    v-if="
                        !userInfoStore.userInfo.is_admin &&
                        userInfoStore.userInfo.is_captain &&
                        tournament.status === 'registration'
                    "
                    class="btn btn-primary"
                    @click="onApplyClick(tournament)"
                >
                    Подать заявку
                </button>

                <button
                    v-if="userInfoStore.userInfo.is_admin"
                    class="btn btn-success"
                    data-bs-toggle="modal"
                    data-bs-target="#editTournamentModal"
                    @click="onTournamentEditClick(tournament)"
                >
                    <i class="bi bi-pen-fill"></i>
                </button>

                <button
                    v-if="userInfoStore.userInfo.is_admin"
                    class="btn btn-danger"
                    @click="onRemoveClick(tournament)"
                >
                    <i class="bi bi-x"></i>
                </button>
            </div>
        </div>

        <div
            v-if="userInfoStore.userInfo.is_admin"
            id="editTournamentModal"
            class="modal fade"
            tabindex="-1"
        >
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h1 class="modal-title fs-5">Редактировать турнир</h1>
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
                                        id="editName"
                                        v-model="tournamentToEdit.name"
                                        type="text"
                                        class="form-control"
                                        placeholder="Название"
                                    >
                                    <label for="editName">Название</label>
                                </div>
                            </div>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <input
                                        id="editStartDate"
                                        v-model="tournamentToEdit.start_date"
                                        type="date"
                                        class="form-control"
                                    >
                                    <label for="editStartDate">Дата начала</label>
                                </div>
                            </div>
                            <div class="col">
                                <div class="form-floating">
                                    <input
                                        id="editEndDate"
                                        v-model="tournamentToEdit.end_date"
                                        type="date"
                                        class="form-control"
                                    >
                                    <label for="editEndDate">Дата окончания</label>
                                </div>
                            </div>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <input
                                        id="editPrizePool"
                                        v-model="tournamentToEdit.prize_pool"
                                        type="number"
                                        class="form-control"
                                        placeholder="Призовой фонд"
                                    >
                                    <label for="editPrizePool">Призовой фонд</label>
                                </div>
                            </div>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <select
                                        id="editDiscipline"
                                        v-model="tournamentToEdit.discipline_id"
                                        class="form-select"
                                    >
                                        <option
                                            v-for="discipline in disciplines"
                                            :key="discipline.id"
                                            :value="discipline.id"
                                        >
                                            {{ discipline.name }}
                                        </option>
                                    </select>
                                    <label for="editDiscipline">Дисциплина</label>
                                </div>
                            </div>
                            <div class="col">
                                <div class="form-floating">
                                    <select
                                        id="editOrganizer"
                                        v-model="tournamentToEdit.organizer"
                                        class="form-select"
                                    >
                                        <option value="">Без организатора</option>
                                        <option
                                            v-for="organizer in organizers"
                                            :key="organizer.id"
                                            :value="organizer.id"
                                        >
                                            {{ organizer.name }}
                                        </option>
                                    </select>
                                    <label for="editOrganizer">Организатор</label>
                                </div>
                            </div>
                        </div>
                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <select
                                        id="editStatus"
                                        v-model="tournamentToEdit.status"
                                        class="form-select"
                                    >
                                        <option value="registration">Регистрация открыта</option>
                                        <option value="closed">Регистрация закрыта</option>
                                        <option value="ongoing">Проводится</option>
                                        <option value="finished">Завершён</option>
                                    </select>
                                    <label for="editStatus">Статус</label>
                                </div>
                            </div>
                        </div>
                        <div class="row g-2 mb-2">
                            <div class="col">
                                <label class="form-label">
                                    Изменить афишу турнира
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
                            @click="onUpdateTournament"
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
.tournament-item {
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