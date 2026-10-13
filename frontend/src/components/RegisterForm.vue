
<script setup>
import { ref } from 'vue'
import api from '../services/api'

const emit = defineEmits(['switch-login'])

const username = ref('')
const password = ref('')
const confirmPassword = ref('')

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

async function handleRegister() {
  errorMessage.value = ''
  successMessage.value = ''

  if (!/^[A-Za-z0-9_]{3,50}$/.test(username.value)) {
    errorMessage.value = '用户名需要3～50位，只能包含字母、数字和下划线'
    return
  }

  if (password.value.length < 8) {
    errorMessage.value = '密码至少需要8个字符'
    return
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }

  loading.value = true

  try {
    await api.post('/auth/register', {
      username: username.value,
      password: password.value
    })

    successMessage.value = '注册成功！请返回登录页面'
    password.value = ''
    confirmPassword.value = ''

  } catch (error) {
    if (error.response?.status === 409) {
      errorMessage.value = '用户名已存在，请更换用户名'
    } else {
      errorMessage.value =
        typeof error.response?.data?.detail === 'string'
          ? error.response.data.detail
          : '注册失败，请检查输入或稍后重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <form class="register-card" @submit.prevent="handleRegister">

      <h1>📚 PaperMind</h1>
      <p class="subtitle">创建你的科研文献库</p>

      <h2>注册账户</h2>

      <input
        v-model.trim="username"
        placeholder="用户名（3～50位）"
        autocomplete="username"
        maxlength="50"
      />

      <input
        v-model="password"
        type="password"
        placeholder="密码（至少8位）"
        autocomplete="new-password"
      />

      <input
        v-model="confirmPassword"
        type="password"
        placeholder="确认密码"
        autocomplete="new-password"
      />

      <p v-if="errorMessage" class="error">
        {{ errorMessage }}
      </p>

      <p v-if="successMessage" class="success">
        {{ successMessage }}
      </p>

      <button type="submit" :disabled="loading">
        {{ loading ? '注册中...' : '创建账户' }}
      </button>

      <p class="switch-text">
        已经有账户？
        <a href="#" @click.prevent="emit('switch-login')">
          返回登录
        </a>
      </p>

    </form>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f7;
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 390px;
  background: white;
  border-radius: 16px;
  padding: 36px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

h1 {
  margin: 0;
  text-align: center;
}

h2 {
  font-size: 20px;
  margin: 10px 0 0;
}

.subtitle {
  font-size: 13px;
  text-align: center;
  color: #888;
  margin: 0 0 12px;
}

input {
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 13px;
  font-size: 14px;
}

button {
  background: #333;
  color: white;
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

.success {
  color: #15803d;
  font-size: 13px;
}

.switch-text {
  text-align: center;
  color: #777;
  font-size: 13px;
}

.switch-text a {
  color: #333;
  font-weight: 600;
}
</style>
