<script setup>
import { ref } from 'vue'
import axios from "axios"
const response = ref("")
async function InitEnv(board_length, pattern_victory_length){
  try{
    const configs = {
      board_length: board_length,
      pattern_victory_length: pattern_victory_length
    }

    response.value = await axios.post("http://127.0.0.1:8000/game/initEnv", configs)
  }
  catch (error){
    response.value = error
  }
}
</script>

<template>
  <button @click="InitEnv(3, 3)">3x3</button>
  <button @click="InitEnv(6, 6)">4x4</button>
  <button @click="InitEnv(9, 9)">5x5</button>
  <h3>{{response}}</h3>
</template>

<style scoped>

</style>
