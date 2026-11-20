<script setup>
import { ref, onMounted } from 'vue'

const API = 'http://127.0.0.1:8001'

const decks = ref([])              
const newName = ref('')
const newDescription = ref('')

async function loadDecks() {
  const res = await fetch(`${API}/decks`)  
  decks.value = await res.json()          
}
async function createDeck(){
  await fetch(`${API}/decks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: newName.value, description: newDescription.value }),
  })
  newName.value = ''
  newDescription.value = ''
  loadDecks()
}

onMounted(loadDecks)                     
</script>

<template>
  <h1>My Decks</h1>
  <p v-if="decks.length === 0">No decks yet.</p>
  <form @submit.prevent="createDeck">
    <input v-model="newName" placeholder="Deck name" required />
    <input v-model="newDescription" placeholder="Deck description" />
    <button>Add deck</button> 
  </form>
  <ul>
    <li v-for="deck in decks" :key="deck.id">
      <RouterLink :to="`/decks/${deck.id}`">{{ deck.name }}</RouterLink>
      <span v-if="deck.description"> — {{ deck.description }}</span>
    </li>
  </ul>
</template>