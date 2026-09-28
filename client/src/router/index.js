
import { createRouter, createWebHistory } from 'vue-router'

import TournamentsView from '../views/TournamentsView.vue'
import DisciplinesView from '../views/DisciplinesView.vue'
import OrganizersView from '../views/OrganizersView.vue'
import TeamsView from '../views/TeamsView.vue'
import MembersView from '../views/MembersView.vue'
import LoginView from '../views/LoginView.vue'
import ApplicationsView from '../views/ApplicationsView.vue'
import ProfileView from '../views/ProfileView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/tournaments',
            name: 'tournaments',
            component: TournamentsView
        },
        {
            path: '/disciplines',
            name: 'disciplines',
            component: DisciplinesView
        },
        {
            path: '/organizers',
            name: 'organizers',
            component: OrganizersView
        },
        {
            path: '/teams',
            name: 'teams',
            component: TeamsView
        },
        {
            path: '/members',
            name: 'members',
            component: MembersView
        },
        {
            path: '/applications',
            name: 'applications',
            component: ApplicationsView
        },
        {
            path: '/login',
            name: 'login',
            component: LoginView
        },
        {
            path: '/profile',
            name: 'profile',
            component: ProfileView
        }
    ],
})

export default router