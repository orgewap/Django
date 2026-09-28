
<script setup>
import { RouterLink, RouterView, useRouter } from "vue-router"
import { onBeforeMount, ref } from "vue"
import { useUserInfoStore } from "./stores/user_info_store"
import axios from "axios"
import Cookies from "js-cookie"
import QRCode from "qrcode"

const router = useRouter()
const userInfoStore = useUserInfoStore()

const showOtp = ref(false)
const qrCode = ref("")
const otpCode = ref("")
const otpMessage = ref("")
const otpError = ref("")

onBeforeMount(() => {
    userInfoStore.fetchUserInfo()
})

async function onLogoutClick() {
    await axios.post("/api/userprofiles/logout/")
    await userInfoStore.fetchUserInfo()
    showOtp.value = false
    qrCode.value = ""
    otpCode.value = ""
    router.push("/login")
}

async function onOtpSetupClick() {
    otpMessage.value = ""
    otpError.value = ""
    otpCode.value = ""
    qrCode.value = ""
    showOtp.value = true

    try {
        const response = await axios.get("/api/userprofiles/otp-setup/")
        qrCode.value = await QRCode.toDataURL(response.data.url)
    } catch (error) {
        otpError.value = "Не удалось загрузить QR-код"
    }
}

async function onOtpLoginClick() {
    otpMessage.value = ""
    otpError.value = ""

    try {
        const response = await axios.post(
            "/api/userprofiles/otp-login/",
            {
                key: otpCode.value
            },
            {
                headers: {
                    "X-CSRFToken": Cookies.get("csrftoken")
                }
            }
        )

        if (response.data.success) {
            otpMessage.value = "Двухфакторная аутентификация пройдена"
            otpCode.value = ""
        } else {
            otpError.value = "Неверный код подтверждения"
        }
    } catch (error) {
        otpError.value = error.response?.data?.detail || "Не удалось проверить код"
    }
}
</script>

<template>
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
        <div class="container-fluid">
            <RouterLink class="navbar-brand" to="/tournaments">
                Киберспортивные турниры
            </RouterLink>

            <div
                v-if="userInfoStore.userInfo.is_authenticated"
                class="navbar-nav"
            >
                <RouterLink class="nav-link" to="/tournaments">
                    Турниры
                </RouterLink>

                <RouterLink class="nav-link" to="/disciplines">
                    Дисциплины
                </RouterLink>

                <RouterLink class="nav-link" to="/organizers">
                    Организаторы
                </RouterLink>

                <RouterLink class="nav-link" to="/teams">
                    Команды
                </RouterLink>

                <RouterLink class="nav-link" to="/members">
                    Участники
                </RouterLink>
                <RouterLink
                    v-if="
                        userInfoStore.userInfo.is_admin
                        || userInfoStore.userInfo.is_captain
                    "
                    class="nav-link"
                    to="/applications"
                >
                    Заявки
                </RouterLink>
                <RouterLink
                    class="nav-link"
                    to="/profile"
                >
                    Профиль
                </RouterLink>
            </div>

            <ul class="navbar-nav ms-auto">
                <li class="nav-item dropdown">
                    <a
                        class="nav-link dropdown-toggle"
                        href="#"
                        role="button"
                        data-bs-toggle="dropdown"
                        aria-expanded="false"
                    >
                        {{ userInfoStore.userInfo.is_authenticated
                            ? userInfoStore.userInfo.username
                            : "Пользователь (не авторизован)"
                        }}
                    </a>

                    <ul class="dropdown-menu dropdown-menu-end">
                        <li v-if="!userInfoStore.userInfo.is_authenticated">
                            <RouterLink class="dropdown-item" to="/login">
                                Войти
                            </RouterLink>
                        </li>

                        <li v-if="userInfoStore.userInfo.is_admin">
                            <a class="dropdown-item" href="/admin/">
                                Админка
                            </a>
                        </li>

                        <li v-if="userInfoStore.userInfo.is_admin">
                            <button
                                class="dropdown-item"
                                @click="onOtpSetupClick"
                            >
                                Google Authenticator
                            </button>
                        </li>

                        <li v-if="userInfoStore.userInfo.is_authenticated">
                            <button
                                class="dropdown-item"
                                @click="onLogoutClick"
                            >
                                Выйти
                            </button>
                        </li>
                    </ul>
                </li>
            </ul>
        </div>
    </nav>

    <div
        v-if="showOtp && userInfoStore.userInfo.is_admin"
        class="container mt-4"
    >
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="card">
                    <div class="card-body">
                        <h4 class="mb-3">Google Authenticator</h4>

                        <p>
                            Отсканируйте QR-код в приложении Google Authenticator.
                            Затем введите шестизначный код подтверждения.
                        </p>

                        <div v-if="qrCode" class="text-center mb-3">
                            <img
                                :src="qrCode"
                                alt="QR-код Google Authenticator"
                                class="img-fluid"
                            >
                        </div>

                        <div class="mb-3">
                            <label class="form-label">
                                Код подтверждения
                            </label>
                            <input
                                v-model="otpCode"
                                type="text"
                                class="form-control"
                                maxlength="6"
                                inputmode="numeric"
                                autocomplete="one-time-code"
                                placeholder="Введите 6 цифр"
                                @keyup.enter="onOtpLoginClick"
                            >
                        </div>

                        <div v-if="otpMessage" class="alert alert-success">
                            {{ otpMessage }}
                        </div>

                        <div v-if="otpError" class="alert alert-danger">
                            {{ otpError }}
                        </div>

                        <div class="d-flex gap-2">
                            <button
                                class="btn btn-primary"
                                :disabled="otpCode.length !== 6"
                                @click="onOtpLoginClick"
                            >
                                Подтвердить
                            </button>

                            <button
                                class="btn btn-secondary"
                                @click="showOtp = false"
                            >
                                Закрыть
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <RouterView v-else />
</template>