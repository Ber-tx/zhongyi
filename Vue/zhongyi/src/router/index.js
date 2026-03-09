import { createRouter, createWebHistory } from 'vue-router'

// 路由组件延迟加载
const ImageReader = () => import('@/views/Culture/ImageReader.vue')
const ModuleFour = () => import('@/views/Culture/ModuleFour.vue') 
const ModuleTen = () => import('@/views/Culture/ModuleTen.vue')

const routes = [
  { 
    path: '/', 
    name: 'Home',
    component: () => import('@/views/Home.vue') 
  },
  {
    path: '/intro',
    name: 'SystemIntro',
    component: () => import('@/views/SystemIntro.vue')
  },
  {
    path: '/hardware',
    name: 'HardwareGuide',
    component: () => import('@/views/HardwareGuide.vue')
  },
  {
    path: '/culture', 
    name: 'Culture',
    component: () => import('@/views/Culture/CultureHome.vue') 
  },
  
  // --- 由特殊到一般 ---

  // 1. 模块 1 的独立路径
  {
    path: '/culture/preventive',
    name: 'Preventive',
    component: ImageReader,
    props: { id: '1' } 
  },

  // 2. 特殊定制板块 4（必须放在动态路由 :id 之前）
  {
    path: '/culture/module/4',
    name: 'ModuleFour',
    component: ModuleFour
  },

  // 3. 特殊定制板块 10
  {
    path: '/culture/module/10',
    name: 'ModuleTen',
    component: ModuleTen
  },

  // 4. 通用动态路由（匹配 2, 3, 5, 6, 7,8, 9,以及4，10的选择页面）
  {
    path: '/culture/module/:id',
    name: 'CultureModule',
    component: ImageReader,
    props: true 
  },

  // --- 四诊辨识路径 ---
  { 
    path: '/detect', 
    name: 'DetectSelect',
    component: () => import('@/views/Detect/DetectSelect.vue') 
  },
  {
    path: '/detect/wenjuan',
    name: 'Wenjuan',
    component: () => import('@/views/Detect/Wenjuan.vue'),
    meta: { title: '问诊 - 智能问卷' }
  },
  { path: '/detect/wang', component: () => import('@/views/Detect/Wang.vue') },
  { path: '/detect/wen', component: () => import('@/views/Detect/Wen.vue') },
  { path: '/detect/qie', component: () => import('@/views/Detect/Qie.vue') },
  { 
    path: '/report', 
    name: 'Report',
    component: () => import('@/views/Report.vue'),
    meta: { title: '诊断报告' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach(() => {
  window.scrollTo(0, 0)
})

export default router