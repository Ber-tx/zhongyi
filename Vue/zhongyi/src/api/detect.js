// src/api/detect.js
import axios from 'axios';

// 望诊：上传舌象图片（通过 Java 后端保存诊断记录）
export function uploadTongue(data) {
  return axios.post('/api/detect/wang', data, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

// YOLO 检测：直接调用 Python AI 服务（不走 Java，用于实时检测和多帧）
export function yoloDetect(file) {
  const formData = new FormData();
  formData.append('file', file);
  return axios.post('/tongue/detect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}

export function submitQuestionnaire(data) {

  return axios.post('/api/tcm/submit', data);
}

export function resetQuestionnaireResult(data) {
  return axios.post('/api/tcm/reset-wen', data);
}