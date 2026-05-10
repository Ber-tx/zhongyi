<template>
  <div class="report-container">
    <!-- 返回按钮 -->
    <div class="header">
      <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
      <h1>{{ reportTitle }}</h1>
      <div class="completion-badge" v-if="!isLoading">
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
        <!-- 实时预览区域：当后端开始返回流式内容时，在等待界面显示逐字输出 -->
        <div v-if="streamRequested || isStreaming || (reportData && reportData.synthesis)" class="live-preview">
          <el-card shadow="hover" class="live-card">
            <div class="live-header">
              <div class="live-title">实时生成预览</div>
                  <div class="live-actions">
                    <span v-if="isStreaming" class="streaming-badge">AI 思考中...</span>
                    <el-button v-if="isStreaming" size="small" type="text" @click="cancelStream">取消</el-button>
                    <el-button v-else size="small" type="primary" @click="viewFullReport">查看完整报告</el-button>
                  </div>
            </div>

            <div class="live-body">
              <div class="preload-patient" v-if="reportData && reportData.patientInfo">
                <div class="pp-row"><strong>患者：</strong>{{ reportData.patientInfo.name }} / {{ reportData.patientInfo.gender }}</div>
                <div class="pp-row"><strong>年龄：</strong>{{ reportData.patientInfo.age || '' }}岁</div>
                <div class="pp-row"><strong>已完成：</strong>
                  <span v-if="reportData.diagnosis?.wang" class="badge-tiny">望</span>
                  <span v-if="reportData.diagnosis?.wen_audio" class="badge-tiny">闻</span>
                  <span v-if="reportData.diagnosis?.wen_questionnaire" class="badge-tiny">问</span>
                  <span v-if="reportData.diagnosis?.qie" class="badge-tiny">切</span>
                </div>
              </div>

              <div class="live-synthesis" v-html="reportData && reportData.synthesis ? markdownToHtml(reportData.synthesis) : (streamRequested ? (reportData ? 'AI 已连接，正在生成内容...' : '正在等待 AI 首段输出...') : '等待 AI 输出...')"></div>
            </div>
          </el-card>
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
        <h2>患者信息：</h2>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="姓名：">{{ reportData.patientInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="性别：">{{ reportData.patientInfo.gender }}</el-descriptions-item>
          <el-descriptions-item label="年龄：">{{ reportData.patientInfo.age || '' }}岁</el-descriptions-item>
          <el-descriptions-item label="生日：">{{ reportData.patientInfo.birthday || '' }}</el-descriptions-item>
          <el-descriptions-item label="住址：" :span="3">{{ reportData.patientInfo.address }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="idCardDisplaySrc" class="report-idcard-card-box">
          <img :src="idCardDisplaySrc" alt="身份证" class="report-idcard-card" />
        </div>
      </section>

      <!-- 四诊初步诊断章节 -->
      <section class="report-section diagnosis">
        <h2>四诊初步诊断</h2>

        <div class="diagnosis-item">
          <h3>望诊（舌象分析）</h3>
          <el-card>
            <div v-if="reportData.diagnosis.wang" class="diagnosis-wang-layout">
              <div v-if="reportData.diagnosis.wang.imageUrl" class="diagnosis-image diagnosis-image-left">
                <img :src="resolveImageUrl(reportData.diagnosis.wang.imageUrl)" alt="舌象图片" />
                <p><strong>舌苔图</strong></p>
              </div>
              <div class="diagnosis-text-block">
                <p class="diagnosis-result">
                  {{ reportData.diagnosis.wang.result }}
                </p>
                <div v-if="showWangSupplementary && wangSupplementaryAnalysis.length" class="supplementary-analysis">
                  <div class="supplementary-title">补充分析</div>
                  <ul>
                    <li v-for="item in wangSupplementaryAnalysis" :key="item">{{ item }}</li>
                  </ul>
                </div>
              </div>
            </div>
            <p v-else class="diagnosis-result">暂未进行舌象检查，请补充望诊数据以获得更准确的诊断。</p>
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
            <div v-if="showNeutralDetail && wenAudioSupplementaryAnalysis.length" class="supplementary-analysis supplement-card">
              <div class="supplementary-title">补充分析</div>
              <ul>
                <li v-for="item in wenAudioSupplementaryAnalysis" :key="item">{{ item }}</li>
              </ul>
            </div>
            <div v-else>暂未进行声音分析，请补充闻诊数据。</div>
          </el-card>
        </div>

        <div class="diagnosis-item">
          <h3>问诊（症状问卷）</h3>
          <el-card>
            <div v-if="reportData.diagnosis.wen_questionnaire" class="questionnaire-result">
              <div class="questionnaire-header">
                <div>
                  <p class="questionnaire-kicker">专项问诊结论</p>
                  <h4>{{ reportData.diagnosis.wen_questionnaire.conclusion }}</h4>
                </div>
                <el-tag type="success" effect="light">{{ questionnaireAnalysis?.title || '问诊结果' }}</el-tag>
              </div>
              <p class="questionnaire-summary">{{ questionnaireAnalysis?.summary }}</p>

              <div v-if="showNeutralDetail && questionnaireAnalysis?.detailNotes?.length" class="supplementary-analysis supplement-card">
                <div class="supplementary-title">补充分析</div>
                <ul>
                  <li v-for="item in questionnaireAnalysis.detailNotes" :key="item">{{ item }}</li>
                </ul>
              </div>

              <el-row v-if="questionnaireAnalysis?.diet?.length || questionnaireAnalysis?.avoid?.length" :gutter="16" class="questionnaire-panels">
                <el-col :span="12" :xs="24">
                  <div class="questionnaire-panel">
                    <strong>饮食建议</strong>
                    <ul>
                      <li v-for="item in questionnaireAnalysis?.diet || []" :key="item">{{ item }}</li>
                    </ul>
                  </div>
                </el-col>
                <el-col :span="12" :xs="24">
                  <div class="questionnaire-panel danger">
                    <strong>禁忌提醒</strong>
                    <ul>
                      <li v-for="item in questionnaireAnalysis?.avoid || []" :key="item">{{ item }}</li>
                    </ul>
                  </div>
                </el-col>
              </el-row>

              <div v-if="questionnaireAnalysis?.suggestions?.length" class="questionnaire-panel">
                <strong>后续建议</strong>
                <ul>
                  <li v-for="item in questionnaireAnalysis?.suggestions || []" :key="item">{{ item }}</li>
                </ul>
              </div>

            </div>
            <div v-else>暂未进行症状问卷调查，请补充问诊数据。</div>
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
            <div v-if="showNeutralDetail && qieSupplementaryAnalysis.length" class="supplementary-analysis supplement-card">
              <div class="supplementary-title">补充分析</div>
              <ul>
                <li v-for="item in qieSupplementaryAnalysis" :key="item">{{ item }}</li>
              </ul>
            </div>
            <div v-else-if="!reportData.diagnosis.qie">暂未进行脉搏检测，请补充切诊数据。</div>
          </el-card>
        </div>
      </section>

      <!-- AI 综合分析章节 -->
      <section class="report-section synthesis">
        <h2>{{ synthesisTitle }} <span v-if="isStreaming" class="streaming-badge">AI 思考中...</span></h2>
        <p class="synthesis-hint">{{ synthesisSubtitle }}</p>
        <el-card shadow="hover">
          <div class="synthesis-content" :class="{'is-typing': isStreaming}">
            <span v-html="reportData.synthesis ? markdownToHtml(reportData.synthesis) : '正在连接 AI 分析引擎...'"></span>
          </div>
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
import { marked } from "marked";
import {
  buildReportPromptTemplate,
  getConstitutionAdvice,
  getConstitutionScoreRanking,
  getReportFocusModeLabel
} from '@/utils/reportUtils';

const router = useRouter();
const route = useRoute();

const reportData = ref(null);
const isLoading = ref(false);
const isExporting = ref(false);
const isStreaming = ref(false);
const streamFinished = ref(false);
const streamRequested = ref(false);
const controllerRef = ref(null);
const currentPatientId = ref(null);
const currentCaseId = ref(null);
const reportRef = ref(null);
const idCardPhotoBase64 = ref(localStorage.getItem("current_idcard_photo_base64") || "");
const idCardFullImageBase64 = ref(localStorage.getItem("current_idcard_image_base64") || "");

const reportTitle = ref("四诊合参诊断报告");
const completionPercentage = ref(0);

// ===== 读取报告设置（localStorage）=====
const reportSettings = computed(() => {
  try {
    const saved = localStorage.getItem("report_settings");
    return saved ? JSON.parse(saved) : {};
  } catch { return {}; }
});

const normalizedFocusMode = computed(() => {
  const raw = String(reportSettings.value?.llmFocusMode || '').trim().toLowerCase();
  if (!raw || ['none', 'no_focus', 'no-focus', 'nofocus', '不侧重', '综合', '综合分析', 'balanced'].includes(raw)) {
    return 'balanced';
  }
  return raw;
});

const showNeutralDetail = computed(() => normalizedFocusMode.value === 'balanced');
const showWangSupplementary = computed(() => showNeutralDetail.value || normalizedFocusMode.value === 'wang');
const synthesisTitle = computed(() => {
  const focusLabel = getReportFocusModeLabel(reportSettings.value?.llmFocusMode || '');
  return focusLabel ? `AI 重点分析（${focusLabel}）` : 'AI 详细分析';
});
const synthesisSubtitle = computed(() => {
  return showNeutralDetail.value
    ? '不侧重模式下，将进行更充分的跨板块综合分析与分层建议。'
    : '本段将围绕所选侧重板块展开更详细分析。';
});

const idCardPhotoSrc = computed(() => {
  const rawPhoto = idCardPhotoBase64.value;
  if (!rawPhoto) return "";
  if (rawPhoto.startsWith("data:")) return rawPhoto;
  return `data:image/bmp;base64,${rawPhoto}`;
});

const idCardFullImageSrc = computed(() => {
  const rawImage = idCardFullImageBase64.value;
  if (!rawImage) return "";
  if (rawImage.startsWith("data:")) return rawImage;
  return `data:image/svg+xml;base64,${rawImage}`;
});

const idCardDisplaySrc = computed(() => idCardFullImageSrc.value || idCardPhotoSrc.value);

const normalizeQuestionnaireScoreMap = (rawScores) => {
  if (!rawScores || typeof rawScores !== 'object') return {};

  // 优先读取模板结构里的 scoreMap（专项问卷）
  if (rawScores.templateResult?.scoreMap && typeof rawScores.templateResult.scoreMap === 'object') {
    return rawScores.templateResult.scoreMap;
  }
  // 兼容 templateResult 下可能嵌套 scores 的情况
  if (rawScores.templateResult?.scores && typeof rawScores.templateResult.scores === 'object') {
    return rawScores.templateResult.scores;
  }
  // 原始问卷：后端常见结构 { scores, candidateConstitutions, mainConstitution }
  if (rawScores.scores && typeof rawScores.scores === 'object') {
    return rawScores.scores;
  }
  // 若本身就是分值映射，直接使用
  return rawScores;
};

const questionnaireAnalysis = computed(() => {
  const diagnosis = reportData.value?.diagnosis?.wen_questionnaire;
  if (!diagnosis) return null;
  const scores = diagnosis.scores || {};
  const rankingScoreMap = normalizeQuestionnaireScoreMap(scores);
  const baseResult = scores && typeof scores === 'object' && scores.templateResult
    ? { ...scores.templateResult }
    : getConstitutionAdvice(diagnosis.conclusion || '', rankingScoreMap);

  if (showNeutralDetail.value) {
    const ranking = getConstitutionScoreRanking(rankingScoreMap || {}, 3);
    return {
      ...baseResult,
      detailNotes: [
        ranking.length
          ? `本次得分靠前的是：${ranking.map((item) => `${item.name}${item.score}分`).join('、')}，可作为后续调理重点。`
          : '当前问卷结果已形成基础判断，可结合整体生活方式继续观察。',
        '问卷分析适合与望诊、闻诊和切诊结果联动解读，不宜单独下结论。',
        '若主诉症状持续存在，建议结合睡眠、饮食、情绪和运动习惯一起评估。',
        '可按 1-2 周为周期复盘症状变化，结合复测结果动态调整调理重点。',
      ],
    };
  }
  return baseResult;
});

const wangSupplementaryAnalysis = computed(() => {
  const diagnosis = reportData.value?.diagnosis?.wang;
  if (!diagnosis) return [];
  const items = [];
  const resultText = String(diagnosis.result || '');
  items.push('舌象结果已提示当前舌体与舌苔特征，建议与饮食、睡眠、情绪状态一起观察。');
  if (resultText.includes('脾虚湿盛')) {
    items.push('这类表现通常和运化偏弱、湿邪偏重有关，日常可留意清淡饮食与作息规律。');
  }
  if (resultText.includes('轻度')) {
    items.push('目前变化偏轻，重在早期干预和持续观察，避免继续累积疲劳与饮食失衡。');
  }
  items.push('如果后续还有闻诊、问诊或切诊结果，可进一步提高整体辨证的稳定性。');
  return items;
});

const wenAudioSupplementaryAnalysis = computed(() => {
  const diagnosis = reportData.value?.diagnosis?.wen_audio;
  if (!diagnosis) return [];
  const items = [];
  const confidence = diagnosis.confidence ? `${(diagnosis.confidence * 100).toFixed(1)}%` : null;
  items.push(confidence ? `当前闻诊置信度为 ${confidence}，可作为参考，但不建议单独定性。` : '当前闻诊结果可用于辅助判断，但仍需结合其他板块。');
  if (Array.isArray(diagnosis.tags) && diagnosis.tags.length) {
    items.push(`体质标签显示：${diagnosis.tags.join('、')}，说明声音特征与当前体质倾向存在一定关联。`);
  }
  items.push('若日常出现乏力、气短、咳嗽或情绪波动，建议结合具体症状继续观察。');
  return items;
});

const qieSupplementaryAnalysis = computed(() => {
  const diagnosis = reportData.value?.diagnosis?.qie;
  if (!diagnosis) return [];
  const items = [];
  items.push(`当前心率 ${diagnosis.heartRate} bpm、血氧 ${diagnosis.spo2}%，可作为循环与呼吸状态的基础参考。`);
  items.push(`信号有效率 ${diagnosis.validRate}%、采样数 ${diagnosis.sampleCount}，说明本次测量质量具备一定参考价值。`);
  if (diagnosis.tcmSuggestion) {
    items.push('脉搏分析已给出中医建议，可与舌象和问卷结果一起综合判断。');
  }
  return items;
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
// 根据实际完成的诊法动态生成步骤
const ALL_STEPS = {
  wang:              { char: "望", label: "舌象分析" },
  wen_audio:         { char: "闻", label: "声纹识别" },
  wen_questionnaire: { char: "问", label: "问卷解析" },
  qie:               { char: "切", label: "脉象推理" },
}

const buildSteps = () => {
  // 优先使用路由参数，若无则从 localStorage 读取已完成的诊法
  let param = route.query.completedTypes || localStorage.getItem("_temp_completedTypes") || ""
  
  // 如果参数仍为空，则根据 localStorage 的完成标记动态收集
  if (!param) {
    const patientId = route.query.id || localStorage.getItem("current_patient_id")
    const completed = []
    const pid = String(patientId || '')
    if (localStorage.getItem('wang_finished_id') === pid) completed.push('wang')
    if (localStorage.getItem('wen_finished_id') === pid) completed.push('wen_audio')
    if (localStorage.getItem('wenjuan_finished_id') === pid) completed.push('wen_questionnaire')
    if (localStorage.getItem('qie_finished_id') === pid) completed.push('qie')
    param = completed.join(',')
  }
  
  const keys = param ? param.split(",").filter(k => ALL_STEPS[k]) : []
  
  // 根据实际完成的诊法生成步骤
  if (keys.length > 0) {
    return keys.map(k => ({ ...ALL_STEPS[k], state: "pending" }))
  }
  
  // 备选：如果无法确定，显示通用的综合分析步骤
  return [
    { char: "综", label: "数据综合分析", state: "pending" },
    { char: "智", label: "AI 智能推理", state: "pending" },
    { char: "成", label: "生成诊断建议", state: "pending" }
  ]
}

const steps = ref(buildSteps())

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
  idCardPhotoBase64.value = localStorage.getItem("current_idcard_photo_base64") || "";
  idCardFullImageBase64.value = localStorage.getItem("current_idcard_image_base64") || "";
  const patientId = route.query.id || localStorage.getItem("current_patient_id");
  const caseId = route.query.caseId || localStorage.getItem("current_case_id");
  const completedTypesParam = route.query.completedTypes;
  if (!patientId) {
    ElMessage.error("缺少患者ID，请先完成诊断操作");
    goBack();
    return;
  }
  currentPatientId.value = Number(patientId);
  currentCaseId.value = caseId ? Number(caseId) : null;
  if (currentCaseId.value) {
    localStorage.setItem("current_case_id", String(currentCaseId.value));
  }
  if (completedTypesParam) localStorage.setItem("_temp_completedTypes", completedTypesParam);
  
  // 在 onMounted 时重新初始化步骤（此时 route.query 已准备好）
  steps.value = buildSteps();
  
  await fetchReportData(patientId, currentCaseId.value);
});

const getCompletedTypes = () => localStorage.getItem("_temp_completedTypes") || "";

const buildReportRequestPayload = (patientId, caseId = null) => {
  const idCard = localStorage.getItem("current_patient_idCard") || "";
  const completedTypes = getCompletedTypes();
  const promptTemplate = buildReportPromptTemplate(
    reportSettings.value?.llmPromptTemplate || "",
    reportSettings.value?.llmFocusMode || ""
  );
  const focusMode = reportSettings.value?.llmFocusMode || "";

  return {
    patientId: Number(patientId),
    caseId: caseId || undefined,
    idCard,
    customPromptTemplate: promptTemplate || undefined,
    focusMode: focusMode || undefined,
    ...(completedTypes ? { completedTypes } : {})
  };
};

const fallbackToNonStreamReport = async (requestPayload, streamErrorMessage = "") => {
  const response = await axios.post("/api/report/generate", requestPayload);
  if (response.data.code !== 200 && !response.data.success) {
    throw new Error(response.data.msg || "普通生成失败");
  }

  if (!response.data.data) {
    throw new Error("普通生成返回为空");
  }

  reportData.value = response.data.data;
  calculateCompletion();
  stopLoadingAnimation();
  const suffix = streamErrorMessage ? `（原因：${streamErrorMessage}）` : "";
  ElMessage.warning(`流式生成失败，已自动切换普通生成${suffix}`);
};

const fetchReportData = async (patientId, caseId = null) => {
  isLoading.value = true;
  startLoadingAnimation();
  try {
    const idCard = localStorage.getItem("current_patient_idCard") || "";
    const response = await axios.get("/api/report/get-diagnosis", {
      params: { patientId: Number(patientId), caseId: caseId || undefined, idCard }
    });
    if (response.data.code !== 200 && !response.data.success) {
      ElMessage.error(response.data.msg || "获取报告失败");
      return;
    }
    if (!response.data.data.synthesis) {
      await generateReport(patientId, caseId);
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

const generateReport = async (patientId, caseId = null) => {
  isLoading.value = true;
  isStreaming.value = false;
  streamFinished.value = false;
  streamRequested.value = true;
  startLoadingAnimation();
  const requestPayload = buildReportRequestPayload(patientId, caseId);

  try {
    // 使用 AbortController 支持取消
    const controller = new AbortController();
    controllerRef.value = controller;

    const response = await fetch("/api/report/generate/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestPayload),
      signal: controller.signal
    });

    if (!response.ok) throw new Error("网络响应异常");

    if (!response.body) throw new Error("浏览器不支持流式响应");

    // 即使后端 Meta 首包延迟，也先初始化可见预览容器，避免等待期空白。
    if (!reportData.value) {
      reportData.value = {
        synthesis: ""
      };
    }
    isStreaming.value = true;

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let hasReceivedMeta = false;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      // 累加数据块
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop(); // 保留不完整的最后一行

      for (const line of lines) {
        if (line.startsWith("data:")) {
          const dataStr = line.slice(5).trim();

            if (dataStr === "[DONE]") {
              isStreaming.value = false;
              streamFinished.value = true;
              // 流结束，显示“查看完整报告”按钮，由用户决定是否进入完整报告或由页面继续显示
              break;
            }

          try {
            const parsed = JSON.parse(dataStr);
            if (parsed && typeof parsed === "object" && parsed.error) {
              throw new Error(parsed.error);
            }
            // 收到 Meta 基础数据，立刻关闭动画，渲染报告框架
            if (parsed.meta) {
              hasReceivedMeta = true;
              reportData.value = {
                ...parsed.meta,
                synthesis: "" // 初始化为空，准备接收打字
              };
              isStreaming.value = true;
              calculateCompletion();
            }
            // 收到 AI 增量文本，追加上去
            else if (parsed.content && reportData.value) {
              reportData.value.synthesis += parsed.content;
            }
            // 兼容某些网关/后端直接返回纯文本 data: xxx 的情况
            else if (typeof parsed === 'string' && reportData.value) {
              reportData.value.synthesis += parsed;
            }
          } catch (e) {
            // 非 JSON 数据按纯文本兜底拼接，避免预览空白。
            if (dataStr && dataStr !== '[DONE]' && reportData.value) {
              reportData.value.synthesis += dataStr;
            }
          }
        }
      }
    }

    // 流结束后做最终处理：先结束等待动画，再自动切到完整报告
    if (!hasReceivedMeta) {
      stopLoadingAnimation();
      isLoading.value = false;
    } else {
      stopLoadingAnimation();
      await new Promise(r => setTimeout(r, 700));
      isLoading.value = false;
    }
    isStreaming.value = false;
    streamRequested.value = false;
    ElMessage.success("报告生成完成");

  } catch (error) {
    // 用户主动取消时，不触发降级与报错。
    if (error?.name === "AbortError") {
      return;
    }

    try {
      await fallbackToNonStreamReport(requestPayload, error.message || "");
      ElMessage.success("报告生成完成");
    } catch (fallbackError) {
      stopLoadingAnimation();
      ElMessage.error("生成报告失败：" + (fallbackError.message || fallbackError));
    } finally {
      isLoading.value = false;
      isStreaming.value = false;
      streamRequested.value = false;
      controllerRef.value = null;
    }
    return;
  }

  controllerRef.value = null;
};

const cancelStream = () => {
  try {
    if (controllerRef.value) controllerRef.value.abort();
  } catch (e) {}
  isStreaming.value = false;
  streamFinished.value = false;
  streamRequested.value = false;
  stopLoadingAnimation();
  isLoading.value = false;
  ElMessage.info('已取消生成');
};

const viewFullReport = () => {
  // 切换到完整报告视图（在当前组件内即可，因为 reportData 已有内容）
  isLoading.value = false;
  isStreaming.value = false;
  // 可选：滚动到报告内容
  setTimeout(() => {
    if (reportRef.value) reportRef.value.scrollIntoView({ behavior: 'smooth' });
  }, 100);
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
const buildPrintableWindow = () => {
  if (!reportRef.value) { ElMessage.error("报告内容未加载"); return null; }

  const styles = [...document.querySelectorAll("style")]
    .map((s) => s.innerHTML).join("\n");

  const printable = window.open("", "_blank", "width=900,height=800");
  if (!printable) {
    ElMessage.error("浏览器阻止了打印窗口，请允许弹窗后重试");
    return null;
  }

  printable.document.write(`<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>诊断报告</title>
<style>
  @page { margin: 15mm; }
  body { margin: 0; padding: 20px; background: white; font-family: "Noto Serif SC","Source Han Serif CN", Arial, sans-serif; }
  img { max-width: 100%; }
  ${styles}
</style>
</head><body>
${reportRef.value.outerHTML}
</body></html>`);
  printable.document.close();
  return printable;
};

const handlePrint = async () => {
  const printable = buildPrintableWindow();
  if (!printable) return;
  printable.focus();
  await new Promise((resolve) => setTimeout(resolve, 300));
  printable.print();
  printable.close();
};

const exportPDF = async () => {
  isExporting.value = true;
  try {
    const printable = buildPrintableWindow();
    if (!printable) return;
    printable.focus();
    await new Promise((resolve) => setTimeout(resolve, 300));
    printable.print();
    setTimeout(() => printable.close(), 500);
    ElMessage.success("请在打印窗口中选择“另存为 PDF”完成导出");
  } catch (e) {
    ElMessage.error("PDF 导出失败：" + e.message);
  } finally {
    isExporting.value = false;
  }
};
</script>

<style scoped>
/* ============ 报告样式 ============ */
.report-container { max-width: 1000px; margin: 0 auto; padding: 20px; background: radial-gradient(ellipse at top, #f5e8c8 0%, #fdf3dc 45%, #fef9f0 100%); min-height: 100vh; font-family: 'Noto Serif SC', 'Source Han Serif CN', serif; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; background: rgba(255,252,242,.95); padding: 20px; border-radius: 8px; border: 1px solid #c8a96e; box-shadow: 0 2px 12px rgba(100,60,10,.10); }
.header h1 { flex: 1; text-align: center; margin: 0; color: #333; }
.completion-badge { position: absolute; right: 20px; top: 20px; }
.badge { display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 600; letter-spacing: 0.5px; }
.badge.incomplete { background: linear-gradient(135deg, #ffa500, #ff8c00); color: white; }
.badge.complete   { background: linear-gradient(135deg, #67c26a, #40ad50); color: white; }
.header-buttons { display: flex; gap: 10px; }
.report-content { background: rgba(255,252,242,.95); border-radius: 8px; overflow: hidden; border: 1px solid #c8a96e; box-shadow: 0 3px 16px rgba(100,60,10,.10); }
.report-section { padding: 30px; border-bottom: 1px solid #eee; }
.report-section:last-child { border-bottom: none; }
.report-section h2 { color: #5a2d00; font-size: 20px; margin-bottom: 20px; border-bottom: 3px solid #c8a020; padding-bottom: 10px; }
.report-section h3 { color: #3d2b10; font-size: 16px; margin-top: 20px; margin-bottom: 15px; }
.diagnosis-item { margin-bottom: 20px; }
.diagnosis-image { text-align: center; margin-bottom: 15px; }
.diagnosis-wang-layout {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}
.diagnosis-image-left {
  flex: 0 0 240px;
  margin-bottom: 0;
}
.diagnosis-image-left img {
  width: 100%;
  max-width: 240px;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(90, 45, 0, 0.15);
}
.diagnosis-image-left p {
  margin-top: 10px;
  margin-bottom: 0;
  text-align: center;
  color: #5a2d00;
}
.diagnosis-text-block {
  flex: 1;
  min-width: 0;
}
.diagnosis-result { color: #4a3020; line-height: 1.8; margin: 0; }
.tag { margin: 5px 5px 5px 0; }
.unit { color: #999; font-size: 14px; margin-left: 5px; }
.tcm-suggestion { margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee; }
.supplementary-analysis {
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 10px;
  background: #fff8ea;
  border: 1px solid #ead3a0;
}
.supplementary-title {
  font-size: 13px;
  font-weight: 700;
  color: #8b3d1a;
  margin-bottom: 8px;
}
.supplementary-analysis ul {
  margin: 0;
  padding-left: 18px;
  color: #4a3020;
  line-height: 1.75;
}
.supplementary-analysis li {
  margin: 6px 0;
}
.supplement-card {
  background: linear-gradient(180deg, #fffaf0 0%, #fff6e8 100%);
}
.questionnaire-result { display: flex; flex-direction: column; gap: 14px; }
.questionnaire-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}
.questionnaire-kicker {
  margin: 0 0 6px;
  font-size: 12px;
  color: #9a7040;
  letter-spacing: 1px;
}
.questionnaire-header h4 { margin: 0; color: #5a2d00; font-size: 18px; }
.questionnaire-summary { margin: 0; color: #4a3020; line-height: 1.8; }
.questionnaire-panels { margin-top: 2px; }
.questionnaire-panel {
  padding: 14px;
  border-radius: 10px;
  border: 1px solid rgba(232, 213, 160, 0.95);
  background: #fffdf7;
}
.questionnaire-panel.danger {
  background: #fff7f4;
  border-color: rgba(192, 57, 43, 0.22);
}
.questionnaire-panel strong {
  display: inline-block;
  margin-bottom: 10px;
  color: #5a2d00;
}
.questionnaire-panel ul {
  margin: 0;
  padding-left: 18px;
  color: #4a3020;
  line-height: 1.7;
}
.questionnaire-score-rule {
  margin: 0 0 8px;
  color: #725130;
  line-height: 1.6;
}
.questionnaire-panel li { margin: 6px 0; }
.synthesis-content { line-height: 1.8; color: #333; font-size: 14px; }
.synthesis-hint { margin: -10px 0 14px; color: #8b6030; font-size: 13px; }
.synthesis-content :deep(h3) { color: #5a2d00; margin-top: 15px; margin-bottom: 10px; }
.synthesis-content :deep(ul), .synthesis-content :deep(ol) { margin: 10px 0; padding-left: 20px; }
.synthesis-content :deep(li) { margin: 5px 0; }
.synthesis-content :deep(strong) { color: #8b3d1a; }
/* 流式打字光标与 badge */
.streaming-badge { font-size: 12px; color: #999; margin-left: 8px; font-weight: 500; }
.synthesis-content.is-typing::after {
  content: "|";
  display: inline-block;
  margin-left: 6px;
  animation: blink-caret 1s steps(1) infinite;
}
@keyframes blink-caret { 50% { opacity: 0; } }

/* 实时预览卡 */
.live-preview { margin: 18px auto 0; max-width: 680px; }
.live-card { padding: 12px; }
.live-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
.live-title { font-weight:700; color:#5a2d00; }
.live-body { padding-top:6px; }
.preload-patient { display:flex; gap:12px; margin-bottom:10px; color:#6b4c24; font-size:13px; }
.pp-row { margin-right:8px; }
.live-synthesis { background: #fff; padding: 12px; border-radius:6px; border:1px solid rgba(200,160,32,0.08); color:#333; line-height:1.8; max-height:320px; overflow:auto; }
.report-footer { padding: 30px; background: #faf3e0; border-top: 1px solid #e8d5a0; text-align: center; color: #8b6030; font-size: 12px; }
.report-footer p { margin: 5px 0; }
.disclaimer { color: #c0392b; font-size: 11px; }
.footer-actions { margin-top: 20px; }
.footer-actions :deep(.el-button) { min-width: 140px; }
.no-data { padding: 60px 20px; text-align: center; }
.report-idcard-card-box {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.report-idcard-card {
  max-width: 420px;
  width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(90, 45, 0, 0.2);
}

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
.loading-card { position: relative; width: 100%; max-width: 680px; background: rgba(255,255,255,0.92); backdrop-filter: blur(20px); border-radius: 28px; border: 1px solid rgba(255,255,255,0.8); box-shadow: 0 30px 80px rgba(100,60,10,.15); overflow: hidden; border: 1px solid #c8a96e; }
.glow { position: absolute; border-radius: 50%; filter: blur(60px); opacity: 0.18; pointer-events: none; }
.glow-blue { width: 300px; height: 300px; background: #8b3d1a; top: -80px; right: -60px; animation: glowPulse 4s ease-in-out infinite alternate; }
.glow-green { width: 250px; height: 250px; background: #c8a020; bottom: -60px; left: -40px; animation: glowPulse 5s ease-in-out infinite alternate-reverse; }
@keyframes glowPulse { 0% { opacity: 0.12; transform: scale(1); } 100% { opacity: 0.25; transform: scale(1.15); } }
.pulse-bar { width: 100%; height: 56px; background: linear-gradient(90deg, #6b2d12 0%, #8b3d1a 50%, #c8a020 100%); display: flex; align-items: center; }
.pulse-bar svg { width: 100%; height: 56px; }
.pulse-line { fill: none; stroke: rgba(255,255,255,0.85); stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; stroke-dasharray: 700; stroke-dashoffset: 700; animation: drawPulse 2.2s ease-out forwards, pulseScan 3s ease-in-out 2.2s infinite; }
@keyframes drawPulse { to { stroke-dashoffset: 0; } }
@keyframes pulseScan { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
.loading-body { padding: 36px 40px 40px; display: flex; flex-direction: column; align-items: center; gap: 0; }
.taiji-wrap { position: relative; width: 96px; height: 96px; margin-bottom: 28px; }
.taiji-ring { position: absolute; border-radius: 50%; border-style: solid; top: 50%; left: 50%; transform: translate(-50%,-50%); }
.ring-outer { width: 96px; height: 96px; border-width: 2.5px; border-color: #c8a020 rgba(200,160,32,0.2) rgba(200,160,32,0.2) #c8a020; animation: spinCCW 3s linear infinite; }
.ring-mid { width: 70px; height: 70px; border-width: 2px; border-color: rgba(139,61,26,0.3) #8b3d1a #8b3d1a rgba(139,61,26,0.3); animation: spinCW 2s linear infinite; }
.taiji-core { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); width: 46px; height: 46px; border-radius: 50%; background: linear-gradient(135deg,#8b3d1a,#c04a20); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 20px rgba(139,61,26,0.5); }
.taiji-core span { font-family: "KaiTi","楷体",serif; font-size: 20px; color: white; font-weight: bold; animation: breathe 2.5s ease-in-out infinite; }
.taiji-orbit { position: absolute; width: 96px; height: 96px; top: 0; left: 0; animation: spinCW 2.5s linear infinite; }
.orbit-dot { position: absolute; top: -5px; left: 50%; transform: translateX(-50%); width: 10px; height: 10px; border-radius: 50%; background: #c8a020; box-shadow: 0 0 8px rgba(200,160,32,0.8); }
@keyframes spinCW  { to { transform: translate(-50%,-50%) rotate(360deg); } }
@keyframes spinCCW { to { transform: translate(-50%,-50%) rotate(-360deg); } }
@keyframes breathe { 0%,100% { transform: scale(1); } 50% { transform: scale(1.12); } }
.loading-title { margin: 0 0 8px; font-size: 22px; font-family: 'Noto Serif SC',"Source Han Serif CN",serif; color: #3d2b10; font-weight: 700; letter-spacing: 1px; }
.loading-sub { margin: 0 0 32px; font-size: 13px; color: #8b6030; text-align: center; line-height: 1.7; }
.steps { display: flex; gap: 16px; margin-bottom: 32px; align-items: flex-start; }
.step { display: flex; flex-direction: column; align-items: center; gap: 8px; transition: opacity 0.5s; }
.step.pending { opacity: 0.35; } .step.active { opacity: 1; } .step.done { opacity: 1; }
.step-icon { position: relative; width: 52px; height: 52px; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
.step.done .step-icon { background: linear-gradient(135deg,#4a7060,#2d5a4a); box-shadow: 0 4px 16px rgba(74,112,96,0.4); }
.step.active .step-icon { background: linear-gradient(135deg,#8b3d1a,#c04a20); box-shadow: 0 4px 20px rgba(139,61,26,0.5); animation: stepPulse 1.5s ease-in-out infinite; }
.step.pending .step-icon { background: #f5ead8; border: 2px solid #e8d5a0; }
@keyframes stepPulse { 0%,100% { box-shadow: 0 4px 20px rgba(139,61,26,0.5); } 50% { box-shadow: 0 4px 32px rgba(139,61,26,0.9); } }
.step-char { font-family: "KaiTi","楷体",serif; font-size: 22px; font-weight: bold; color: white; line-height: 1; }
.step.pending .step-char { color: #c8a96e; }
.step-spinner { position: absolute; inset: -4px; border-radius: 20px; border: 2.5px solid transparent; border-top-color: rgba(255,255,255,0.8); border-right-color: rgba(255,255,255,0.4); animation: spin 1s linear infinite; }
.step-check { position: absolute; bottom: -4px; right: -4px; width: 18px; height: 18px; background: white; border-radius: 50%; padding: 2px; stroke: #4a7060; stroke-width: 3; fill: none; stroke-linecap: round; }
@keyframes spin { to { transform: rotate(360deg); } }
.step-label { font-size: 12px; color: #6b4c24; white-space: nowrap; }
.step.active .step-label { color: #8b3d1a; font-weight: 600; }
.step.done  .step-label { color: #4a7060; font-weight: 600; }
.progress-track { position: relative; width: 100%; height: 8px; background: #e8d5a0; border-radius: 100px; overflow: visible; margin-bottom: 10px; }
.progress-fill { height: 100%; border-radius: 100px; background: linear-gradient(90deg,#8b3d1a,#c8a020,#4a7060); background-size: 200% 100%; transition: width 2s cubic-bezier(0.4,0,0.2,1); animation: shimmer 2.5s linear infinite; }
.progress-glow { position: absolute; top: 50%; transform: translateY(-50%) translateX(-50%); width: 20px; height: 20px; border-radius: 50%; background: radial-gradient(circle,rgba(200,160,32,0.6) 0%,transparent 70%); transition: left 2s cubic-bezier(0.4,0,0.2,1); pointer-events: none; }
@keyframes shimmer { 0% { background-position: 200% center; } 100% { background-position: -200% center; } }
.progress-text { font-size: 12.5px; color: #9a7040; margin: 0 0 24px; text-align: center; }
.loading-tip { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #8b6030; background: rgba(200,160,32,0.06); border: 1px solid rgba(200,160,32,0.2); border-radius: 100px; padding: 8px 18px; margin: 0; }
.tip-dot { width: 6px; height: 6px; border-radius: 50%; background: #c8a020; flex-shrink: 0; animation: blink 1.4s ease-in-out infinite; }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.2; } }

/* 响应式 */
@media (max-width: 768px) {
  .report-container { padding: 10px; }
  .header { flex-direction: column; gap: 10px; }
  .header h1 { font-size: 18px; margin: 10px 0; }
  .report-section { padding: 20px; }
  .questionnaire-header { flex-direction: column; }
  .loading-body { padding: 28px 20px 32px; }
  .steps { gap: 10px; }
  .step-icon { width: 44px; height: 44px; border-radius: 13px; }
  .step-char { font-size: 18px; }
}

/* 打印 */
@page { margin: 15mm; size: A4; }
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
