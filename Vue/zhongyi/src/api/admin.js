// 路径：Vue/zhongyi/src/api/admin.js
import axios from 'axios'

const BASE = '/api/admin'

// 创建带 Token 的 axios 实例
const adminHttp = axios.create({ baseURL: BASE })

// 请求拦截：自动带上 Token
adminHttp.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token')
  if (token) config.headers['Authorization'] = `Bearer ${token}`
  return config
})

// 响应拦截：401 自动跳转登录
adminHttp.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('admin_token')
      window.location.href = '/admin/login'
    }
    return Promise.reject(err)
  }
)

// ===== 接口方法 =====

export const adminLogin = (username, password) =>
  adminHttp.post('/login', { username, password })

export const getStats = () =>
  adminHttp.get('/stats')

export const getPatients = (page = 1, size = 10, keyword = '') =>
  adminHttp.get('/patients', { params: { page, size, keyword } })

export const deletePatient = (id) =>
  adminHttp.delete(`/patient/${id}`)

export const getDiagnoses = (page = 1, size = 10) =>
  adminHttp.get('/diagnoses', { params: { page, size } })
