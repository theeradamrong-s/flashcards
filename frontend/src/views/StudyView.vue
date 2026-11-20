<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'

const route = useRoute()
const deckId = route.params.id

const deck = ref(null)
const queue = ref([]) // cards still to review in this session
const reviewed = ref(0)
const showAnswer = ref(false)
const loading = ref(true)
const busy = ref(false)
const error = ref('')

const current = computed(() => queue.value[0])
const total = computed(() => reviewed.value + queue.value.length)

// The four buttons map to SM-2 quality scores (0-5)
const ratings = [
  { label: 'Again', quality: 1, key: '1', style: 'again' },
  { label: 'Hard', quality: 3, key: '2', style: 'hard' },
  { label: 'Good', quality: 4, key: '3', style: 'good' },
  { label: 'Easy', quality: 5, key: '4', style: 'easy' },
]

async function load() {
  try {
    deck.value = await api(`/decks/${deckId}`)
    queue.value = await api(`/decks/${deckId}/due`)
  } catch (err) {
    error.value = err.status === 404 ? 'Deck not found.' : err.message
  } finally {
    loading.value = false
  }
}

async function rate(quality) {
  if (!current.value || busy.value) return
  busy.value = true
  error.value = ''
  try {
    const card = queue.value.shift()
    await api(`/cards/${card.id}/review`, { method: 'POST', body: { quality } })
    if (quality < 3) {
      queue.value.push(card) // forgot it: see it again at the end of this session
    } else {
      reviewed.value++
    }
    showAnswer.value = false
  } catch (err) {
    error.value = err.message
    await load() // resync with the server if something went wrong
  } finally {
    busy.value = false
  }
}

// Keyboard shortcuts: Space shows the answer, 1-4 rate it
function onKey(event) {
  if (!current.value || event.target.closest?.('input, textarea')) return
  if (!showAnswer.value && (event.key === ' ' || event.key === 'Enter')) {
    event.preventDefault()
    showAnswer.value = true
  } else if (showAnswer.value) {
    const rating = ratings.find((r) => r.key === event.key)
    if (rating) rate(rating.quality)
  }
}

onMounted(() => {
  load()
  window.addEventListener('keydown', onKey)
})
onUnmounted(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <RouterLink :to="`/decks/${deckId}`" class="back">← Back to deck</RouterLink>

  <p v-if="loading" class="muted">Loading…</p>

  <div v-else-if="error && !deck" class="empty">
    <p>{{ error }}</p>
  </div>

  <template v-else>
    <div class="study-header">
      <h1>{{ deck.name }}</h1>
      <span v-if="total" class="muted">{{ reviewed }} / {{ total }} done</span>
    </div>
    <div v-if="total" class="progress">
      <div class="progress-bar" :style="{ width: `${(reviewed / total) * 100}%` }"></div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="current" class="flashcard panel">
      <p class="label muted">Question</p>
      <p class="face">{{ current.front }}</p>
      <template v-if="showAnswer">
        <hr />
        <p class="label muted">Answer</p>
        <p class="face">{{ current.back }}</p>
      </template>
    </div>

    <div v-if="current" class="controls">
      <button v-if="!showAnswer" class="btn btn-primary btn-wide" @click="showAnswer = true">
        Show answer <kbd>Space</kbd>
      </button>
      <div v-else class="ratings">
        <button
          v-for="r in ratings"
          :key="r.label"
          class="btn rating"
          :class="r.style"
          :disabled="busy"
          @click="rate(r.quality)"
        >
          {{ r.label }} <kbd>{{ r.key }}</kbd>
        </button>
      </div>
    </div>

    <div v-else class="empty done">
      <p class="big">🎉 All done!</p>
      <p class="muted">
        {{
          reviewed ? `You reviewed ${reviewed} cards.` : 'No cards are due in this deck right now.'
        }}
        Come back later for the next reviews.
      </p>
      <RouterLink :to="`/decks/${deckId}`" class="btn btn-primary">Back to deck</RouterLink>
    </div>
  </template>
</template>

<style scoped>
.study-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
}
.progress {
  height: 6px;
  background: var(--surface-2);
  border-radius: 999px;
  overflow: hidden;
  margin: 0.5rem 0 1.5rem;
}
.progress-bar {
  height: 100%;
  background: var(--accent);
  transition: width 0.3s;
}
.flashcard {
  min-height: 240px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
  padding: 2rem;
}
.flashcard hr {
  border: none;
  border-top: 1px dashed var(--border);
  margin: 1.25rem 0;
}
.label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.face {
  font-size: 1.5rem;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.controls {
  margin-top: 1.25rem;
}
.btn-wide {
  width: 100%;
}
.ratings {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}
@media (max-width: 480px) {
  .ratings {
    grid-template-columns: repeat(2, 1fr);
  }
}
.rating {
  color: #fff;
}
.again {
  background: var(--danger);
}
.hard {
  background: var(--warning);
}
.good {
  background: var(--success);
}
.easy {
  background: var(--accent);
}
kbd {
  font-size: 0.7rem;
  opacity: 0.7;
  margin-left: 0.35rem;
  font-family: inherit;
}
.done {
  margin-top: 2rem;
}
.big {
  font-size: 1.75rem;
}
</style>
