<template>
  <div class="health-report-container">
    <!-- 页头 -->
    <div class="report-header">
      <el-button @click="goBack">← 返回</el-button>
      <h1>居民健康体检报告</h1>
      <div class="header-actions">
        <el-button type="primary" @click="exportPDF" :loading="isExporting">📥 导出PDF</el-button>
        <el-button @click="handlePrint">🖨️ 打印</el-button>
      </div>
    </div>

    <!-- 报告内容 -->
    <div v-if="examData" class="report-content" ref="reportRef">
      <!-- 患者基本信息 -->
      <div class="section">
        <h2 class="section-title">👤 患者基本信息</h2>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">姓名：</span>
            <span class="value">{{ examData.patientName || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="label">性别：</span>
            <span class="value">{{ examData.patientGender || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="label">年龄：</span>
            <span class="value">{{ examData.patientAge || '—' }}岁</span>
          </div>
          <div class="info-item">
            <span class="label">出生日期：</span>
            <span class="value">{{ fmtDate(examData.patientBirthday) }}</span>
          </div>
          <div class="info-item">
            <span class="label">身份证号：</span>
            <span class="value">{{ maskIdCard(examData.patientIdCard) }}</span>
          </div>
          <div class="info-item">
            <span class="label">联系电话：</span>
            <span class="value">{{ examData.phone || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="label">住址：</span>
            <span class="value">{{ examData.address || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="label">职业：</span>
            <span class="value">{{ examData.occupation || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="label">婚姻状况：</span>
            <span class="value">{{ examData.marital || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="label">体检日期：</span>
            <span class="value">{{ fmtDate(examData.examDate || examData.createTime) }}</span>
          </div>
          <div class="info-item">
            <span class="label">体质结论：</span>
            <el-tag v-if="examData.constitutionType" type="warning" size="small">{{ examData.constitutionType }}</el-tag>
            <span v-else class="text-muted">—</span>
          </div>
        </div>
      </div>

      <!-- 生活习惯 -->
      <div class="section" v-if="hasLifestyleData">
        <h2 class="section-title">🚭 生活习惯</h2>
        <div class="info-grid">
          <div class="info-item" v-if="examData.smoking">
            <span class="label">吸烟：</span>
            <el-tag class="lifestyle-tag" :type="getSmokingTagType(examData.smoking)">{{ examData.smoking }}</el-tag>
          </div>
          <div class="info-item" v-if="examData.drinking">
            <span class="label">饮酒：</span>
            <el-tag class="lifestyle-tag" :type="getDrinkingTagType(examData.drinking)">{{ examData.drinking }}</el-tag>
          </div>
          <div class="info-item" v-if="examData.exercise">
            <span class="label">运动频率：</span>
            <span class="value">{{ examData.exercise }}</span>
          </div>
          <div class="info-item" v-if="examData.sleepQuality">
            <span class="label">睡眠质量：</span>
            <el-tag class="lifestyle-tag" :type="getSleepTagType(examData.sleepQuality)">{{ examData.sleepQuality }}</el-tag>
          </div>
        </div>
      </div>

      <!-- 病史信息 -->
      <div class="section" v-if="hasHistoryData">
        <h2 class="section-title">📋 病史信息</h2>
        <div v-if="examData.medicalHistory" class="history-item">
          <strong>既往病史：</strong>
          <p>{{ examData.medicalHistory }}</p>
        </div>
        <div v-if="examData.familyHistory" class="history-item">
          <strong>家族病史：</strong>
          <p>{{ examData.familyHistory }}</p>
        </div>
        <div v-if="examData.allergyHistory" class="history-item">
          <strong>过敏史：</strong>
          <p>{{ examData.allergyHistory }}</p>
        </div>
      </div>

      <!-- 体格检查详细信息 -->
      <div class="section" v-if="hasPhysicalData">
        <h2 class="section-title">📏 体格检查</h2>
        
        <div class="subsection">
          <h3>身体测量</h3>
          <div class="info-grid">
            <div class="info-item" v-if="examData.height">
              <span class="label">身高：</span>
              <span class="value">{{ examData.height }} cm</span>
            </div>
            <div class="info-item" v-if="examData.weight">
              <span class="label">体重：</span>
              <span class="value">{{ examData.weight }} kg</span>
            </div>
            <div class="info-item" v-if="examData.bmi">
              <span class="value-card" :class="'bmi-' + getBMILevel(examData.bmi)">
                <div class="value-label">BMI</div>
                <div class="value-number">{{ examData.bmi }}</div>
                <div class="value-status">{{ getBMILabel(examData.bmi) }}</div>
              </span>
            </div>
            <div class="info-item" v-if="examData.waistCircumference">
              <span class="label">腰围：</span>
              <span class="value">{{ examData.waistCircumference }} cm</span>
            </div>
            <div class="info-item" v-if="examData.hipCircumference">
              <span class="label">臀围：</span>
              <span class="value">{{ examData.hipCircumference }} cm</span>
            </div>
          </div>
        </div>

        <div class="subsection">
          <h3>生命体征</h3>
          <div class="info-grid">
            <div class="info-item" v-if="examData.temperature">
              <span class="label">体温：</span>
              <span class="value" :class="getTemperatureClass(examData.temperature)">{{ examData.temperature }} ℃</span>
            </div>
            <div class="info-item" v-if="examData.heartRate">
              <span class="label">心率：</span>
              <span class="value" :class="getHeartRateClass(examData.heartRate)">{{ examData.heartRate }} bpm</span>
            </div>
            <div class="info-item" v-if="examData.spo2">
              <span class="label">血氧 SpO₂：</span>
              <span class="value" :class="getSPO2Class(examData.spo2)">{{ examData.spo2 }} %</span>
            </div>
            <div v-if="examData.bloodPressureSystolic && examData.bloodPressureDiastolic" class="info-item full-width">
              <span class="label">血压：</span>
              <span class="value-card" :class="'bp-' + getBPLevel(examData.bloodPressureSystolic, examData.bloodPressureDiastolic)">
                <div class="value-number">{{ examData.bloodPressureSystolic }}/{{ examData.bloodPressureDiastolic }} mmHg</div>
                <div class="value-status">{{ getBPLabel(examData.bloodPressureSystolic, examData.bloodPressureDiastolic) }}</div>
              </span>
            </div>
          </div>
        </div>

        <div class="subsection" v-if="hasVisionData">
          <h3>感觉器官检查</h3>
          <div class="info-grid">
            <div class="info-item" v-if="examData.visionLeft">
              <span class="label">视力（左）：</span>
              <span class="value">{{ examData.visionLeft }}</span>
            </div>
            <div class="info-item" v-if="examData.visionRight">
              <span class="label">视力（右）：</span>
              <span class="value">{{ examData.visionRight }}</span>
            </div>
            <div class="info-item" v-if="examData.hearing">
              <span class="label">听力：</span>
              <span class="value">{{ examData.hearing }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 实验室检查 -->
      <div class="section" v-if="hasLabData">
        <h2 class="section-title">🔬 实验室检查</h2>
        
        <div class="subsection">
          <h3>血糖代谢</h3>
          <div class="info-grid">
            <div class="info-item" v-if="examData.fastingBloodGlucose">
              <span class="label">空腹血糖：</span>
              <span class="value" :class="getGlucoseClass(examData.fastingBloodGlucose)">{{ examData.fastingBloodGlucose }} mmol/L</span>
            </div>
            <div class="info-item" v-if="examData.postprandialGlucose">
              <span class="label">餐后2h血糖：</span>
              <span class="value" :class="getPostprandialClass(examData.postprandialGlucose)">{{ examData.postprandialGlucose }} mmol/L</span>
            </div>
            <div class="info-item" v-if="examData.hba1c">
              <span class="label">糖化血红蛋白：</span>
              <span class="value" :class="getHbA1cClass(examData.hba1c)">{{ examData.hba1c }} %</span>
            </div>
          </div>
        </div>

        <div class="subsection" v-if="hasLipidData">
          <h3>血脂四项</h3>
          <div class="info-grid">
            <div class="info-item" v-if="examData.totalCholesterol">
              <span class="label">总胆固醇：</span>
              <span class="value" :class="getCholesterolClass(examData.totalCholesterol)">{{ examData.totalCholesterol }} mmol/L</span>
            </div>
            <div class="info-item" v-if="examData.triglycerides">
              <span class="label">甘油三酯：</span>
              <span class="value" :class="getTriglyceridesClass(examData.triglycerides)">{{ examData.triglycerides }} mmol/L</span>
            </div>
            <div class="info-item" v-if="examData.hdl">
              <span class="label">HDL：</span>
              <span class="value" :class="getHDLClass(examData.hdl)">{{ examData.hdl }} mmol/L</span>
            </div>
            <div class="info-item" v-if="examData.ldl">
              <span class="label">LDL：</span>
              <span class="value" :class="getLDLClass(examData.ldl)">{{ examData.ldl }} mmol/L</span>
            </div>
          </div>
        </div>

        <div class="subsection" v-if="hasLiverData">
          <h3>肝功能</h3>
          <div class="info-grid">
            <div class="info-item" v-if="examData.alt">
              <span class="label">ALT：</span>
              <span class="value" :class="getALTClass(examData.alt)">{{ examData.alt }} U/L</span>
            </div>
            <div class="info-item" v-if="examData.ast">
              <span class="label">AST：</span>
              <span class="value" :class="getASTClass(examData.ast)">{{ examData.ast }} U/L</span>
            </div>
            <div class="info-item" v-if="examData.totalBilirubin">
              <span class="label">总胆红素：</span>
              <span class="value" :class="getBilirubinClass(examData.totalBilirubin)">{{ examData.totalBilirubin }} μmol/L</span>
            </div>
            <div class="info-item" v-if="examData.albumin">
              <span class="label">白蛋白：</span>
              <span class="value" :class="getAlbuminClass(examData.albumin)">{{ examData.albumin }} g/L</span>
            </div>
          </div>
        </div>

        <div class="subsection" v-if="hasKidneyData">
          <h3>肾功能</h3>
          <div class="info-grid">
            <div class="info-item" v-if="examData.creatinine">
              <span class="label">肌酐：</span>
              <span class="value" :class="getCreatinineClass(examData.creatinine)">{{ examData.creatinine }} μmol/L</span>
            </div>
            <div class="info-item" v-if="examData.bun">
              <span class="label">尿素氮：</span>
              <span class="value" :class="getBUNClass(examData.bun)">{{ examData.bun }} mmol/L</span>
            </div>
            <div class="info-item" v-if="examData.uricAcid">
              <span class="label">尿酸：</span>
              <span class="value" :class="getUricAcidClass(examData.uricAcid)">{{ examData.uricAcid }} μmol/L</span>
            </div>
          </div>
        </div>

        <div class="subsection" v-if="hasBloodData">
          <h3>血常规</h3>
          <div class="info-grid">
            <div class="info-item" v-if="examData.hemoglobin">
              <span class="label">血红蛋白：</span>
              <span class="value" :class="getHemoglobinClass(examData.hemoglobin)">{{ examData.hemoglobin }} g/L</span>
            </div>
            <div class="info-item" v-if="examData.wbc">
              <span class="label">白细胞：</span>
              <span class="value" :class="getWBCClass(examData.wbc)">{{ examData.wbc }} ×10⁹/L</span>
            </div>
            <div class="info-item" v-if="examData.rbc">
              <span class="label">红细胞：</span>
              <span class="value" :class="getRBCClass(examData.rbc)">{{ examData.rbc }} ×10¹²/L</span>
            </div>
            <div class="info-item" v-if="examData.platelets">
              <span class="label">血小板：</span>
              <span class="value" :class="getPlateletsClass(examData.platelets)">{{ examData.platelets }} ×10⁹/L</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 辅助检查 -->
      <div class="section" v-if="hasAuxData">
        <h2 class="section-title">📸 辅助检查</h2>
        
        <div class="subsection" v-if="hasImagingData">
          <h3>影像学检查</h3>
          <div v-if="examData.chestXray" class="aux-item">
            <strong>胸部X光：</strong>
            <p>{{ examData.chestXray }}</p>
          </div>
          <div v-if="examData.abdominalUltrasound" class="aux-item">
            <strong>腹部超声：</strong>
            <p>{{ examData.abdominalUltrasound }}</p>
          </div>
          <div v-if="examData.ecg" class="aux-item">
            <strong>心电图：</strong>
            <p>{{ examData.ecg }}</p>
          </div>
          <div v-if="examData.otherImaging" class="aux-item">
            <strong>其他影像：</strong>
            <p>{{ examData.otherImaging }}</p>
          </div>
        </div>

        <div class="subsection" v-if="hasUrineData">
          <h3>尿常规</h3>
          <div class="info-grid">
            <div class="info-item" v-if="examData.urineProtein">
              <span class="label">尿蛋白：</span>
              <el-tag :type="getUrineProteinTagType(examData.urineProtein)"  size="small">{{ examData.urineProtein }}</el-tag>
            </div>
            <div class="info-item" v-if="examData.urineGlucose">
              <span class="label">尿糖：</span>
              <el-tag :type="getUrineGlucoseTagType(examData.urineGlucose)" size="small">{{ examData.urineGlucose }}</el-tag>
            </div>
            <div class="info-item" v-if="examData.urineBlood">
              <span class="label">尿潜血：</span>
              <el-tag :type="getUrineBloodTagType(examData.urineBlood)" size="small">{{ examData.urineBlood }}</el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 医生建议 -->
      <div class="section" v-if="examData.doctorAdvice || examData.healthGrade">
        <h2 class="section-title">💉 健康评估与建议</h2>
        <div v-if="examData.healthGrade" class="health-grade">
          <strong>健康等级：</strong>
          <el-tag :type="getGradeTagType(examData.healthGrade)" size="large">
            {{ getGradeLabel(examData.healthGrade) }}
          </el-tag>
        </div>
        <div v-if="examData.doctorAdvice" class="doctor-advice">
          <strong>医生建议：</strong>
          <p>{{ examData.doctorAdvice }}</p>
        </div>
      </div>

      <!-- 备注 -->
      <div class="section" v-if="examData.remarks">
        <h2 class="section-title">📝 备注</h2>
        <p class="remark-text">{{ examData.remarks }}</p>
      </div>

      <!-- 报告生成信息 -->
      <div class="report-footer">
        <p>报告生成时间：{{ new Date().toLocaleString('zh-CN') }}</p>
        <p v-if="examData.createTime">记录创建时间：{{ fmtDate(examData.createTime) }}</p>
      </div>
    </div>

    <!-- 数据加载 -->
    <div v-else class="loading">
      <el-empty description="加载报告中..." />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const examData = ref(null)
const isExporting = ref(false)
const reportRef = ref(null)
const isLoading = ref(false)

const hasLifestyleData = computed(() => {
  if (!examData.value) return false
  const d = examData.value
  return !!(d.smoking || d.drinking || d.exercise || d.sleepQuality)
})

const hasHistoryData = computed(() => {
  if (!examData.value) return false
  const d = examData.value
  return !!(d.medicalHistory || d.familyHistory || d.allergyHistory)
})

const hasVisionData = computed(() => {
  if (!examData.value) return false
  const d = examData.value
  return !!(d.visionLeft || d.visionRight || d.hearing)
})

const hasPhysicalData = computed(() => {
  if (!examData.value) return false
  const d = examData.value
  // 只要有任何一个体格检查字段不是null/undefined就显示
  return !!(d.height || d.weight || d.bmi || d.waistCircumference || d.hipCircumference ||
    d.temperature || d.heartRate || d.spo2 ||
    (d.bloodPressureSystolic && d.bloodPressureDiastolic) ||
    d.visionLeft || d.visionRight || d.hearing)
})

const hasLabData = computed(() => {
  if (!examData.value) return false
  const d = examData.value
  // 只有当至少有一个实验室检查字段非空
  return !!(d.fastingBloodGlucose || d.postprandialGlucose || 
    d.hba1c || d.totalCholesterol || 
    d.triglycerides || d.hdl || d.ldl ||
    d.alt || d.ast || d.totalBilirubin ||
    d.albumin || d.creatinine || d.bun || 
    d.uricAcid || d.hemoglobin || d.wbc || 
    d.rbc || d.platelets)
})

const hasLipidData = computed(() => {
  if (!examData.value) return false
  const d = examData.value
  return !!(d.totalCholesterol || d.triglycerides || d.hdl || d.ldl)
})

const hasLiverData = computed(() => {
  if (!examData.value) return false
  const d = examData.value
  return !!(d.alt || d.ast || d.totalBilirubin || d.albumin)
})

const hasKidneyData = computed(() => {
  if (!examData.value) return false
  const d = examData.value
  return !!(d.creatinine || d.bun || d.uricAcid)
})

const hasBloodData = computed(() => {
  if (!examData.value) return false
  const d = examData.value
  return !!(d.hemoglobin || d.wbc || d.rbc || d.platelets)
})

const hasImagingData = computed(() => {
  if (!examData.value) return false
  const d = examData.value
  return !!(d.chestXray || d.abdominalUltrasound || d.ecg || d.otherImaging)
})

const hasUrineData = computed(() => {
  if (!examData.value) return false
  const d = examData.value
  return !!(d.urineProtein || d.urineGlucose || d.urineBlood)
})

const hasAuxData = computed(() => {
  return hasImagingData.value || hasUrineData.value
})

const fmtDate = (t) => {
  if (!t) return '—'
  return new Date(t).toLocaleDateString('zh-CN')
}

const maskIdCard = (idCard) => {
  if (!idCard || idCard.length < 8) return idCard
  return idCard.substring(0, 4) + '****' + idCard.substring(idCard.length - 4)
}

// ===== BMI 相关 =====
const getBMILevel = (bmi) => {
  const v = parseFloat(bmi)
  if (v < 18.5) return 'low'
  if (v < 24) return 'normal'
  if (v < 28) return 'high'
  return 'critical'
}

const getBMIClass = (bmi) => {
  const v = parseFloat(bmi)
  if (v < 18.5) return 'text-blue'
  if (v < 24) return 'text-green'
  if (v < 28) return 'text-orange'
  return 'text-red'
}

const getBMILabel = (bmi) => {
  const v = parseFloat(bmi)
  if (v < 18.5) return '偏瘦'
  if (v < 24) return '正常体重'
  if (v < 28) return '超重'
  return '肥胖'
}

// ===== 血压相关 =====
const getBPLevel = (systolic, diastolic) => {
  const s = Number(systolic), d = Number(diastolic)
  if (s < 120 && d < 80) return 'normal'
  if (s < 130 && d < 80) return 'elevated'
  if (s < 140 || d < 90) return 'high1'
  return 'high2'
}

const getBPClass = (systolic, diastolic) => {
  const s = Number(systolic), d = Number(diastolic)
  if (s < 120 && d < 80) return 'text-green'
  if (s < 130 && d < 80) return 'text-blue'
  if (s < 140 || d < 90) return 'text-orange'
  return 'text-red'
}

const getBPLabel = (systolic, diastolic) => {
  const s = Number(systolic), d = Number(diastolic)
  if (s < 120 && d < 80) return '✓ 正常血压'
  if (s < 130 && d < 80) return '血压正常高值'
  if (s < 140 || d < 90) return '⚠ 1级高血压'
  return '⛔ 2级及以上高血压'
}

// ===== 血糖相关 =====
const getGlucoseClass = (glucose) => {
  const v = Number(glucose)
  if (v < 6.1) return 'text-green'
  if (v < 7.0) return 'text-orange'
  return 'text-red'
}

const getPostprandialClass = (glucose) => {
  const v = Number(glucose)
  if (v < 7.8) return 'text-green'
  if (v < 11.1) return 'text-orange'
  return 'text-red'
}

const getHbA1cClass = (hba1c) => {
  const v = Number(hba1c)
  if (v < 5.7) return 'text-green'
  if (v < 6.5) return 'text-orange'
  return 'text-red'
}

// ===== 血脂相关 =====
const getCholesterolClass = (chol) => {
  const v = Number(chol)
  if (v < 5.18) return 'text-green'
  if (v < 6.19) return 'text-blue'
  return 'text-red'
}

const getTriglyceridesClass = (tg) => {
  const v = Number(tg)
  if (v < 1.7) return 'text-green'
  return 'text-red'
}

const getHDLClass = (hdl) => {
  const v = Number(hdl)
  if (v > 1.04) return 'text-green'
  return 'text-red'
}

const getLDLClass = (ldl) => {
  const v = Number(ldl)
  if (v < 3.37) return 'text-green'
  if (v < 4.14) return 'text-blue'
  return 'text-red'
}

// ===== 肝功能相关 =====
const getALTClass = (alt) => {
  const v = Number(alt)
  if (v > 40) return 'text-red'
  return 'text-green'
}

const getASTClass = (ast) => {
  const v = Number(ast)
  if (v > 40) return 'text-red'
  return 'text-green'
}

const getBilirubinClass = (bili) => {
  const v = Number(bili)
  if (v > 20) return 'text-red'
  return 'text-green'
}

const getAlbuminClass = (alb) => {
  const v = Number(alb)
  if (v >= 35 && v <= 50) return 'text-green'
  return 'text-red'
}

// ===== 肾功能相关 =====
const getCreatinineClass = (creat) => {
  const v = Number(creat)
  if (v > 130) return 'text-red'
  return 'text-green'
}

const getBUNClass = (bun) => {
  const v = Number(bun)
  if (v > 7.1) return 'text-red'
  return 'text-green'
}

const getUricAcidClass = (ua) => {
  const v = Number(ua)
  if (v > 420) return 'text-red'
  return 'text-green'
}

// ===== 血常规相关 =====
const getHemoglobinClass = (hb) => {
  const v = Number(hb)
  if (v >= 120 && v <= 160) return 'text-green'
  return 'text-red'
}

const getWBCClass = (wbc) => {
  const v = Number(wbc)
  if (v >= 4.5 && v <= 11) return 'text-green'
  return 'text-red'
}

const getRBCClass = (rbc) => {
  const v = Number(rbc)
  if (v >= 4 && v <= 5.5) return 'text-green'
  return 'text-red'
}

const getPlateletsClass = (plt) => {
  const v = Number(plt)
  if (v >= 125 && v <= 350) return 'text-green'
  return 'text-red'
}

// ===== 生命体征相关 =====
const getTemperatureClass = (temp) => {
  const v = Number(temp)
  if (v >= 36.3 && v <= 37.2) return 'text-green'
  if (v >= 37.3 && v <= 38) return 'text-orange'
  return 'text-red'
}

const getHeartRateClass = (hr) => {
  const v = Number(hr)
  if (v >= 60 && v <= 100) return 'text-green'
  return 'text-orange'
}

const getSPO2Class = (spo2) => {
  const v = Number(spo2)
  if (v >= 95) return 'text-green'
  if (v >= 90) return 'text-orange'
  return 'text-red'
}

// ===== 尿常规相关 =====
const getUrineProteinTagType = (val) => val === '-' ? 'success' : 'warning'
const getUrineGlucoseTagType = (val) => val === '-' ? 'success' : 'warning'
const getUrineBloodTagType = (val) => val === '-' ? 'success' : 'warning'

// ===== 生活习惯相关 =====
const getSmokingTagType = (smoking) => {
  if (smoking.includes('不吸') || smoking.includes('已戒')) return 'success'
  if (smoking.includes('偶尔')) return 'warning'
  return 'danger'
}

const getDrinkingTagType = (drinking) => {
  if (drinking.includes('不饮') || drinking.includes('已戒')) return 'success'
  if (drinking.includes('偶尔')) return 'warning'
  return 'danger'
}

const getSleepTagType = (sleep) => {
  if (sleep === '良好') return 'success'
  if (sleep === '一般') return 'warning'
  return 'danger'
}

// ===== 健康等级相关 =====
const getGradeLabel = (grade) => {
  const labels = { A: 'A 健康', B: 'B 基本健康', C: 'C 存在异常', D: 'D 需要干预' }
  return labels[grade] || grade
}

const getGradeTagType = (grade) => {
  const types = { A: 'success', B: 'info', C: 'warning', D: 'danger' }
  return types[grade] || 'info'
}

const goBack = () => {
  router.back()
}

const handlePrint = () => {
  window.print()
}

const buildPrintableWindow = () => {
  if (!reportRef.value) return null

  const styles = [...document.querySelectorAll('style')].map((s) => s.innerHTML).join('\n')
  const printable = window.open('', '_blank', 'width=900,height=800')
  if (!printable) {
    ElMessage.error('浏览器阻止了打印窗口，请允许弹窗后重试')
    return null
  }

  printable.document.write(`<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>健康体检报告</title>
<style>
  @page { margin: 15mm; }
  body { margin: 0; padding: 20px; background: white; font-family: Arial, sans-serif; }
  img { max-width: 100%; }
  ${styles}
</style>
</head><body>
${reportRef.value.outerHTML}
</body></html>`)
  printable.document.close()
  return printable
}

const exportPDF = async () => {
  isExporting.value = true
  try {
    const printable = buildPrintableWindow()
    if (!printable) return
    printable.focus()
    await new Promise(resolve => setTimeout(resolve, 300))
    printable.print()
    setTimeout(() => printable.close(), 500)
    ElMessage.success('请在打印窗口中选择“另存为 PDF”完成导出')
  } catch (error) {
    ElMessage.error('导出PDF失败：' + error.message)
  } finally {
    isExporting.value = false
  }
}

onMounted(async () => {
  // 从localStorage获取体检ID
  const data = localStorage.getItem('health_exam_data')
  let examId = null
  let fallbackData = null
  
  if (data) {
    try {
      fallbackData = JSON.parse(data)
      examId = fallbackData.id
      console.log('从localStorage中获取的备用数据：', fallbackData)
      localStorage.removeItem('health_exam_data')
      localStorage.removeItem('health_exam_view_mode')
    } catch (e) {
      console.error('localStorage数据解析失败', e)
    }
  }
  
  if (!examId) {
    ElMessage.warning('缺少报告数据')
    router.back()
    return
  }
  
  // 优先从API加载完整的体检数据
  isLoading.value = true
  try {
    const res = await axios.get(`/api/health-exam/${examId}`)
    console.log('API返回的完整数据：', res.data)
    if (res.data.code === 200 && res.data.data) {
      examData.value = res.data.data
      console.log('✓ 成功从API加载完整数据')
    } else if (fallbackData) {
      // API加载失败时使用localStorage中的备用数据
      examData.value = fallbackData
      console.log('⚠ 使用localStorage备用数据')
      ElMessage.info('使用本地缓存数据')
    } else {
      ElMessage.error('加载报告数据失败')
      router.back()
    }
  } catch (error) {
    console.error('从API加载数据失败', error)
    if (fallbackData) {
      examData.value = fallbackData
      console.log('⚠ 使用localStorage备用数据（API失败）')
      ElMessage.info('使用本地缓存数据')
    } else {
      ElMessage.error('加载报告数据失败：' + error.message)
      router.back()
    }
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
@import '@/styles/tcm-shared.css';

.health-report-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(135deg, #faf3e0 0%, #fef9f0 100%);
  overflow: hidden;
}

.report-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background: #f5e8c8;
  border-bottom: 2px solid #e8d5a0;
  flex-shrink: 0;
}

.report-header h1 {
  flex: 1;
  text-align: center;
  font-size: 20px;
  font-weight: 700;
  color: #5a2d00;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.report-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  border-left: 4px solid #c8a020;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #5a2d00;
  margin: 0 0 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8d5a0;
}

.subsection {
  margin-bottom: 16px;
}

.subsection h3 {
  font-size: 13px;
  font-weight: 600;
  color: #8b6030;
  margin: 0 0 10px;
  padding-left: 8px;
  border-left: 2px solid #c8a020;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #faf3e0;
  border-radius: 4px;
  font-size: 13px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item .label {
  font-weight: 600;
  color: #8b6030;
  min-width: 80px;
}

.info-item .value {
  color: #3d2b10;
  flex: 1;
}

.value-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 12px;
  border-radius: 6px;
  text-align: center;
  min-width: 100px;
  font-weight: 600;
}

.value-card .value-label {
  font-size: 11px;
  color: #666;
  margin-bottom: 4px;
}

.value-card .value-number {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 2px;
}

.value-card .value-status {
  font-size: 12px;
  margin-top: 4px;
}

.bmi-low {
  background: #e6f7ff;
  border-left: 3px solid #1890ff;
  color: #1890ff;
}

.bmi-normal {
  background: #f6ffed;
  border-left: 3px solid #52c41a;
  color: #52c41a;
}

.bmi-high {
  background: #fff7e6;
  border-left: 3px solid #fa8c16;
  color: #fa8c16;
}

.bmi-critical {
  background: #fff1f0;
  border-left: 3px solid #ff4d4f;
  color: #ff4d4f;
}

.bp-normal {
  background: #f6ffed;
  border-left: 3px solid #52c41a;
  color: #52c41a;
}

.bp-elevated {
  background: #e6f7ff;
  border-left: 3px solid #1890ff;
  color: #1890ff;
}

.bp-high1 {
  background: #fff7e6;
  border-left: 3px solid #fa8c16;
  color: #fa8c16;
}

.bp-high2 {
  background: #fff1f0;
  border-left: 3px solid #ff4d4f;
  color: #ff4d4f;
}

.text-blue { color: #409eff; }
.text-green { color: #67c23a; }
.text-orange { color: #e6a23c; }
.text-red { color: #f56c6c; }
.text-muted { color: #bbb; }

.lifestyle-tag {
  margin-left: 8px;
}

.history-item {
  margin: 12px 0;
  padding: 12px;
  background: #faf3e0;
  border-radius: 4px;
  border-left: 3px solid #c8a020;
}

.history-item strong {
  color: #8b6030;
  display: block;
  margin-bottom: 6px;
}

.history-item p {
  margin: 0;
  color: #3d2b10;
  line-height: 1.6;
}

.aux-item {
  margin: 12px 0;
  padding: 12px;
  background: #faf3e0;
  border-radius: 4px;
  border-left: 3px solid #c8a020;
}

.aux-item strong {
  color: #8b6030;
  display: block;
  margin-bottom: 6px;
}

.aux-item p {
  margin: 0;
  color: #3d2b10;
  line-height: 1.6;
}

.health-grade {
  margin-bottom: 12px;
}

.doctor-advice,
.remark-text {
  margin: 8px 0;
  padding: 12px;
  background: #faf3e0;
  border-radius: 4px;
  line-height: 1.6;
  color: #3d2b10;
}

.report-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e8d5a0;
  margin-top: 24px;
  color: #8b6030;
  font-size: 12px;
  line-height: 1.8;
}

@media print {
  .report-header {
    display: none;
  }
  .report-content {
    padding: 0;
  }
  .section {
    page-break-inside: avoid;
    box-shadow: none;
    border: 1px solid #e8d5a0;
  }
}
</style>
