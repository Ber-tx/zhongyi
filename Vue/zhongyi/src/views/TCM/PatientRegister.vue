<template>
  <div class="tcm-panel reg-panel">
    <div class="panel-title-bar">
      <span class="panel-step">第一步：确认个人信息</span>
      <span class="panel-hint">填写完毕后，确认信息后点击「下一步」前往四诊辨识，* 标记为必填项目。</span>
    </div>

    <!-- 录入方式切换 -->
    <div class="input-mode-bar">
      <div class="mode-tab" :class="{ active: inputMode === 'manual' }" @click="inputMode = 'manual'">
        ✏️ 手动填写
      </div>
      <div class="mode-tab" :class="{ active: inputMode === 'scan' }" @click="inputMode = 'scan'">
        💳 身份证感应
      </div>
    </div>

    <!-- 身份证感应区 -->
    <div v-if="inputMode === 'scan'" class="scan-zone">
      <div class="scan-card" :class="{ scanning: isScanning, done: scanDone }">
        <div class="card-chip"></div>
        <div class="card-lines">
          <div class="card-line"></div>
          <div class="card-line short"></div>
        </div>
        <div class="scan-glow"></div>
        <div class="scan-sweep" v-if="isScanning"></div>
      </div>
      <p class="scan-status">{{ scanStatus }}</p>
      <el-button
        class="btn-primary"
        :loading="isScanning"
        @click="startScan"
        :disabled="scanDone"
      >
        {{ isScanning ? '读取中...' : scanDone ? '✓ 读取完成' : '开始感应读取' }}
      </el-button>
      <p v-if="scanDone" class="scan-tip">
        已自动填入信息，请在下方确认后提交。
        <span class="link" @click="switchToManual">手动修改</span>
      </p>
    </div>

    <!-- 表单 -->
    <div class="form-scroll" :class="{ 'show-after-scan': inputMode === 'scan' && scanDone }">
      <el-form :model="form" label-width="88px" class="tcm-form patient-form" ref="formRef">

        <div class="section-heading">基本信息（必填）</div>

        <el-row :gutter="18">
          <el-col :span="8">
            <el-form-item label="姓名 *" prop="name"
              :rules="[{ required: true, message: '请输入姓名', trigger: 'blur' }]">
              <el-input v-model="form.name" placeholder="真实姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="性别 *" prop="gender">
              <el-radio-group v-model="form.gender">
                <el-radio value="男">男</el-radio>
                <el-radio value="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="出生日期 *">
              <el-date-picker v-model="form.birthday" type="date"
                placeholder="选择出生日期" style="width:100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="18">
          <el-col :span="12">
            <el-form-item label="身份证号 *" prop="idCard"
              :rules="[{ required: true, len: 18, message: '请输入18位身份证号', trigger: 'blur' }]">
              <el-input v-model="form.idCard" placeholder="18位身份证号码" maxlength="18" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="住址 *">
              <el-input v-model="form.address" placeholder="家庭住址" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 选填分区 -->
        <div class="section-heading">
          补充信息
          <span class="opt-tag">以下均为选填，有助于更精准的体质分析</span>
        </div>

        <el-row :gutter="18">
          <el-col :span="8">
            <el-form-item label="民族">
              <el-input v-model="form.nation" placeholder="如：汉族" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="联系电话">
              <el-input v-model="form.phone" placeholder="手机号码" maxlength="11" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="职业">
              <el-select v-model="form.occupation" placeholder="选择职业" clearable>
                <el-option v-for="o in occupations" :key="o" :label="o" :value="o" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="18">
          <el-col :span="8">
            <el-form-item label="文化程度">
              <el-select v-model="form.education" placeholder="选择" clearable>
                <el-option v-for="e in educations" :key="e" :label="e" :value="e" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="婚姻状况">
              <el-select v-model="form.marital" placeholder="选择" clearable>
                <el-option label="未婚" value="未婚" />
                <el-option label="已婚" value="已婚" />
                <el-option label="离异" value="离异" />
                <el-option label="丧偶" value="丧偶" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="吸烟习惯">
              <el-select v-model="form.smoking" placeholder="选择" clearable>
                <el-option label="不吸烟" value="不吸烟" />
                <el-option label="偶尔吸烟" value="偶尔吸烟" />
                <el-option label="规律吸烟" value="规律吸烟" />
                <el-option label="已戒烟" value="已戒烟" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="18">
          <el-col :span="8">
            <el-form-item label="饮酒习惯">
              <el-select v-model="form.drinking" placeholder="选择" clearable>
                <el-option label="不饮酒" value="不饮酒" />
                <el-option label="偶尔饮酒" value="偶尔饮酒" />
                <el-option label="规律饮酒" value="规律饮酒" />
                <el-option label="已戒酒" value="已戒酒" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="运动习惯">
              <el-select v-model="form.exercise" placeholder="选择" clearable>
                <el-option label="几乎不运动" value="几乎不运动" />
                <el-option label="偶尔运动" value="偶尔运动" />
                <el-option label="每周1-2次" value="每周1-2次" />
                <el-option label="每周3次以上" value="每周3次以上" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="睡眠质量">
              <el-select v-model="form.sleepQuality" placeholder="选择" clearable>
                <el-option label="良好" value="良好" />
                <el-option label="一般" value="一般" />
                <el-option label="较差（失眠）" value="较差" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="18">
          <el-col :span="12">
            <el-form-item label="既往病史">
              <el-input v-model="form.medicalHistory" placeholder="如：高血压、糖尿病等，无则留空"
                type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="家族病史">
              <el-input v-model="form.familyHistory" placeholder="如：父亲有冠心病，无则留空"
                type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="18">
          <el-col :span="12">
            <el-form-item label="过敏史">
              <el-input v-model="form.allergyHistory" placeholder="药物/食物过敏史，无则留空" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主要症状">
              <el-input v-model="form.chiefComplaint" placeholder="近期主要不适，如：乏力、失眠等" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <el-button class="btn-next" @click="handleSubmit" :loading="submitting">
            下 一 步 ，进入四诊辨识 →
          </el-button>
          <el-button class="btn-secondary" @click="resetForm">重 填</el-button>
        </div>
      </el-form>
    </div>

    <!-- 底部提示 -->
    <div class="panel-footer-tip">
      💡 点击左上角「开始测试」按钮，可以返回到主页面
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { loginAndSave } from '@/api/auth'

const router = useRouter()

// ===== 录入模式 =====
const inputMode = ref('manual')
const isScanning = ref(false)
const scanDone = ref(false)
const scanStatus = ref('请将二代居民身份证平放在读卡区域，感应距离约 2~5 cm')

const startScan = async () => {
  isScanning.value = true
  scanStatus.value = '正在读取身份证信息...'
  // 模拟读卡延迟
  await new Promise(r => setTimeout(r, 2200))
  // 模拟读到的数据（实际接入读卡器 SDK 替换此处）
  Object.assign(form, {
    name: '张三丰',
    gender: '男',
    birthday: '1980-05-15',
    idCard: '420301198005153219',
    address: '湖北省武当山特区太极路1号',
    nation: '汉族',
  })
  isScanning.value = false
  scanDone.value = true
  scanStatus.value = '✓ 读取成功！请确认以下信息后提交。'
  inputMode.value = 'scan' // 保留感应模式，显示表单
}

const switchToManual = () => {
  inputMode.value = 'manual'
}

// ===== 表单数据 =====
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  name: '', gender: '男', birthday: '', idCard: '', address: '',
  nation: '', phone: '', occupation: '', education: '', marital: '',
  smoking: '', drinking: '', exercise: '', sleepQuality: '',
  medicalHistory: '', familyHistory: '', allergyHistory: '', chiefComplaint: '',
})

const resetForm = () => {
  Object.keys(form).forEach(k => { form[k] = k === 'gender' ? '男' : '' })
  scanDone.value = false
  scanStatus.value = '请将二代居民身份证平放在读卡区域，感应距离约 2~5 cm'
}

const occupations = ['农民', '工人', '职员', '教师', '医务人员', '个体经营', '学生', '退休', '无业', '其他']
const educations  = ['小学及以下', '初中', '高中/中专', '大专', '本科', '研究生及以上']

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    ElMessage.warning('请填写必填项（姓名、身份证号、住址）')
    return
  }

  submitting.value = true
  try {
    const payload = {
      name:     form.name,
      gender:   form.gender,
      birthday: form.birthday,
      idCard:   form.idCard,
      address:  form.address,
    }
    const res = await loginAndSave(payload)
    const result = res.data
    if (result.code === 200) {
      const patient = result.data
      if (patient?.id) {
        localStorage.setItem('current_patient_id', String(patient.id))
        localStorage.setItem('current_patient_idCard', patient.idCard)
        // 存储补充信息供后续使用
        localStorage.setItem('patient_extra', JSON.stringify({
          phone: form.phone, occupation: form.occupation,
          smoking: form.smoking, drinking: form.drinking,
          medicalHistory: form.medicalHistory, chiefComplaint: form.chiefComplaint,
        }))
      }
      // 清除上一轮的检测完成状态
      ;['wang', 'wen', 'wenjuan', 'qie'].forEach(k =>
        localStorage.removeItem(`${k}_finished_id`)
      )
      ElMessage.success('信息录入成功，正在跳转四诊辨识...')
      setTimeout(() => router.push('/detect'), 700)
    } else {
      ElMessage.error(result.msg || '保存失败')
    }
  } catch {
    ElMessage.error('网络错误，请检查后端服务')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
@import '@/styles/tcm-shared.css';

.reg-panel { height: 100%; overflow: hidden; }

/* 录入模式切换 */
.input-mode-bar {
  display: flex;
  background: #faf3e0;
  border-bottom: 1px solid #e8d5a0;
  flex-shrink: 0;
}
.mode-tab {
  flex: 1; text-align: center;
  padding: 10px; font-size: 13px; font-weight: 600;
  color: #8b6030; cursor: pointer; transition: .2s;
  border-right: 1px solid #e8d5a0;
}
.mode-tab:last-child { border-right: none; }
.mode-tab:hover { background: #f5e8c8; }
.mode-tab.active {
  background: linear-gradient(180deg, #f5e4a8, #ebd07a);
  color: #5a2d00; border-bottom: 2px solid #c8a020;
}

/* 身份证感应区 */
.scan-zone {
  display: flex; flex-direction: column; align-items: center;
  padding: 28px 20px 20px;
  gap: 14px; flex-shrink: 0;
}

.scan-card {
  position: relative; width: 200px; height: 126px;
  background: linear-gradient(135deg, #2c4a8a 0%, #1a3060 40%, #3d2b10 100%);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,.25);
  overflow: hidden;
  transition: box-shadow .3s;
}
.scan-card.scanning {
  box-shadow: 0 0 0 3px #c8a020, 0 8px 24px rgba(0,0,0,.25);
}
.scan-card.done {
  box-shadow: 0 0 0 3px #4a907e, 0 8px 24px rgba(0,0,0,.25);
}

.card-chip {
  position: absolute; top: 22px; left: 22px;
  width: 30px; height: 22px;
  background: linear-gradient(135deg, #d4aa30, #a07820);
  border-radius: 3px;
  box-shadow: inset 0 1px 2px rgba(255,220,100,.4);
}
.card-lines {
  position: absolute; bottom: 22px; left: 22px; right: 22px;
}
.card-line { height: 2px; background: rgba(255,255,255,.35); margin-bottom: 5px; border-radius: 1px; }
.card-line.short { width: 55%; }

.scan-glow {
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 60% 40%, rgba(200,160,32,.12) 0%, transparent 65%);
}

.scan-sweep {
  position: absolute; left: 0; right: 0; top: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(200,255,200,.8), transparent);
  animation: sweep 1.2s infinite linear;
}
@keyframes sweep { from { top: 0; } to { top: 100%; } }

.scan-status { font-size: 13px; color: #6b4c24; text-align: center; }
.scan-tip { font-size: 12px; color: #7a5520; text-align: center; }
.link { color: #8b3d1a; cursor: pointer; text-decoration: underline; }

/* 表单区 */
.form-scroll {
  flex: 1; overflow-y: auto; padding: 16px 24px 8px;
}

.section-heading {
  font-size: 13px; font-weight: 700; color: #5a2d00;
  padding: 6px 0 8px;
  border-bottom: 1px solid #e8d5a0;
  margin: 12px 0 10px;
  display: flex; align-items: center; gap: 6px;
}
.section-heading::before { content: '◈'; color: #c8a020; }

.opt-tag {
  font-size: 11px; color: #999;
  background: #f5f0e6; border: 1px solid #e0cfa0;
  padding: 1px 8px; border-radius: 10px; font-weight: 400;
}

.form-actions {
  display: flex; gap: 14px; padding: 14px 0 6px;
}

.btn-next {
  background: linear-gradient(135deg,#8b3d1a,#c04a20) !important;
  color: #fdeabb !important; border: none !important;
  padding: 10px 36px !important; font-size: 14px !important;
  font-weight: 700 !important; letter-spacing: 2px !important;
  border-radius: 4px !important;
  box-shadow: 0 4px 12px rgba(139,61,26,.35) !important;
}
.btn-next:hover { transform: translateY(-1px) !important; }

.btn-secondary {
  background: #f5f0e6 !important; color: #6b4c24 !important;
  border: 1px solid #c8a96e !important;
  padding: 10px 24px !important; font-size: 13px !important;
  border-radius: 4px !important;
}

.panel-footer-tip {
  padding: 9px 20px;
  background: linear-gradient(180deg, #f9f1d8, #f4e8c0);
  border-top: 1px solid #e0c87a;
  font-size: 12px; color: #7a5520; flex-shrink: 0;
}

/* show-after-scan 让感应后的表单动画进入 */
.show-after-scan {
  animation: slideDown .4s ease;
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>