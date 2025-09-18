<script setup>
import {onMounted, ref} from 'vue'
import axios from "axios"
const opponents = ref([])
const emit = defineEmits(['game'])
const selectedOpponent = ref(null)
const boardContainer_ = ref('boardContainer')

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
  <div :class="boardContainer_">
    <select
      v-model="selectedOpponent"
      @change="SaveAgent(selectedOpponent)"
      size="5"
      class="custom-select"
    >
      <option
        v-for="opponent in opponents"
        :key="opponent.name"
        :value="opponent"
        class="custom-option glass"
        :style="{margin: '15px', padding:'10px'}"


      >
        {{ opponent.name }}
      </option>
    </select>
  </div>
</template>


<style scoped>
.custom-select {
  border: none;
  outline: none;
  background: none;
  font-size: 30px;
  width: 500px;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  text-align: center;
}

.custom-option {
  background: rgba(255,255,255,0.2);
  margin: 4px 0;
  cursor: pointer;
}

.custom-option:hover {
  background: rgba(0, 150, 255, 0.4);
}

.boardContainer{
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  flex-direction: column;
  background: linear-gradient(to bottom, rgba(255,255,255,0.15) 0%, rgba(0,0,0,0.15) 100%), radial-gradient(at top center, rgba(255,255,255,0.40) 0%, rgba(0,0,0,0.40) 120%) #989898;
  background-blend-mode: multiply,multiply;
}

.glass{
  /* From https://css.glass */
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(7.9px);
  -webkit-backdrop-filter: blur(7.9px);
  border: 1px solid rgba(255, 255, 255, 0.26);
}

</style>
