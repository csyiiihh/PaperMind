
<script setup>
import { ref } from 'vue'
import api from '../services/api'

const emit = defineEmits([
  'login-success',
  'switch-register'
])

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  if (!username.value || !password.value) {
    errorMessage.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const response = await api.post('/auth/login', {
      username: username.value,
      password: password.value
    })

    const token = response.data.access_token

    sessionStorage.setItem('access_token', token)

    emit('login-success')
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail || '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <form class="login-card" @submit.prevent="handleLogin">
      <h1>📚 PaperMind</h1>
      <p class="subtitle">AI 科研文献智能助手</p>

      <h2>欢迎登录</h2>

      <input
        v-model="username"
        type="text"
        placeholder="用户名"
        autocomplete="username"
      />

      <input
        v-model="password"
        type="password"
        placeholder="密码"
        autocomplete="current-password"
      />

      <p v-if="errorMessage" class="error">
        {{ errorMessage }}
      </p>

      <button type="submit" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>

    <p class="switch-text">
        还没有账户？
        <a href="#" @click.prevent="emit('switch-register')">
            立即注册
        </a>
    </p>

    </form>
  </div>
</template>

<style scoped>
.login-page {
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f7;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: #fff;
  padding: 36px;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 15px;
}

h1 {
  text-align: center;
  margin: 0;
}

h2 {
  font-size: 20px;
  margin: 12px 0 0;
}

.subtitle {
  text-align: center;
  color: #888;
  margin: 0 0 15px;
  font-size: 13px;
}

input {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 13px;
  font-size: 14px;
}

button {
  background: #333;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 13px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
}

.error {
  color: #dc2626;
  font-size: 13px;
}

.switch-text {
  text-align: center;
  font-size: 13px;
  color: #777;
}

.switch-text a {
  color: #333;
  font-weight: 600;
}
</style>
