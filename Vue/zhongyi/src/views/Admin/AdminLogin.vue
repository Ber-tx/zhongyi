<template>
  <div class="login-wrap">
    <div class="bg-texture"></div>

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
          class="login-btn"
          size="large"
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
  } catch {
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
  background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%);
  position: relative;
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
}

/* 宣纸纹理 */
.bg-texture {
  position: fixed; inset: 0; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
}

.login-card {
  position: relative; z-index: 10;
  width: 400px;
  background: rgba(255, 252, 242, 0.92);
  backdrop-filter: blur(12px);
  border: 1px solid #c8a96e;
  border-radius: 12px;
  padding: 48px 40px;
  text-align: center;
  box-shadow: 0 20px 50px rgba(100,60,10,.15),
              inset 0 1px 0 rgba(255,248,220,.8);
}

/* 顶部金线 */
.login-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, transparent, #c8a020 50%, transparent);
  border-radius: 12px 12px 0 0;
}

.logo {
  width: 72px; height: 72px;
  border-radius: 12px;
  background: linear-gradient(135deg, #8b3d1a, #c04a20);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 6px 18px rgba(139,61,26,.35);
}

.logo-char {
  font-size: 32px; color: #fdeabb;
  font-family: 'Noto Serif SC', "KaiTi", serif;
}

.title {
  color: #3d2b10;
  font-size: 20px; margin: 0 0 6px; font-weight: 700;
  letter-spacing: 2px;
}

.subtitle {
  color: #8b6030;
  font-size: 13px; margin: 0 0 32px;
  letter-spacing: 4px;
}

:deep(.el-input__wrapper) {
  background: #fffdf5 !important;
  box-shadow: 0 0 0 1px #d4b483 !important;
  border-radius: 6px !important;
}
:deep(.el-input__wrapper:hover),
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #8b3d1a !important;
}
:deep(.el-input__inner) {
  color: #3d2b10 !important;
  font-family: inherit !important;
}
:deep(.el-input__inner::placeholder) {
  color: #b09060 !important;
}
:deep(.el-input__prefix-inner .el-icon) {
  color: #8b6030 !important;
}

.login-btn {
  width: 100% !important;
  height: 46px !important;
  border-radius: 6px !important;
  font-size: 16px !important;
  letter-spacing: 4px !important;
  font-family: inherit !important;
  font-weight: 700 !important;
  background: linear-gradient(135deg, #8b3d1a, #c04a20) !important;
  border: none !important;
  color: #fdeabb !important;
  margin-top: 8px !important;
  box-shadow: 0 4px 14px rgba(139,61,26,.35) !important;
  transition: all .3s !important;
}
.login-btn:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 8px 20px rgba(139,61,26,.45) !important;
}

.back-link {
  margin-top: 24px;
  color: #9a7040;
  font-size: 13px; cursor: pointer;
  transition: color .2s;
}
.back-link:hover { color: #5a2d00; }
</style>