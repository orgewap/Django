<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"
import Cookies from "js-cookie"

import { useUserInfoStore } from "../stores/user_info_store"

const router = useRouter()
const userInfoStore = useUserInfoStore()

const username = ref("")
const password = ref("")
const error = ref("")


async function onLoginClick() {
    error.value = ""

    try {
        const response = await axios.post(
            "/api/userprofiles/login/",
            {
                username: username.value,
                password: password.value
            },
            {
                headers: {
                    "X-CSRFToken": Cookies.get("csrftoken")
                }
            }
        )

        if (response.data.success) {
            await userInfoStore.fetchUserInfo()
            router.push("/tournaments")
        } else {
            error.value = "Неверный логин или пароль"
        }
    } catch (e) {
        error.value = "Не удалось выполнить вход"
    }
}
</script>

<template>
    <div class="container mt-5">

        <div class="row justify-content-center">

            <div class="col-md-4">

                <h3 class="mb-3">
                    Авторизация
                </h3>

                <div class="mb-3">

                    <label class="form-label">
                        Логин
                    </label>

                    <input
                        type="text"
                        class="form-control"
                        v-model="username"
                    >

                </div>

                <div class="mb-3">

                    <label class="form-label">
                        Пароль
                    </label>

                    <input
                        type="password"
                        class="form-control"
                        v-model="password"
                        @keyup.enter="onLoginClick"
                    >

                </div>

                <div
                    v-if="error"
                    class="alert alert-danger"
                >
                    {{ error }}
                </div>

                <button
                    class="btn btn-primary"
                    @click="onLoginClick"
                >
                    Войти
                </button>

            </div>

        </div>

    </div>
</template>