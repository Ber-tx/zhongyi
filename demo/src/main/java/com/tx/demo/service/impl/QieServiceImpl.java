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
            // 1. 提取前端传来的“事实数据”
            Long patientId = Long.valueOf(payload.get("userId").toString());
            Double hr = Double.valueOf(payload.get("heartRate").toString());
            Double spo2 = Double.valueOf(payload.get("spo2").toString());
            String rawData = (String) payload.get("rawData");

            // 2. 【核心】调用算法，生成中医结论
            String tcmDiagnosis = generateTcmConclusion(hr, spo2);

            // 3. 数据库操作 (标准流程)
            Diagnosis record = diagnosisMapper.findTodayRecord(patientId);

            if (record != null) {
                // 更新
                record.setQieHeartRate(hr);
                record.setQieSpo2(spo2);
                record.setQieRawData(rawData);
                record.setQieResult(tcmDiagnosis);
                diagnosisMapper.updateQie(record);
            } else {
                // 新增
                Diagnosis newOne = new Diagnosis();
                newOne.setPatientId(patientId);
                newOne.setQieHeartRate(hr);
                newOne.setQieSpo2(spo2);
                newOne.setQieRawData(rawData);
                newOne.setQieResult(tcmDiagnosis);
                newOne.setCreateTime(LocalDateTime.now());
                newOne.setStatus(0);
                diagnosisMapper.insert(newOne);
            }

            // 返回给前端，前端可以弹窗显示这个 tcmDiagnosis
            return Result.success(tcmDiagnosis);

        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("切诊数据保存失败: " + e.getMessage());
        }
    }

    /**
     * 【私有算法方法】将现代医学指标映射为中医脉象
     * 依据：中医诊断学 - 脉诊章节
     */
    private String generateTcmConclusion(Double hr, Double spo2) {
        StringBuilder sb = new StringBuilder();

        // --- 1. 频率判断 (迟数) ---
        // 成人正常心率 60-100，中医称“一息四至”为平脉
        if (hr > 90) {
            sb.append("【脉象】：数脉（脉来急促）。\n");
            sb.append("【主病】：多主热证。若脉有力为实热，无力为虚热。\n");
            sb.append("【建议】：饮食宜清淡，忌辛辣，可适量食用绿豆、苦瓜等清热之品。");
        } else if (hr < 60) {
            sb.append("【脉象】：迟脉（脉来迟缓）。\n");
            sb.append("【主病】：多主寒证。若有力为冷积，无力为虚寒。\n");
            sb.append("【建议】：注意保暖，少食生冷，可适当食用生姜、羊肉等温补之物。");
        } else {
            sb.append("【脉象】：缓脉（一息四至，不快不慢）。\n");
            sb.append("【主病】：平人脉象，气血调和。若身有不适，可能为湿邪困脾。\n");
        }

        // --- 2. 结合血氧判断气血 ---
        // 血氧代表携带氧气的能力，可对应中医的“气”
        if (spo2 < 95) {
            sb.append("\n【提示】：气虚血瘀之兆（血氧偏低）。\n");
            sb.append("【调养】：建议补气养血，避免剧烈运动，可根据医嘱服用黄芪、党参等。");
        }

        return sb.toString();
    }
}
