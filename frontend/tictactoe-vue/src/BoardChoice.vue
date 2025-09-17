<script setup>
import { ref } from 'vue'
import axios from "axios"
const response = ref("")
const emit = defineEmits(['opponents'])
const boardContainer_ = ref('boardContainer')

async function InitEnv(board_length, pattern_victory_length){
  try{
    const configs = {
      board_length: board_length,
      pattern_victory_length: pattern_victory_length
    }

    response.value = await axios.post("http://127.0.0.1:8000/game/initEnv", configs)
    emit('opponents', 'Opponent')
  }
  catch (error){
    response.value = error
  }
}
</script>

<template>
  <div :class="boardContainer_">
    <h2 class="title">BOARD SIZE CHOICE</h2>
    <button class="glass" :style="{padding: '10px', margin: '30px', fontSize: '50px', width: '500px'}"
            @click="InitEnv(3, 3)">3x3</button>
    <button class="glass" :style="{padding: '10px', margin: '30px', fontSize: '50px', width: '500px'}"
            @click="InitEnv(5, 4)">5x5</button>
    <button class="glass" :style="{padding: '10px', margin: '30px', fontSize: '50px', width: '500px'}"
            @click="InitEnv(9, 5)">9x9</button>
  </div>
</template>

<style scoped>
.boardContainer{
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  flex-direction: column;
  background: linear-gradient(to bottom, rgba(255,255,255,0.15) 0%, rgba(0,0,0,0.15) 100%), radial-gradient(at top center, rgba(255,255,255,0.40) 0%, rgba(0,0,0,0.40) 120%) #989898;
  background-blend-mode: multiply,multiply;
}

.glass {
  background: rgba(255, 255, 255, 0.38);
  border-radius: 16px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(13.2px);
  -webkit-backdrop-filter: blur(13.2px);
  padding: 20px 40px;
  font-size: 1.5rem;
  color: #097777;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* Hover → changement de background et texte blanc */
.glass:hover {
  background: #14a3a3;
  color: white;
}

/* Active → bouton s’enfonce */
.glass:active {
  transform: translateY(4px);
  box-shadow: 0 2px 15px rgba(0,0,0,0.2);
}

.title{
  text-shadow: 18px 17px 16px rgba(0,0,0,0.44);
  font-size: 30px;
}

</style>
