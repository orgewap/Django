
import { defineStore } from "pinia"
import { ref } from "vue"
import axios from "axios"
import Cookies from "js-cookie"

export const useUserInfoStore = defineStore("userInfoStore", () => {

    const userInfo = ref({
        is_authenticated: false,
        is_superuser: false,
        username: null,
        role: null,
        is_admin: false,
        is_captain: false,
        team_id: null
    })

    async function fetchUserInfo() {
        const response = await axios.get(
            "/api/userprofiles/info/"
        )

        userInfo.value = response.data

        axios.defaults.headers.common["X-CSRFToken"] =
            Cookies.get("csrftoken")
    }

    return {
        userInfo,
        fetchUserInfo
    }
})