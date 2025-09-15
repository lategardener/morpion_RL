<script setup>
import {onMounted, ref} from 'vue'
import axios from "axios"
const board = ref([])
const playOrder = 0
const isDone = ref(false)
const board_size = ref(0)
const cell_ = ref('cell')
const globalDiv_ = ref('globalDiv')
const boardContainer_ = ref('boardContainer')
const currentPlayer = ref(0)
async function GetBoardInfo(){
  try{

    const response = await axios.get("http://127.0.0.1:8000/game/observation")
    board.value = response.data.observation
    currentPlayer.value = response.data.current_player
    isDone.value = response.data.is_done
    board_size.value = response.data.board_size


  }
  catch (error){
    board.value = error
  }
}

async function play(action){


}

onMounted(() => {
  GetBoardInfo()
})
</script>

<template>
<div :class="boardContainer_">
  <div v-for="(row, rowIndex) in board" :key="rowIndex">
    <span v-for="(col, colIndex) in row" :key="colIndex">
      <button v-if="Number(col) === 3" :class="cell_" @click:="play(board_size * row + col)">{{ col === 3 ? '' : col === 0 ? 'X' : 'O' }}</button>
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
