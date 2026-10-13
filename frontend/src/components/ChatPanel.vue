
<script setup>
import { ref, nextTick } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

// ============================================
// 1. 接收父组件的数据
// ============================================

defineProps({
  currentPaper: {
    type: Object,
    default: null
  },
  messages: {
    type: Array,
    required: true
  },
  question: {
    type: String,
    default: ''
  },
  asking: Boolean,
  askError: String,
  loadingMessages: Boolean,
  messageError: String
})

// ============================================
// 2. 向父组件发送事件
// ============================================

const emit = defineEmits([
  'update:question',
  'send-question'
])

// ============================================
// 3. Markdown 渲染
// ============================================

marked.setOptions({
  gfm: true,
  breaks: true
})

function renderMarkdown(content) {
  const html = marked.parse(content || '')
  return DOMPurify.sanitize(html)
}

// ============================================
// 4. 自动滚动到底部
// ============================================

const messageContainer = ref(null)

async function scrollToBottom() {
  await nextTick()

  if (messageContainer.value) {
    messageContainer.value.scrollTop =
      messageContainer.value.scrollHeight
  }
}

// 让 App.vue 可以调用子组件的滚动函数
defineExpose({
  scrollToBottom
})
</script>

<template>
  <main class="main-content">

    <!-- 顶部标题 -->
    <header class="chat-header">
      <h2>论文智能问答</h2>

      <p v-if="currentPaper">
        当前论文：{{ currentPaper.name }}
      </p>

      <p v-else>
        选择一篇论文，开始与 AI 对话
      </p>
    </header>

    <!-- 聊天消息区域 -->
    <div
      ref="messageContainer"
      class="chat-messages"
    >
      <p
        v-if="loadingMessages"
        class="loading-message"
      >
        正在加载历史对话...
      </p>

      <p
        v-if="messageError"
        class="error-text"
      >
        {{ messageError }}
      </p>

      <!-- 欢迎页面 -->
      <div
        v-if="!loadingMessages && messages.length === 0"
        class="welcome-message"
      >
        <h1>欢迎使用 PaperMind</h1>
        <p>上传一篇 PDF 论文，然后向 AI 提问。</p>
      </div>

      <!-- 消息列表 -->
      <div
        v-if="messages.length > 0"
        class="message-list"
      >
        <div
          v-for="(message, index) in messages"
          :key="message.id ?? index"
          class="message"
          :class="message.role"
        >
          <div class="message-role">
            {{
              message.role === 'user'
                ? '你'
                : 'PaperMind AI'
            }}
          </div>

          <!-- 用户提问 -->
          <div
            v-if="message.role === 'user'"
            class="message-content"
          >
            {{ message.content }}
          </div>

          <!-- AI Markdown 回答 -->
          <div
            v-else-if="message.role === 'assistant'"
            class="message-content markdown-body"
            v-html="renderMarkdown(message.content)"
          ></div>

          <!-- AI 引用来源 -->
          <div
            v-if="
              message.role === 'assistant' &&
              message.sources?.length
            "
            class="sources-section"
          >
            <details>
              <summary>
                📚 参考来源（{{ message.sources.length }} 个片段）
              </summary>

              <div
                v-for="(source, sourceIndex) in message.sources"
                :key="sourceIndex"
                class="source-card"
              >
                <div class="source-header">
                  <strong>
                    PDF 第 {{ source.page }} 页
                  </strong>

                  <span class="source-score">
                    检索分数：
                    {{ Number(source.score).toFixed(3) }}
                  </span>
                </div>

                <p class="source-text">
                  {{ source.text }}
                </p>
              </div>
            </details>
          </div>
        </div>
      </div>

      <div
        v-if="asking"
        class="loading-message"
      >
        AI 正在阅读论文并生成回答...
      </div>
    </div>

    <!-- 底部提问区域 -->
    <div class="chat-footer">

      <p v-if="askError" class="error-text">
        {{ askError }}
      </p>

      <div class="chat-input">
        <input
          :value="question"
          type="text"
          placeholder="向论文提问，例如：ResNet 为什么引入残差连接？"
          :disabled="asking || !currentPaper"
          @input="emit('update:question', $event.target.value)"
          @keyup.enter="emit('send-question')"
        />

        <button
          type="button"
          :disabled="
            asking ||
            !currentPaper ||
            !question.trim()
          "
          @click="emit('send-question')"
        >
          {{ asking ? '思考中...' : '发送' }}
        </button>
      </div>
    </div>

  </main>
</template>

<style scoped>
.main-content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.chat-header {
  background: white;
  padding: 20px 32px;
  border-bottom: 1px solid #e5e5e5;
}

.chat-header h2 {
  margin: 0 0 8px;
  font-size: 18px;
}

.chat-header p {
  margin: 0;
  color: #999;
  font-size: 13px;
}

.chat-messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 24px;
}

.welcome-message {
  margin: 15vh auto 0;
  text-align: center;
}

.welcome-message h1 {
  font-size: 28px;
  color: #333;
}

.welcome-message p {
  color: #999;
}

.message-list {
  width: 100%;
  max-width: 850px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  max-width: 85%;
}

.message.user {
  align-self: flex-end;
  background: #e5e7eb;
  padding: 14px 18px;
  border-radius: 14px;
}

.message.assistant {
  align-self: flex-start;
  background: white;
  padding: 14px 18px;
  border-radius: 14px;
}

.message-role {
  font-size: 12px;
  color: #777;
  margin-bottom: 8px;
}

.message-content {
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.loading-message {
  color: #888;
  font-size: 13px;
  text-align: center;
  margin: 12px auto;
}

.error-text {
  color: #dc2626;
  font-size: 12px;
  overflow-wrap: anywhere;
}

.chat-footer {
  background: white;
}

.chat-footer .error-text {
  padding: 8px 32px 0;
  margin: 0;
}

.chat-input {
  display: flex;
  gap: 12px;
  padding: 24px 32px;
  background: white;
}

.chat-input input {
  flex: 1;
  min-width: 0;
  padding: 14px;
  border: 1px solid #ddd;
  border-radius: 10px;
  outline: none;
}

.chat-input button {
  padding: 12px 25px;
  background: #333;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}

.chat-input button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Markdown 样式 */

.markdown-body {
  color: #333;
  white-space: normal;
}

.markdown-body :deep(p) {
  margin: 0 0 12px;
}

.markdown-body :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin: 18px 0 10px;
  line-height: 1.4;
}

.markdown-body :deep(h1) {
  font-size: 20px;
}

.markdown-body :deep(h2) {
  font-size: 18px;
}

.markdown-body :deep(h3) {
  font-size: 16px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 24px;
  margin: 8px 0 14px;
}

.markdown-body :deep(li) {
  margin-bottom: 6px;
}

.markdown-body :deep(strong) {
  font-weight: 600;
}

.markdown-body :deep(pre) {
  background: #f5f5f7;
  padding: 14px;
  border-radius: 8px;
  overflow-x: auto;
}

.markdown-body :deep(code) {
  font-family: Consolas, monospace;
  font-size: 13px;
}

.markdown-body :deep(blockquote) {
  border-left: 3px solid #bbb;
  padding-left: 14px;
  margin: 12px 0;
  color: #666;
}

.markdown-body :deep(table) {
  display: block;
  max-width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
}

/* 引用来源 */

.sources-section {
  margin-top: 18px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.sources-section summary {
  font-size: 13px;
  color: #555;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
}

.source-card {
  background: #f5f5f7;
  border-radius: 8px;
  padding: 12px;
  margin-top: 12px;
}

.source-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
}

.source-score {
  color: #888;
  white-space: nowrap;
}

.source-text {
  margin: 10px 0 0;
  font-size: 12px;
  line-height: 1.7;
  color: #666;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  max-height: 180px;
  overflow-y: auto;
}
</style>
