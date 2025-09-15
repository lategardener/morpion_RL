<script setup>
import {onMounted, ref, watch} from 'vue'
import axios from "axios"
const board = ref([])
const playOrder = ref(0)
const isDone = ref(0)
const board_size = ref(0)
const cell_ = ref('cell')
const globalDiv_ = ref('globalDiv')
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

async function play(move){
  console.log(currentPlayer.value !== playOrder.value)
  console.log(!isDone.value && currentPlayer.value === playOrder.value)
  if (!isDone.value && currentPlayer.value === playOrder.value){
    console.log("In...")
    console.log("move", move)
    try{
      const action = {
        action: move,
      }
      const response = await axios.post("http://127.0.0.1:8000/game/actionPlayed", action)
      console.log(response)
    }
    catch (error){
      console.log(error)
    }

    await GetBoardInfo()
  }
}

watch(currentPlayer, (newCurrentPlayer) => {
  if (currentPlayer.value !== playOrder.value){
    //pass
  }
})


onMounted(() => {
  GetBoardInfo()
})
</script>

<template>
<div :class="boardContainer_">
  <div v-for="(row, rowIndex) in board" :key="rowIndex">
    <span v-for="(col, colIndex) in row" :key="colIndex">
      <button :class="cell_" @click="play(board_size * rowIndex + colIndex)">
        {{ col === 3 ? '' : col === 0 ? 'X' : 'O' }}
      </button>
    </span>
  </div>
</div>
</template>

<style scoped>
.cell {
  width: 50px;
  height: 50px;
  color: green;
  font-weight: bold;
}


.boardContainer{
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  flex-direction: column;
}
</style>
