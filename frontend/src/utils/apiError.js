
// ============================================
// PaperMind 统一 API 错误处理
// ============================================

export function getApiErrorMessage(
  error,
  defaultMessage = '操作失败，请稍后重试'
) {
  // 1. 主动取消的请求
  if (error.code === 'ERR_CANCELED') {
    return ''
  }

  // 2. 请求超时
  if (error.code === 'ECONNABORTED' ||
      error.code === 'ETIMEDOUT') {
    return '请求超时，请稍后重试'
  }

  // 3. 网络故障或后端无法连接
  if (!error.response) {
    return '无法连接服务器，请检查网络或后端服务'
  }

  const status = error.response.status
  const detail = error.response.data?.detail

  // 4. 401：JWT 无效
  // api.js 已经负责自动退出
  if (status === 401) {
    return '登录已失效，请重新登录'
  }

  // 5. 422：处理 FastAPI / Pydantic 校验错误
  if (status === 422 && Array.isArray(detail)) {
    const messages = detail.map(item => {
      const field = item.loc?.slice(1).join('.') || '参数'
      return `${field}：${item.msg}`
    })

    return messages.join('；')
  }

  // 6. 后端返回明确的业务错误
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  // 7. 其他 HTTP 状态码
  const statusMessages = {
    400: '请求参数不正确',
    403: '没有权限执行此操作',
    404: '请求的资源不存在或无权访问',
    409: '数据发生冲突，请检查后重试',
    413: '上传文件过大',
    422: '提交的数据不符合要求',
    429: '请求过于频繁，请稍后重试',
    500: '服务器内部错误，请稍后重试',
    502: '上游服务暂时异常，请稍后重试',
    503: '服务暂时不可用，请稍后重试',
    504: '服务器响应超时，请稍后重试'
  }

  return statusMessages[status] || defaultMessage
}
