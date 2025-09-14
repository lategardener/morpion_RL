<script setup>
import {onMounted, ref} from 'vue'
import axios from "axios"
const opponents = ref({})
async function GetOpponent(){
  try{

    opponents.value = await axios.get("http://127.0.0.1:8000/game/opponents")
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
  <h3>{{opponents}}</h3>
</template>

<style scoped>

</style>
