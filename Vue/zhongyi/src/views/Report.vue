<template>
  <div class="report-container">
    <!-- 返回按钮 -->
    <div class="header">
      <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
      <h1>{{ reportTitle }}</h1>
      <div class="completion-badge">
        <span v-if="completionPercentage < 100" class="badge incomplete">
          {{ completionPercentage }}% 完成度
        </span>
        <span v-else class="badge complete">✓ 四诊完整</span>
      </div>
      <div class="header-buttons">
        <el-button type="primary" @click="exportPDF" :loading="isExporting" icon="Download">
          导出PDF
        </el-button>
        <el-button @click="handlePrint" icon="Printer">
          打印
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-wrapper">
      <div class="loading-card">
        <div class="glow glow-blue"></div>
        <div class="glow glow-green"></div>
        <div class="pulse-bar">
          <svg viewBox="0 0 400 60" preserveAspectRatio="none">
            <polyline class="pulse-line" points="0,30 60,30 80,5 95,55 110,30 150,30 170,18 185,42 200,30 260,30 275,8 292,52 308,30 400,30"/>
          </svg>
        </div>
        <div class="loading-body">
          <div class="taiji-wrap">
            <div class="taiji-ring ring-outer"></div>
            <div class="taiji-ring ring-mid"></div>
            <div class="taiji-core"><span>诊</span></div>
            <div class="taiji-orbit"><div class="orbit-dot"></div></div>
          </div>
          <h2 class="loading-title">四诊合参 · 智慧分析中</h2>
          <p class="loading-sub">正在融合望闻问切数据，调用 AI 引擎生成综合诊断建议</p>
          <div class="steps">
            <div class="step" v-for="(step, i) in steps" :key="i" :class="step.state">
              <div class="step-icon">
                <span class="step-char">{{ step.char }}</span>
                <div class="step-spinner" v-if="step.state === 'active'"></div>
                <svg class="step-check" v-if="step.state === 'done'" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
              <span class="step-label">{{ step.label }}</span>
            </div>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: progressWidth }"></div>
            <div class="progress-glow" :style="{ left: progressWidth }"></div>
          </div>
          <p class="progress-text">{{ progressText }}</p>
          <p class="loading-tip">
            <span class="tip-dot"></span>
            AI 正在结合中医理论进行辨证分析，请稍候...
          </p>
        </div>
      </div>
    </div>

    <!-- 报告内容 -->
    <div v-else-if="reportData" class="report-content" ref="reportRef">

      <!-- ===== 机构抬头（读取报告设置）===== -->
      <div v-if="reportSettings.orgName" class="org-header">
        <div class="org-name">{{ reportSettings.orgName }}</div>
        <div class="org-sub">四诊合参体质辨识报告</div>
        <div class="org-info" v-if="reportSettings.orgAddress || reportSettings.orgPhone">
          <span v-if="reportSettings.orgAddress">📍 {{ reportSettings.orgAddress }}</span>
          <span v-if="reportSettings.orgPhone">📞 {{ reportSettings.orgPhone }}</span>
        </div>
        <div class="org-divider"></div>
      </div>

      <!-- 患者信息章节 -->
      <section class="report-section patient-info">
        <h2>患者信息</h2>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="姓名">{{ reportData.patientInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ reportData.patientInfo.gender }}</el-descriptions-item>
          <el-descriptions-item label="年龄">{{ reportData.patientInfo.age || '' }}岁</el-descriptions-item>
          <el-descriptions-item label="生日">{{ reportData.patientInfo.birthday || '' }}</el-descriptions-item>
          <el-descriptions-item label="住址" :span="3">{{ reportData.patientInfo.address }}</el-descriptions-item>
        </el-descriptions>
      </section>

      <!-- 四诊初步诊断章节 -->
      <section class="report-section diagnosis">
        <h2>四诊初步诊断</h2>

        <div class="diagnosis-item">
          <h3>望诊（舌象分析）</h3>
          <el-card>
            <div v-if="reportData.diagnosis.wang && reportData.diagnosis.wang.imageUrl" class="diagnosis-image">
              <img :src="resolveImageUrl(reportData.diagnosis.wang.imageUrl)" alt="舌象图片" style="max-width: 100%; height: auto;" />
              <p><strong>舌苔图</strong></p>
            </div>
            <p class="diagnosis-result">
              {{ reportData.diagnosis.wang ? reportData.diagnosis.wang.result : '暂未进行舌象检查，请补充望诊数据以获得更准确的诊断。' }}
            </p>
          </el-card>
        </div>

        <div class="diagnosis-item">
          <h3>闻诊（体质诊断）</h3>
          <el-card>
            <el-row v-if="reportData.diagnosis.wen_audio" :gutter="20">
              <el-col :span="12">
                <div><strong>诊断结论：</strong>{{ reportData.diagnosis.wen_audio.conclusion }}</div>
                <div v-if="reportData.diagnosis.wen_audio.confidence">
                  <strong>置信度：</strong>{{ (reportData.diagnosis.wen_audio.confidence * 100).toFixed(1) }}%
                </div>
              </el-col>
              <el-col :span="12">
                <div v-if="reportData.diagnosis.wen_audio.tags">
                  <strong>体质标签：</strong>
                  <el-tag v-for="tag in reportData.diagnosis.wen_audio.tags" :key="tag" effect="light" class="tag">{{ tag }}</el-tag>
                </div>
              </el-col>
            </el-row>
            <div v-else>暂未进行声音分析，请补充闻诊数据。</div>
          </el-card>
        </div>

        <div class="diagnosis-item">
          <h3>问诊（症状问卷）</h3>
          <el-card>
            <p>{{ reportData.diagnosis.wen_questionnaire ? reportData.diagnosis.wen_questionnaire.conclusion : '暂未进行症状问卷调查，请补充问诊数据。' }}</p>
          </el-card>
        </div>

        <div class="diagnosis-item">
          <h3>切诊（脉搏检测）</h3>
          <el-card>
            <el-row v-if="reportData.diagnosis.qie" :gutter="20">
              <el-col :span="12">
                <div><strong>心率：</strong>{{ reportData.diagnosis.qie.heartRate }}<span class="unit">bpm</span></div>
                <div><strong>血氧：</strong>{{ reportData.diagnosis.qie.spo2 }}<span class="unit">%</span></div>
              </el-col>
              <el-col :span="12">
                <div><strong>信号有效率：</strong>{{ reportData.diagnosis.qie.validRate }}<span class="unit">%</span></div>
                <div><strong>采样数：</strong>{{ reportData.diagnosis.qie.sampleCount }}</div>
              </el-col>
            </el-row>
            <div v-if="reportData.diagnosis.qie && reportData.diagnosis.qie.tcmSuggestion" class="tcm-suggestion">
              <strong>中医建议：</strong>
              <p>{{ reportData.diagnosis.qie.tcmSuggestion }}</p>
            </div>
            <div v-else-if="!reportData.diagnosis.qie">暂未进行脉搏检测，请补充切诊数据。</div>
          </el-card>
        </div>
      </section>

      <!-- 综合诊断建议章节 -->
      <section class="report-section synthesis">
        <h2>综合诊断建议</h2>
        <el-card shadow="hover">
          <div class="synthesis-content" v-html="reportData.synthesis ? markdownToHtml(reportData.synthesis) : '暂无综合诊断建议，请确保所有四诊数据完整。'"></div>
        </el-card>
      </section>

      <section class="report-footer">
        <p>报告生成时间：{{ formatDate(reportData.createdAt) }}</p>
        <p class="disclaimer">
          {{ reportSettings.disclaimer || '本报告仅供参考，请在医生指导下使用。' }}
        </p>
        <div class="footer-extra" v-if="reportSettings.doctorName || reportSettings.validityNote">
          <span v-if="reportSettings.doctorName">签发医师：{{ reportSettings.doctorName }}</span>
          <span v-if="reportSettings.validityNote">{{ reportSettings.validityNote }}</span>
        </div>
        <div class="footer-actions">
          <el-button type="primary" size="large" @click="goHome" icon="Home">返回首页</el-button>
        </div>
      </section>
    </div>

    <!-- 无数据状态 -->
    <div v-else class="no-data">
      <el-empty description="未找到报告数据" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import axios from "axios";
import html2pdf from "html2pdf.js";
import { marked } from "marked";

const router = useRouter();
const route = useRoute();

const reportData = ref(null);
const isLoading = ref(false);
const isExporting = ref(false);
const reportRef = ref(null);

const reportTitle = ref("四诊合参诊断报告");
const completionPercentage = ref(100);

// ===== 读取报告设置（localStorage）=====
const reportSettings = computed(() => {
  try {
    const saved = localStorage.getItem("report_settings");
    return saved ? JSON.parse(saved) : {};
  } catch { return {}; }
});

const calculateCompletion = () => {
  if (!reportData.value || !reportData.value.diagnosis) {
    completionPercentage.value = 0;
    return;
  }
  const diagnosis = reportData.value.diagnosis;
  let count = 0;
  ["wang", "wen_audio", "wen_questionnaire", "qie"].forEach(t => {
    if (diagnosis[t]) count++;
  });
  completionPercentage.value = Math.round((count / 4) * 100);
  if (count === 4)      reportTitle.value = "四诊合参诊断报告";
  else if (count === 1) reportTitle.value = `单板块诊断报告 - ${getCompletedType(diagnosis)}`;
  else                  reportTitle.value = `部分诊断报告 (${count}/4板块)`;
};

const getCompletedType = (diagnosis) => {
  if (diagnosis.wang) return "望诊";
  if (diagnosis.wen_audio) return "闻诊";
  if (diagnosis.wen_questionnaire) return "问诊";
  if (diagnosis.qie) return "切诊";
  return "诊断";
};

// ===== 加载动画 =====
const steps = ref([
  { char: "望", label: "舌象分析", state: "pending" },
  { char: "闻", label: "声纹识别", state: "pending" },
  { char: "问", label: "问卷解析", state: "pending" },
  { char: "切", label: "脉象推理", state: "pending" },
]);

const progressWidth = ref("0%");
const progressText = ref("正在初始化...");
let stepTimer = null;
let progressTimer = null;

const progressStages = [
  { width: "15%", text: "正在读取四诊数据..." },
  { width: "30%", text: "正在构建辨证分析模型..." },
  { width: "48%", text: "AI 正在分析体质与证型..." },
  { width: "65%", text: "正在生成调理建议..." },
  { width: "80%", text: "正在整合诊断结论..." },
  { width: "92%", text: "即将完成，请稍候..." },
];

const startLoadingAnimation = () => {
  let stageIdx = 0;
  let stepIdx = 0;
  progressTimer = setInterval(() => {
    if (stageIdx < progressStages.length) {
      const s = progressStages[stageIdx++];
      progressWidth.value = s.width;
      progressText.value = s.text;
    }
  }, 3500);
  stepTimer = setInterval(() => {
    steps.value.forEach((s, i) => {
      if (i < stepIdx) s.state = "done";
      else if (i === stepIdx) s.state = "active";
      else s.state = "pending";
    });
    if (stepIdx < steps.value.length - 1) stepIdx++;
  }, 4000);
};

const stopLoadingAnimation = () => {
  clearInterval(progressTimer);
  clearInterval(stepTimer);
  steps.value.forEach(s => s.state = "done");
  progressWidth.value = "100%";
  progressText.value = "分析完成！";
};

onUnmounted(() => {
  clearInterval(progressTimer);
  clearInterval(stepTimer);
});

// ===== 数据获取 =====
onMounted(async () => {
  const patientId = route.query.id || localStorage.getItem("current_patient_id");
  const completedTypesParam = route.query.completedTypes;
  if (!patientId) {
    ElMessage.error("缺少患者ID，请先完成诊断操作");
    goBack();
    return;
  }
  if (completedTypesParam) localStorage.setItem("_temp_completedTypes", completedTypesParam);
  await fetchReportData(patientId);
});

const getCompletedTypes = () => localStorage.getItem("_temp_completedTypes") || "";

const fetchReportData = async (patientId) => {
  isLoading.value = true;
  startLoadingAnimation();
  try {
    const idCard = localStorage.getItem("current_patient_idCard") || "";
    const response = await axios.get("/api/report/get-diagnosis", {
      params: { patientId: Number(patientId), idCard }
    });
    if (response.data.code !== 200 && !response.data.success) {
      ElMessage.error(response.data.msg || "获取报告失败");
      return;
    }
    if (!response.data.data.synthesis) {
      await generateReport(patientId);
    } else {
      stopLoadingAnimation();
      await new Promise(r => setTimeout(r, 600));
      reportData.value = response.data.data;
      calculateCompletion();
    }
  } catch (error) {
    ElMessage.error("获取报告失败：" + error.message);
  } finally {
    isLoading.value = false;
  }
};

const generateReport = async (patientId) => {
  try {
    const idCard = localStorage.getItem("current_patient_idCard") || "";
    const completedTypes = getCompletedTypes();
    const response = await axios.post("/api/report/generate", {
      patientId: Number(patientId),
      idCard,
      ...(completedTypes ? { completedTypes } : {})
    });
    if (response.data.code === 200 || response.data.success) {
      stopLoadingAnimation();
      await new Promise(r => setTimeout(r, 600));
      reportData.value = response.data.data;
      calculateCompletion();
      ElMessage.success("报告生成成功");
    } else {
      ElMessage.error(response.data.msg || "报告生成失败");
    }
  } catch (error) {
    ElMessage.error("生成报告失败：" + error.message);
  }
};

const exportPDF = async () => {
  if (!reportRef.value) { ElMessage.error("报告数据加载失败"); return; }
  isExporting.value = true;
  const header = document.querySelector(".header");
  if (header) header.style.display = "none";
  const footerActions = document.querySelector(".footer-actions");
  if (footerActions) footerActions.style.display = "none";

  const imgs = reportRef.value.querySelectorAll("img");
  const originalSrcs = [];
  await Promise.all([...imgs].map(async (img, i) => {
    originalSrcs[i] = img.src;
    if (!img.src || img.src.startsWith("data:")) return;
    try {
      const res = await fetch(img.src);
      const blob = await res.blob();
      await new Promise(resolve => {
        const reader = new FileReader();
        reader.onload = () => { img.src = reader.result; resolve(); };
        reader.onerror = () => resolve();
        reader.readAsDataURL(blob);
      });
    } catch {}
  }));

  const tags = reportRef.value.querySelectorAll(".el-tag");
  tags.forEach(tag => {
    tag.style.cssText += ";display:inline-block;padding:2px 9px;border-radius:4px;font-size:12px;line-height:1.8;background-color:#ecf5ff;color:#409eff;border:1px solid #d9ecff;margin:3px 4px 3px 0;white-space:nowrap;";
  });

  const opt = {
    margin: 10,
    filename: `诊断报告_${reportData.value.patientInfo.name}_${formatDate(reportData.value.createdAt)}.pdf`,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true, allowTaint: false, logging: false },
    jsPDF: { orientation: "portrait", unit: "mm", format: "a4" },
  };

  try {
    await html2pdf().set(opt).from(reportRef.value).save();
    ElMessage.success("PDF 导出成功");
  } catch (e) {
    ElMessage.error("PDF 导出失败：" + e.message);
  } finally {
    imgs.forEach((img, i) => { if (originalSrcs[i]) img.src = originalSrcs[i]; });
    tags.forEach(tag => { tag.style.cssText = ""; });
    if (header) header.style.display = "";
    if (footerActions) footerActions.style.display = "";
    isExporting.value = false;
  }
};

const resolveImageUrl = (url) => {
  if (!url) return "";
  if (url.startsWith("http") || url.startsWith("data:")) return url;
  const normalized = url.replace(/\\/g, "/");
  const marker = "zhongyi_uploads/";
  const idx = normalized.indexOf(marker);
  const relativePath = idx !== -1 ? normalized.slice(idx + marker.length) : normalized.split("/").pop();
  return `/uploads/${relativePath}`;
};

const markdownToHtml = (markdown) => markdown ? marked.parse(markdown) : "";

const formatDate = (timestamp) => {
  if (!timestamp) return "";
  const date = new Date(timestamp);
  return date.toLocaleDateString("zh-CN") + " " + date.toLocaleTimeString("zh-CN");
};

const goBack = () => router.push({ path: "/detect", query: { id: route.query.id } });
const goHome = () => router.push({ path: "/" });
const handlePrint = () => window.print();
</script>

<style scoped>
/* ============ 报告样式 ============ */
.report-container { max-width: 1000px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100vh; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
.header h1 { flex: 1; text-align: center; margin: 0; color: #333; }
.completion-badge { position: absolute; right: 20px; top: 20px; }
.badge { display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 600; letter-spacing: 0.5px; }
.badge.incomplete { background: linear-gradient(135deg, #ffa500, #ff8c00); color: white; }
.badge.complete   { background: linear-gradient(135deg, #67c26a, #40ad50); color: white; }
.header-buttons { display: flex; gap: 10px; }
.report-content { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
.report-section { padding: 30px; border-bottom: 1px solid #eee; }
.report-section:last-child { border-bottom: none; }
.report-section h2 { color: #1e6ba8; font-size: 20px; margin-bottom: 20px; border-bottom: 3px solid #1e6ba8; padding-bottom: 10px; }
.report-section h3 { color: #2c3e50; font-size: 16px; margin-top: 20px; margin-bottom: 15px; }
.diagnosis-item { margin-bottom: 20px; }
.diagnosis-image { text-align: center; margin-bottom: 15px; }
.diagnosis-result { color: #555; line-height: 1.8; margin: 0; }
.tag { margin: 5px 5px 5px 0; }
.unit { color: #999; font-size: 14px; margin-left: 5px; }
.tcm-suggestion { margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee; }
.synthesis-content { line-height: 1.8; color: #333; font-size: 14px; }
.synthesis-content :deep(h3) { color: #1e6ba8; margin-top: 15px; margin-bottom: 10px; }
.synthesis-content :deep(ul), .synthesis-content :deep(ol) { margin: 10px 0; padding-left: 20px; }
.synthesis-content :deep(li) { margin: 5px 0; }
.synthesis-content :deep(strong) { color: #1e6ba8; }
.report-footer { padding: 30px; background: #f9f9f9; text-align: center; color: #999; font-size: 12px; }
.report-footer p { margin: 5px 0; }
.disclaimer { color: #e74c3c; font-size: 11px; }
.footer-actions { margin-top: 20px; }
.footer-actions :deep(.el-button) { min-width: 140px; }
.no-data { padding: 60px 20px; text-align: center; }

/* ===== 机构抬头 ===== */
.org-header {
  text-align: center;
  padding: 28px 30px 20px;
  background: linear-gradient(180deg, #fdf8ef 0%, #fff 100%);
  border-bottom: 1px solid #e8d5a0;
}
.org-name {
  font-size: 22px; font-weight: 700; color: #3d2b10;
  font-family: "Noto Serif SC", "Source Han Serif CN", serif;
  letter-spacing: 3px; margin-bottom: 6px;
}
.org-sub { font-size: 13px; color: #8b6030; letter-spacing: 2px; margin-bottom: 8px; }
.org-info {
  display: flex; justify-content: center; gap: 24px;
  font-size: 12px; color: #9a7040; margin-bottom: 12px;
}
.org-divider {
  height: 2px;
  background: linear-gradient(90deg, transparent, #c8a020 30%, #c8a020 70%, transparent);
  margin: 0 30px;
}
.footer-extra {
  display: flex; justify-content: space-between;
  font-size: 12px; color: #8b6030;
  margin-top: 8px; padding-top: 8px;
  border-top: 1px dashed #e8d5a0;
}

/* ============ 加载动画 ============ */
.loading-wrapper { display: flex; justify-content: center; align-items: flex-start; padding-top: 20px; }
.loading-card { position: relative; width: 100%; max-width: 680px; background: rgba(255,255,255,0.92); backdrop-filter: blur(20px); border-radius: 28px; border: 1px solid rgba(255,255,255,0.8); box-shadow: 0 30px 80px rgba(30,107,168,0.15); overflow: hidden; }
.glow { position: absolute; border-radius: 50%; filter: blur(60px); opacity: 0.18; pointer-events: none; }
.glow-blue { width: 300px; height: 300px; background: #409eff; top: -80px; right: -60px; animation: glowPulse 4s ease-in-out infinite alternate; }
.glow-green { width: 250px; height: 250px; background: #67c23a; bottom: -60px; left: -40px; animation: glowPulse 5s ease-in-out infinite alternate-reverse; }
@keyframes glowPulse { 0% { opacity: 0.12; transform: scale(1); } 100% { opacity: 0.25; transform: scale(1.15); } }
.pulse-bar { width: 100%; height: 56px; background: linear-gradient(90deg, #1e6ba8 0%, #409eff 50%, #67c23a 100%); display: flex; align-items: center; }
.pulse-bar svg { width: 100%; height: 56px; }
.pulse-line { fill: none; stroke: rgba(255,255,255,0.85); stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; stroke-dasharray: 700; stroke-dashoffset: 700; animation: drawPulse 2.2s ease-out forwards, pulseScan 3s ease-in-out 2.2s infinite; }
@keyframes drawPulse { to { stroke-dashoffset: 0; } }
@keyframes pulseScan { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
.loading-body { padding: 36px 40px 40px; display: flex; flex-direction: column; align-items: center; gap: 0; }
.taiji-wrap { position: relative; width: 96px; height: 96px; margin-bottom: 28px; }
.taiji-ring { position: absolute; border-radius: 50%; border-style: solid; top: 50%; left: 50%; transform: translate(-50%,-50%); }
.ring-outer { width: 96px; height: 96px; border-width: 2.5px; border-color: #409eff rgba(64,158,255,0.2) rgba(64,158,255,0.2) #409eff; animation: spinCCW 3s linear infinite; }
.ring-mid { width: 70px; height: 70px; border-width: 2px; border-color: rgba(103,194,58,0.3) #67c23a #67c23a rgba(103,194,58,0.3); animation: spinCW 2s linear infinite; }
.taiji-core { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); width: 46px; height: 46px; border-radius: 50%; background: linear-gradient(135deg,#1e6ba8,#409eff); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 20px rgba(64,158,255,0.5); }
.taiji-core span { font-family: "KaiTi","楷体",serif; font-size: 20px; color: white; font-weight: bold; animation: breathe 2.5s ease-in-out infinite; }
.taiji-orbit { position: absolute; width: 96px; height: 96px; top: 0; left: 0; animation: spinCW 2.5s linear infinite; }
.orbit-dot { position: absolute; top: -5px; left: 50%; transform: translateX(-50%); width: 10px; height: 10px; border-radius: 50%; background: #e6a23c; box-shadow: 0 0 8px rgba(230,162,60,0.8); }
@keyframes spinCW  { to { transform: translate(-50%,-50%) rotate(360deg); } }
@keyframes spinCCW { to { transform: translate(-50%,-50%) rotate(-360deg); } }
@keyframes breathe { 0%,100% { transform: scale(1); } 50% { transform: scale(1.12); } }
.loading-title { margin: 0 0 8px; font-size: 22px; font-family: "Source Han Serif CN","Noto Serif SC",serif; color: #1a2a3a; font-weight: 700; letter-spacing: 1px; }
.loading-sub { margin: 0 0 32px; font-size: 13px; color: #7a8da0; text-align: center; line-height: 1.7; }
.steps { display: flex; gap: 16px; margin-bottom: 32px; align-items: flex-start; }
.step { display: flex; flex-direction: column; align-items: center; gap: 8px; transition: opacity 0.5s; }
.step.pending { opacity: 0.35; } .step.active { opacity: 1; } .step.done { opacity: 1; }
.step-icon { position: relative; width: 52px; height: 52px; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
.step.done .step-icon { background: linear-gradient(135deg,#67c23a,#85ce61); box-shadow: 0 4px 16px rgba(103,194,58,0.4); }
.step.active .step-icon { background: linear-gradient(135deg,#1e6ba8,#409eff); box-shadow: 0 4px 20px rgba(64,158,255,0.5); animation: stepPulse 1.5s ease-in-out infinite; }
.step.pending .step-icon { background: #eef2f7; border: 2px solid #dde4ed; }
@keyframes stepPulse { 0%,100% { box-shadow: 0 4px 20px rgba(64,158,255,0.5); } 50% { box-shadow: 0 4px 32px rgba(64,158,255,0.9); } }
.step-char { font-family: "KaiTi","楷体",serif; font-size: 22px; font-weight: bold; color: white; line-height: 1; }
.step.pending .step-char { color: #b0bec5; }
.step-spinner { position: absolute; inset: -4px; border-radius: 20px; border: 2.5px solid transparent; border-top-color: rgba(255,255,255,0.8); border-right-color: rgba(255,255,255,0.4); animation: spin 1s linear infinite; }
.step-check { position: absolute; bottom: -4px; right: -4px; width: 18px; height: 18px; background: white; border-radius: 50%; padding: 2px; stroke: #67c23a; stroke-width: 3; fill: none; stroke-linecap: round; }
@keyframes spin { to { transform: rotate(360deg); } }
.step-label { font-size: 12px; color: #5a6a7a; white-space: nowrap; }
.step.active .step-label { color: #1e6ba8; font-weight: 600; }
.step.done  .step-label { color: #67c23a; font-weight: 600; }
.progress-track { position: relative; width: 100%; height: 8px; background: #eef2f7; border-radius: 100px; overflow: visible; margin-bottom: 10px; }
.progress-fill { height: 100%; border-radius: 100px; background: linear-gradient(90deg,#1e6ba8,#409eff,#67c23a); background-size: 200% 100%; transition: width 2s cubic-bezier(0.4,0,0.2,1); animation: shimmer 2.5s linear infinite; }
.progress-glow { position: absolute; top: 50%; transform: translateY(-50%) translateX(-50%); width: 20px; height: 20px; border-radius: 50%; background: radial-gradient(circle,rgba(64,158,255,0.6) 0%,transparent 70%); transition: left 2s cubic-bezier(0.4,0,0.2,1); pointer-events: none; }
@keyframes shimmer { 0% { background-position: 200% center; } 100% { background-position: -200% center; } }
.progress-text { font-size: 12.5px; color: #8fa3b8; margin: 0 0 24px; text-align: center; }
.loading-tip { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #a0b0c0; background: rgba(64,158,255,0.05); border: 1px solid rgba(64,158,255,0.1); border-radius: 100px; padding: 8px 18px; margin: 0; }
.tip-dot { width: 6px; height: 6px; border-radius: 50%; background: #409eff; flex-shrink: 0; animation: blink 1.4s ease-in-out infinite; }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.2; } }

/* 响应式 */
@media (max-width: 768px) {
  .report-container { padding: 10px; }
  .header { flex-direction: column; gap: 10px; }
  .header h1 { font-size: 18px; margin: 10px 0; }
  .report-section { padding: 20px; }
  .loading-body { padding: 28px 20px 32px; }
  .steps { gap: 10px; }
  .step-icon { width: 44px; height: 44px; border-radius: 13px; }
  .step-char { font-size: 18px; }
}

/* 打印 */
@media print {
  .report-container { background: white; padding: 0; max-width: 100%; }
  .header, .footer-actions, .loading-wrapper { display: none !important; }
  .report-content { box-shadow: none; border-radius: 0; }
  .report-section { border: none; padding: 8px 0; margin: 0; page-break-inside: auto; }
  .report-section h2 { page-break-after: avoid; margin: 10px 0 8px; font-size: 15px; padding-bottom: 3px; border-width: 2px !important; }
  .diagnosis-item { margin-bottom: 8px; page-break-inside: auto; }
  .diagnosis-item h3 { page-break-after: avoid; margin: 8px 0 6px; font-size: 13px; }
  .el-card { box-shadow: none !important; border: 1px solid #ddd; margin: 0; padding: 10px !important; }
  .el-descriptions { font-size: 12px !important; }
  .diagnosis-result, .tcm-suggestion { font-size: 12px; line-height: 1.5; margin: 5px 0; }
  .synthesis-content { font-size: 12px; line-height: 1.5; }
  .synthesis-content :deep(h3) { font-size: 13px; margin: 8px 0 4px; }
  .synthesis-content :deep(ul), .synthesis-content :deep(ol) { margin: 5px 0; padding-left: 15px; }
  .synthesis-content :deep(li) { margin: 2px 0; }
  .report-footer { font-size: 10px; padding: 8px 0; margin-top: 10px; }
  body { background: white; font-size: 12px; }
  .tag { margin: 2px 2px 2px 0 !important; padding: 1px 6px !important; font-size: 11px !important; }
  img { max-width: 150px !important; height: auto !important; }
  .diagnosis-image { page-break-inside: auto; text-align: center; }
  .diagnosis-image p { margin: 3px 0 !important; font-size: 11px; }
  .org-header { padding: 16px 20px 12px; }
  .org-name { font-size: 18px; }
}
</style>