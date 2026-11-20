<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const decks = ref([])
const loading = ref(true)
const error = ref('')
const newName = ref('')
const newDescription = ref('')

async function loadDecks() {
  try {
    decks.value = await api('/decks')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function createDeck() {
  error.value = ''
  try {
    await api('/decks', {
      method: 'POST',
      body: { name: newName.value, description: newDescription.value },
    })
    newName.value = ''
    newDescription.value = ''
    await loadDecks()
  } catch (err) {
    error.value = err.message
  }
}

onMounted(loadDecks)
</script>

<template>
  <h1>My Decks</h1>

  <form class="panel new-deck" @submit.prevent="createDeck">
    <input v-model="newName" placeholder="Deck name" required maxlength="100" />
    <input v-model="newDescription" placeholder="Description (optional)" maxlength="500" />
    <button class="btn btn-primary">Add deck</button>
  </form>

  <p v-if="error" class="error">{{ error }}</p>
  <p v-if="loading" class="muted">Loading…</p>
  <p v-else-if="decks.length === 0" class="empty">No decks yet. Create your first one above.</p>

  <ul class="deck-grid">
    <li v-for="deck in decks" :key="deck.id" class="panel deck">
      <RouterLink :to="`/decks/${deck.id}`" class="deck-name">{{ deck.name }}</RouterLink>
      <p v-if="deck.description" class="muted">{{ deck.description }}</p>
      <div class="deck-footer">
        <span class="muted">
          {{ deck.card_count }} {{ deck.card_count === 1 ? 'card' : 'cards' }}
          <span v-if="deck.due_count" class="badge">{{ deck.due_count }} due</span>
        </span>
        <RouterLink
          v-if="deck.due_count"
          :to="`/decks/${deck.id}/study`"
          class="btn btn-primary btn-small"
        >
          Study
        </RouterLink>
      </div>
    </li>
  </ul>
</template>

<style scoped>
.new-deck {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1rem 0 1.5rem;
}
.new-deck input {
  flex: 1 1 180px;
}
.deck-grid {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}
.deck {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.deck-name {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text);
  text-decoration: none;
}
.deck-name:hover {
  color: var(--accent);
}
.deck-footer {
  margin-top: auto;
  padding-top: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}
</style>
