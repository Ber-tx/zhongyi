<template>
  <div class="wenjuan-wrapper">
    <div class="ink-bg"><div class="blob"></div></div>
    <div class="paper-texture"></div>

    <div class="main-content" v-if="!isDone">
      <div class="quiz-card">
        <div class="tcm-seal">问诊采集</div>
        
        <div class="header-nav">
          <div class="progress-info">
            <span class="count">第 <b>{{ currentIndex + 1 }}</b> / 33 题</span>
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

            <div v-if="currentIndex === 8" class="bmi-input-area">
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
                v-for="(label, idx) in currentOptions" 
                :key="idx"
                class="option-box"
                :class="{ 'is-active': answers[currentIndex] === (idx + 1) }"
                @click="handleSelect(idx + 1)"
              >
                <div class="opt-indicator">{{ String.fromCharCode(65 + idx) }}</div>
                <div class="opt-text">{{ label }}</div>
              </div>
            </div>
          </div>
        </transition>

        <div class="control-footer">
          <el-button @click="goPrev" :disabled="currentIndex === 0" round size="large">上一题</el-button>
          
          <div class="action-group">
            <el-button v-if="currentIndex === 8" type="primary" round size="large" @click="handleBMIFinish">确认并继续</el-button>
            <el-button v-else-if="currentIndex === 32" type="success" round size="large" @click="handleFinish" :loading="submitting" :disabled="!answers[currentIndex]">
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
        <p class="desc">您的 33 项问诊指标已成功同步至诊断系统。</p>
        <div class="next-step-box">
          <p>请返回诊断中心继续完成其他检测项目</p>
          <small>（例如：面色采集、舌苔检测等）</small>
          <div class="reference-section" style="margin-top: 16px;">
            <p class="ref-title">📖 参考文献与出处</p>
            <div class="ref-list">
              <div v-for="(ref, idx) in wen_qReferences" :key="idx" class="ref-item">
                <span class="ref-authors">{{ ref.authors }} ({{ ref.year }})</span>
                <p class="ref-desc">{{ ref.title }}</p>
                <a v-if="ref.url" :href="ref.url" target="_blank" class="ref-link">
                  查看 → {{ ref.source }}
                </a>
              </div>
            </div>
          </div>
        </div>
        <div class="finish-actions">
          <el-button type="primary" size="large" round @click="generateDiagnosisReport" class="final-btn">
            生成报告
          </el-button>
          <el-button type="success" size="large" round plain @click="backToCenter" class="final-btn">
            返回诊断中心
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
import { submitQuestionnaire } from '@/api/detect';
import { navigateToDiagnosisReport } from '@/utils/reportUtils';
import { algorithmReferences } from '@/constants/algorithmReferences';

const router = useRouter();
const route = useRoute(); // 【核心修复】初始化 route 对象
const audio = new Audio();

// 核心状态
const currentIndex = ref(0);
const answers = ref(new Array(33).fill(null));
const isDone = ref(false);
const submitting = ref(false);
const wen_qReferences = ref(algorithmReferences.wen_questionnaire.references);

// BMI 逻辑
const bmiHeight = ref(1.72);
const bmiWeight = ref(65.0);
const computedBMI = computed(() => (bmiWeight.value / (bmiHeight.value * bmiHeight.value)).toFixed(1));

// 题目数据（保持不变...）
const questions = [
  { content: "您精力充沛吗?", remark: "指精神头足, 乐于做事" },
  { content: "您容易疲乏吗?", remark: "指体力如何, 动一下就累" },
  { content: "您容易气短吗，呼吸短促, 接不上气", remark: "" },
  { content: "您说话声音低弱无力吗?", remark: "指说话没有力气" },
  { content: "您感到闷闷不乐，情绪低沉", remark: "指心情不愉快, 情绪低落" },
  { content: "您容易精神紧张，焦虑不安吗", remark: "指遇事是否容易紧张" },
  { content: "您因为生活状态改变而感到孤独、失落吗?", remark: "" },
  { content: "您容易感到害怕或受到惊吓吗?", remark: "" },
  { content: "您感到身体超重不轻松吗", remark: "系统将通过身高体重自动计算BMI指数" }, 
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

const defaultOpts = ["没有(根本不)", "很少(有一点)", "有时(有些)", "经常(相当)", "总是(非常)"];

const currentQuestion = computed(() => questions[currentIndex.value]);
const currentOptions = computed(() => currentQuestion.value.options || defaultOpts);
const progress = computed(() => Math.round(((currentIndex.value + 1) / 33) * 100));

// 音频播放逻辑
const playAudio = () => {
  audio.pause();
  audio.src = `/src/assets/audio/question/${currentIndex.value + 1}.wav`;
  audio.play().catch(() => {});
};

// 交互操作
const handleSelect = (val) => {
  answers.value[currentIndex.value] = val;
  if (currentIndex.value < 32) {
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
    const postData = {
      answers: answers.value,
      bmi: computedBMI.value,
      idCard: finalIdCard,
      patientId: finalPid,
      diagnosisId: route.query.caseId || localStorage.getItem('current_case_id')
    };

    const res = await submitQuestionnaire(postData);

    if (res.data.success || res.data.code === 200) {
      // 【关键修复】将完成状态与当前这个 finalPid 绑定，而不是笼统的 true/false
      localStorage.setItem('wenjuan_finished_id', String(finalPid));
      
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

onMounted(() => playAudio());
watch(currentIndex, () => playAudio());
</script>

<style scoped>
/* 问诊沿用卷轴背景，微调配色统一暖棕系 */
.wenjuan-wrapper {
  min-height: 100vh;
  display: flex; justify-content: center; align-items: center;
  position: relative; overflow: hidden;
  background: url('../../assets/images/answerDialog/background_scroll.png') no-repeat center center;
  background-size: cover; background-attachment: fixed;
  padding: 40px 20px;
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
}

.wenjuan-wrapper::before, .wenjuan-wrapper::after {
  content: ""; position: absolute; top: 0; bottom: 0; width: 180px;
  pointer-events: none;
}
.wenjuan-wrapper::before { left: 0;  box-shadow: inset -30px 0 40px rgba(0,0,0,0.06); }
.wenjuan-wrapper::after  { right: 0; box-shadow: inset  30px 0 40px rgba(0,0,0,0.06); }

.ink-bg { position: absolute; inset: 0; pointer-events: none; z-index: 1; }
.blob {
  width: 760px; height: 760px;
  background: radial-gradient(circle, rgba(139,61,26,.05) 0%, transparent 70%);
  position: absolute; top: -160px; right: -80px; filter: blur(8px);
}
.paper-texture {
  position: absolute; inset: 0; opacity: 0.07; pointer-events: none;
  background-image: url('https://www.transparenttextures.com/patterns/natural-paper.png');
  mix-blend-mode: multiply; z-index: 2;
}

.quiz-card {
  width: 920px; max-width: calc(100% - 120px);
  backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
  border-radius: 16px; padding: 56px 64px;
  position: relative; z-index: 10;
  background: linear-gradient(180deg, rgba(255,252,242,.98) 0%, rgba(255,248,230,.92) 100%);
  border: 1px solid rgba(200,169,110,.4);
  box-shadow: 0 30px 60px rgba(100,50,10,.10), inset 0 1px 0 rgba(255,255,255,.6);
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

.question-container { min-height: 380px; padding: 12px 0 6px; }
.question-text {
  font-size: 2.2rem; color: #3d2b10;
  font-family: 'Noto Serif SC', "Source Han Serif CN", serif;
  line-height: 1.4; margin-bottom: 30px;
}
.q-index { color: #8b3d1a; margin-right: 12px; font-style: italic; font-weight: 700; }
.remark-text { font-size: 1rem; color: #9a7040; font-weight: 400; }

/* 选项 */
.options-grid { display: grid; gap: 12px; }
.option-box {
  display: flex; align-items: center; padding: 16px 24px; border-radius: 10px;
  cursor: pointer;
  transition: transform .25s ease, box-shadow .25s ease, background .25s ease;
  background: linear-gradient(180deg, #fffdf8 0%, #fffaf0 100%);
  border: 1px solid rgba(200,169,110,.5);
  box-shadow: 0 4px 16px rgba(100,60,10,.04);
}
.option-box:hover { transform: translateX(8px); box-shadow: 0 10px 24px rgba(100,60,10,.10); }
.option-box.is-active {
  background: linear-gradient(180deg, #8b3d1a 0%, #6b2d12 100%);
  color: #fdeabb; border-color: rgba(139,61,26,.8);
  box-shadow: 0 16px 32px rgba(139,61,26,.2);
}
.opt-indicator {
  width: 46px; height: 46px; display: flex; align-items: center; justify-content: center;
  font-size: 1.05rem; font-weight: 700; color: #8b3d1a; border-radius: 50%;
  background: rgba(139,61,26,.08); margin-right: 16px;
}
.option-box.is-active .opt-indicator { background: rgba(255,255,255,.15); color: #fdeabb; }
.opt-text { font-size: 1.1rem; color: inherit; }

/* BMI */
.bmi-input-area {
  background: linear-gradient(180deg, #faf3e0, #f5eacc);
  padding: 28px; border-radius: 12px;
  border: 1px solid #e8d5a0;
  display: flex; justify-content: space-between; align-items: center; gap: 20px;
}
.bmi-row { margin-bottom: 12px; display: flex; align-items: center; font-size: 1.05rem; }
.bmi-row .label { width: 64px; color: #6b4c24; font-weight: 700; }
.unit { margin-left: 10px; color: #9a7040; }
.bmi-result-panel {
  text-align: center;
  border-left: 1px dashed #e8d5a0; padding-left: 28px; min-width: 150px;
}
.bmi-val { font-size: 3rem; color: #8b3d1a; font-weight: 800; }

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
  .quiz-card { padding: 34px 24px; }
  .question-text { font-size: 1.6rem; }
  .opt-indicator { width: 40px; height: 40px; margin-right: 12px; }
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
