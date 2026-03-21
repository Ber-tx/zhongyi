/**
 * 诊断报告工具函数
 * 用于在诊断完成后处理"生成报告"或"继续下一个"的选择
 */

import axios from 'axios';
import { ElMessage } from 'element-plus';

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
    const response = await axios.post("/api/report/generate", {
      patientId: Number(patientId),
      idCard: idCard,
      completedTypes: diagnosisType
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
    const response = await axios.post("/api/report/generate", {
      patientId: Number(patientId),
      idCard: idCard,
      completedTypes: completedTypes
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
