<template>
  <div class="wenjuan-wrapper">
    <div class="ink-bg"><div class="blob"></div></div>
    <div class="paper-texture"></div>

    <div class="template-select-panel" v-if="!questionnaireStarted && !isDone">
      <div class="template-select-card">
        <div class="tcm-seal">模板选择</div>
        <h2 class="template-title">先选择问诊人群 / 场景</h2>
        <p class="template-desc">标准 33 题保留读题音频；专项模板仅保留文字题目，适合不同人群的问诊路径。</p>

        <div class="template-topline">
          <span>当前可用 {{ templateCards.length }} 套模板</span>
          <span>已选：{{ selectedTemplateCard?.title }}</span>
        </div>

        <div class="template-section">
          <div class="template-section-head">
            <h3>标准体质问卷</h3>
            <p>适合完整采集 33 项体质指标，并保留读题音频。</p>
          </div>
          <div
            v-if="originalTemplateCard"
            :key="originalTemplateCard.code"
            class="template-item"
            :class="{ 'is-active': selectedTemplateCode === originalTemplateCard.code }"
            @click="selectTemplate(originalTemplateCard.code)"
          >
            <div class="template-item-head">
              <div>
                <h3>{{ originalTemplateCard.title }}</h3>
                <p>{{ originalTemplateCard.subtitle }}</p>
              </div>
              <el-tag effect="light" :type="originalTemplateCard.audioEnabled ? 'success' : 'warning'">
                {{ originalTemplateCard.audioEnabled ? '含读题音频' : '仅文字问诊' }}
              </el-tag>
            </div>
            <div class="template-meta">
              <span>{{ originalTemplateCard.questionCount }} 题</span>
              <span>{{ originalTemplateCard.badge }}</span>
              <span>{{ originalTemplateCard.durationText }}</span>
            </div>
          </div>
        </div>

        <div class="template-section">
          <div class="template-section-head">
            <h3>专项问诊模板</h3>
            <p>按场景定制问题，快速完成专项体质评估。</p>
          </div>
          <div class="template-grid">
            <div
              v-for="item in specialTemplateCards"
              :key="item.code"
              class="template-item"
              :class="{ 'is-active': selectedTemplateCode === item.code }"
              @click="selectTemplate(item.code)"
            >
              <div class="template-item-head">
                <div>
                  <h3>{{ item.title }}</h3>
                  <p>{{ item.subtitle }}</p>
                </div>
                <el-tag effect="light" :type="item.audioEnabled ? 'success' : 'warning'">
                  {{ item.audioEnabled ? '含读题音频' : '仅文字问诊' }}
                </el-tag>
              </div>
              <div class="template-meta">
                <span>{{ item.questionCount }} 题</span>
                <span>{{ item.badge }}</span>
                <span>{{ item.durationText }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="selected-template-panel" v-if="selectedTemplateCard">
          <p class="selected-title">即将开始：{{ selectedTemplateCard.title }}</p>
          <p>{{ selectedTemplateCard.subtitle }}</p>
        </div>

        <div class="template-actions">
          <el-button type="primary" size="large" round @click="startQuestionnaire">
            开始{{ selectedTemplateCode === 'original' ? '标准' : '专项' }}问诊
          </el-button>
          <el-button size="large" round plain @click="backToCenter">返回诊断中心</el-button>
        </div>
      </div>
    </div>

    <div class="main-content" v-else-if="!isDone">
      <div class="quiz-card">
        <div class="tcm-seal">问诊采集</div>
        
        <div class="header-nav">
          <div class="progress-info">
            <span class="count">第 <b>{{ currentIndex + 1 }}</b> / {{ questionCount }} 题</span>
            <span class="template-badge">{{ activeTemplate.title }}</span>
            <el-progress :percentage="progress" :stroke-width="8" color="#5d665a" :show-text="false" />
          </div>
        </div>

        <transition name="q-slide" mode="out-in">
          <div :key="currentIndex" class="question-container">
            <h2 class="question-text">
              <span class="q-index">{{ currentIndex + 1 }}.</span>
              {{ currentQuestion.content }}
              <span class="remark-text" v-if="currentQuestion.remark">（{{ currentQuestion.remark }}）</span>
            </h2>

            <div v-if="currentQuestion.kind === 'bmi'" class="bmi-input-area">
              <div class="bmi-form">
                <div class="bmi-row">
                  <span class="label">身高:</span>
                  <el-input-number v-model="bmiHeight" :precision="2" :step="0.01" :min="1.0" :max="2.5" />
                  <span class="unit">m</span>
                </div>
                <div class="bmi-row">
                  <span class="label">体重:</span>
                  <el-input-number v-model="bmiWeight" :precision="1" :step="0.5" :min="30" :max="200" />
                  <span class="unit">kg</span>
                </div>
              </div>
              <div class="bmi-result-panel">
                <p>计算 BMI 指数</p>
                <div class="bmi-val">{{ computedBMI }}</div>
              </div>
            </div>

            <div class="options-grid" v-else>
              <div 
                v-for="(option, idx) in currentOptionItems" 
                :key="idx"
                class="option-box"
                :class="{ 'is-active': answers[currentIndex] === option.value }"
                @click="handleSelect(option.value)"
              >
                <div class="opt-indicator">{{ String.fromCharCode(65 + idx) }}</div>
                <div class="opt-text">{{ option.label }}</div>
              </div>
            </div>
          </div>
        </transition>

        <div class="control-footer">
          <el-button @click="goPrev" :disabled="currentIndex === 0" round size="large">上一题</el-button>
          
          <div class="action-group">
            <el-button v-if="currentQuestion.kind === 'bmi'" type="primary" round size="large" @click="handleBMIFinish">确认并继续</el-button>
            <el-button v-else-if="isLastQuestion" type="success" round size="large" @click="handleFinish" :loading="submitting" :disabled="!answers[currentIndex]">
              提交并完成采集
            </el-button>
            <el-button v-else round size="large" @click="goNext" :disabled="!answers[currentIndex]">下一题</el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="finish-dialog" v-else>
      <div class="dialog-inner">
        <div class="icon-wrapper">
          <el-icon class="done-icon"><CircleCheckFilled /></el-icon>
        </div>
        <h2>问诊数据采集完成</h2>
        <p class="desc">{{ finishDescription }}</p>

        <div class="result-card">
          <div class="result-header">
            <div>
              <p class="result-kicker">问诊结论</p>
              <h3>{{ resultAdvice.title }}</h3>
            </div>
            <el-tag type="success" effect="light">{{ resultTag }}</el-tag>
          </div>

          <p class="result-summary">{{ resultAdvice.summary }}</p>

          <div class="result-grid">
            <div class="result-block">
              <h4>饮食建议</h4>
              <ul>
                <li v-for="item in resultAdvice.diet" :key="item">{{ item }}</li>
              </ul>
            </div>
            <div class="result-block danger">
              <h4>禁忌提醒</h4>
              <ul>
                <li v-for="item in resultAdvice.avoid" :key="item">{{ item }}</li>
              </ul>
            </div>
          </div>

          <div class="result-block">
            <h4>后续建议</h4>
            <ul>
              <li v-for="item in resultAdvice.suggestions" :key="item">{{ item }}</li>
            </ul>
          </div>

          <div class="result-grid" v-if="resultAdvice.music?.length || resultAdvice.behavior?.length">
            <div class="result-block" v-if="resultAdvice.music?.length">
              <h4>音乐养生</h4>
              <ul>
                <li v-for="item in resultAdvice.music" :key="item">{{ item }}</li>
              </ul>
            </div>
            <div class="result-block danger" v-if="resultAdvice.behavior?.length">
              <h4>行为养生</h4>
              <ul>
                <li v-for="item in resultAdvice.behavior" :key="item">{{ item }}</li>
              </ul>
            </div>
          </div>

        </div>

        <div class="next-step-box">
          <p>如需继续完成综合诊断，请返回诊断中心继续其他项目</p>
          <small>（例如：面色采集、舌苔检测、脉搏检测等）</small>
          <el-collapse style="margin-top: 16px;">
            <el-collapse-item title="📖 参考文献与出处" name="1">
              <div class="ref-list">
                <div v-for="(ref, idx) in wen_qReferences" :key="idx" class="ref-item">
                  <span class="ref-authors">{{ ref.authors }} ({{ ref.year }})</span>
                  <p class="ref-desc">{{ ref.title }}</p>
                  <a v-if="ref.url" :href="ref.url" target="_blank" class="ref-link">
                    查看 → {{ ref.source }}
                  </a>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
        <div class="finish-actions">
          <el-button size="large" round plain :loading="resetting" @click="redoQuestionnaire" class="final-btn">
            重新答题
          </el-button>
          <el-button type="primary" size="large" round @click="generateDiagnosisReport" class="final-btn">
            生成阶段性报告
          </el-button>
          <el-button type="success" size="large" round plain @click="backToCenter" class="final-btn">
            确认并返回
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router'; // 【修复】必须引入 useRoute
import { CircleCheckFilled } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus'; // 【补充】确保 ElMessage 可用
import { submitQuestionnaire, resetQuestionnaireResult } from '@/api/detect';
import { navigateToDiagnosisReport, getConstitutionAdvice } from '@/utils/reportUtils';
import { algorithmReferences } from '@/constants/algorithmReferences';
import { SPECIAL_QUESTIONNAIRE_TEMPLATES, buildSpecialQuestionnaireResult, getSpecialQuestionnaireDefaultOptions } from '@/constants/questionnaireTemplates';

const router = useRouter();
const route = useRoute(); // 【核心修复】初始化 route 对象
const audio = new Audio();

const ORIGINAL_QUESTIONS = [
  { content: "您精力充沛吗?", remark: "指精神头足, 乐于做事" },
  { content: "您容易疲乏吗?", remark: "指体力如何, 动一下就累" },
  { content: "您容易气短吗，呼吸短促, 接不上气", remark: "" },
  { content: "您说话声音低弱无力吗?", remark: "指说话没有力气" },
  { content: "您感到闷闷不乐，情绪低沉", remark: "指心情不愉快, 情绪低落" },
  { content: "您容易精神紧张，焦虑不安吗", remark: "指遇事是否容易紧张" },
  { content: "您因为生活状态改变而感到孤独、失落吗?", remark: "" },
  { content: "您容易感到害怕或受到惊吓吗?", remark: "" },
  { content: "您感到身体超重不轻松吗", remark: "系统将通过身高体重自动计算BMI指数", kind: 'bmi' }, 
  { content: "您眼睛干涩吗?", remark: "" },
  { content: "您手脚发凉吗?", remark: "不包含因周围温度改变或穿的少导致的手脚发凉" },
  { content: "您胃脘部，背部，或腰膝部怕冷吗?", remark: "" },
  { content: "您比一般人耐受不了寒冷吗?", remark: "指比别人更害怕冬天或者夏天的空天、电扇等" },
  { content: "您容易患感冒吗?", remark: "指1年内感冒次数", options: ["少于2次", "2-4次", "5-6次", "8次以上", "几乎每月"] }, 
  { content: "您没有感冒时也会鼻塞，流鼻涕吗?", remark: "" },
  { content: "您有口粘口腻，或睡眠打鼾吗?", remark: "" },
  { content: "您过敏的频率是?", remark: "药物、食物、花粉等", options: ["从不", "一年1，2次", "一年3，4次", "一年5，6次", "每次遇到上述原因都过敏"] },
  { content: "您的皮肤容易起荨麻疹吗?", remark: "包括风团，风疹块，风疙瘩" },
  { content: "您皮肤在不知不觉间出现青紫瘀斑，皮下出血吗?", remark: "指皮肤没有在外伤的情况下出现" },
  { content: "您的皮肤一抓就红，并出现抓痕吗?", remark: "指被指甲或者钝物划过的反应" },
  { content: "您皮肤或口唇干燥吗?", remark: "" },
  { content: "您有肢体麻木或固定部位疼痛的感觉吗?", remark: "" },
  { content: "您面部或鼻部有油腻或者油亮发光吗?", remark: "指脸上或鼻子" },
  { content: "您面色晦暗或目眶晦暗，或出现褐色斑块/斑点吗?", remark: "" },
  { content: "您有皮肤湿疹，疮疖吗?", remark: "" },
  { content: "您感到口干咽燥，总想喝水吗?", remark: "" },
  { content: "您感到口苦或嘴里有异味吗?", remark: "指口臭或口苦" },
  { content: "您腹部肥大吗?", remark: "腹部脂肪肥厚", options: ["腹围<80cm，相当于2.4尺", "腹围80-85cm，2.4-2.55尺", "腹围<86-90cm，2.56-2.7尺", "腹围91-105cm，2.71-3.15尺", "腹围>105cm，3.15尺"] },
  { content: "您吃(喝)凉的东西会感到不舒服或者怕吃（喝）凉的东西吗?", remark: "" },
  { content: "您有大便粘滞不爽或解不尽的感觉吗?", remark: "" },
  { content: "您容易大便干燥吗?", remark: "" },
  { content: "您舌苔厚腻或有舌苔厚厚的感觉吗？", remark: "如果自我感觉不清楚可由调查员观察后填写" },
  { content: "您舌下脉络瘀紫或增粗吗?", remark: "可由调查员观察后填写" }
];

const QUESTIONNAIRE_TEMPLATE_MAP = {
  original: {
    code: 'original',
    title: '标准体质问卷',
    subtitle: '33 题标准版本，保留读题音频',
    badge: '标准版',
    audioEnabled: true,
    questions: ORIGINAL_QUESTIONS,
    questionCount: ORIGINAL_QUESTIONS.length,
    buildResult: (answers = [], payload = {}) => ({
      kind: 'constitution',
      title: getConstitutionAdvice(payload.mainType || 'ph', payload.scoreMap || {}).title,
      summary: getConstitutionAdvice(payload.mainType || 'ph', payload.scoreMap || {}).summary,
      diet: getConstitutionAdvice(payload.mainType || 'ph', payload.scoreMap || {}).diet,
      avoid: getConstitutionAdvice(payload.mainType || 'ph', payload.scoreMap || {}).avoid,
      suggestions: getConstitutionAdvice(payload.mainType || 'ph', payload.scoreMap || {}).suggestions,
      badge: payload.mainType || '平和质',
    }),
  },
  ...SPECIAL_QUESTIONNAIRE_TEMPLATES,
};

// 核心状态
const selectedTemplateCode = ref('original');
const questionnaireStarted = ref(false);
const currentIndex = ref(0);
const answers = ref([]);
const isDone = ref(false);
const submitting = ref(false);
const resetting = ref(false);
const wen_qReferences = ref(algorithmReferences.wen_questionnaire.references);
const resultData = ref({
  kind: 'constitution',
  mainType: '',
  scoreMap: {},
  diagnosisId: null,
  templateCode: 'original',
  templateResult: null,
  templateTitle: '标准体质问卷',
});

// BMI 逻辑
const bmiHeight = ref(1.72);
const bmiWeight = ref(65.0);
const computedBMI = computed(() => (bmiWeight.value / (bmiHeight.value * bmiHeight.value)).toFixed(1));

const activeTemplate = computed(() => QUESTIONNAIRE_TEMPLATE_MAP[selectedTemplateCode.value] || QUESTIONNAIRE_TEMPLATE_MAP.original);
const questions = computed(() => activeTemplate.value.questions || []);
const questionCount = computed(() => questions.value.length || 0);
const currentQuestion = computed(() => questions.value[currentIndex.value] || {});
const currentOptions = computed(() => currentQuestion.value.options || getSpecialQuestionnaireDefaultOptions());
const currentOptionItems = computed(() =>
  (currentOptions.value || []).map((item, idx) => {
    if (typeof item === 'string') {
      return { label: item, value: idx + 1 };
    }
    return {
      label: item.label,
      value: Number.isFinite(Number(item.value)) ? Number(item.value) : idx + 1,
    };
  })
);
const progress = computed(() => questionCount.value ? Math.round(((currentIndex.value + 1) / questionCount.value) * 100) : 0);
const isLastQuestion = computed(() => currentIndex.value === questionCount.value - 1);
const resultAdvice = computed(() => {
  if (resultData.value.templateResult) {
    return resultData.value.templateResult;
  }
  if (resultData.value.kind === 'special') {
    return buildSpecialQuestionnaireResult(resultData.value.templateCode, answers.value) || {
      title: resultData.value.templateTitle || '专项问诊结果',
      summary: '专项问诊已完成，请结合生活方式和线下评估进一步判断。',
      diet: [],
      avoid: [],
      suggestions: [],
    };
  }
  return getConstitutionAdvice(resultData.value.mainType || 'ph', resultData.value.scoreMap || {});
});

const buildSpecialSubmissionTemplateResult = () => {
  const advice = resultAdvice.value || {};
  if (resultData.value.templateCode === 'original') {
    return null;
  }

  return {
    title: advice.title || activeTemplate.value.title,
    dominantConstitution: advice.badge || advice.title || activeTemplate.value.title,
    scoreMap: advice.scoreMap || {},
    constitutionScores: (advice.constitutionScores || []).map((item) => ({
      key: item.key,
      name: item.name,
      score: item.score,
      level: item.level,
    })),
  };
};
const resultTag = computed(() => {
  if (resultData.value.templateCode === 'original') {
    return resultData.value.mainType || activeTemplate.value.title;
  }
  return resultData.value.templateResult?.badge || resultData.value.templateTitle || activeTemplate.value.title;
});
const finishDescription = computed(() => {
  if (resultData.value.templateCode && resultData.value.templateCode !== 'original') {
    return `您的 ${activeTemplate.value.title} 已完成，系统已生成对应的问诊建议。`;
  }
  return '您的 33 项问诊指标已成功同步至诊断系统，系统已生成本次体质判断与调理建议。';
});

const templateCards = computed(() =>
  Object.values(QUESTIONNAIRE_TEMPLATE_MAP).map((item) => ({
    code: item.code,
    title: item.title,
    subtitle: item.subtitle,
    questionCount: item.questionCount || (item.questions ? item.questions.length : 0),
    audioEnabled: !!item.audioEnabled,
    badge: item.badge || (item.audioEnabled ? '标准版' : '专项版'),
    durationText: (item.questionCount || (item.questions ? item.questions.length : 0)) >= 30 ? '预计 6-8 分钟' : '预计 3-5 分钟',
  }))
);
const originalTemplateCard = computed(() => templateCards.value.find((item) => item.code === 'original') || null);
const specialTemplateCards = computed(() => templateCards.value.filter((item) => item.code !== 'original'));
const selectedTemplateCard = computed(() =>
  templateCards.value.find((item) => item.code === selectedTemplateCode.value) || originalTemplateCard.value
);

const resetAnswers = (template = activeTemplate.value) => {
  answers.value = new Array(template.questions.length).fill(null);
  currentIndex.value = 0;
  bmiHeight.value = 1.72;
  bmiWeight.value = 65.0;
};

const selectTemplate = (code) => {
  selectedTemplateCode.value = code;
  isDone.value = false;
};

const startQuestionnaire = () => {
  resetAnswers(QUESTIONNAIRE_TEMPLATE_MAP[selectedTemplateCode.value] || QUESTIONNAIRE_TEMPLATE_MAP.original);
  questionnaireStarted.value = true;
  isDone.value = false;
  resultData.value = {
    kind: selectedTemplateCode.value === 'original' ? 'constitution' : 'special',
    mainType: '',
    scoreMap: {},
    diagnosisId: null,
    templateCode: selectedTemplateCode.value,
    templateResult: null,
    templateTitle: activeTemplate.value.title,
  };
  if (activeTemplate.value.audioEnabled) {
    playAudio();
  }
};

const stopAudio = () => {
  audio.pause();
  audio.removeAttribute('src');
};

// 音频播放逻辑
const playAudio = () => {
  if (!questionnaireStarted.value || !activeTemplate.value.audioEnabled || currentQuestion.value.kind === 'bmi') {
    stopAudio();
    return;
  }
  audio.pause();
  audio.src = `/src/assets/audio/question/${currentIndex.value + 1}.mp3`;
  audio.play().catch(() => {});
};

// 交互操作
const handleSelect = (val) => {
  answers.value[currentIndex.value] = val;
  if (!isLastQuestion.value) {
    setTimeout(() => currentIndex.value++, 300);
  }
};

const handleBMIFinish = () => {
  const bmiVal = parseFloat(computedBMI.value);
  let score = 1;
  if (bmiVal >= 28) score = 5;
  else if (bmiVal >= 25) score = 3; 
  answers.value[8] = score;
  currentIndex.value++;
};

const goNext = () => currentIndex.value++;
const goPrev = () => currentIndex.value--;

// 核心提交函数
const handleFinish = async () => {
  if (submitting.value) return;
  submitting.value = true;

  try {
    // 1. 路由参数优先（从路由获取 ID）
    const routeId = route.query.id;
    // 注意：localStorage 建议统一用 idCard (大写C)，这取决于你 DetectSelect 怎么存的
    const routeIdCard = route.query.idCard;

    // 2. 备选方案（从缓存获取）
    const storageId = localStorage.getItem('current_patient_id');
    const storageIdCard = localStorage.getItem('current_patient_idCard') || localStorage.getItem('current_patient_idcard');

    // 确定最终使用的 ID
    const finalPid = routeId || storageId;
    const finalIdCard = routeIdCard || storageIdCard;

    console.log("==== [DEBUG] 问卷提交会话检查 ====");
    console.log("路由 ID:", routeId, " 缓存 ID:", storageId);
    console.log("最终判定 ID:", finalPid);

    if (!finalPid) {
      ElMessage.error("未找到有效的病人会话，请返回登记！");
      submitting.value = false;
      return;
    }

    // 3. 构造数据
    const templateCode = selectedTemplateCode.value || 'original';
    const template = activeTemplate.value;
    const fullTemplateResult = templateCode === 'original'
      ? null
      : buildSpecialQuestionnaireResult(templateCode, answers.value);
    const templateResult = templateCode === 'original'
      ? null
      : buildSpecialSubmissionTemplateResult();

    const postData = {
      answers: answers.value,
      idCard: finalIdCard,
      patientId: finalPid,
      diagnosisId: route.query.caseId || localStorage.getItem('current_case_id'),
      templateCode,
      templateTitle: template.title,
      templateResult,
    };

    if (templateCode === 'original') {
      postData.bmi = computedBMI.value;
    }

    const res = await submitQuestionnaire(postData);

    if (res.data.success || res.data.code === 200) {
      const payload = res.data.data || {};
      resultData.value = {
        kind: templateCode === 'original' ? 'constitution' : 'special',
        mainType: payload.mainType || payload.mainConclusion || '',
        scoreMap: payload.scores || payload.scoreMap || {},
        diagnosisId: payload.diagnosisId || null,
        templateCode,
        templateResult: templateCode === 'original'
          ? (payload.templateResult || payload.scores?.templateResult || null)
          : (fullTemplateResult || payload.templateResult || payload.scores?.templateResult || templateResult),
        templateTitle: template.title,
      };
      // 【关键修复】将完成状态与当前这个 finalPid 绑定，而不是笼统的 true/false
      localStorage.setItem('wenjuan_finished_id', String(finalPid));
      localStorage.setItem('wenjuan_template_code', templateCode);
      
      isDone.value = true;
      ElMessage.success("问卷提交成功！");
    } else {
      ElMessage.error("提交失败：" + (res.data.msg || "服务器繁忙"));
    }

  } catch (err) {
    console.error("提交过程报错:", err);
    ElMessage.error("系统连接失败，请检查网络");
  } finally {
    submitting.value = false;
  }
};

const backToCenter = () => {
  router.push('/detect');
};

const redoQuestionnaire = async () => {
  if (resetting.value) return;
  resetting.value = true;

  const routeId = route.query.id;
  const storageId = localStorage.getItem('current_patient_id');
  const finalPid = routeId || storageId;
  const diagnosisId = resultData.value.diagnosisId || route.query.caseId || localStorage.getItem('current_case_id');

  if (diagnosisId) {
    try {
      const res = await resetQuestionnaireResult({ diagnosisId, patientId: finalPid });
      if (!(res?.data?.success || res?.data?.code === 200)) {
        ElMessage.error(res?.data?.msg || '清空上次问诊结果失败，请重试');
        resetting.value = false;
        return;
      }
    } catch (error) {
      ElMessage.error('清空上次问诊结果失败，请检查网络后重试');
      resetting.value = false;
      return;
    }
  }

  stopAudio();
  submitting.value = false;
  isDone.value = false;
  questionnaireStarted.value = false;
  currentIndex.value = 0;
  answers.value = [];
  bmiHeight.value = 1.72;
  bmiWeight.value = 65.0;
  resultData.value = {
    kind: selectedTemplateCode.value === 'original' ? 'constitution' : 'special',
    mainType: '',
    scoreMap: {},
    diagnosisId: null,
    templateCode: selectedTemplateCode.value,
    templateResult: null,
    templateTitle: activeTemplate.value.title,
  };
  resetting.value = false;
};

const generateDiagnosisReport = () => {
  const routeId = route.query.id;
  const storageId = localStorage.getItem('current_patient_id');
  const finalPid = routeId || storageId;
  const idCard =
    route.query.idCard ||
    localStorage.getItem('current_patient_idCard') ||
    localStorage.getItem('current_patient_idcard') ||
    '';
  if (!finalPid) {
    ElMessage.error('未找到患者信息，无法生成报告');
    return;
  }
  navigateToDiagnosisReport(router, finalPid, idCard);
};

onMounted(() => {
  resetAnswers(QUESTIONNAIRE_TEMPLATE_MAP[selectedTemplateCode.value] || QUESTIONNAIRE_TEMPLATE_MAP.original);
});
watch([currentIndex, questionnaireStarted, selectedTemplateCode], () => playAudio());
</script>

<style scoped>
/* 问诊沿用卷轴背景，微调配色统一暖棕系 */
.wenjuan-wrapper {
  min-height: 100vh;
  display: flex; justify-content: center; align-items: center;
  position: relative; overflow: hidden;
  /* 使用更深的渐变背景以增强对比 */
  background: linear-gradient(180deg, #f6efe0 0%, #efe2c7 100%);
  padding: 40px 20px;
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
}

.wenjuan-wrapper::before, .wenjuan-wrapper::after {
  content: ""; position: absolute; top: 0; bottom: 0; width: 180px;
  pointer-events: none;
  z-index: 0;
}
.wenjuan-wrapper::before { left: 0;  box-shadow: inset -30px 0 40px rgba(0,0,0,0.06); }
.wenjuan-wrapper::after  { right: 0; box-shadow: inset  30px 0 40px rgba(0,0,0,0.06); }

.template-select-panel,
.main-content,
.finish-dialog {
  position: relative;
  z-index: 1;
}

.template-select-panel {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.template-select-card {
  width: 920px;
  max-width: calc(100% - 40px);
  position: relative;
  padding: 44px 40px;
  border-radius: 14px;
  background: linear-gradient(180deg, #fff9f0 0%, #f7ead0 100%);
  border: 1px solid rgba(150,100,45,.32);
  box-shadow: 0 24px 56px rgba(70,40,20,.12);
}

.template-title {
  margin: 0 0 8px;
  color: #4c2a10;
  font-size: 2rem;
}

.template-desc {
  margin: 0 0 24px;
  color: #7c5731;
  line-height: 1.8;
}

.template-topline {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(255, 252, 244, 0.7);
  border: 1px dashed rgba(150, 100, 45, 0.25);
  color: #7a522e;
  font-size: 0.95rem;
  margin-bottom: 16px;
}

.template-section {
  margin-bottom: 16px;
}

.template-section-head {
  margin-bottom: 10px;
}

.template-section-head h3 {
  margin: 0;
  color: #5a2d00;
  font-size: 1.08rem;
}

.template-section-head p {
  margin: 4px 0 0;
  color: #8b5f34;
  font-size: 0.92rem;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.template-item {
  padding: 18px 20px;
  border-radius: 12px;
  border: 1px solid rgba(200,169,110,.45);
  background: linear-gradient(180deg, #fffdf8 0%, #fff8eb 100%);
  box-shadow: 0 6px 18px rgba(100,60,10,.04);
  cursor: pointer;
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}

.template-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(70,40,20,.12);
}

.template-item.is-active {
  border-color: rgba(107,42,18,.85);
  background: linear-gradient(180deg, #fff2df 0%, #f9e4c6 100%);
}

.template-item-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.template-item-head h3 {
  margin: 0 0 6px;
  color: #4c2a10;
  font-size: 1.2rem;
}

.template-item-head p {
  margin: 0;
  color: #8a6340;
  line-height: 1.6;
}

.template-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #8b5f34;
  font-size: 0.95rem;
}

.template-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  justify-content: center;
  margin-top: 18px;
}

.selected-template-panel {
  margin-top: 6px;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid rgba(139, 61, 26, 0.18);
  background: linear-gradient(180deg, #fff6e8 0%, #fffaf1 100%);
  color: #6e4624;
}

.selected-template-panel .selected-title {
  margin: 0 0 4px;
  color: #5a2d00;
  font-weight: 700;
}

.selected-template-panel p {
  margin: 0;
  line-height: 1.6;
}

/* 隐藏旧的装饰元素（保持模板兼容） */
.ink-bg, .paper-texture, .blob { display: none !important; }

.quiz-card {
  width: 760px; max-width: calc(100% - 80px);
  backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px);
  border-radius: 12px; padding: 44px 48px;
  position: relative; z-index: 10;
  background: linear-gradient(180deg, #fff9f0 0%, #f7ead0 100%);
  border: 1px solid rgba(150,100,45,.32);
  box-shadow: 0 24px 56px rgba(70,40,20,.12);
}

/* 顶部金线 */
.quiz-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, transparent, #c8a020 50%, transparent);
  border-radius: 16px 16px 0 0;
}

/* 印章 — 颜色已符合系统红棕色 */
.tcm-seal {
  position: absolute; top: 26px; right: 42px;
  width: 64px; height: 64px;
  border: 2px solid #8b3d1a; color: #8b3d1a;
  font-family: "KaiTi", "Kaiti", serif;
  display: flex; align-items: center; justify-content: center;
  transform: rotate(15deg); font-weight: 700; opacity: 0.8;
  border-radius: 6px; font-size: 1.1rem;
  background: rgba(255,245,235,.6);
}

.header-nav { margin-bottom: 8px; }
.count b { font-size: 2rem; color: #8b3d1a; margin: 0 6px; }
.template-badge {
  margin-left: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(139,61,26,.08);
  color: #8b3d1a;
  font-size: 0.92rem;
}

.question-container { min-height: 340px; padding: 6px 0 6px; }
.question-text {
  font-size: 2.2rem; color: #3d2b10;
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
  line-height: 1.4; margin-bottom: 30px;
}
.q-index { color: #8b3d1a; margin-right: 12px; font-style: italic; font-weight: 700; }
.remark-text { font-size: 1rem; color: #9a7040; font-weight: 400; }

/* 选项 */
.options-grid { display: grid; gap: 14px; grid-template-columns: 1fr; max-width: 640px; margin: 0 auto; }
.option-box {
  display: flex; align-items: center; padding: 16px 24px; border-radius: 10px;
  cursor: pointer;
  transition: transform .25s ease, box-shadow .25s ease, background .25s ease;
  background: linear-gradient(180deg, #fffdf8 0%, #fffaf0 100%);
  border: 1px solid rgba(200,169,110,.5);
  box-shadow: 0 4px 16px rgba(100,60,10,.04);
}
.option-box:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(70,40,20,.12); }
.option-box.is-active {
  background: linear-gradient(180deg, #6b2a12 0%, #4f1a0a 100%);
  color: #fff3d9; border-color: rgba(90,40,15,.9);
  box-shadow: 0 18px 44px rgba(70,35,15,.18);
}
.opt-indicator {
  width: 46px; height: 46px; display: flex; align-items: center; justify-content: center;
  font-size: 1.05rem; font-weight: 700; color: #6b2a12; border-radius: 50%;
  background: rgba(139,61,26,.12); margin-right: 16px;
}
.option-box.is-active .opt-indicator { background: rgba(255,255,255,.15); color: #fdeabb; }
.opt-text { font-size: 1.1rem; color: inherit; }

/* BMI */
.bmi-input-area {
  background: linear-gradient(180deg, #fbf3e6, #f6e9cf);
  padding: 20px; border-radius: 10px;
  border: 1px solid #e6cfa0;
  display: flex; justify-content: space-between; align-items: center; gap: 16px;
}
.bmi-row { margin-bottom: 12px; display: flex; align-items: center; font-size: 1.05rem; }
.bmi-row .label { width: 64px; color: #6b4c24; font-weight: 700; }
.unit { margin-left: 10px; color: #9a7040; }
.bmi-result-panel {
  text-align: center;
  border-left: 1px dashed #e8d5a0; padding-left: 28px; min-width: 150px;
}
.bmi-val { font-size: 3rem; color: #6b2a12; font-weight: 800; }

.control-footer {
  margin-top: 40px; display: flex; justify-content: space-between; align-items: center;
  border-top: 1px solid #e8d5a0; padding-top: 26px;
}

/* 完成页 */
.finish-dialog {
  text-align: center; background: rgba(255,252,242,.98);
  padding: 56px; border-radius: 14px;
  border: 1px solid #c8a96e;
  box-shadow: 0 30px 80px rgba(100,50,10,.12); width: 620px;
}
.icon-wrapper { margin-bottom: 20px; }
.done-icon { font-size: 72px; color: #4a7060; }
.result-card {
  text-align: left;
  margin: 20px 0;
  padding: 20px;
  border-radius: 12px;
  background: linear-gradient(180deg, #faf3e0, #fffaf0);
  border: 1px solid #e8d5a0;
  box-shadow: 0 8px 24px rgba(100, 60, 10, 0.08);
}
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}
.result-kicker {
  margin: 0 0 6px;
  font-size: 12px;
  color: #9a7040;
  letter-spacing: 1px;
}
.result-header h3 {
  margin: 0;
  color: #5a2d00;
  font-size: 20px;
}
.result-summary {
  margin: 0 0 16px;
  color: #4a3020;
  line-height: 1.8;
}
.result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}
.result-block {
  padding: 14px;
  border-radius: 10px;
  background: #fff;
  border: 1px solid rgba(232, 213, 160, 0.9);
  text-align: left;
  margin-bottom: 12px;
}
.result-block h4 {
  margin: 0 0 10px;
  color: #5a2d00;
  font-size: 15px;
}
.result-block ul {
  margin: 0;
  padding-left: 18px;
  color: #4a3020;
  line-height: 1.7;
}
.result-block li { margin: 6px 0; }
.result-block.danger {
  background: #fff7f4;
  border-color: rgba(192, 57, 43, 0.22);
}
.score-rule {
  margin: 0 0 8px;
  color: #725130;
  line-height: 1.6;
}
.next-step-box {
  background: linear-gradient(180deg, #faf3e0, #f5eacc);
  padding: 20px; border-radius: 10px;
  margin: 20px 0; border: 1px solid #e8d5a0;
}
.next-step-box p { font-size: 1.05rem; color: #5a2d00; font-weight: 700; margin-bottom: 6px; }
.next-step-box small { color: #9a7040; }
.final-btn { padding: 16px 52px; font-size: 1.05rem; }
.finish-actions { display: flex; flex-wrap: wrap; gap: 14px; justify-content: center; margin-top: 8px; }

/* 动画 */
.q-slide-enter-active, .q-slide-leave-active { transition: all .38s cubic-bezier(.2,.9,.2,1); }
.q-slide-enter-from { opacity: 0; transform: translateX(26px); }
.q-slide-leave-to   { opacity: 0; transform: translateX(-26px); }

@media (max-width: 960px) {
  .template-select-card { padding: 30px 18px; }
  .template-topline { flex-direction: column; }
  .template-grid { grid-template-columns: 1fr; }
  .template-item-head { flex-direction: column; }
  .template-actions { justify-content: stretch; }
  .template-actions .el-button { flex: 1; }
  .quiz-card { padding: 34px 24px; }
  .question-text { font-size: 1.6rem; }
  .opt-indicator { width: 40px; height: 40px; margin-right: 12px; }
  .finish-dialog { width: min(760px, calc(100% - 24px)); padding: 30px 18px; }
  .result-grid { grid-template-columns: 1fr; }
  .result-header { flex-direction: column; }
}

.reference-note {
  font-size: 12px; color: #5d7a8a; line-height: 1.6;
  background: #f0f4ff; padding: 8px 12px; border-radius: 6px;
  border-left: 3px solid #5d9cec; text-align: left;
}

.reference-section {
  margin-top: 12px; padding: 10px; background: #f0f4ff;
  border: 1px solid #d0e0ff; border-radius: 6px;
}

.ref-title {
  font-size: 12px; font-weight: 600; color: #333;
  margin: 0 0 8px 0;
}

.ref-list {
  display: flex; flex-direction: column; gap: 8px;
}

.ref-item {
  padding: 8px; background: #fff;
  border-left: 2px solid #5d9cec; border-radius: 3px;
  font-size: 11px;
}

.ref-authors {
  display: block; color: #666; font-weight: 600;
  margin-bottom: 3px;
}

.ref-desc {
  margin: 3px 0; color: #666; line-height: 1.4;
}

.ref-link {
  display: inline-block; color: #5d9cec; text-decoration: none;
  font-size: 10px; margin-top: 3px;
  transition: all 0.2s;
}

.ref-link:hover {
  color: #1890ff; text-decoration: underline;
}
</style>
