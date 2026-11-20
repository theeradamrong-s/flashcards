import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api, setToken } from '@/api'

const STORAGE_KEY = 'flashcards-auth'

function loadSaved() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) ?? {}
  } catch {
    return {}
  }
}

export const useAuthStore = defineStore('auth', () => {
  const saved = loadSaved()
  const token = ref(saved.token ?? null)
  const username = ref(saved.username ?? null)
  setToken(token.value)

  const isLoggedIn = computed(() => Boolean(token.value))

  // Keep the token in localStorage so a page refresh doesn't log you out
  function save() {
    setToken(token.value)
    try {
      if (token.value) {
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({ token: token.value, username: username.value }),
        )
      } else {
        localStorage.removeItem(STORAGE_KEY)
      }
    } catch {
      // storage blocked (e.g. private mode): stay logged in for this tab only
    }
  }

  async function login(name, password) {
    const data = await api('/auth/login', { method: 'POST', body: { username: name, password } })
    token.value = data.access_token
    username.value = name.trim().toLowerCase()
    save()
  }

  async function register(name, password) {
    await api('/auth/register', { method: 'POST', body: { username: name, password } })
    await login(name, password)
  }

  function logout() {
    token.value = null
    username.value = null
    save()
  }

  return { token, username, isLoggedIn, login, register, logout }
})
