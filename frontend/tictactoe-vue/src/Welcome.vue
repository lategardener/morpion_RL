<script setup>
import {ref} from "vue";

const boardContainer_ = ref('boardContainer')

</script>

<template>
  <div :class="boardContainer_" class="welcome">
    <h2>WELCOME TO TICTACTOE GAME</h2>
    <button class="glass" :style="{margin: '30px', fontSize: '50px', width: '500px'}"
            @click="$emit('board-choice', 'BoardChoice')"> START </button>
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

.welcome {
  text-shadow: 0 0 1px #FFF, 0 0 5px #FFF, 0 0 15px #FFF, 0 0 5px #14a3a3, 0 0 30px #14a3a3, 0 0 40px #14a3a3, 0 0 55px #14a3a3, 0 0 75px #14a3a3;
  color: #FFFFFF;
  font-size: 30px;
}
</style>
