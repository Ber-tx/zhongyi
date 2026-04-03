/**
 * 诊断报告工具函数
 * 用于在诊断完成后处理"生成报告"或"继续下一个"的选择
 */

import axios from 'axios';
import { ElMessage } from 'element-plus';

const CONSTITUTION_NAME_TO_CODE = {
  '平和质': 'ph',
  '气虚质': 'qx',
  '阳虚质': 'yx1',
  '阴虚质': 'yx0',
  '痰湿质': 'ts',
  '湿热质': 'sr',
  '血瘀质': 'xy',
  '气郁质': 'qy',
  '特禀质': 'tb',
};

const CONSTITUTION_ADVICE_MAP = {
  ph: {
    title: '平和质',
    summary: '体质总体协调，阴阳气血较为平衡，日常以维持稳定作息和均衡饮食为主。',
    diet: ['三餐规律，饮食均衡，不偏食', '谷物、蔬菜、优质蛋白搭配摄入', '保持清淡适度，避免长期暴饮暴食'],
    avoid: ['避免长期熬夜', '避免过度劳累和久坐不动', '避免饮食过于油腻或极端节食'],
    suggestions: ['坚持每周适量运动', '保持情绪平稳，规律作息', '定期体检，动态观察体质变化'],
  },
  qx: {
    title: '气虚质',
    summary: '常见精神不足、容易疲劳、气短懒言等表现，调理重点在于补气养气与适度活动。',
    diet: ['可多吃山药、莲子、红枣、黄豆等温和食材', '饮食宜少量多餐，避免过饱', '汤粥类和熟食更适合日常调养'],
    avoid: ['避免过度节食', '避免长期吃生冷寒凉食物', '避免高强度、超负荷运动'],
    suggestions: ['保证充足睡眠，减少熬夜', '选择散步、八段锦等轻中度运动', '如乏力明显或持续加重，建议线下复诊'],
  },
  yx1: {
    title: '阳虚质',
    summary: '多见怕冷、四肢不温、精神不振等表现，调理重点在于温阳散寒与保暖。',
    diet: ['可适当选择羊肉、牛肉、生姜、葱、桂圆等温性食材', '饮食宜温热熟食，少吃过冷食物', '冬季可偏向热汤热粥和少量多餐'],
    avoid: ['避免长期贪凉饮冷', '避免受寒和熬夜耗损阳气', '避免久居潮湿阴冷环境'],
    suggestions: ['注意腰腹和四肢保暖', '适当进行温和运动以助阳气运行', '若畏寒明显或伴随症状加重，建议就医评估'],
  },
  yx0: {
    title: '阴虚质',
    summary: '常见口干咽燥、五心烦热、睡眠不稳等倾向，调理重点在于滋阴润燥、减少耗伤。',
    diet: ['可适当选择银耳、百合、梨、黑芝麻、蜂蜜等润燥食材', '饮食宜清淡，少辛辣刺激', '注意补充水分，避免过度耗津'],
    avoid: ['避免辛辣烧烤和重口味饮食', '避免熬夜和情绪过度紧张', '避免长期处于干燥高温环境'],
    suggestions: ['保持充足睡眠，少熬夜', '适当做舒缓运动，避免过度出汗', '如口干、心烦、失眠长期存在，建议进一步评估'],
  },
  ts: {
    title: '痰湿质',
    summary: '常见形体偏胖、困重、口黏、苔腻等表现，调理重点在于健脾化湿、控制饮食。',
    diet: ['饮食宜清淡，减少油腻、甜食和夜宵', '可适当增加薏米、冬瓜、山药等食材', '规律进餐，避免暴饮暴食'],
    avoid: ['避免过多油炸、甜腻、冷饮', '避免久坐少动', '避免晚睡和过量进食'],
    suggestions: ['坚持步行、慢跑、骑行等有氧运动', '保持作息规律，帮助脾运化湿', '若体重持续上升或伴明显不适，建议线下检查'],
  },
  sr: {
    title: '湿热质',
    summary: '常见口苦口黏、面油、易烦热等表现，调理重点在于清热利湿、饮食清爽。',
    diet: ['饮食宜清淡，可多选择蔬菜、水果和清爽汤羹', '适当减少苦辣重口味刺激', '保持饮食节制，减少夜宵与烧烤油炸'],
    avoid: ['避免饮酒过量', '避免辛辣烧烤和高油高糖饮食', '避免久处闷热环境'],
    suggestions: ['保证排便通畅和适量饮水', '规律运动有助于湿热代谢', '如口苦、痤疮或大便异常明显，建议进一步评估'],
  },
  xy: {
    title: '血瘀质',
    summary: '常见面色晦暗、刺痛、瘀斑或血行不畅倾向，调理重点在于活血通络、避免久滞。',
    diet: ['可适当选择山楂、玫瑰花、黑木耳、洋葱等食材', '饮食宜温和、规律，避免过度油腻', '保持充足水分和膳食纤维摄入'],
    avoid: ['避免久坐不动', '避免长期情绪抑郁或紧张', '避免烟酒过度和作息紊乱'],
    suggestions: ['加强步行、拉伸、太极等舒缓运动', '注意情绪疏导和睡眠质量', '若疼痛、麻木或瘀斑明显，建议线下就诊'],
  },
  qy: {
    title: '气郁质',
    summary: '常见情绪波动、胸胁不舒、叹气、郁闷等表现，调理重点在于疏肝理气、调畅情志。',
    diet: ['可适当选择玫瑰花、陈皮、佛手、萝卜等理气食材', '饮食宜规律，少暴饮暴食', '适当增加新鲜蔬果和优质蛋白'],
    avoid: ['避免长期压抑情绪', '避免过度咖啡因和酒精刺激', '避免长期熬夜和高压生活节奏'],
    suggestions: ['保持规律运动和社交活动', '学习放松训练、深呼吸或冥想', '若情绪低落持续时间较长，建议进一步评估'],
  },
  tb: {
    title: '特禀质',
    summary: '常见过敏、易反复发作或先天敏感倾向，调理重点在于规避诱因、稳定环境。',
    diet: ['饮食保持简单、清洁，注意观察过敏原', '新食物建议少量尝试并记录反应', '保持规律饮食和均衡营养'],
    avoid: ['避免已知过敏原', '避免环境刺激、灰尘和烟雾', '避免过度频繁更换护肤或饮食习惯'],
    suggestions: ['建议建立过敏记录', '必要时配合过敏原筛查', '如反复过敏或呼吸道症状明显，建议就医'],
  },
};

function normalizeConstitutionCode(typeOrName = '') {
  const raw = String(typeOrName || '').trim();
  if (!raw) return 'ph';
  const lower = raw.toLowerCase();
  if (CONSTITUTION_ADVICE_MAP[lower]) return lower;
  return CONSTITUTION_NAME_TO_CODE[raw] || 'ph';
}

/**
 * 获取体质建议、饮食与禁忌说明
 * @param {string} typeOrName 体质代码或中文名称
 * @param {Record<string, number>} scoreMap 分值映射
 */
export function getConstitutionAdvice(typeOrName, scoreMap = {}) {
  const code = normalizeConstitutionCode(typeOrName);
  const base = CONSTITUTION_ADVICE_MAP[code] || CONSTITUTION_ADVICE_MAP.ph;
  return {
    code,
    title: base.title,
    summary: base.summary,
    diet: [...base.diet],
    avoid: [...base.avoid],
    suggestions: [...base.suggestions],
    topScores: getConstitutionScoreRanking(scoreMap),
  };
}

/**
 * 获取分值排行
 * @param {Record<string, number>} scoreMap
 * @param {number} limit
 */
export function getConstitutionScoreRanking(scoreMap = {}, limit = 3) {
  const nameMap = {
    ph: '平和质',
    qx: '气虚质',
    yx1: '阳虚质',
    yx0: '阴虚质',
    ts: '痰湿质',
    sr: '湿热质',
    xy: '血瘀质',
    qy: '气郁质',
    tb: '特禀质',
  };

  return Object.entries(scoreMap || {})
    .map(([code, score]) => ({
      code,
      name: nameMap[code] || code,
      score: Number(score) || 0,
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}

function getPromptSettings() {
  try {
    const settings = JSON.parse(localStorage.getItem('report_settings') || '{}');
    return {
      customPromptTemplate: settings.llmPromptTemplate || undefined,
      focusMode: settings.llmFocusMode || undefined,
    };
  } catch (e) {
    return {
      customPromptTemplate: undefined,
      focusMode: undefined,
    };
  }
}

/**
 * 生成部分板块的诊断报告
 * @param {string} diagnosisType - 诊断类型：'wang', 'wen_audio', 'wen_questionnaire', 'qie'
 * @param {number|string} patientId - 患者ID
 * @param {string} idCard - 身份证（可选）
 * @returns {Promise}
 */
export async function generatePartialDiagnosisReport(diagnosisType, patientId, idCard = '') {
  if (!patientId) {
    ElMessage.error("患者ID丢失，无法生成报告");
    return false;
  }

  try {
    const promptSettings = getPromptSettings();
    const response = await axios.post("/api/report/generate", {
      patientId: Number(patientId),
      idCard: idCard,
      completedTypes: diagnosisType,
      ...promptSettings
    });

    if (response.data.code === 200 || response.data.success) {
      return response.data.data;
    } else {
      ElMessage.error(response.data.msg || "生成报告失败");
      return false;
    }
  } catch (error) {
    ElMessage.error("生成报告失败：" + error.message);
    return false;
  }
}

/**
 * 生成多个板块的诊断报告
 * @param {string} completedTypes - 已完成的诊断类型，逗号分隔
 * @param {number|string} patientId - 患者ID
 * @param {string} idCard - 身份证（可选）
 * @returns {Promise}
 */
export async function generateMultiBlockReport(completedTypes, patientId, idCard = '') {
  if (!patientId) {
    ElMessage.error("患者ID丢失，无法生成报告");
    return false;
  }

  try {
    const promptSettings = getPromptSettings();
    const response = await axios.post("/api/report/generate", {
      patientId: Number(patientId),
      idCard: idCard,
      completedTypes: completedTypes,
      ...promptSettings
    });

    if (response.data.code === 200 || response.data.success) {
      return response.data.data;
    } else {
      ElMessage.error(response.data.msg || "生成报告失败");
      return false;
    }
  } catch (error) {
    ElMessage.error("生成报告失败：" + error.message);
    return false;
  }
}

/**
 * 获取当前已完成的诊断类型
 * @returns {string} 逗号分隔的诊断类型字符串
 */
export function getCompletedDiagnosisTypes() {
  const completed = [];
  
  if (localStorage.getItem('wang_finished_id')) {
    completed.push('wang');
  }
  if (localStorage.getItem('wen_audio_finished_id')) {
    completed.push('wen_audio');
  }
  if (localStorage.getItem('wen_questionnaire_finished_id')) {
    completed.push('wen_questionnaire');
  }
  if (localStorage.getItem('qie_finished_id')) {
    completed.push('qie');
  }
  
  return completed.join(',');
}

/**
 * 获取诊断类型的中文名称
 * @param {string} type - 诊断类型
 * @returns {string} 中文名称
 */
export function getDiagnosisTypeName(type) {
  const typeMap = {
    'wang': '望诊（舌象分析）',
    'wen_audio': '闻诊（音频分析）',
    'wen_questionnaire': '问诊（症状问卷）',
    'qie': '切诊（脉搏检测）'
  };
  return typeMap[type] || '诊断';
}

/**
 * 根据 localStorage 中与当前患者 ID 绑定的完成标记，汇总已完成的诊断类型
 * @param {string|number} patientId
 * @returns {string[]}
 */
export function collectCompletedTypesForPatient(patientId) {
  const pid = String(patientId || '');
  if (!pid) return [];
  const types = [];
  if (localStorage.getItem('wang_finished_id') === pid) types.push('wang');
  if (localStorage.getItem('wen_finished_id') === pid) types.push('wen_audio');
  if (localStorage.getItem('wenjuan_finished_id') === pid) types.push('wen_questionnaire');
  if (localStorage.getItem('qie_finished_id') === pid) types.push('qie');
  return types;
}

/**
 * 跳转报告页（与诊断中心「生成报告」一致：query 携带 id、completedTypes）
 * @param {import('vue-router').Router} router
 * @param {string|number} patientId
 * @param {string} [_idCard] 预留，与路由保持一致
 * @param {string[]} [extraCompletedTypes] 当前页刚完成但尚未写入 finished_id 时可追加
 */
export function navigateToDiagnosisReport(router, patientId, _idCard = '', extraCompletedTypes = []) {
  if (!patientId) {
    ElMessage.error('缺少患者ID，无法生成报告');
    return;
  }
  const set = new Set(collectCompletedTypesForPatient(patientId));
  (Array.isArray(extraCompletedTypes) ? extraCompletedTypes : []).forEach((t) => {
    if (t) set.add(t);
  });
  const completedTypes = [...set].join(',');
  const caseId = localStorage.getItem('current_case_id');
  router.push({
    path: '/report',
    query: { id: String(patientId), caseId: caseId || undefined, completedTypes }
  });
}
