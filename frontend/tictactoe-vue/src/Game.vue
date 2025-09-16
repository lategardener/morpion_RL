<script setup>
import {onMounted, ref, watch} from 'vue'
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

async function GetBoardInfo(){
  try{

    const response = await axios.get("http://127.0.0.1:8000/game/observation")
    console.log("response :", response.data)
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
  console.log(typeof move)
  try{
    const actionConfig = {
      move: action,
    }
    const response = await axios.post("http://127.0.0.1:8000/game/actionPlayed", actionConfig)
    console.log("Play response", response)
  }
  catch (error){
    console.log(error)
  }
}

async function userPlayed(action){
  console.log(currentPlayer.value !== playOrder.value)
  console.log(!isDone.value && currentPlayer.value === playOrder.value)
  if (!isDone.value && currentPlayer.value === playOrder.value){
    console.log("In...")
    console.log("action", action)
    await play(action)
    await GetBoardInfo()
  }
}

watch(currentPlayer, async (newCurrentPlayer) => {
  console.log(newCurrentPlayer)
  console.log(playOrder.value)
  if (newCurrentPlayer !== playOrder.value) {
    console.log("here")
    const response = await axios.get("http://127.0.0.1:8000/game/move")
    console.log(response)
    const action = response.data
    await play(action)
    await GetBoardInfo()
  }
})


onMounted(() => {
  GetBoardInfo()
})
</script>

<template>
<div :class="boardContainer_">
  <div class="envActions">
    <button :style="{padding: '10px', marginRight: '10px', fontSize: '20px', width: '150px'}">Restart</button>
    <button :style="{padding: '10px', marginLeft: '10px', fontSize: '20px'}">Change configs</button>
  </div>
  <div v-for="(row, rowIndex) in board" :key="rowIndex" class="row">
    <div v-for="(col, colIndex) in row" :key="colIndex">
      <button :class="[cell_, col === 1 ? agent_color_ : '']" @click="userPlayed(board_size * rowIndex + colIndex)">
        {{ col === 3 ? '' : col === 0 ? 'X' : 'O' }}
      </button>
    </div>
  </div>

</div>
</template>

<style scoped>
.cell {
  width: 100px;
  height: 100px;
  font-weight: bold;
  font-size: 50px;
  color:cornflowerblue;
  /* From https://css.glass */
  background: rgba(255, 255, 255, 0.52);
  border-radius: 16px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(9px);
  -webkit-backdrop-filter: blur(9px);
  border: 1px solid rgba(255, 255, 255, 0.23);
}

.agent_color{
  color : mediumvioletred;
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
}

.envActions{
  margin-bottom: 50px;
}
</style>
