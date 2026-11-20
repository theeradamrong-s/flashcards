import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AuthView from '../views/AuthView.vue'
import DeckListView from '../views/DeckListView.vue'
import DeckView from '../views/DeckView.vue'
import StudyView from '../views/StudyView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/login', name: 'login', component: AuthView, meta: { public: true } },
    { path: '/register', name: 'register', component: AuthView, meta: { public: true } },
    { path: '/', name: 'decks', component: DeckListView },
    { path: '/decks/:id', name: 'deck', component: DeckView },
    { path: '/decks/:id/study', name: 'study', component: StudyView },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

// Send logged-out users to the login page, and logged-in users away from it
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isLoggedIn) {
    return { name: 'login', query: to.fullPath === '/' ? {} : { redirect: to.fullPath } }
  }
  if (to.meta.public && auth.isLoggedIn) {
    return { name: 'decks' }
  }
})

export default router
