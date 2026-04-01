/**
 * 诊断报告工具函数
 * 用于在诊断完成后处理"生成报告"或"继续下一个"的选择
 */

import axios from 'axios';
import { ElMessage } from 'element-plus';

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
