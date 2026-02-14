package com.tx.demo.service.impl;

import com.tx.demo.entity.Diagnosis;
import com.tx.demo.mapper.DiagnosisMapper;
import com.tx.demo.service.QieService;
import com.tx.demo.utils.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Map;

@Service
public class QieServiceImpl implements QieService {

    @Autowired
    private DiagnosisMapper diagnosisMapper;

    @Override
    public Result saveAndAnalyze(Map<String, Object> payload) {
        try {
            // 提取前端传来的数据
            Long patientId = Long.valueOf(payload.get("userId").toString());
            Double hr = Double.valueOf(payload.get("heartRate").toString());
            Double spo2 = Double.valueOf(payload.get("spo2").toString());

            // 🔧 修复：提取新字段
            Double validRate = payload.containsKey("validRate")
                    ? Double.valueOf(payload.get("validRate").toString())
                    : null;

            Integer sampleCount = payload.containsKey("sampleCount")
                    ? Integer.valueOf(payload.get("sampleCount").toString())
                    : null;

            String tcmSuggestion = payload.containsKey("tcmSuggestion")
                    ? (String) payload.get("tcmSuggestion")
                    : null;

            // 数据验证
            if (hr < 40 || hr > 180) {
                return Result.error("心率数据异常");
            }

            if (spo2 < 70 || spo2 > 100) {
                return Result.error("血氧数据异常");
            }

            // 数据库操作
            Diagnosis record = diagnosisMapper.findTodayRecord(patientId);

            if (record != null) {
                // 更新已有记录
                record.setQieHeartRate(hr);
                record.setQieSpo2(spo2);
                record.setQieValidRate(validRate);              // 🔧 新字段
                record.setQieSampleCount(sampleCount);           // 🔧 新字段
                record.setQieTcmSuggestion(tcmSuggestion);       // 🔧 新字段

                int rows = diagnosisMapper.updateQie(record);

                if (rows > 0) {
                    return Result.success(tcmSuggestion != null ? tcmSuggestion : "切诊完成");
                } else {
                    return Result.error("更新失败");
                }
            } else {
                // 新增记录
                Diagnosis newRecord = new Diagnosis();
                newRecord.setPatientId(patientId);
                newRecord.setQieHeartRate(hr);
                newRecord.setQieSpo2(spo2);
                newRecord.setQieValidRate(validRate);            // 🔧 新字段
                newRecord.setQieSampleCount(sampleCount);         // 🔧 新字段
                newRecord.setQieTcmSuggestion(tcmSuggestion);     // 🔧 新字段
                newRecord.setCreateTime(LocalDateTime.now());
                newRecord.setStatus(0);

                int rows = diagnosisMapper.insert(newRecord);

                if (rows > 0) {
                    return Result.success(tcmSuggestion != null ? tcmSuggestion : "切诊完成");
                } else {
                    return Result.error("插入失败");
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("切诊数据保存失败: " + e.getMessage());
        }
    }
}
