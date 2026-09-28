<script setup>
import { ref, onBeforeMount } from "vue"
import axios from "axios"
import Cookies from "js-cookie"
import { useUserInfoStore } from "../stores/user_info_store"

const userInfoStore = useUserInfoStore()

const disciplines = ref([])
const statistics = ref({})

const filters = ref({
    name: "",
    genre: "",
    description: ""
})

const newDisciplineName = ref("")
const newDisciplineGenre = ref("")
const newDisciplineDescription = ref("")
const newDisciplinePicture = ref(null)
const pictureInput = ref(null)

const disciplineToEdit = ref({})
const editDisciplinePicture = ref(null) 
const pictureToShow = ref("")


onBeforeMount(async () => {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken")
    await userInfoStore.fetchUserInfo()
    await onLoadClick()
})


async function onLoadClick() {
    const response = await axios.get(
        "/api/disciplines/",
        {
            params: filters.value
        }
    )

    disciplines.value = response.data

    if (userInfoStore.userInfo.is_admin) {
        const statsResponse = await axios.get("/api/disciplines/stats/")
        statistics.value = statsResponse.data
    }
}
async function onResetFilters() {
    filters.value = {
        name: "",
        genre: "",
        description: ""
    }

    await onLoadClick()
}

function onPictureChange(event) {
    newDisciplinePicture.value = event.target.files[0]
}

function onEditPictureChange(event) {
    editDisciplinePicture.value = event.target.files[0]
}

async function onCreateClick() {
    const formData = new FormData()

    formData.append("name", newDisciplineName.value)
    formData.append("genre", newDisciplineGenre.value)
    formData.append("description", newDisciplineDescription.value)

    if (newDisciplinePicture.value) {
        formData.append("picture", newDisciplinePicture.value)
    }

    await axios.post("/api/disciplines/", formData)

    newDisciplineName.value = ""
    newDisciplineGenre.value = ""
    newDisciplineDescription.value = ""
    newDisciplinePicture.value = null
    pictureInput.value.value = ""

    await onLoadClick()
}


async function onRemoveClick(discipline) {
    await axios.delete(`/api/disciplines/${discipline.id}/`)
    await onLoadClick()
}


function onDisciplineEditClick(discipline) {
    disciplineToEdit.value = { ...discipline }
}


async function onUpdateDiscipline() {
    const formData = new FormData()

    formData.append("name", disciplineToEdit.value.name)
    formData.append("genre", disciplineToEdit.value.genre)
    formData.append("description", disciplineToEdit.value.description)

    if (editDisciplinePicture.value) {
        formData.append("picture", editDisciplinePicture.value)
    }

    await axios.put(
        `/api/disciplines/${disciplineToEdit.value.id}/`,
        formData
    )

    editDisciplinePicture.value = null

    await onLoadClick()
}

</script>


<template>
    <div class="p-2">

        <div v-if="userInfoStore.userInfo.is_admin" class="row g-2 mb-2">

            <div class="col">
                <div class="form-floating">
                    <input
                        type="text"
                        class="form-control"
                        id="disciplineName"
                        placeholder="Название"
                        v-model="newDisciplineName"
                    >
                    <label for="disciplineName">Название</label>
                </div>
            </div>

            <div class="col">
                <div class="form-floating">
                    <input
                        type="text"
                        class="form-control"
                        id="disciplineGenre"
                        placeholder="Жанр"
                        v-model="newDisciplineGenre"
                    >
                    <label for="disciplineGenre">Жанр</label>
                </div>
            </div>

            <div class="col">
                <div class="form-floating">
                    <input
                        type="text"
                        class="form-control"
                        id="disciplineDescription"
                        placeholder="Описание"
                        v-model="newDisciplineDescription"
                    >
                    <label for="disciplineDescription">Описание</label>
                </div>
            </div>
            
            
            <div class="col">
                <div class="form-floating">
                    <input
                        ref="pictureInput"
                        type="file"
                        class="form-control"
                        id="disciplinePicture"
                        accept="image/*"
                        @change="onPictureChange"
                    >
                    <label for="disciplinePicture">
                        Изображение
                    </label>
                </div>
            </div>  

            <div class="col-auto">
                <button
                    class="btn btn-primary"
                    @click="onCreateClick"
                >
                    Добавить
                </button>
            </div>

        </div>

        <div class="card mb-3">
            <div class="card-body">

                <h5 class="card-title mb-3">
                    Фильтрация дисциплин
                </h5>

                <div class="row g-2 mb-3">
                    <div class="col-md-6">
                        <label class="form-label">
                            Название
                        </label>

                        <input
                            type="text"
                            class="form-control"
                            v-model="filters.name"
                            placeholder="Поиск по названию"
                        >
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">
                            Жанр
                        </label>

                        <input
                            type="text"
                            class="form-control"
                            v-model="filters.genre"
                            placeholder="Поиск по жанру"
                        >
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">
                            Описание
                        </label>

                        <input
                            type="text"
                            class="form-control"
                            v-model="filters.description"
                            placeholder="Поиск по описанию"
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

        <div v-if="userInfoStore.userInfo.is_admin" class="row g-2 mb-3">

            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            Количество дисциплин
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
                            Количество жанров
                        </h5>

                        <p class="card-text">
                            {{ statistics.total_genres ?? 0 }}
                        </p>
                    </div>
                </div>
            </div>

        </div>

        <div>
            <div
                v-for="discipline in disciplines"
                :key="discipline.id"
                class="discipline-item"
            >
                <div class="d-flex align-items-center gap-3">
                    <img
                        v-if="discipline.picture"
                        :src="discipline.picture"
                        width="60"
                        height="60"
                        style="object-fit: cover; cursor: pointer;"
                        @click="pictureToShow = discipline.picture"
                        data-bs-toggle="modal"
                        data-bs-target="#pictureModal"
                    >

                    <div>
                        {{ discipline.name }}
                    </div>
                </div>

                <button
                    v-if="userInfoStore.userInfo.is_admin"
                    class="btn btn-success"
                    @click="onDisciplineEditClick(discipline)"
                    data-bs-toggle="modal"
                    data-bs-target="#editDisciplineModal"
                >
                    <i class="bi bi-pen-fill"></i>
                </button>

                <button
                    v-if="userInfoStore.userInfo.is_admin"
                    class="btn btn-danger"
                    @click="onRemoveClick(discipline)"
                >
                    <i class="bi bi-x"></i>
                </button>
            </div>
        </div>


        <div
            v-if="userInfoStore.userInfo.is_admin"
            class="modal fade"
            id="editDisciplineModal"
            tabindex="-1"
        >
            <div class="modal-dialog">
                <div class="modal-content">

                    <div class="modal-header">
                        <h1 class="modal-title fs-5">
                            Редактировать дисциплину
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
                                    <input
                                        type="text"
                                        class="form-control"
                                        id="editDisciplineName"
                                        placeholder="Название"
                                        v-model="disciplineToEdit.name"
                                    >
                                    <label for="editDisciplineName">
                                        Название
                                    </label>
                                </div>
                            </div>
                        </div>


                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <input
                                        type="text"
                                        class="form-control"
                                        id="editDisciplineGenre"
                                        placeholder="Жанр"
                                        v-model="disciplineToEdit.genre"
                                    >
                                    <label for="editDisciplineGenre">
                                        Жанр
                                    </label>
                                </div>
                            </div>
                        </div>


                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <input
                                        type="text"
                                        class="form-control"
                                        id="editDisciplineDescription"
                                        placeholder="Описание"
                                        v-model="disciplineToEdit.description"
                                    >
                                    <label for="editDisciplineDescription">
                                        Описание
                                    </label>
                                </div>
                            </div>
                        </div>


                    <div class="row g-2 mb-2">
                        <div class="col">
                            <label class="form-label">
                                Изменить изображение
                            </label>

                            <input
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
                            @click="onUpdateDiscipline"
                        >
                            Сохранить
                        </button>
                    </div>

                </div>
            </div>
        </div>
        <div
            class="modal fade"
            id="pictureModal"
            tabindex="-1"
        >
            <div class="modal-dialog modal-lg">
                <div class="modal-content">

                    <div class="modal-header">
                        <h5 class="modal-title">
                            Просмотр изображения
                        </h5>

                        <button
                            type="button"
                            class="btn-close"
                            data-bs-dismiss="modal"
                        ></button>
                    </div>

                    <div class="modal-body text-center">
                        <img
                            :src="pictureToShow"
                            class="img-fluid"
                        >
                    </div>

                </div>
            </div>
        </div>
    </div>
</template>


<style scoped>
.discipline-item {
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