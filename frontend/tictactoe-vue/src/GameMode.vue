<script setup>
import { ref } from 'vue'
import axios from "axios"
const response = ref("")
async function InitGaMeMode(gameMode){
  try{
    const configs = {
      mode: gameMode
    }

    response.value = await axios.post("http://127.0.0.1:8000/game/initGameMode", configs)
  }
  catch (error){
    response.value = error
  }
}
</script>

<template>
  <button @click="InitGaMeMode('IA Vs IA')">IA Vs IA</button>
  <button @click="InitGaMeMode('IA Vs Human')">IA Vs Human</button>
  <button @click="InitGaMeMode('Human Vs Human')">Human Vs Human</button>
  <h3>{{response}}</h3>
</template>

<style scoped>

</style>
