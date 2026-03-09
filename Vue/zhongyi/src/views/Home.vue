<template>
  <div class="home-container">
    <div class="music-control" @click="toggleMusic">
  <div class="music-icon" :class="{ 'is-playing': isPlaying }">
    <el-icon :size="24">
      <VideoPause v-if="isPlaying" />
      <VideoPlay v-else />
    </el-icon>
  </div>
  <span class="music-text">{{ isPlaying ? '背景音乐: 开' : '背景音乐: 关' }}</span>
</div>

<audio ref="audioRef" loop>
  <source src="../assets/audio/bgm/梁祝.wav" type="audio/mpeg">
</audio>
    <div class="bg-overlay"></div>

    <div class="content-wrapper">
      <div class="left-section">
        <h1 class="main-title">中医智慧诊疗系统</h1>
        <p class="sub-title">Traditional Chinese Medicine Smart Diagnosis</p>
        
        <div class="info-cards">
          <div class="card" @click="navigateTo('intro')">
            <el-icon><Guide /></el-icon>
            <div class="text">
              <h3>系统介绍</h3>
              <p>了解望闻问切智能化流程</p>
            </div>
          </div>
          <div class="card" @click="navigateTo('history')">
            <el-icon><Collection /></el-icon>
            <div class="text">
              <h3>中医文化</h3>
              <p>探索千年医学智慧</p>
            </div>
          </div>
          <div class="card" @click="navigateTo('hardware')">
            <el-icon><Cpu /></el-icon>
            <div class="text">
              <h3>硬件指引</h3>
              <p>脉诊仪与采集设备说明</p>
            </div>
          </div>
        </div>
      </div>

      <div class="right-section">
        <div class="login-panel">
          <h2 class="panel-title">用户登录</h2>
          
          <el-tabs v-model="loginType" class="custom-tabs" stretch>
            
            <el-tab-pane label="身份证感应" name="auto">
              <div class="sensor-box">
                <div class="scan-animation" :class="{ scanning: isScanning }">
                  <el-icon :size="60" color="#409EFF"><Postcard /></el-icon>
                  <div class="scan-line"></div>
                </div>
                <p class="hint-text">{{ scanStatusText }}</p>
                <el-button type="primary" round @click="startScan" :loading="isScanning">
                  {{ isScanning ? '正在读取...' : '点击开始感应' }}
                </el-button>
              </div>
            </el-tab-pane>

            <el-tab-pane label="手动输入" name="manual">
              <el-form :model="form" label-width="70px" class="login-form">
                <el-form-item label="姓名">
                  <el-input v-model="form.name" placeholder="请输入姓名" />
                </el-form-item>
                
                <el-row :gutter="10">
                  <el-col :span="12">
                    <el-form-item label="性别">
                      <el-select v-model="form.gender" placeholder="选择">
                        <el-option label="男" value="男" />
                        <el-option label="女" value="女" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="民族">
                      <el-input v-model="form.nation" placeholder="如：汉族" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-form-item label="出生">
                  <el-date-picker 
                    v-model="form.birthday" 
                    type="date" 
                    placeholder="选择出生日期" 
                    style="width: 100%" 
                  />
                </el-form-item>

                <el-form-item label="住址">
                  <el-input v-model="form.address" placeholder="请输入家庭住址" />
                </el-form-item>

                <el-form-item label="身份证">
                  <el-input v-model="form.idCard" placeholder="请输入18位身份证号" />
                </el-form-item>

                <el-button type="primary" class="submit-btn" @click="handleLogin">
                  登录并开始检测
                </el-button>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive,onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { ElMessage } from 'element-plus'
import { VideoPlay, VideoPause, Guide, Collection, Cpu, Postcard } from '@element-plus/icons-vue'
//登录接口，传入信息到数据库
import { loginAndSave } from '@/api/auth'




const router = useRouter()
//日期转换函数
const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}


// src/views/Home.vue 中的 handleLogin 函数
// src/views/Home.vue

const handleLogin = async () => {
  try {
    const submitForm = {
      ...form,
      birthday: formatDate(form.birthday)
    }

    const res = await loginAndSave(submitForm)
    // 关键点：这里打印一下 res.data 到底长什么样
    console.log("后端返回的原始数据:", res.data)

    // 注意：根据你的截图，后端返回的结构中 res.data 本身就是 result 对象
    const result = res.data

    if (result.code === 200) {
      // 这里的 result.data 应该是后端返回的 Patient 实体
      const patient = result.data 
      
      if (patient && patient.id) {
        // 存储 ID，注意强制转为字符串，防止 ID 过长丢失精度
        localStorage.setItem('current_patient_id', String(patient.id));
        localStorage.setItem('current_patient_idCard', patient.idCard );
        
        console.log("存储成功，ID 为:", localStorage.getItem('current_patient_id'));
      }

      ElMessage.success('录入成功')
      localStorage.setItem('temp_id_card', patient.idCard);
      
      
      // 执行跳转
      router.push('/detect')
    } else {
      ElMessage.error(result.msg || '保存失败')
    }
  } catch (error) {
    // 如果上面 if 块里的代码运行报错（比如访问了不存在的属性），就会掉到这里
    console.error("代码运行报错:", error);
    ElMessage.error('程序逻辑异常，请检查控制台日志');
  }
}



const loginType = ref('auto') // 默认选中身份证感应
const isScanning = ref(false)
const scanStatusText = ref('请将二代身份证放置在读卡区')
const isPlaying = ref(false)
const audioRef = ref(null)

// 表单数据
const form = reactive({
  name: '',
  gender: '男',

  birthday: '',
  address: '',
  idCard: ''
})

// 左侧板块点击跳转
const navigateTo = (type) => {
  if (type === 'history') {
    router.push('/culture'); 
  } else if (type === 'intro') {
    router.push('/intro');
  } else if (type === 'hardware') {
    router.push('/hardware');
  } else {
    ElMessage.info(`跳转到 ${type} 详情页 (功能待开发)`);
  }
}

// 模拟身份证感应逻辑
const startScan = () => {
  isScanning.value = true
  scanStatusText.value = '正在读取硬件信息...'
  
  // 模拟3秒后的硬件回调
  setTimeout(() => {
    isScanning.value = false
    scanStatusText.value = '读取成功！'
    // 自动填充表单（模拟数据）
    form.name = '张三丰'
    form.gender = '男'
    form.nation = '汉族'
    form.idCard = '110101199001011234'
    form.address = '湖北省武当山特区'
    loginType.value = 'manual' // 切换过去让用户确认
    ElMessage.success('身份证读取成功')
  }, 2000)
}



// 切换播放/暂停
const toggleMusic = () => {
  if (isPlaying.value) {
    audioRef.value.pause()
  } else {
    audioRef.value.play().catch(err => {
      console.warn("浏览器拦截了自动播放，需用户手动点击", err)
    })
  }
  isPlaying.value = !isPlaying.value
}

// 可选：页面加载后尝试自动播放（注意：现代浏览器通常会拦截带声音的自动播放）
onMounted(() => {
  // audioRef.value.play() 
})
</script>

<style scoped>
/* 容器布局 */
.home-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  /* 使用覆盖模式，确保没有白边 */
  background: url('../assets/images/answerDialog/background_no_scroll.png') no-repeat center center / cover; 
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.bg-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  /* 重点：去掉 blur(模糊)，改用深色渐变蒙层 */
  background: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.5));
  z-index: 1;
}

.content-wrapper {
  position: relative;
  z-index: 2;
  display: flex;
  width: 85%;
  max-width: 1200px;
  height: 80vh;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.3);
  overflow: hidden;
}

/* 左侧样式 */
.left-section {
  flex: 1;
  background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%);
  color: white;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.main-title {
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: bold;
  letter-spacing: 2px;
}

.sub-title {
  font-size: 1rem;
  opacity: 0.8;
  margin-bottom: 50px;
  font-family: 'Times New Roman', serif;
}

.info-cards .card {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid rgba(255,255,255,0.1);
}

.info-cards .card:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(10px);
}

.info-cards .card .el-icon {
  font-size: 28px;
  margin-right: 15px;
}

.info-cards h3 { margin: 0; font-size: 1.1rem; }
.info-cards p { margin: 5px 0 0; font-size: 0.85rem; opacity: 0.7; }

/* 右侧样式 */
.right-section {
  flex: 1;
  padding: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fff;
}

.login-panel {
  width: 100%;
  max-width: 400px;
}

.panel-title {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 1.8rem;
}

/* 身份证感应区样式 */
.sensor-box {
  text-align: center;
  padding: 40px 0;
}

.scan-animation {
  position: relative;
  width: 100px;
  height: 80px;
  margin: 0 auto 20px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: #409EFF;
  box-shadow: 0 0 5px #409EFF;
  display: none;
}

.scan-animation.scanning {
  border-color: #409EFF;
}

.scan-animation.scanning .scan-line {
  display: block;
  animation: scan 1.5s infinite linear;
}

@keyframes scan {
  0% { top: 0; }
  100% { top: 100%; }
}

.hint-text {
  color: #666;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.submit-btn {
  width: 100%;
  height: 40px;
  font-size: 16px;
  margin-top: 10px;
  background-color: #4ca1af; /* 使用与左侧呼应的主题色 */
  border-color: #4ca1af;
}

.submit-btn:hover {
  background-color: #3b8d99;
  border-color: #3b8d99;
}
/* 音乐控制悬浮按钮 */
.music-control {
  position: absolute;
  top: 30px;
  right: 30px;
  z-index: 100;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  padding: 8px 15px;
  border-radius: 30px;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  color: white;
}

.music-control:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: scale(1.05);
}

.music-icon {
  display: flex;
  margin-right: 8px;
}

/* 播放时的旋转动画 */
.is-playing {
  animation: rotate 3s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.music-text {
  font-size: 14px;
  font-weight: 300;
}
</style>