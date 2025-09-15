<script setup>
import { ref } from 'vue'
import Welcome from './Welcome.vue'
import BoardChoice from './BoardChoice.vue'
import Opponent from "@/Opponent.vue"
import Game from "@/Game.vue";
const page = ref("Welcome")
const opponent = ref("")

</script>

<template>
  <Welcome v-if="page === 'Welcome'" @board-choice="(BoardChoicePage) => page = BoardChoicePage" />
  <BoardChoice v-else-if="page === 'BoardChoice'" @opponents="(OpponentPage) => page = OpponentPage" />
  <Opponent v-else-if="page === 'Opponent'" @game="(GamePage, opponentName) => {page = GamePage
  opponent = opponentName}" />
  <Game v-else-if="page === 'Game'"/>
  <h1>{{page}}</h1>
  <h1>{{opponent}}</h1>
</template>

<style scoped></style>
