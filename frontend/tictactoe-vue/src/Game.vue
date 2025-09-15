<script setup>
import {onMounted, ref} from 'vue'
import axios from "axios"
const board = ref([])
const playOrder = 0
const currentPlayer = ref(0)
async function GetBoardInfo(){
  try{

    const response = await axios.get("http://127.0.0.1:8000/game/observation")
    board.value = response.data.observation
    currentPlayer.value = response.data.current_player

  }
  catch (error){
    board.value = error
  }
}

onMounted(() => {
  GetBoardInfo()
})
</script>

<template>
    <div v-for="(row, rowIndex) in board" :key="rowIndex">
      <span v-for="(col, colIndex) in row" :key="colIndex">
        <button v-if="Number(col) === 3"></button>
        <button v-else-if="Number(col) === 0">X</button>
        <button v-else>O</button>
      </span>
    </div>

</template>

<style scoped>

</style>
