// src/api/auth.js

import request from 'axios' 
export function loginAndSave(data) {
  return request({
    url: '/api/user/save',
    method: 'post',
    data: data
  })
}