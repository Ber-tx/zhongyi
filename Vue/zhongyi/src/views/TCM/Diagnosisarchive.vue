<template>
  <div class="tcm-panel">
    <div class="panel-title-bar">
      <span class="panel-step">辨识档案</span>
      <span class="panel-hint">展示所有人员的四诊辨识记录，仅供查阅，不支持编辑或删除。</span>
      <span class="readonly-badge">👁 只读</span>
    </div>

    <!-- 搜索栏 -->
    <div class="toolbar-row">
      <el-input
        v-model="keyword"
        placeholder="按姓名或身份证号搜索"
        clearable
        style="width:260px"
        @keyup.enter="load(1)"
        @clear="load(1)"
      >
        <template #append>
          <el-button @click="load(1)">搜索</el-button>
        </template>
      </el-input>
      <span class="record-count">共 {{ total }} 条辨识记录</span>
    </div>

    <!-- 表格 -->
    <div class="table-wrap">
      <el-table
        :data="list"
        v-loading="loading"
        class="tcm-table"
        stripe
        empty-text="暂无辨识记录"
        height="100%"
      >
        <el-table-column prop="id" label="编号" width="65" />
        <el-table-column prop="patientName" label="姓名" width="88" />
        <el-table-column prop="patientGender" label="性别" width="55" />
        <el-table-column label="身份证号" min-width="168" show-overflow-tooltip>
          <template #default="{ row }">
            {{ maskId(row.patientIdCard || row.idCard) }}
          </template>
        </el-table-column>
        <el-table-column label="四诊完成情况" width="170">
          <template #default="{ row }">
            <el-tag :type="row.wangResult         ? 'success' : 'info'" size="small" class="diag-tag">望</el-tag>
            <el-tag :type="row.wenAudioConclusion  ? 'success' : 'info'" size="small" class="diag-tag">闻</el-tag>
            <el-tag :type="row.wenConclusion       ? 'success' : 'info'" size="small" class="diag-tag">问</el-tag>
            <el-tag :type="row.qieHeartRate        ? 'success' : 'info'" size="small" class="diag-tag">切</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="辨识时间" width="138">
          <template #default="{ row }">{{ fmt(row.createTime) }}</template>
        </el-table-column>
        <el-table-column label="问诊摘要" min-width="170" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ getWenSummary(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="闻诊摘要" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ getWenAudioSummary(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="openDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next, jumper, total"
        @current-change="load"
        background
        small
      />
    </div>

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="辨识档案详情"
      direction="rtl"
      size="420px"
      :modal="false"
      :append-to-body="true"
    >
      <template v-if="selected">
        <div class="detail-block">
          <div class="detail-title">基本信息</div>
          <div class="detail-row"><span>姓名</span><b>{{ selected.patientName || '—' }}</b></div>
          <div class="detail-row"><span>性别</span><b>{{ selected.patientGender || '—' }}</b></div>
          <div class="detail-row"><span>身份证号</span><b>{{ maskId(selected.patientIdCard || selected.idCard) }}</b></div>
          <div class="detail-row"><span>辨识时间</span><b>{{ fmt(selected.createTime) }}</b></div>
        </div>

        <div class="detail-block" v-if="selected.wangResult">
          <div class="detail-title">👁 望诊结果</div>
          <div class="detail-content">{{ selected.wangResult }}</div>
        </div>

        <div class="detail-block" v-if="selected.wenAudioConclusion">
          <div class="detail-title">🔊 闻诊结论</div>
          <div class="detail-row"><span>体质判断</span><b>{{ selected.wenAudioConclusion }}</b></div>
          <div class="detail-row" v-if="selected.wenAudioConfidence">
            <span>置信度</span>
            <b>{{ (selected.wenAudioConfidence * 100).toFixed(1) }}%</b>
          </div>
          <div class="detail-row" v-if="selected.wenAudioTagsList?.length">
            <span>声纹标签</span>
            <b>{{ selected.wenAudioTagsList.join('、') }}</b>
          </div>
          <div class="detail-content" v-if="selected.wenAudioFeatureSummary">
            {{ selected.wenAudioFeatureSummary }}
          </div>
        </div>

        <div class="detail-block" v-if="selected.wenConclusion">
          <div class="detail-title">📋 问诊结论</div>
          <div class="detail-content">{{ selected.wenConclusion }}</div>
          <div class="detail-row" v-if="selected.wenTemplateTitle">
            <span>问诊模板</span><b>{{ selected.wenTemplateTitle }}</b>
          </div>
          <div class="detail-row" v-if="selected.wenDominantConstitution">
            <span>主导体质</span><b>{{ selected.wenDominantConstitution }}</b>
          </div>
          <div class="detail-row" v-if="selected.wenAnswerCount">
            <span>答题数量</span><b>{{ selected.wenAnswerCount }} 题</b>
          </div>
          <div class="detail-row" v-if="selected.wenTopScores?.length">
            <span>体质得分</span><b>{{ selected.wenTopScores.join('，') }}</b>
          </div>
          <div class="detail-content" v-if="selected.wenCandidatesText">候选体质：{{ selected.wenCandidatesText }}</div>
        </div>

        <div class="detail-block" v-if="selected.qieHeartRate">
          <div class="detail-title">💓 切诊数据</div>
          <div class="detail-row"><span>心率</span><b>{{ selected.qieHeartRate }} bpm</b></div>
          <div class="detail-row"><span>血氧</span><b>{{ selected.qieSpo2 }} %</b></div>
          <div class="detail-row" v-if="selected.qieValidRate">
            <span>信号有效率</span><b>{{ selected.qieValidRate }}%</b>
          </div>
          <div class="detail-content" v-if="selected.qieTcmSuggestion" style="margin-top:8px">
            {{ selected.qieTcmSuggestion }}
          </div>
        </div>

        <div class="detail-empty"
          v-if="!selected.wangResult && !selected.wenAudioConclusion
                && !selected.wenConclusion && !selected.qieHeartRate">
          该记录暂无四诊详细数据
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const list     = ref([])
const total    = ref(0)
const page     = ref(1)
const pageSize = 12
const keyword  = ref('')
const loading  = ref(false)

const drawerVisible = ref(false)
const selected      = ref(null)

const openDetail = (row) => {
  selected.value = buildDetailRecord(row)
  drawerVisible.value = true
}

const constitutionAlias = {
  ph: '平和质', qx: '气虚质', yx: '阳虚质', yx0: '阴虚质', yx1: '阳虚质', yinXu: '阴虚质',
  ts: '痰湿质', tanShi: '痰湿质', sr: '湿热质', shiRe: '湿热质', xy: '血瘀质', xueYu: '血瘀质',
  qy: '气郁质', qiYu: '气郁质', tb: '特禀质', teBing: '特禀质', qiXu: '气虚质', yangXu: '阳虚质',
}

const safeJson = (raw, fallback = null) => {
  if (!raw) return fallback
  if (typeof raw === 'object') return raw
  try { return JSON.parse(raw) } catch { return fallback }
}

const mapScoreKeyName = (key) => constitutionAlias[key] || key

const pickTopScores = (scoreMap = {}, limit = 3) => {
  return Object.entries(scoreMap || {})
    .map(([key, score]) => ({ key, score: Number(score) || 0 }))
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map((item) => `${mapScoreKeyName(item.key)} ${item.score}分`)
}

const parseWenScores = (row) => {
  const parsed = safeJson(row.wenScores, {}) || {}
  const templateResult = parsed.templateResult || {}
  const scoreMap = templateResult.scoreMap || parsed.scores || {}
  const candidates = templateResult.candidateConstitutions || parsed.candidateConstitutions || []

  return {
    wenTemplateTitle: parsed.templateTitle || templateResult.templateTitle || templateResult.title || ('原始体质问卷'),
    wenDominantConstitution: templateResult.dominantConstitution || parsed.mainConstitution || row.wenConclusion || '',
    wenAnswerCount: templateResult.answerCount || (Array.isArray(parsed.answers) ? parsed.answers.length : 0),
    wenTopScores: pickTopScores(scoreMap, 3),
    wenCandidatesText: Array.isArray(candidates)
      ? candidates.slice(0, 3).map((item) => item?.name).filter(Boolean).join('、')
      : '',
  }
}

const parseWenAudio = (row) => {
  const tags = safeJson(row.wenAudioTags, [])
  const feature = safeJson(row.wenAudioFeatures, null)
  const featureSummary = feature && typeof feature === 'object'
    ? Object.entries(feature).slice(0, 4).map(([k, v]) => `${k}:${typeof v === 'number' ? v.toFixed?.(2) ?? v : v}`).join('；')
    : ''

  return {
    wenAudioTagsList: Array.isArray(tags) ? tags : [],
    wenAudioFeatureSummary: featureSummary,
  }
}

const buildDetailRecord = (row) => {
  return {
    ...row,
    ...parseWenScores(row),
    ...parseWenAudio(row),
  }
}

const getWenSummary = (row) => {
  if (!row.wenConclusion) return '暂无问诊结论'
  const parsed = parseWenScores(row)
  if (parsed.wenTopScores.length) return `${parsed.wenDominantConstitution || row.wenConclusion}（${parsed.wenTopScores[0]}）`
  return parsed.wenDominantConstitution || row.wenConclusion
}

const getWenAudioSummary = (row) => {
  if (!row.wenAudioConclusion) return '暂无闻诊结论'
  const conf = row.wenAudioConfidence ? ` ${(Number(row.wenAudioConfidence) * 100).toFixed(0)}%` : ''
  return `${row.wenAudioConclusion}${conf}`
}

const load = async (p = page.value) => {
  loading.value = true
  page.value = p
  try {
    const res = await axios.get('/api/admin/diagnoses-with-patient', {
      params: { page: p, size: pageSize, keyword: keyword.value }
    })
    if (res.data.code === 200) {
      list.value  = res.data.data.list  || []
      total.value = res.data.data.total || 0
    }
  } catch {
    try {
      const res = await axios.get('/api/admin/diagnoses', {
        params: { page: p, size: pageSize }
      })
      if (res.data.code === 200) {
        list.value  = res.data.data.list  || []
        total.value = res.data.data.total || 0
      }
    } catch {
      list.value = []
    }
  } finally {
    loading.value = false
  }
}

const maskId = (id) => {
  if (!id || id.length < 8) return id || '—'
  return id.slice(0, 3) + '******' + id.slice(-4)
}

const fmt = (t) => {
  if (!t) return '—'
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

onMounted(() => load(1))
</script>

<style scoped>
@import '@/styles/tcm-shared.css';

.tcm-panel { height: 100%; display: flex; flex-direction: column; overflow: hidden; }

.readonly-badge {
  margin-left: auto;
  font-size: 12px; font-weight: 600; color: #7a5520;
  background: #f5e4a8; border: 1px solid #c8a020;
  padding: 2px 10px; border-radius: 10px;
}

.table-wrap { flex: 1; overflow: hidden; }
.diag-tag { margin-right: 3px; }

/* 抽屉样式 */
.detail-block {
  background: #faf3e0;
  border: 1px solid #e8d5a0;
  border-radius: 6px;
  padding: 14px 16px;
  margin-bottom: 14px;
}

.detail-title {
  font-size: 13px; font-weight: 700; color: #5a2d00;
  padding-bottom: 8px; margin-bottom: 10px;
  border-bottom: 1px solid #e8d5a0;
}

.detail-row {
  display: flex; justify-content: space-between;
  font-size: 13px; padding: 5px 0;
  border-bottom: 1px dashed #eedcb0;
  color: #6b4c24;
}
.detail-row:last-child { border-bottom: none; }
.detail-row b { color: #3d2b10; font-weight: 600; }

.detail-content {
  font-size: 13px; color: #3d2b10; line-height: 1.7;
}

.detail-empty {
  text-align: center; color: #bbb;
  font-size: 13px; padding: 30px 0;
}
</style>