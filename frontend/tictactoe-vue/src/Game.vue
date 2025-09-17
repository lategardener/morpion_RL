<script setup>
import {computed, onMounted, ref, watch} from 'vue'
import axios from "axios"
const board = ref([])
const playOrder = ref(0)
const isDone = ref(0)
const board_size = ref(0)
const cell_ = ref('cell')
const agent_color_ = ref('agent_color')
const boardContainer_ = ref('boardContainer')
const currentPlayer = ref(0)
const actionMask = ref([])
const winner = ref(null)
const can_play = ref(true)

const buttonSize = computed(() => {
  if (board_size.value === 3) return 190
  if (board_size.value === 5) return 120
  if (board_size.value === 9) return 70
  return 50
})

const fontSize = computed(() => {
  if (board_size.value === 3) return 100
  if (board_size.value === 5) return 60
  if (board_size.value === 9) return 50
  return 25
})

async function GetBoardInfo(){
  try{

    const response = await axios.get("http://127.0.0.1:8000/game/observation")
    board.value = response.data.observation
    currentPlayer.value = response.data.current_player
    isDone.value = response.data.is_done
    board_size.value = response.data.board_size
    actionMask.value = response.data.action_mask
  }
  catch (error){
    board.value = error
  }
}

async function play(action){
  try{
    const actionConfig = {
      move: action,
    }
    const response = await axios.post("http://127.0.0.1:8000/game/actionPlayed", actionConfig)
  }
  catch (error){
    console.log(error)
  }
}

async function userPlayed(action){
  if (!isDone.value && currentPlayer.value === playOrder.value){
    await play(action)
    await GetBoardInfo()
  }
}

async function reset(newOrder){
  can_play.value = false
  await axios.post("http://127.0.0.1:8000/game/resetEnv")
  await GetBoardInfo()
  console.log("reset")
  if (newOrder !== null){
    playOrder.value = 1 - playOrder.value
  }
  if (playOrder.value !== currentPlayer.value){
    const response = await axios.get("http://127.0.0.1:8000/game/move")
    const action = response.data
    await play(action)
    await GetBoardInfo()
  }
  can_play.value = true
  winner.value = null
}


watch(currentPlayer, async (newCurrentPlayer) => {
  if (can_play.value === true && newCurrentPlayer !== playOrder.value && !isDone.value) {
    console.log("watch : ", newCurrentPlayer)

    const response = await axios.get("http://127.0.0.1:8000/game/move")
    const action = response.data
    await play(action)
    await GetBoardInfo()
  }
})

watch(isDone, (isDoneUpdate) => {
  console.log("Is done ?", isDoneUpdate)
  if (isDoneUpdate === 1){
    const onlyOnes = actionMask.value.every(v => v === 0);
    console.log("Is board full ?", onlyOnes)
    if (onlyOnes === true){
      winner.value = "Draw"
    }
    else if (playOrder.value === currentPlayer.value){
      winner.value = "Agent win"
    }
    else{
      winner.value = "You win"
    }

    console.log("Winner ?", winner.value)
  }
})

onMounted(() => {
  GetBoardInfo()
})

</script>

<template>
<div :class="boardContainer_">
  <div class="envActions">
    <button
      class="glass"
      :style="{
    padding: '10px',
    marginRight: '10px',
    fontSize: '20px',
    width: '150px',
    backgroundColor: playOrder === 0 ? '#1049af' : '#b80db5',
    color: 'white',
    fontWeight: 'bold'
  }"
      @click="reset(true)"
    >
      {{ playOrder === 0 ? '1st player' : '2nd player' }}
    </button>

    <button class="glass" :style="{padding: '10px', marginRight: '10px', fontSize: '20px', width: '150px'}" @click="reset(null)">
      Restart
    </button>
    <button @click="$emit('board-choice', 'BoardChoice')" class="glass" :style="{padding: '10px', marginLeft: '10px', fontSize: '20px'}">
      Change configs
    </button>
  </div>
  <div v-for="(row, rowIndex) in board" :key="rowIndex" class="row">
    <div v-for="(col, colIndex) in row" :key="colIndex">
      <button :class="[cell_, col === 1 ? agent_color_ : '']"
              @click="userPlayed(board_size * rowIndex + colIndex)"
              :style="{width: buttonSize + 'px', height: buttonSize + 'px', fontSize: fontSize + 'px'}">
        {{ col === 3 ? '' : col === 0 ? 'X' : 'O' }}
      </button>
    </div>
  </div>
  <p :style="{ visibility: winner ? 'visible' : 'hidden', height: '60px', padding: '10px' }">{{ winner }}</p>
</div>
</template>


<style scoped>

:global(body) {
  margin: 0;
  padding: 0;
}

.cell {
  font-weight: bold;
  color: #1049af;
  /* From https://css.glass */
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(7.9px);
  -webkit-backdrop-filter: blur(7.9px);
  border: 1px solid rgba(255, 255, 255, 0.26);

}

.agent_color{
  color : #b80db5;
}

.boardContainer{
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  flex-direction: column;
}

.row {
  display: flex;
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

.envActions{
  margin-bottom: 50px;
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
