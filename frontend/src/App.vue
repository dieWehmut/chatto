<template>
  <div id="app">
    <component :is="currentComponent"></component>
  </div>
</template>

<script>
import Login from './components/Login.vue'
import Chat from './components/Chat.vue'
import { ref, computed } from 'vue'
import { getUserInfo } from './utils/storage'

export default {
  components: {
    Login,
    Chat
  },
  setup() {
    const userInfo = ref(getUserInfo())
    const isLoggedIn = computed(() => !!userInfo.value)

    const currentComponent = computed(() => {
      return isLoggedIn.value ? 'Chat' : 'Login'
    })

    return {
      currentComponent,
      isLoggedIn
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
  overflow: hidden;
}

body {
  margin: 0;
  padding: 0;
}
</style>