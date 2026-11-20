import { createRouter, createWebHistory } from 'vue-router'
import DeckListView from '../views/DeckListView.vue'
import DeckView from '../views/DeckView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'decks', component: DeckListView },
    { path: '/decks/:id', name: 'deck', component: DeckView },
  ],
})

export default router