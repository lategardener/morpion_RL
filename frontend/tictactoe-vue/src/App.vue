<script setup>
import { ref } from 'vue'
import Welcome from './Welcome.vue'
import BoardChoice from './BoardChoice.vue'
import GameMode from "./GameMode.vue"

const page = ref("Welcome")

</script>

<template>
  <Welcome v-if="page === 'Welcome'" @board-choice="(BoardChoicePage) => page = BoardChoicePage" />
  <BoardChoice v-else-if="page === 'BoardChoice'" @game_mode="(GameModePage) => page = GameModePage" />
  <GameMode v-else-if="page === 'GameMode'"/>
</template>

<style scoped></style>
