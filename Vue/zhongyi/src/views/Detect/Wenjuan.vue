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
        </div>
        <el-button type="primary" size="large" round @click="backToCenter" class="final-btn">
          返回诊断中心
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { CircleCheckFilled } from '@element-plus/icons-vue';
import axios from 'axios';
import { submitQuestionnaire } from '@/api/detect';
const router = useRouter();
const audio = new Audio();

// 核心状态
const currentIndex = ref(0);
const answers = ref(new Array(33).fill(null));
const isDone = ref(false);
const submitting = ref(false);

// BMI 逻辑
const bmiHeight = ref(1.72);
const bmiWeight = ref(65.0);
const computedBMI = computed(() => (bmiWeight.value / (bmiHeight.value * bmiHeight.value)).toFixed(1));

// 完整题目数据
const questions = [
  { content: "您精力充沛吗?", remark: "指精神头足, 乐于做事" },
  { content: "您容易疲乏吗?", remark: "指体力如何, 动一下就累" },
  { content: "您容易气短吗，呼吸短促, 接不上气", remark: "" },
  { content: "您说话声音低弱无力吗?", remark: "指说话没有力气" },
  { content: "您感到闷闷不乐，情绪低沉", remark: "指心情不愉快, 情绪低落" },
  { content: "您容易精神紧张，焦虑不安吗", remark: "指遇事是否容易紧张" },
  { content: "您因为生活状态改变而感到孤独、失落吗?", remark: "" },
  { content: "您容易感到害怕或受到惊吓吗?", remark: "" },
  { content: "您感到身体超重不轻松吗", remark: "系统将通过身高体重自动计算BMI指数" }, // Index 8
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

// 音频播放
const playAudio = () => {
  audio.pause();
  audio.src = `/src/assets/audio/question/${currentIndex.value + 1}.wav`;
  audio.play().catch(() => {});
};

// 交互操作
const handleSelect = (val) => {
  answers.value[currentIndex.value] = val;
  // 自动跳转下一题
  if (currentIndex.value < 32 ) {
    setTimeout(() => currentIndex.value++, 300);
  }
};

const handleBMIFinish = () => {
  const bmiVal = parseFloat(computedBMI.value);
  let score = 1;
  if (bmiVal >= 28) score = 5;
  else if (bmiVal >= 25) score = 3; // 中医简易BMI评分逻辑
  answers.value[8] = score;
  currentIndex.value++;
};

const goNext = () => currentIndex.value++;
const goPrev = () => currentIndex.value--;

// 核心：提交到后端并显示引导页
const handleFinish = async () => {
  if (submitting.value) return;
  submitting.value = true;

  try {
    // 去缓存拿 ID，不引用那个报错的 patientInfo
    const pid = localStorage.getItem('current_patient_id');
    const idCard = localStorage.getItem('current_patient_idcard');

    console.log("==== [DEBUG] 尝试提交，从缓存获取到的 ID:", pid);

    if (!pid) {
      // 如果没拿到ID，说明你之前的页面没存好，或者你直接刷新的问卷页
      alert("错误：没找到病人ID，请先去登记病人信息！");
      submitting.value = false;
      return;
    }

    // 构造发送给后端的数据
    const postData = {
      // 这里的 answers 和 computedBMI 确保你组件里有定义这两个变量
      answers: answers.value,
      bmi: computedBMI.value,
      idCard: idCard,
      patientId: pid 
    };

    const res = await submitQuestionnaire(postData);

    if (res.data.success || res.data.code === 200) {
      const pid = localStorage.getItem('current_patient_id');
      localStorage.setItem('wenjuan_finished_id', pid);
      isDone.value = true;
    } else {
      alert("后端拒收了数据：" + (res.data.msg || "未知原因"));
    }

  } catch (err) {
    console.error("提交过程报错:", err);
    // 这里会打印具体的错误，比如是不是 answers 也没定义
    alert("提交失败，请按F12查看控制台 Console 的红色错误");
  } finally {
    submitting.value = false;
  }
};

// 返回选择中心
const backToCenter = () => {
  router.push('/detect');
};

onMounted(() => playAudio());
watch(currentIndex, () => playAudio());
</script>

<style scoped>
.wenjuan-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  background: url('../../assets/images/answerDialog/background_scroll.png') no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
  padding: 40px 20px;
}

.wenjuan-wrapper::before,
.wenjuan-wrapper::after {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  width: 180px;
  pointer-events: none;
  background-repeat: no-repeat;
  background-position: center top;
  background-size: contain;
  opacity: 0.95;
}
.wenjuan-wrapper::before { left: 0; background-image: linear-gradient(135deg, rgba(29,151,108,0.06) 0%, rgba(29,151,108,0.0) 60%); box-shadow: inset -30px 0 40px rgba(0,0,0,0.08); }
.wenjuan-wrapper::after { right: 0; background-image: linear-gradient(-135deg, rgba(29,151,108,0.06) 0%, rgba(29,151,108,0.0) 60%); box-shadow: inset 30px 0 40px rgba(0,0,0,0.08); }

.ink-bg { position: absolute; inset: 0; pointer-events: none; z-index: 1; }
.blob { width: 760px; height: 760px; background: radial-gradient(circle, rgba(93, 102, 90, 0.06) 0%, transparent 70%); position: absolute; top: -160px; right: -80px; filter: blur(8px); }
.paper-texture { position: absolute; inset: 0; opacity: 0.08; pointer-events: none; background-image: url('https://www.transparenttextures.com/patterns/natural-paper.png'); mix-blend-mode: multiply; z-index: 2; }

.quiz-card {
  width: 920px;
  max-width: calc(100% - 120px);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  border-radius: 20px;
  padding: 56px 64px;
  position: relative;
  z-index: 10;
  background: linear-gradient(180deg, rgba(255,255,250,0.98) 0%, rgba(255,250,240,0.9) 100%);
  border: 1px solid rgba(210,185,140,0.35);
  box-shadow: 0 30px 60px rgba(20,20,20,0.08), inset 0 1px 0 rgba(255,255,255,0.6);
}

.tcm-seal {
  position: absolute;
  top: 26px;
  right: 42px;
  width: 64px;
  height: 64px;
  border: 2px solid #a62c2b;
  color: #a62c2b;
  font-family: "Kaiti", serif;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: rotate(15deg);
  font-weight: 700;
  opacity: 0.85;
  border-radius: 6px;
  font-size: 1.1rem;
  background: rgba(255,245,240,0.6);
}

.header-nav { margin-bottom: 8px; }
.count b { font-size: 2rem; color: #4b5b4f; margin: 0 6px; }

.question-container { min-height: 380px; padding: 12px 0 6px; }
.question-text { font-size: 2.2rem; color: #21313a; font-family: "Source Han Serif CN", serif; line-height: 1.4; margin-bottom: 30px; }
.q-index { color: #476054; margin-right: 12px; font-style: italic; font-weight: 700; }
.remark-text { font-size: 1rem; color: #7a7a7a; font-weight: 400; }

.options-grid { display: grid; gap: 14px; }
.option-box {
  display: flex; align-items: center; padding: 18px 26px; border-radius: 14px;
  cursor: pointer; transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
  background: linear-gradient(180deg,#fffdf8 0%, #fffaf0 100%);
  border: 1px solid rgba(230,225,215,0.8);
  box-shadow: 0 6px 20px rgba(35,41,37,0.03);
}
.option-box:hover { transform: translateX(8px); box-shadow: 0 14px 30px rgba(60,70,60,0.08); }
.option-box.is-active { background: linear-gradient(180deg,#5d665a 0%, #525a50 100%); color: #fff; border-color: rgba(80,88,80,0.9); box-shadow: 0 20px 40px rgba(80,90,80,0.15); }
.opt-indicator { width: 48px; height: 48px; display:flex; align-items:center; justify-content:center; font-size:1.1rem; font-weight:700; color: #5d665a; border-radius: 50%; background: rgba(93,102,90,0.06); margin-right: 18px; }
.option-box.is-active .opt-indicator { background: rgba(255,255,255,0.12); color: #fff; }
.opt-text { font-size: 1.15rem; color: inherit; }

/* BMI 样式 */
.bmi-input-area { background: linear-gradient(180deg,#fbfbf9,#f7f5ee); padding: 30px; border-radius: 16px; border: 1px solid rgba(230,225,215,0.7); display: flex; justify-content: space-between; align-items: center; gap: 20px; }
.bmi-row { margin-bottom: 12px; display: flex; align-items: center; font-size: 1.05rem; }
.bmi-row .label { width: 64px; color: #4b5b4f; font-weight: 700; }
.unit { margin-left: 10px; color: #8b8b8b; }
.bmi-result-panel { text-align: center; border-left: 1px dashed rgba(120,120,120,0.12); padding-left: 32px; min-width: 160px; }
.bmi-val { font-size: 3.2rem; color: #476054; font-weight: 800; }

.control-footer { margin-top: 42px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(240,238,233,0.7); padding-top: 28px; }

/* 完成页样式 */
.finish-dialog { text-align: center; background: rgba(255,255,255,0.98); padding: 64px; border-radius: 18px; box-shadow: 0 30px 80px rgba(0,0,0,0.12); width: 620px; }
.icon-wrapper { margin-bottom: 20px; }
.done-icon { font-size: 72px; color: #67c23a; }
.next-step-box { background: linear-gradient(180deg,#fffaf5,#fff7ee); padding: 22px; border-radius: 12px; margin: 22px 0; border: 1px solid rgba(240,236,228,0.6); }
.next-step-box p { font-size: 1.05rem; color: #4b5b4f; font-weight: 700; margin-bottom: 6px; }
.next-step-box small { color: #8e8e8e; }
.final-btn { padding: 18px 56px; font-size: 1.05rem; }

/* 动画 */
.q-slide-enter-active, .q-slide-leave-active { transition: all 0.38s cubic-bezier(.2,.9,.2,1); }
.q-slide-enter-from { opacity: 0; transform: translateX(26px); }
.q-slide-leave-to { opacity: 0; transform: translateX(-26px); }

@media (max-width: 960px) {
  .quiz-card { padding: 36px 28px; }
  .question-text { font-size: 1.6rem; }
  .opt-indicator { width: 40px; height: 40px; margin-right: 12px; }
}

</style>