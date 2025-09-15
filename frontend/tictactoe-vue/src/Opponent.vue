<script setup>
import {onMounted, ref} from 'vue'
import axios from "axios"
const opponents = ref([])
async function GetOpponent(){
  try{

    const response = await axios.get("http://127.0.0.1:8000/game/opponents")
    opponents.value = response.data

  }
  catch (error){
    opponents.value = error
  }
}

onMounted(() => {
  GetOpponent()
})

</script>

<template>
  <button v-for="opponent in opponents" :key="opponent.name" @click="$emit('game', 'Game', opponent.name)">
    {{ opponent.name }}
  </button>
</template>

<style scoped>

</style>
