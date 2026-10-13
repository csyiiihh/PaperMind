
<script setup>
import {
  ref,
  watch,
  onMounted,
  onUnmounted
} from 'vue'
import { getApiErrorMessage } from './utils/apiError'

import LoginForm from './components/LoginForm.vue'
import RegisterForm from './components/RegisterForm.vue'
import api from './services/api'

import PaperSidebar from './components/PaperSidebar.vue'
import ChatPanel from './components/ChatPanel.vue'

// ============================================
// 1. 登录与认证状态
// ============================================

const authPage = ref('login')

const currentUser = ref(null)
const checkingAuth = ref(true)

// 登录会话版本号：防止旧请求污染新账户的数据
let authVersion = 0

// 记录最新的论文列表和消息请求
let latestPaperRequest = 0
let latestMessageRequest = 0

let paperListController = null
let messageController = null

// ============================================
// 2. 论文状态
// ============================================

const currentPaper = ref(null)
const papers = ref([])

const uploading = ref(false)
const uploadError = ref('')

const loadingPapers = ref(false)
const paperListError = ref('')

const deletingPaperId = ref(null)

// const fileInput = ref(null)


// ============================================
// 3. 聊天状态
// ============================================

const question = ref('')
const messages = ref([])

const asking = ref(false)
const askError = ref('')

const loadingMessages = ref(false)
const messageError = ref('')

// const messageContainer = ref(null)


// ============================================
// 4. Markdown 渲染
// ============================================

// marked.setOptions({
//   gfm: true,
//   breaks: true
// })

// function renderMarkdown(content) {
//   const html = marked.parse(content || '')

//   return DOMPurify.sanitize(html)
// }


// ============================================
// 5. 页面滚动
// ============================================

const chatPanelRef = ref(null)

async function scrollToBottom() {
  await chatPanelRef.value?.scrollToBottom()
}

// async function scrollToBottom() {
//   await nextTick()

//   if (messageContainer.value) {
//     messageContainer.value.scrollTop =
//       messageContainer.value.scrollHeight
//   }
// }


// ============================================
// 6. 清除当前账户的数据
// ============================================

function clearUserData() {
  paperListController?.abort()
  messageController?.abort()

  paperListController = null
  messageController = null

  // 使正在执行的旧请求失效
  authVersion++
  latestPaperRequest++
  latestMessageRequest++

  currentPaper.value = null
  papers.value = []
  messages.value = []
  question.value = ''

  uploading.value = false
  loadingPapers.value = false
  loadingMessages.value = false
  asking.value = false
  deletingPaperId.value = null

  uploadError.value = ''
  paperListError.value = ''
  messageError.value = ''
  askError.value = ''
}


// ============================================
// 7. 验证登录状态
// ============================================

async function checkLogin() {
  const requestVersion = authVersion

  checkingAuth.value = true

  try {
    const response = await api.get('/auth/me')

    // 如果期间已经退出或切换账户，则忽略结果
    if (requestVersion !== authVersion) return

    currentUser.value = response.data

  } catch (error) {
    if (requestVersion !== authVersion) return

    // 清理无效登录状态
    sessionStorage.removeItem('access_token')
    currentUser.value = null

  } finally {
    if (requestVersion === authVersion) {
      checkingAuth.value = false
    }
  }
}


// ============================================
// 8. 登录成功
// ============================================

async function handleLoginSuccess() {
  // 新登录账户开始一个新会话
  clearUserData()

  currentUser.value = null
  authPage.value = 'login'

  await checkLogin()
}


// ============================================
// 9. 退出登录
// ============================================

function logout() {
  sessionStorage.removeItem('access_token')

  clearUserData()

  currentUser.value = null
  checkingAuth.value = false
  authPage.value = 'login'
}


// ============================================
// 10. Token 失效事件
// ============================================

function handleUnauthorized() {
  logout()
}


// ============================================
// 11. 加载论文列表
// ============================================

async function loadPapers() {
  if (!currentUser.value) return

  paperListController?.abort()

  const controller = new AbortController()
  paperListController = controller

  const requestId = ++latestPaperRequest
  const requestVersion = authVersion

  loadingPapers.value = true
  paperListError.value = ''

  try {
    const response = await api.get('/papers', {
      signal: controller.signal
    })

    // 防止旧账户或旧请求覆盖页面
    if (
      requestId !== latestPaperRequest ||
      requestVersion !== authVersion ||
      !currentUser.value
    ) {
      return
    }

    papers.value = response.data.papers.map(paper => ({
      id: paper.id,
      name: paper.filename,
      createdAt: paper.created_at
    }))

    // 如果当前论文已不存在，则重新选择
    const selectedPaper = papers.value.find(
      paper => paper.id === currentPaper.value?.id
    )

    if (selectedPaper) {
      currentPaper.value = selectedPaper
    } else {
      currentPaper.value = papers.value[0] || null
    }

  } catch (error) {

    if (error.code === 'ERR_CANCELED') {
      return
    }

    if (
      requestId !== latestPaperRequest ||
      requestVersion !== authVersion
    ) {
      return
    }

    console.error('加载论文列表失败：', error)

    paperListError.value = getApiErrorMessage(
      error,
      '加载论文列表失败'
    )

  } finally {
    if (
      requestId === latestPaperRequest &&
      requestVersion === authVersion
    ) {
      loadingPapers.value = false
    }
  }
}


// ============================================
// 12. 加载当前论文的历史聊天记录
// ============================================

async function loadMessages(paperId) {
  messageController?.abort()

  const requestId = ++latestMessageRequest
  const requestVersion = authVersion

  messages.value = []
  messageError.value = ''

  if (!paperId || !currentUser.value) {
    loadingMessages.value = false
    return
  }

  const controller = new AbortController()
  messageController = controller

  loadingMessages.value = true

  try {
    const response = await api.get(
      `/papers/${paperId}/messages`,
      {
        signal: controller.signal
      }
    )

    if (
      requestId !== latestMessageRequest ||
      requestVersion !== authVersion ||
      currentPaper.value?.id !== paperId ||
      !currentUser.value
    ) {
      return
    }

    messages.value = response.data.messages.map(message => ({
      id: message.id,
      role: message.role,
      content: message.content,
      sources: message.sources || []
    }))

    await scrollToBottom()

  } catch (error) {
    if (error.code === 'ERR_CANCELED') {
      return
    }

    if (
      requestId !== latestMessageRequest ||
      requestVersion !== authVersion
    ) {
      return
    }

    console.error('加载聊天记录失败：', error)

    messageError.value = getApiErrorMessage(
      error,
      '加载聊天记录失败'
    )

  } finally {
    if (
      requestId === latestMessageRequest &&
      requestVersion === authVersion
    ) {
      loadingMessages.value = false
    }
  }
}


// ============================================
// 13. 选择论文后自动加载聊天记录
// ============================================

watch(
  () => currentPaper.value?.id,
  paperId => {
    loadMessages(paperId)
  }
)


// ============================================
// 14. 切换账户后重新加载文献库
// ============================================

watch(
  () => currentUser.value?.id,
  async userId => {
    if (!userId) return

    currentPaper.value = null
    papers.value = []
    messages.value = []

    await loadPapers()
  }
)


// ============================================
// 15. 选择 PDF 文件
// ============================================

// function selectFile() {
//   if (uploading.value || asking.value) return

//   fileInput.value?.click()
// }


// ============================================
// 16. 上传 PDF
// ============================================

async function handleFileChange(event) {
  const file = event.target.files?.[0]

  if (!file) return

  if (
    !currentUser.value ||
    uploading.value ||
    asking.value
  ) {
    event.target.value = ''
    return
  }

  if (!file.name.toLowerCase().endsWith('.pdf')) {
    uploadError.value = getApiErrorMessage(
      error,
      'PDF 上传失败'
    )
    event.target.value = ''
    return
  }

  const requestVersion = authVersion
  const userId = currentUser.value.id

  uploading.value = true
  uploadError.value = ''

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post(
      '/papers/upload',
      formData
    )

    // 若用户已退出或切换账户，不更新旧结果
    if (
      requestVersion !== authVersion ||
      currentUser.value?.id !== userId
    ) {
      return
    }

    const paper = {
      id: response.data.paper_id,
      name: file.name
    }

    if (!paper.id) {
      throw new Error('后端没有返回 paper_id')
    }

    // 重新从数据库读取列表，确保前后端一致
    await loadPapers()

    if (
      requestVersion === authVersion &&
      currentUser.value?.id === userId
    ) {
      currentPaper.value = papers.value.find(
        item => item.id === paper.id
      ) || paper

      console.log('上传成功：', response.data)
    }

  } catch (error) {
    if (requestVersion !== authVersion) return

    console.error('上传失败：', error)

    uploadError.value =
      typeof error.response?.data?.detail === 'string'
        ? error.response.data.detail
        : error.message || '上传失败，请检查后端服务'

  } finally {
    if (requestVersion === authVersion) {
      uploading.value = false
    }

    event.target.value = ''
  }
}


// ============================================
// 17. 删除论文
// ============================================

async function deletePaper(paper) {
  if (
    !currentUser.value ||
    asking.value ||
    uploading.value ||
    deletingPaperId.value !== null
  ) {
    return
  }

  const confirmed = window.confirm(
    `确定要删除论文《${paper.name}》吗？\n删除后无法恢复。`
  )

  if (!confirmed) return

  const requestVersion = authVersion
  const userId = currentUser.value.id

  deletingPaperId.value = paper.id

  try {
    const response = await api.delete(
      `/papers/${paper.id}`
    )

    if (
      requestVersion !== authVersion ||
      currentUser.value?.id !== userId
    ) {
      return
    }

    const failedFiles = response.data.failed_files || []

    if (failedFiles.length > 0) {
      alert(
        `数据库记录已删除，但有 ${failedFiles.length} 个文件清理失败，请检查后端日志。`
      )
    }

    if (currentPaper.value?.id === paper.id) {
      currentPaper.value = null
      messages.value = []
      question.value = ''
    }

    await loadPapers()

  } catch (error) {
    if (requestVersion !== authVersion) return

    console.error('删除论文失败：', error)

    alert(
      getApiErrorMessage(error, '删除论文失败')
    )

  } finally {
    if (requestVersion === authVersion) {
      deletingPaperId.value = null
    }
  }
}


// ============================================
// 18. 发送 AI 问题
// ============================================

async function sendQuestion() {
  const text = question.value.trim()

  if (!text || asking.value) return

  if (!currentUser.value || !currentPaper.value) {
    askError.value = '请先登录并选择一篇论文'
    return
  }

  const paperId = currentPaper.value.id
  const userId = currentUser.value.id
  const requestVersion = authVersion

  asking.value = true
  askError.value = ''

  // 先显示用户问题
  messages.value.push({
    role: 'user',
    content: text
  })

  question.value = ''

  await scrollToBottom()

  try {
    const response = await api.post(
      `/papers/${paperId}/ask`,
      {
        question: text
      }
    )

    if (
      requestVersion !== authVersion ||
      currentUser.value?.id !== userId ||
      currentPaper.value?.id !== paperId
    ) {
      return
    }

    messages.value.push({
      role: 'assistant',
      content: response.data.answer,
      sources: response.data.sources || []
    })

    await scrollToBottom()

    console.log('AI 问答成功：', response.data)

  } catch (error) {
    if (
      requestVersion !== authVersion ||
      currentUser.value?.id !== userId ||
      currentPaper.value?.id !== paperId
    ) {
      return
    }

    console.error('AI 问答失败：', error)

    askError.value = getApiErrorMessage(
      error,
      'AI 问答失败，请稍后重试'
    )

    // 移除未成功保存的用户消息
    const lastMessage = messages.value.at(-1)

    if (
      lastMessage?.role === 'user' &&
      lastMessage.content === text
    ) {
      messages.value.pop()
    }

    // 允许用户修改并重新发送
    question.value = text

  } finally {
    if (requestVersion === authVersion) {
      asking.value = false
    }
  }
}


// ============================================
// 19. 组件生命周期
// ============================================

onMounted(() => {
  window.addEventListener(
    'papermind:unauthorized',
    handleUnauthorized
  )

  checkLogin()
})

onUnmounted(() => {
  window.removeEventListener(
    'papermind:unauthorized',
    handleUnauthorized
  )
})

</script>


<template>
  <div class="app-root">

    <!-- 1. 正在检查登录状态 -->
    <div v-if="checkingAuth" class="auth-loading">
      正在验证登录状态...
    </div>

    <!-- 2. 未登录：显示登录或注册页面 -->
    <div v-else-if="!currentUser" class="auth-container">

      <LoginForm
        v-if="authPage === 'login'"
        @login-success="handleLoginSuccess"
        @switch-register="authPage = 'register'"
      />

      <RegisterForm
        v-else
        @switch-login="authPage = 'login'"
      />

    </div>

    <!-- 3. 已登录：显示 PaperMind 主界面 -->
    <div v-else class="app-container">

      <!-- ==================== 左侧文献库 ==================== -->

      <PaperSidebar
        :current-user="currentUser"
        :papers="papers"
        :current-paper="currentPaper"
        :uploading="uploading"
        :upload-error="uploadError"
        :loading-papers="loadingPapers"
        :paper-list-error="paperListError"
        :asking="asking"
        :deleting-paper-id="deletingPaperId"
        @file-change="handleFileChange"
        @select-paper="paper => currentPaper = paper"
        @delete-paper="deletePaper"
        @logout="logout"
      />

      <!-- ==================== 右侧聊天区域 ==================== -->

      <ChatPanel
        ref="chatPanelRef"
        :current-paper="currentPaper"
        :messages="messages"
        :question="question"
        :asking="asking"
        :ask-error="askError"
        :loading-messages="loadingMessages"
        :message-error="messageError"
        @update:question="question = $event"
        @send-question="sendQuestion"
      />

    </div>

  </div>
</template>



<style scoped>
/* 整个 PaperMind 应用根节点 */
.app-root {
  width: 100%;
  min-height: 100vh;
}

/* 登录和注册页面的容器 */
.auth-container {
  width: 100%;
  min-height: 100vh;
}

/* 已登录后的主界面布局 */
.app-container {
  display: flex;
  width: 100%;
  height: 100vh;
  min-height: 100vh;
  overflow: hidden;
  background: #f5f5f7;
  font-family: Arial, sans-serif;
}

/* 初次进入应用时的认证加载状态 */
.auth-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 100vh;
  color: #777;
}
</style>
