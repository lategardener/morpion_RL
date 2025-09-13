<script setup>
import { ref } from 'vue'
import Welcome from './Welcome.vue'

const page = ref("Welcome")
</script>

<template>
  <Welcome v-if="page === 'Welcome'"></Welcome>
</template>

<style scoped></style>
