// src/api/detect.js
import axios from 'axios';

// 望诊：上传舌象图片
// 参数 data: 这是一个 FormData 对象，里面包含了图片文件、病人ID等
export function uploadTongue(data) {
  return axios.post('/api/tongue/detect', data, {
    headers: {
      'Content-Type': 'multipart/form-data' 
    }
  });
}
export function submitQuestionnaire(data) {
  
  return axios.post('/api/tcm/submit', data);
}