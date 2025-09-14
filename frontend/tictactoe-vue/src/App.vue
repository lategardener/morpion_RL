<script setup>
import { ref } from 'vue'
import Welcome from './Welcome.vue'
import BoardChoice from './BoardChoice.vue'
import Opponent from "@/Opponent.vue";
const page = ref("Welcome")

</script>

<template>
  <Welcome v-if="page === 'Welcome'" @board-choice="(BoardChoicePage) => page = BoardChoicePage" />
  <BoardChoice v-else-if="page === 'BoardChoice'" @opponents="(OpponentPage) => page = OpponentPage" />
  <Opponent v-else-if="page === 'Opponent'" />
  <h1>{{page}}</h1>
</template>

<style scoped></style>
