
import axios from 'axios'

// ============================================
// 1. 创建 Axios 实例
// ============================================

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 120000
})


// ============================================
// 2. 请求拦截器：自动携带 JWT
// ============================================

api.interceptors.request.use(
  config => {
    const token = sessionStorage.getItem(
      'access_token'
    )

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },

  error => Promise.reject(error)
)


// ============================================
// 3. 响应拦截器：安全处理 401
// ============================================

api.interceptors.response.use(
  response => response,

  error => {
    const status = error.response?.status
    const url = error.config?.url || ''

    // 登录密码错误，不触发全局退出
    const isLoginRequest = url
      .split('?')[0]
      .endsWith('/auth/login')

    if (status === 401 && !isLoginRequest) {

      // 当前浏览器中保存的 Token
      const currentToken = sessionStorage.getItem(
        'access_token'
      )

      // 发生错误的请求当时携带的 Token
      const requestAuthorization =
        error.config?.headers?.get?.('Authorization') ??
        error.config?.headers?.Authorization

      // 只有请求属于当前登录会话时，才退出
      if (
        currentToken &&
        requestAuthorization === `Bearer ${currentToken}`
      ) {

        sessionStorage.removeItem('access_token')

        window.dispatchEvent(
          new Event('papermind:unauthorized')
        )
      }
    }

    return Promise.reject(error)
  }
)

export default api
