<script setup>
import {onMounted, ref} from 'vue'
import axios from "axios"
const opponents = ref([])
const emit = defineEmits(['game'])
async function GetOpponents(){
  try{

    const response = await axios.get("http://127.0.0.1:8000/game/opponents")
    opponents.value = response.data

  }
  catch (error){
    opponents.value = error
  }

}

async function SaveAgent(agent_configs){
  try{

    const agentConfig = {
      agent: agent_configs,
    }

    const response = await axios.post("http://127.0.0.1:8000/game/saveAgent", agentConfig)

  }
  catch (error){
    console.log(error)
  }

  emit('game', 'Game', agent_configs.name)
}

onMounted(() => {
  GetOpponents()
})

</script>

<template>
  <button v-for="opponent in opponents" :key="opponent.name" @click="SaveAgent(opponent)">
    {{ opponent.name }}
  </button>
</template>

<style scoped>

</style>
