<template>
  <div class="archive-overlay">
    <div class="paper-texture"></div>
    
    <audio ref="audioPlayer" preload="none"></audio>
    
    <header class="floating-header">
      <button class="modern-back" @click="handleBack">
        <span class="icon">❮</span> 退出
      </button>
      <div class="header-info">{{ currentConfig?.title }} · 数字化图志</div>
    </header>

    <div 
      class="scrubber-container" 
      ref="scrubberRef"
      @mousemove="handleScrubberMove" 
      @mouseleave="handleScrubberLeave"
      @click="handleScrubberClick"
    >
      <div class="scrubber-track">
        <div class="scrubber-fill" :style="{ width: progress + '%' }"></div>
      </div>

      <transition name="fade">
        <div 
          v-if="hoveredIndex !== null" 
          class="scrubber-preview"
          :style="{ left: previewPos + 'px' }"
        >
          <div class="p-img-box">
            <img
              :src="getImageUrl(props.id || '1', archiveList[hoveredIndex]?.pageNum)"
              alt="preview"
              loading="lazy"
              decoding="async"
            />
            <div class="p-page-badge">P{{ hoveredIndex + 1 }}</div>
          </div>
          <div class="p-content">
            <div class="p-title">{{ archiveList[hoveredIndex]?.title }}</div>
          </div>
        </div>
      </transition>
    </div>

    <div class="viewer-layout">
      <div class="scroll-container" ref="scrollContainer" @scroll="handleScroll">
        <div v-for="(item, index) in archiveList" :key="index" class="scroll-item">
          <div class="image-wrapper">
            <div v-if="index === 0 && !firstImageReady" class="first-image-loading">首图加载中...</div>
            <img v-if="Math.abs(index - currentIndex) <= 3 && !(index === 0 && !firstImageReady)"
              :src="getImageUrl(props.id || '1', item.pageNum)"
              class="archive-img"
              :loading="index === currentIndex ? 'eager' : 'lazy'"
              :fetchpriority="index === currentIndex ? 'high' : 'auto'"
              decoding="async"
            />
            <div v-else class="archive-img-placeholder"></div>
          </div>
        </div>
      </div>
    </div>

    <footer class="compact-footer" v-if="archiveList.length > 0">
      <div class="mini-progress-track">
        <div class="bar" :style="{ width: progress + '%' }"></div>
      </div>

      <div class="control-row">
        <div class="audio-control" @click="toggleMute">
          <div class="audio-waves" :class="{ 'is-active': !isMuted }">
            <span class="wave-bar"></span>
            <span class="wave-bar"></span>
            <span class="wave-bar"></span>
          </div>
          <span class="audio-label">{{ isMuted ? '播放讲解' : '正在讲解' }}</span>
        </div>

        <nav class="modern-pagination">
          <button class="p-btn" @click="goToPage(currentIndex-1)" :disabled="currentIndex===0">PREV</button>
          <div class="p-numbers">
             <span class="p-current">{{ currentIndex + 1 }}</span>
             <span class="p-divider">/</span>
             <span class="p-total">{{ archiveList.length }}</span>
          </div>
          <button class="p-btn" @click="goToPage(currentIndex+1)" :disabled="currentIndex >= archiveList.length - 1">NEXT</button>
        </nav>

        <div class="modern-jump">
          <input type="number" v-model.number="jumpPage" :min="1" :max="archiveList.length" />
          <button class="jump-action" @click="goToPage(jumpPage - 1)">跳转</button>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// --- 接收 ID 识别板块 ---
const props = defineProps(['id'])
const router = useRouter()
const route = useRoute()

// --- 全局板块配置数据库 ---
const ARCHIVE_DATA = {
  "1": {
    title: "中医治未病",
    total: 25,
    rules: [
      [1, 2, "目录索引"], [3, 3, "中医治未病的内涵"], [4, 5, "何为“未病”"],
      [6, 10, "中医治未病的思想原则"], [11, 11, "亚健康是未病的表现形式"],
      [12, 12, "如何治未病"], [13, 14, "亚健康的人群有哪些"],
      [15, 15, "亚健康的临床特点"], [16, 16, "亚健康的分类"],
      [17, 18, "合理膳食的十字经"], [19, 23, "中医的养生境界就是“治未病”"],
      [24, 24, "简单养生方法"], [25, 25, "特别推荐可以多吃的食物"]
    ]
  },
  "2": {
    title: "音乐养生",
    total: 18,
    rules: [
      [1, 2, "目录索引"], [3, 3, "音乐养生导览"], [4, 5, "传统音乐疗法"],
      [6, 8, "情绪调节音乐选择"], [12, 12, "音乐与生理关系"], [16, 18, "音乐处方"]
    ]
  },
  "3": {
    title: "0-6岁儿童健康指导",
    total: 44,
    rules: [
    [1, 1, "目录"],
    [2, 4, "小儿的生理病理特点"],
    [5, 8, "小儿保健中的常用望诊方法"],
    [9, 19, "小儿日常保健"],
    [20, 37, "小儿常见疾病的保健方法"],
    [38, 41, "十个常见推拿穴位保健"],
    [42, 44, "小儿常见中成药"]
    ]
  },
  "5": {
    title: "常见慢性病保健",
    total: 69,
    rules: [
    [1, 3, "目录"],
    [4, 9, "高脂血症的预防与日常保健"],
    [10, 20, "脑血管病的预防与日常保健"],
    [21, 22, "高血压病人的家庭护理"],
    [23, 24, "走路是高血压患者的最佳运动"],
    [25, 26, "冠心病患者睡眠前的自我护理"],
    [27, 30, "有氧运动抵抗心脏的衰老"],
    [30, 32, "支气管哮喘病人的家庭护理"],
    [33, 34, "预防控制糖尿病"],
    [35, 36, "糖尿病患者的家庭护理"],
    [37, 43, "减肥与肥胖病的预防"],
    [44, 50, "高血压人群的健康食膳忠告"],
    [51, 57, "高血糖（糖尿病）人群的健康食膳忠告"],
    [58, 59, "高血脂人群的健康食膳忠告"],
    [60, 62, "糖尿病伴高血压高血脂症患者参考食谱"],
    [63, 66, "肿瘤病人的健康食膳忠告"],
    [67, 67, "冠心病病人的饮食调理"],
    [68, 69, "高血压的食疗"]
    ]
  },
  "6": {
    title: "情志调摄——心理健康",
    total: 59,
    rules: [
    [1, 3, "目录"],
    [4, 6, "情志"],
    [7, 10, "情志的调摄"],
    [11, 12, "如何清净养神？"],
    [13, 13, "何谓修性怡神法"],
    [14, 17, "心理健康的十大标准"],
    [18, 18, "心理健康的人所具备的品质"],
    [19, 19, "中医对精神调摄的理解"],
    [20, 20, "健康的基石之首是"],
    [21, 22, "心理平衡中庸之道”乃幸福之道"],
    [23, 25, "天堂与地狱”就在你心中"],
    [26, 27, "多想幸福的，少想不幸的"],
    [28, 31, "职场白领的心理减压处方"],
    [32, 32, "何谓心理疲劳"],
    [33, 33, "产生心理疲劳的原因"],
    [34, 34, "心理疲劳造成的后果是什么"],
    [35, 36, "心理疲劳的调节技巧"],
    [37, 38, "消除心理疲劳的方法"],
    [39, 39, "何谓焦虑症"],
    [40, 41, "抑郁情绪和抑郁症的区别"],
    [42, 42, "幸福指数十要素"],
    [43, 43, "负面情绪对机体的不良影响"],
    [44, 59, "介绍几种心理小测验"]
    ]
  },
  "7": {
    title: "SLEEP/睡眠养生",
    total: 53,
    rules: [
    [1, 3, "目录"],
    [4, 4, "失眠的定义"],
    [5, 5, "失眠按临床医学表现分类"],
    [6, 6, "睡眠按严重程序分类"],
    [7, 7, "睡眠按周期分类"],
    [8, 9, "睡眠的中医分类"],
    [10, 12, "失眠的常见原因"],
    [13, 13, "现代神经生理学对失眠研究进展"],
    [14, 15, "孕妇失眠的常见原因"],
    [16, 18, "失眠的催眠疗法"],
    [19, 23, "推荐失眠的食物疗法"],
    [24, 25, "提高睡眠的六个良好建议"],
    [26, 27, "提高睡眠质量的十个方法"],
    [28, 29, "注意失眠的九大忌宜"],
    [30, 31, "预防失眠的妙括"],
    [32, 33, "失眠的心理护理"],
    [34, 36, "失眠的日常理法"],
    [37, 39, "老年人如何克服失眠"],
    [40, 41, "老年人慎服安眠药"],
    [42, 43, "促进良好睡眠的外部环境"],
    [44, 46, "失眠常见的危害"],
    [47, 49, "治疗失眠的中药药膳粥"],
    [50, 51, "睡眠养生法"],
    [52, 53, "睡眠是最好的养生"]
    ]
  },
  "8": {
    title: "休闲养生",
    total: 28,
    rules: [
    [1, 1, "目录"],
    [2, 7, "琴与音乐"],
    [8, 11, "弈棋"],
    [12, 15, "书画"],
    [16, 20, "花木"],
    [21, 22, "垂钓"],
    [23, 28, "旅游"]
    ]
  },
  "9": {
    title: "节气养生",
    total: 160,
    rules: [
    [1, 5, "目录"],
    [6, 8, "节气养生"],
    [9, 10, "二十四节气"],
    [11, 15, "一、春光正好时 - （一）、立春（2月4/5日）"],
    [16, 20, "一、春光正好时 - （二）、雨水（2月19/20日）"],
    [21, 30, "一、春光正好时 - （三）、惊蛰（3月5/6日）"],
    [32, 37, "一、春光正好时 - （四）、春分（3月20/21日）"],
    [38, 41, "一、春光正好时 - （五）、清明（4月4/5日）"],
    [41, 49, "一、春光正好时 - （六）、谷雨（4月20/21日）"],
    [50, 54, "二、夏日当头时 - （一）、立夏（5月5/6日）"],
    [55, 62, "二、夏日当头时 - （二）、小满（5月21/22日）"],
    [63, 65, "二、夏日当头时 - （三）、芒种（6月5/6日）"],
    [66, 70, "二、夏日当头时 - （四）、夏至（6月21/22日）"],
    [71, 74, "二、夏日当头时 - （五）、小暑（7月7/8日）"],
    [75, 81, "二、夏日当头时 - （六）、大暑（7月23/24日）"],
    [82, 86, "三、秋风送爽时 - （一）、立秋（8月7/8日）"],
    [87, 93, "三、秋风送爽时 - （二）、处暑（8月23/24日）"],
    [94, 99, "三、秋风送爽时 - （三）、白露（9月7/8日）"],
    [100, 107, "三、秋风送爽时 - （四）、秋分（9月23/24日）"],
    [108, 113, "三、秋风送爽时 - （五）、寒露（10月8/9日）"],
    [114, 122, "三、秋风送爽时 - （六）、霜降（10月23/24日）"],
    [123, 126, "四、冬挂冰凌时 - （一）、立冬（11月7/8日）"],
    [127, 130, "四、冬挂冰凌时 - （二）、小雪（11月22/23日）"],
    [131, 137, "四、冬挂冰凌时 - （三）、大雪（12月7/8日）"],
    [138, 147, "四、冬挂冰凌时 - （四）、冬至（12月21/22日）"],
    [148, 152, "四、冬挂冰凌时 - （五）、小寒（1月5/6日）"],
    [153, 160, "四、冬挂冰凌时 - （六）、大寒（1月20/21日）"]
    ]
  },
  "4-1": {
    title: "妇婴保健—产妇",
    total: 50,
    rules: [
    [1, 3, "目录"],
    [4, 7, "产妇中医保健"],
    [8, 8, "乳腺炎的中医药治疗"],
    [9, 9, "产后乳汁少的中药方"],
    [10, 13, "产妇的个人卫生"],
    [14, 15, "产后运动注意事项"],
    [16, 20, "产妇饮食禁忌哺乳期妇女外用药要慎用"],
    [21, 23, "母乳喂养的重要性"],
    [24, 24, "初乳对宝宝的重要性"],
    [25, 25, "正确的哺乳体位"],
    [26, 26, "如何帮助宝宝吸吃奶"],
    [27, 27, "关于哺乳用品的准备"],
    [28, 28, "喂哺时间有何规定？"],
    [29, 29, "注意哺乳用具的卫生和消毒"],
    [30, 30, "如何增加产妇乳汁？"],
    [31, 31, "如何增加哺乳母亲自身营养？"],
    [32, 38, "产后常见症状的中医膳食调理"],
    [39, 50, "产后抑郁症"]
    ]
  },
  "4-2": {
    title: "妇女中医保健",
    total: 17,
    rules: [
    [1, 2, "目录"],
    [3, 5, "经期保健"],
    [6, 9, "更年期保健"],
    [10, 17, "乳腺癌预防"]
    ]
  },
  "4-3": {
    title: "妇婴保健—婴幼儿",
    total: 43,
    rules: [
    [1, 4, "目录"],
    [5, 5, "新生儿的体格特征"],
    [6, 6, "新生宝宝的体重为何有变化"],
    [7, 7, "新生儿的皮肤特征"],
    [8, 8, "如何清洁新生宝宝的肚脐"],
    [9, 9, "如何保护新生宝宝免遭感染"],
    [10, 11, "宝宝为什么夜哭？"],
    [12, 12, "新生儿会看吗？"],
    [13, 13, "新生儿的听觉能力"],
    [14, 14, "新生儿会交流吗？"],
    [15, 15, "怎样防止宝宝便秘？"],
    [16, 16, "一定要让宝宝多呼吸新鲜空气"],
    [17, 17, "适当的日照对宝宝有好处十三"],
    [18, 18, "如何为宝宝添加辅食？"],
    [19, 19, "宝宝睡觉时多汗是病吗？"],
    [20, 21, "导致宝宝睡眠不安的因素有哪些？"],
    [22, 22, "如何防止宝宝发生缺铁性贫血？"],
    [23, 23, "夏天谨防宝宝空调病"],
    [24, 24, "按时带宝宝到医院预防接种"],
    [25, 27, "拇食指推拿治疗婴幼儿湿疹"],
    [28, 33, "中医药治疗小儿感冒发热"],
    [34, 37, "小儿腹泻"],
    [38, 39, "小儿流涎"],
    [40, 41, "小儿厌食症"],
    [42, 43, "小儿夜啼"]
    ]
  },
  "4-4": {
    title: "妇婴保健—孕妇",
    total: 42,
    rules: [
    [1, 2, "目录"],
    [3, 3, "如何推算预产期"],
    [4, 4, "什么是孕期保健"],
    [5, 5, "孕期保健的目的是什么"],
    [6, 10, "孕期保健内容"],
    [11, 20, "孕早期保健"],
    [21, 25, "六孕中期保健"],
    [26, 30, "孕晚期保健"],
    [31, 31, "孕妇的环境养生"],
    [32, 33, "孕妇怎样加强营养？"],
    [34, 36, "孕服中医膳食"],
    [37, 37, "孕妇多吃鱼、虾有什么益处？"],
    [38, 38, "孕妇睡电热毯为什么有害？"],
    [39, 40, "孕妇不宜养猫狗"],
    [41, 42, "过期妊娠不宜胎儿发育"]
    ]
  },
  "10-1": {
    title: "四季养生—春季养生",
    total: 38,
    rules: [
    [1, 2, "目录"],
    [3, 7, "春季养生要则"],
    [8, 12, "春季饮食养生"],
    [13, 15, "春季起居养生"],
    [16, 19, "春季情志养生"],
    [20, 22, "春季经络养生"],
    [23, 24, "春季药膳养生"],
    [25, 29, "春季运动养生"],
    [30, 38, "春季疾病预防"]
    ]
  },
  "10-2": {
    title: "四季养生—夏季养生",
    total: 42,
    rules: [
    [1, 2, "目录"],
    [3, 5, "夏季养生法则"],
    [6, 17, "夏季饮食养生"],
    [18, 20, "夏季起居养生"],
    [21, 22, "夏季情致养生"],
    [23, 27, "夏季经络养生"],
    [28, 32, "夏季药膳养生"],
    [33, 35, "夏季运动养生"],
    [36, 40, "夏季疾病预防"],
    [41, 42, "夏季养生不宜"]
    ]
  },
  "10-3": {
    title: "四季养生—秋季养生",
    total: 37,
    rules: [
    [1, 1, "目录"],
    [2, 5, "秋季养生要则"],
    [6, 13, "秋季饮食养生"],
    [14, 15, "秋季起居养生"],
    [16, 17, "秋季情志养生"],
    [18, 26, "秋季经络养生"],
    [27, 28, "秋季药膳养生"],
    [29, 30, "秋季运动锻炼养生"],
    [31, 37, "秋季疾病预防"]
    ]
  },
  "10-4": {
    title: "四季养生—冬季养生",
    total: 29,
    rules: [
    [1, 2, "目录"],
    [3, 5, "冬季养生要则"],
    [6, 10, "冬季饮食养生"],
    [11, 13, "冬季起居养生"],
    [14, 15, "冬季情志养生"],
    [16, 16, "冬季经络养生"],
    [17, 20, "冬季药膳养生"],
    [21, 22, "冬季运动养生"],
    [23, 26, "冬季疾病预防"],
    [27, 29, "冬季养生八益"]
    ]
  }
}

// --- 状态变量 ---
const archiveList = ref([])
const currentIndex = ref(0)
const jumpPage = ref(1)
const isMuted = ref(true)
const hoveredIndex = ref(null)
const previewPos = ref(0)
const scrollContainer = ref(null)
const scrubberRef = ref(null)
const audioPlayer = ref(null)
const firstImageReady = ref(false)
let hoverTimer = null
let scrollRafId = 0

const PRELOAD_RADIUS = 3
let idlePreloadTaskId = null

// --- 获取当前生效的配置 ---
const currentConfig = computed(() => {
  const activeId = props.id || '1'
  return ARCHIVE_DATA[activeId] || ARCHIVE_DATA["1"]
})

const _imgByteWarmupSet = new Set()

const resolveImageUrl = (moduleId, pageNum) => `/src/assets/images/mainShow/imageReader/button_${moduleId}/${pageNum}.jpg`

const resolveAudioUrl = (moduleId, pageNum) => `/src/assets/audio/imageReader/button_${moduleId}/${pageNum}.mp3`

const ensureImageLoaded = (moduleId, pageNum) => {
  const url = resolveImageUrl(moduleId, pageNum)
  if (!url || _imgByteWarmupSet.has(url)) return
  _imgByteWarmupSet.add(url)

  const img = new Image()
  img.decoding = 'async'
  img.loading = 'eager'
  img.fetchPriority = 'high'
  img.src = url
}

const warmupImageBytes = (moduleId, pageNum) => {
  ensureImageLoaded(moduleId, pageNum)
}

const getImageUrl = (moduleId, pageNum) => {
  return resolveImageUrl(moduleId, pageNum)
}

const ensureFirstImageReady = async (moduleId) => {
  const url = resolveImageUrl(moduleId, 1)
  if (!url) {
    firstImageReady.value = true
    return
  }

  firstImageReady.value = false
  const img = new Image()
  img.decoding = 'async'
  img.loading = 'eager'
  img.fetchPriority = 'high'
  img.onload = () => {
    firstImageReady.value = true
  }
  img.onerror = () => {
    firstImageReady.value = true
  }
  img.src = url
}

const syncImageWindow = () => {
  const activeId = props.id || '1'
  const total = archiveList.value.length
  if (!total) return

  const center = currentIndex.value + 1
  const start = Math.max(1, center - PRELOAD_RADIUS)
  const end = Math.min(total, center + PRELOAD_RADIUS)

  for (let i = start; i <= end; i++) {
    warmupImageBytes(activeId, i)
  }
}

// 音频加载
const loadAndPlayAudio = async () => {
  if (isMuted.value || !audioPlayer.value) return
  const activeId = props.id || '1'
  const url = resolveAudioUrl(activeId, currentIndex.value + 1)
  audioPlayer.value.pause()
  audioPlayer.value.src = url
  audioPlayer.value.load()
  audioPlayer.value.addEventListener('canplay', () => {
    audioPlayer.value?.play().catch(err => console.warn('翻页播放失败:', err))
  }, { once: true })
}

// --- 初始化板块 ---
const initModule = () => {
  const cfg = currentConfig.value
  const list = []
  for (let i = 1; i <= cfg.total; i++) {
    const rule = cfg.rules.find(([s, e]) => i >= s && i <= e)
    list.push({ title: rule ? rule[2] : cfg.title, pageNum: i })
  }
  archiveList.value = list
  currentIndex.value = 0
  jumpPage.value = 1
  scrollContainer.value?.scrollTo({ left: 0 })
}

// --- 计算属性 ---
const progress = computed(() => {
  if (archiveList.value.length === 0) return 0
  return ((currentIndex.value + 1) / archiveList.value.length) * 100
})

watch(() => props.id, () => {
  firstImageReady.value = false
  initModule()
  syncImageWindow()
  ensureFirstImageReady(props.id || '1')
  warmupImageBytes(props.id || '1', 1)
  warmupImageBytes(props.id || '1', 2)
  warmupImageBytes(props.id || '1', 3)
  if (!isMuted.value) loadAndPlayAudio()
}, { immediate: true })

// 监听翻页，触发资源窗口同步
watch(currentIndex, () => {
  syncImageWindow()
  if (!isMuted.value) loadAndPlayAudio()
})

// --- 交互方法 ---
const handleBack = () => router.back()

const toggleMute = () => {
  isMuted.value = !isMuted.value
  if (!isMuted.value) {
    loadAndPlayAudio()
  } else {
    audioPlayer.value?.pause()
  }
}

const handleScroll = () => {
  if (!scrollContainer.value) return
  if (scrollRafId) return
  scrollRafId = requestAnimationFrame(() => {
    const { scrollLeft, clientWidth } = scrollContainer.value || {}
    if (clientWidth) {
      currentIndex.value = Math.round(scrollLeft / clientWidth)
    }
    scrollRafId = 0
  })
}

const scrollToPage = (index) => {
  if (!scrollContainer.value) return
  const width = scrollContainer.value.clientWidth
  scrollContainer.value.scrollTo({ left: width * index, behavior: 'smooth' })
}

const goToPage = (index) => {
  const target = Math.max(0, Math.min(index, archiveList.value.length - 1))
  scrollToPage(target)
}

// 预览逻辑
const handleScrubberMove = (e) => {
  if (!scrubberRef.value) return
  const rect = scrubberRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const ratio = Math.max(0, Math.min(1, x / rect.width))
  const targetIdx = Math.floor(ratio * archiveList.value.length)
  
  clearTimeout(hoverTimer)
  hoverTimer = setTimeout(() => {
    hoveredIndex.value = Math.min(targetIdx, archiveList.value.length - 1)
  }, 50)
  previewPos.value = x
}

const handleScrubberLeave = () => {
  clearTimeout(hoverTimer)
  hoveredIndex.value = null
}

const handleScrubberClick = () => {
  if (hoveredIndex.value !== null) scrollToPage(hoveredIndex.value)
}

onMounted(() => {
  const preloadTask = () => {
    const activeId = props.id || '1'
    warmupImageBytes(activeId, 1)
    warmupImageBytes(activeId, 2)
    warmupImageBytes(activeId, 3)
    warmupImageBytes(activeId, 4)
  }

  if (typeof window.requestIdleCallback === 'function') {
    idlePreloadTaskId = window.requestIdleCallback(preloadTask, { timeout: 800 })
  } else {
    idlePreloadTaskId = window.setTimeout(preloadTask, 0)
  }
})

onBeforeUnmount(() => {
  if (idlePreloadTaskId === null) return
  if (typeof window.cancelIdleCallback === 'function') {
    window.cancelIdleCallback(idlePreloadTaskId)
  } else {
    window.clearTimeout(idlePreloadTaskId)
  }
  idlePreloadTaskId = null
})
</script>

<style scoped>
.archive-overlay { 
  background: #f4f1ea; inset: 0; position: fixed; 
  display: flex; flex-direction: column; 
  align-items: center; justify-content: center; z-index: 1000;
}
.paper-texture { 
  position: absolute; inset: 0; opacity: 0.08; pointer-events: none; 
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E");
  z-index: 1; 
}
.floating-header {
  position: absolute; top: 20px; left: 4vw; right: 4vw;
  display: flex; justify-content: space-between; align-items: center; z-index: 100;
}
.modern-back {
  background: rgba(255,255,255,0.8); backdrop-filter: blur(10px);
  border: 1px solid rgba(0,0,0,0.05); padding: 8px 18px;
  border-radius: 50px; cursor: pointer; font-weight: 600;
}

/* ⚠️ 核心修改区：取消了 absolute，将其放入正常的 Flex 布局中排队 */
.scrubber-container {
  position: relative; 
  width: 80vw;
  height: 30px; 
  margin-top: 60px; /* 避开头部绝对定位的按钮 */
  margin-bottom: 15px; /* 与下方图片的距离 */
  display: flex; align-items: center; z-index: 500; cursor: pointer;
}

.scrubber-track {
  width: 100%; height: 4px; background: rgba(0,0,0,0.08);
  border-radius: 4px; position: relative; overflow: hidden;
}
.scrubber-fill { height: 100%; background: #4A907E; transition: width 0.2s ease-out; }
.scrubber-preview {
  position: absolute; bottom: 35px; width: 200px; 
  background: white; border-radius: 10px;
  box-shadow: 0 12px 35px rgba(0,0,0,0.15);
  transform: translateX(-50%); pointer-events: none; overflow: hidden;
  display: flex; flex-direction: column;
}
.p-img-box { position: relative; width: 100%; height: 110px; }
.p-img-box img { width: 100%; height: 100%; object-fit: cover; }
.p-page-badge {
  position: absolute; bottom: 5px; right: 5px;
  background: rgba(0,0,0,0.6); color: white;
  font-size: 10px; padding: 2px 6px; border-radius: 4px;
}
.p-content { padding: 10px; background: #fff; }
.p-title { font-size: 13px; font-weight: 700; color: #333; line-height: 1.4; }
.audio-control {
  display: flex; align-items: center; gap: 10px;
  cursor: pointer; padding: 8px 15px; background: #f0f7f5;
  border-radius: 30px; transition: 0.3s;
}
.audio-waves { display: flex; align-items: flex-end; gap: 2px; height: 12px; }
.wave-bar { width: 2px; height: 100%; background: #4A907E; border-radius: 1px; }
.audio-waves.is-active .wave-bar { animation: wave 1s infinite alternate; }
@keyframes wave { from { height: 20%; } to { height: 100%; } }
.audio-label { font-size: 12px; font-weight: bold; color: #4A907E; }

/* ⚠️ 核心修改区：限制高度，让给进度条和底栏空间 */
.viewer-layout { display: flex; align-items: center; max-height: 60vh; width: 95vw; z-index: 10; }
.scroll-container { flex: 1; display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; }
.scroll-item { flex: 0 0 100%; display: flex; justify-content: center; scroll-snap-align: center; }

/* 将图片的高宽上限统一调小 10vh 以避免挤压底部 */
.archive-img { max-height: 60vh; max-width: 90vw; border-radius: 4px; box-shadow: 0 15px 40px rgba(0,0,0,0.1); }
.first-image-loading {
  width: min(90vw, 700px);
  height: min(60vh, 900px);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #5f6f69;
  background: linear-gradient(120deg, rgba(74,144,126,0.08), rgba(74,144,126,0.02));
  border: 1px solid rgba(74,144,126,0.2);
  border-radius: 4px;
  letter-spacing: 0.05em;
  font-size: 14px;
}
.archive-img-placeholder {
  width: min(90vw, 700px);
  height: min(60vh, 900px);
  max-height: 60vh; max-width: 90vw;
}

.compact-footer {
  margin-top: 18px; width: 84vw; max-width: 850px;
  background: white; padding: 14px 18px; border-radius: 14px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.06); z-index: 20;
}
.mini-progress-track { width: 100%; height: 3px; background: rgba(0,0,0,0.05); border-radius: 3px; margin-bottom: 12px; }
.bar { height: 100%; background: #4A907E; transition: width 0.3s; }
.control-row { display: flex; justify-content: space-between; align-items: center; }
.modern-pagination { display: flex; align-items: center; gap: 15px; }
.p-btn { background: white; border: 1px solid #ddd; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: bold; }
.p-current { color: #4A907E; font-size: 18px; font-weight: bold; }
.modern-jump { display: flex; gap: 8px; }
.modern-jump input { width: 50px; border: 1px solid #ddd; border-radius: 6px; text-align: center; }
.jump-action { background: #4A907E; color: white; border: none; padding: 6px 15px; border-radius: 6px; cursor: pointer; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translate(-50%, 10px); }
</style>
