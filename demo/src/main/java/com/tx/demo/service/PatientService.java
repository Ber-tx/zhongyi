package com.tx.demo.service;

import com.tx.demo.entity.Patient;


public interface PatientService {
    /**
     * 根据身份证号保存或更新用户信息
     */

    Patient saveOrUpdateByCard(Patient patient);
}