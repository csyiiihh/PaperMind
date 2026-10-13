
<script setup>
import { ref } from 'vue'

// =====================================
// 1. 接收父组件传来的数据
// =====================================

const props = defineProps({
  currentUser: {
    type: Object,
    required: true
  },
  papers: {
    type: Array,
    required: true
  },
  currentPaper: {
    type: Object,
    default: null
  },
  uploading: Boolean,
  uploadError: String,
  loadingPapers: Boolean,
  paperListError: String,
  asking: Boolean,
  deletingPaperId: {
    type: String,
    default: null
  }
})

// =====================================
// 2. 向父组件发送事件
// =====================================

const emit = defineEmits([
  'file-change',
  'select-paper',
  'delete-paper',
  'logout'
])

const fileInput = ref(null)

function selectFile() {
  if (props.asking || props.uploading) return

  fileInput.value?.click()
}

function handleFileChange(event) {
  emit('file-change', event)
}

function selectPaper(paper) {
  if (props.asking) return

  emit('select-paper', paper)
}
</script>

<template>
  <aside class="sidebar">

    <h2 class="logo">📚 PaperMind</h2>
    <p class="subtitle">AI 科研文献助手</p>

    <!-- 上传 PDF -->
    <div
      class="upload-box"
      :class="{ disabled: asking || uploading }"
      @click="selectFile"
    >
      {{ uploading ? '正在上传和解析...' : '＋ 上传 PDF 论文' }}
    </div>

    <input
      ref="fileInput"
      type="file"
      accept=".pdf,application/pdf"
      style="display: none"
      :disabled="asking || uploading"
      @change="handleFileChange"
    />

    <p v-if="uploadError" class="error-text">
      {{ uploadError }}
    </p>

    <h3>我的文献</h3>

    <!-- 论文列表 -->
    <div class="paper-list">

      <p v-if="loadingPapers" class="empty-text">
        正在加载论文...
      </p>

      <p v-if="paperListError" class="error-text">
        {{ paperListError }}
      </p>

      <p
        v-if="!loadingPapers && !paperListError && papers.length === 0"
        class="empty-text"
      >
        还没有上传论文
      </p>

      <div
        v-for="paper in papers"
        :key="paper.id"
        class="paper-item"
        :class="{ active: currentPaper?.id === paper.id }"
        @click="selectPaper(paper)"
      >
        <span class="paper-name">
          📄 {{ paper.name }}
        </span>

        <button
          type="button"
          class="delete-btn"
          :disabled="
            asking ||
            uploading ||
            deletingPaperId !== null
          "
          @click.stop="emit('delete-paper', paper)"
        >
          {{
            deletingPaperId === paper.id
              ? '删除中...'
              : '删除'
          }}
        </button>
      </div>
    </div>

    <!-- 底部账户信息 -->
    <div class="account-panel">

      <div class="account-avatar">
        {{ currentUser.username.charAt(0).toUpperCase() }}
      </div>

      <div class="account-details">
        <span class="account-name">
          {{ currentUser.username }}
        </span>

        <span class="account-status">
          已登录
        </span>
      </div>

      <button
        type="button"
        class="account-logout"
        title="退出登录"
        aria-label="退出登录"
        @click="emit('logout')"
      >
        ↪
      </button>

    </div>

  </aside>
</template>

<style scoped>
.sidebar {
  width: 270px;
  flex-shrink: 0;
  height: 100%;
  padding: 24px;
  background: white;
  border-right: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo {
  margin-bottom: 4px;
  font-size: 23px;
}

.subtitle {
  color: #888;
  font-size: 13px;
  margin-bottom: 36px;
}

.upload-box {
  padding: 14px;
  background: #f5f5f7;
  border: 1px dashed #aaa;
  border-radius: 10px;
  text-align: center;
  cursor: pointer;
  margin-bottom: 35px;
}

.upload-box:hover {
  background: #ededf0;
}

.upload-box.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sidebar h3 {
  font-size: 14px;
  color: #555;
}

.paper-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.paper-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  background: #f5f5f7;
  font-size: 13px;
  cursor: pointer;
}

.paper-item:hover {
  background: #e9e9ee;
}

.paper-item.active {
  background: #e5e7eb;
  font-weight: 600;
}

.paper-name {
  flex: 1;
  min-width: 0;
  overflow-wrap: anywhere;
}

.delete-btn {
  flex-shrink: 0;
  border: none;
  background: transparent;
  color: #999;
  padding: 5px 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.delete-btn:hover {
  color: #dc2626;
  background: #fee2e2;
}

.delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-text {
  color: #aaa;
  font-size: 13px;
}

.error-text {
  color: #dc2626;
  font-size: 12px;
  overflow-wrap: anywhere;
}

.account-panel {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 10px;
}

.account-avatar {
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  border-radius: 50%;
  background: #e7e7ec;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.account-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.account-name {
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-status {
  font-size: 11px;
  color: #888;
}

.account-logout {
  border: none;
  background: transparent;
  color: #777;
  font-size: 22px;
  cursor: pointer;
  border-radius: 7px;
  padding: 5px 9px;
}

.account-logout:hover {
  color: #dc2626;
  background: #fee2e2;
}
</style>
