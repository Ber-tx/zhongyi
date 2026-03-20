<template>
  <div class="login-wrap">
    <div class="login-card">
      <div class="logo">
        <span class="logo-char">管</span>
      </div>
      <h2 class="title">中医诊疗系统</h2>
      <p class="subtitle">管理员后台</p>

      <el-form :model="form" @keyup.enter="handleLogin">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          class="login-btn"
          :loading="loading"
          @click="handleLogin"
        >
          登 录
        </el-button>
      </el-form>

      <div class="back-link" @click="router.push('/')">← 返回患者入口</div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { adminLogin } from '@/api/admin'

const router = useRouter()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const handleLogin = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await adminLogin(form.username, form.password)
    const result = res.data
    if (result.code === 200) {
      localStorage.setItem('admin_token', result.data.token)
      localStorage.setItem('admin_username', result.data.username)
      ElMessage.success('登录成功')
      router.push('/admin')
    } else {
      ElMessage.error(result.msg || '登录失败')
    }
  } catch (e) {
    ElMessage.error('网络错误，请检查后端服务')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1c2e 0%, #2d4a3e 100%);
}

.login-card {
  width: 380px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 48px 40px;
  text-align: center;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.4);
}

.logo {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: linear-gradient(135deg, #4a907e, #2d7d65);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.logo-char {
  font-size: 32px;
  color: #fff;
  font-family: "Noto Serif SC", serif;
}

.title {
  color: #fff;
  font-size: 20px;
  margin: 0 0 6px;
  font-weight: 600;
}

.subtitle {
  color: rgba(255,255,255,0.5);
  font-size: 13px;
  margin: 0 0 32px;
  letter-spacing: 3px;
}

.el-form-item {
  margin-bottom: 16px;
}

:deep(.el-input__wrapper) {
  background: rgba(255,255,255,0.08) !important;
  border: 1px solid rgba(255,255,255,0.15) !important;
  box-shadow: none !important;
  border-radius: 10px;
}

:deep(.el-input__inner) {
  color: #fff !important;
}

:deep(.el-input__inner::placeholder) {
  color: rgba(255,255,255,0.35);
}

:deep(.el-input__prefix-inner .el-icon) {
  color: rgba(255,255,255,0.4);
}

.login-btn {
  width: 100%;
  height: 46px;
  border-radius: 10px;
  font-size: 16px;
  letter-spacing: 4px;
  background: linear-gradient(135deg, #4a907e, #2d7d65);
  border: none;
  margin-top: 8px;
}

.login-btn:hover {
  opacity: 0.9;
}

.back-link {
  margin-top: 24px;
  color: rgba(255,255,255,0.35);
  font-size: 13px;
  cursor: pointer;
  transition: color 0.2s;
}

.back-link:hover {
  color: rgba(255,255,255,0.7);
}
</style>