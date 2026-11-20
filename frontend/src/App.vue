<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <RouterLink to="/">Flashcards</RouterLink>
  </header>
  <main>
    <RouterView />
  </main>
</template>