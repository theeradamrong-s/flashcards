<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <header class="topbar">
    <div class="container topbar-inner">
      <RouterLink to="/" class="brand">Flashcards</RouterLink>
      <div v-if="auth.isLoggedIn" class="user">
        <span class="muted">{{ auth.username }}</span>
        <button class="btn btn-ghost btn-small" @click="logout">Log out</button>
      </div>
    </div>
  </header>
  <main class="container">
    <!-- key: rebuild the page when the URL changes, e.g. /decks/1 → /decks/2 -->
    <RouterView :key="$route.fullPath" />
  </main>
</template>
