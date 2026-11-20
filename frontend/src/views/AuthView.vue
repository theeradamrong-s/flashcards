<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// One page for both /login and /register
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const isRegister = computed(() => route.name === 'register')
const username = ref('')
const password = ref('')
const error = ref('')
const busy = ref(false)

async function submit() {
  error.value = ''
  busy.value = true
  try {
    if (isRegister.value) {
      await auth.register(username.value, password.value)
    } else {
      await auth.login(username.value, password.value)
    }
    // Go back to the page they wanted before being sent to login
    const redirect = route.query.redirect
    router.push(typeof redirect === 'string' && redirect.startsWith('/') ? redirect : '/')
  } catch (err) {
    error.value = err.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <section class="auth panel">
    <h1>{{ isRegister ? 'Create an account' : 'Log in' }}</h1>
    <p class="muted">
      {{ isRegister ? 'Start building decks and studying smarter.' : 'Welcome back.' }}
    </p>

    <form class="stack" @submit.prevent="submit">
      <label>
        Username
        <input v-model="username" autocomplete="username" required minlength="3" maxlength="30" />
      </label>
      <label>
        Password
        <input
          v-model="password"
          type="password"
          :autocomplete="isRegister ? 'new-password' : 'current-password'"
          required
          :minlength="isRegister ? 6 : undefined"
        />
        <small v-if="isRegister" class="muted">At least 6 characters.</small>
      </label>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="btn btn-primary" :disabled="busy">
        {{ busy ? 'Please wait…' : isRegister ? 'Sign up' : 'Log in' }}
      </button>
    </form>

    <p class="muted switch">
      <template v-if="isRegister">
        Already have an account? <RouterLink to="/login">Log in</RouterLink>
      </template>
      <template v-else>
        New here? <RouterLink to="/register">Create an account</RouterLink>
      </template>
    </p>
  </section>
</template>

<style scoped>
.auth {
  max-width: 400px;
  margin: 3rem auto;
}
.auth h1 {
  margin-bottom: 0.25rem;
}
.auth form {
  margin-top: 1.5rem;
}
.switch {
  margin-top: 1.25rem;
  text-align: center;
}
</style>
