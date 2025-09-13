<script setup>
import { ref } from 'vue'
import Welcome from './Welcome.vue'
import BoardChoice from './BoardChoice.vue'
const page = ref("Welcome")

</script>

<template>
  <Welcome v-if="page === 'Welcome'" @change-page="(newPage) => page = newPage" />
  <BoardChoice v-else-if="page === 'BoardChoice'" />
</template>

<style scoped></style>
