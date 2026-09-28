<script setup>
import { ref, onBeforeMount } from "vue"
import axios from "axios"
import Cookies from "js-cookie"
import { useUserInfoStore } from "../stores/user_info_store"

const userInfoStore = useUserInfoStore()

const organizers = ref([])
const statistics = ref({})

const filters = ref({
    name: "",
    email: "",
    social_media: ""
})

const newOrganizerName = ref("")
const newOrganizerEmail = ref("")
const newOrganizerSocialMedia = ref("")
const newOrganizerPicture = ref(null)

const pictureInput = ref(null)

const organizerToEdit = ref({})
const editOrganizerPicture = ref(null)
const editPictureInput = ref(null)

const pictureToShow = ref("")


onBeforeMount(async () => {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken")
    await userInfoStore.fetchUserInfo()
    await onLoadClick()
})



async function onLoadClick() {
    const response = await axios.get(
        "/api/organizers/",
        {
            params: filters.value
        }
    )

    organizers.value = response.data

    if (userInfoStore.userInfo.is_admin) {
        const statsResponse = await axios.get("/api/organizers/stats/")
        statistics.value = statsResponse.data
    }
}


async function onResetFilters() {
    filters.value = {
        name: "",
        email: "",
        social_media: ""
    }

    await onLoadClick()
}

function onPictureChange(event) {
    newOrganizerPicture.value = event.target.files[0] || null
}


async function onCreateClick() {
    const formData = new FormData()

    formData.append("name", newOrganizerName.value)
    formData.append("email", newOrganizerEmail.value)
    formData.append("social_media", newOrganizerSocialMedia.value)

    if (newOrganizerPicture.value) {
        formData.append("picture", newOrganizerPicture.value)
    }

    await axios.post("/api/organizers/", formData)

    newOrganizerName.value = ""
    newOrganizerEmail.value = ""
    newOrganizerSocialMedia.value = ""
    newOrganizerPicture.value = null

    if (pictureInput.value) {
        pictureInput.value.value = ""
    }

    await onLoadClick()
}


async function onRemoveClick(organizer) {
    await axios.delete(`/api/organizers/${organizer.id}/`)
    await onLoadClick()
}


function onOrganizerEditClick(organizer) {
    organizerToEdit.value = { ...organizer }

    editOrganizerPicture.value = null

    if (editPictureInput.value) {
        editPictureInput.value.value = ""
    }
}


function onEditPictureChange(event) {
    editOrganizerPicture.value = event.target.files[0] || null
}


async function onUpdateOrganizer() {
    const formData = new FormData()

    formData.append("name", organizerToEdit.value.name)
    formData.append("email", organizerToEdit.value.email)
    formData.append("social_media", organizerToEdit.value.social_media)

    if (editOrganizerPicture.value) {
        formData.append("picture", editOrganizerPicture.value)
    }

    await axios.put(
        `/api/organizers/${organizerToEdit.value.id}/`,
        formData
    )

    editOrganizerPicture.value = null

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
                        type="text"
                        class="form-control"
                        id="organizerName"
                        placeholder="Название"
                        v-model="newOrganizerName"
                    >
                    <label for="organizerName">Название</label>
                </div>
            </div>

            <div class="col">
                <div class="form-floating">
                    <input
                        type="email"
                        class="form-control"
                        id="organizerEmail"
                        placeholder="Электронная почта"
                        v-model="newOrganizerEmail"
                    >
                    <label for="organizerEmail">
                        Электронная почта
                    </label>
                </div>
            </div>

            <div class="col">
                <div class="form-floating">
                    <input
                        type="text"
                        class="form-control"
                        id="organizerSocialMedia"
                        placeholder="Социальные сети"
                        v-model="newOrganizerSocialMedia"
                    >
                    <label for="organizerSocialMedia">
                        Социальные сети
                    </label>
                </div>
            </div>

        </div>


        <div v-if="userInfoStore.userInfo.is_admin" class="row g-2 mb-2">

            <div class="col">
                <div class="form-floating">
                    <input
                        ref="pictureInput"
                        type="file"
                        class="form-control"
                        id="organizerPicture"
                        accept="image/*"
                        @change="onPictureChange"
                    >
                    <label for="organizerPicture">
                        Логотип организатора
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
                    Фильтрация организаторов
                </h5>

                <div class="row g-2 mb-3">

                    <div class="col-md-4">
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

                    <div class="col-md-4">
                        <label class="form-label">
                            Электронная почта
                        </label>

                        <input
                            type="text"
                            class="form-control"
                            v-model="filters.email"
                            placeholder="Поиск по почте"
                        >
                    </div>

                    <div class="col-md-4">
                        <label class="form-label">
                            Социальные сети
                        </label>

                        <input
                            type="text"
                            class="form-control"
                            v-model="filters.social_media"
                            placeholder="Поиск по социальным сетям"
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
                            Количество организаторов
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
                            Уникальные адреса электронной почты
                        </h5>

                        <p class="card-text">
                            {{ statistics.total_emails ?? 0 }}
                        </p>
                    </div>
                </div>
            </div>

        </div>

        <div>
            <div
                v-for="organizer in organizers"
                :key="organizer.id"
                class="organizer-item"
            >

                <div class="d-flex align-items-center gap-3">

                    <img
                        v-if="organizer.picture"
                        :src="organizer.picture"
                        width="60"
                        height="60"
                        style="object-fit: cover; cursor: pointer;"
                        @click="pictureToShow = organizer.picture"
                        data-bs-toggle="modal"
                        data-bs-target="#pictureModal"
                    >

                    <div>
                        {{ organizer.name }}
                    </div>

                </div>


                <button
                    v-if="userInfoStore.userInfo.is_admin"
                    class="btn btn-success"
                    @click="onOrganizerEditClick(organizer)"
                    data-bs-toggle="modal"
                    data-bs-target="#editOrganizerModal"
                >
                    <i class="bi bi-pen-fill"></i>
                </button>


                <button
                    v-if="userInfoStore.userInfo.is_admin"
                    class="btn btn-danger"
                    @click="onRemoveClick(organizer)"
                >
                    <i class="bi bi-x"></i>
                </button>

            </div>
        </div>


        <div
            v-if="userInfoStore.userInfo.is_admin"
            class="modal fade"
            id="editOrganizerModal"
            tabindex="-1"
        >
            <div class="modal-dialog">
                <div class="modal-content">

                    <div class="modal-header">
                        <h1 class="modal-title fs-5">
                            Редактировать организатора
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
                                        id="editOrganizerName"
                                        placeholder="Название"
                                        v-model="organizerToEdit.name"
                                    >
                                    <label for="editOrganizerName">
                                        Название
                                    </label>
                                </div>
                            </div>
                        </div>


                        <div class="row g-2 mb-2">
                            <div class="col">
                                <div class="form-floating">
                                    <input
                                        type="email"
                                        class="form-control"
                                        id="editOrganizerEmail"
                                        placeholder="Электронная почта"
                                        v-model="organizerToEdit.email"
                                    >
                                    <label for="editOrganizerEmail">
                                        Электронная почта
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
                                        id="editOrganizerSocialMedia"
                                        placeholder="Социальные сети"
                                        v-model="organizerToEdit.social_media"
                                    >
                                    <label for="editOrganizerSocialMedia">
                                        Социальные сети
                                    </label>
                                </div>
                            </div>
                        </div>


                        <div class="row g-2 mb-2">
                            <div class="col">

                                <label class="form-label">
                                    Изменить логотип организатора
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
                            @click="onUpdateOrganizer"
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
.organizer-item {
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