<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'

const route = useRoute()
const router = useRouter()
const deckId = route.params.id // "1" from /decks/1

const deck = ref(null) // null = not loaded yet
const cards = ref([])
const notFound = ref(false)
const error = ref('')

// Add card form
const newFront = ref('')
const newBack = ref('')

// Editing state: the deck header, or one card at a time
const editingDeck = ref(false)
const deckForm = ref({ name: '', description: '' })
const editingCardId = ref(null)
const cardForm = ref({ front: '', back: '' })

const today = new Date().toISOString().slice(0, 10)
const dueCount = computed(() => cards.value.filter((c) => c.due_date <= today).length)

async function load() {
  try {
    deck.value = await api(`/decks/${deckId}`)
    cards.value = await api(`/decks/${deckId}/cards`)
  } catch (err) {
    if (err.status === 404) notFound.value = true
    else error.value = err.message
  }
}

async function run(action) {
  error.value = ''
  try {
    await action()
  } catch (err) {
    error.value = err.message
  }
}

function addCard() {
  return run(async () => {
    const card = await api(`/decks/${deckId}/cards`, {
      method: 'POST',
      body: { front: newFront.value, back: newBack.value },
    })
    cards.value.push(card)
    newFront.value = ''
    newBack.value = ''
  })
}

function startEditCard(card) {
  editingCardId.value = card.id
  cardForm.value = { front: card.front, back: card.back }
}

function saveCard(card) {
  return run(async () => {
    const updated = await api(`/cards/${card.id}`, { method: 'PATCH', body: cardForm.value })
    Object.assign(card, updated)
    editingCardId.value = null
  })
}

function deleteCard(card) {
  if (!confirm(`Delete the card "${card.front}"?`)) return
  return run(async () => {
    await api(`/cards/${card.id}`, { method: 'DELETE' })
    cards.value = cards.value.filter((c) => c.id !== card.id)
  })
}

function startEditDeck() {
  deckForm.value = { name: deck.value.name, description: deck.value.description }
  editingDeck.value = true
}

function saveDeck() {
  return run(async () => {
    deck.value = await api(`/decks/${deckId}`, { method: 'PATCH', body: deckForm.value })
    editingDeck.value = false
  })
}

function deleteDeck() {
  if (!confirm(`Delete "${deck.value.name}" and all ${cards.value.length} of its cards?`)) return
  return run(async () => {
    await api(`/decks/${deckId}`, { method: 'DELETE' })
    router.push('/')
  })
}

function nextReview(card) {
  if (card.due_date <= today) return 'Due now'
  const days = Math.round((new Date(card.due_date) - new Date(today)) / 86_400_000)
  return days === 1 ? 'Next review tomorrow' : `Next review in ${days} days`
}

onMounted(load)
</script>

<template>
  <RouterLink to="/" class="back">← All decks</RouterLink>

  <div v-if="notFound" class="empty">
    <p>Deck not found.</p>
  </div>

  <div v-else-if="deck">
    <!-- Deck header -->
    <form v-if="editingDeck" class="panel stack" @submit.prevent="saveDeck">
      <input v-model="deckForm.name" required maxlength="100" placeholder="Deck name" />
      <input v-model="deckForm.description" maxlength="500" placeholder="Description" />
      <div class="row">
        <button class="btn btn-primary">Save</button>
        <button type="button" class="btn btn-ghost" @click="editingDeck = false">Cancel</button>
      </div>
    </form>
    <div v-else class="deck-header">
      <div>
        <h1>{{ deck.name }}</h1>
        <p v-if="deck.description" class="muted">{{ deck.description }}</p>
      </div>
      <div class="row">
        <RouterLink v-if="dueCount" :to="`/decks/${deckId}/study`" class="btn btn-primary">
          Study {{ dueCount }} due
        </RouterLink>
        <button class="btn btn-ghost" @click="startEditDeck">Edit</button>
        <button class="btn btn-danger" @click="deleteDeck">Delete</button>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <!-- Add card -->
    <form class="panel add-card" @submit.prevent="addCard">
      <textarea
        v-model="newFront"
        required
        maxlength="1000"
        rows="2"
        placeholder="Front (question)"
      />
      <textarea v-model="newBack" required maxlength="1000" rows="2" placeholder="Back (answer)" />
      <button class="btn btn-primary">Add card</button>
    </form>

    <!-- Card list -->
    <h2>Cards ({{ cards.length }})</h2>
    <p v-if="cards.length === 0" class="empty">No cards yet. Add your first one above.</p>
    <ul class="card-list">
      <li v-for="card in cards" :key="card.id" class="panel">
        <form v-if="editingCardId === card.id" class="stack" @submit.prevent="saveCard(card)">
          <textarea v-model="cardForm.front" required maxlength="1000" rows="2" />
          <textarea v-model="cardForm.back" required maxlength="1000" rows="2" />
          <div class="row">
            <button class="btn btn-primary btn-small">Save</button>
            <button type="button" class="btn btn-ghost btn-small" @click="editingCardId = null">
              Cancel
            </button>
          </div>
        </form>
        <div v-else class="card-row">
          <div class="card-text">
            <strong>{{ card.front }}</strong>
            <span>{{ card.back }}</span>
            <small class="muted">{{ nextReview(card) }}</small>
          </div>
          <div class="row">
            <button class="btn btn-ghost btn-small" @click="startEditCard(card)">Edit</button>
            <button class="btn btn-ghost btn-small danger-text" @click="deleteCard(card)">
              Delete
            </button>
          </div>
        </div>
      </li>
    </ul>
  </div>

  <p v-else-if="error" class="error">{{ error }}</p>
  <p v-else class="muted">Loading…</p>
</template>

<style scoped>
.deck-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.add-card {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 0.5rem;
  align-items: start;
  margin-bottom: 1.5rem;
}
@media (max-width: 640px) {
  .add-card {
    grid-template-columns: 1fr;
  }
}
.card-list {
  list-style: none;
  padding: 0;
  display: grid;
  gap: 0.6rem;
}
.card-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}
.card-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
</style>
