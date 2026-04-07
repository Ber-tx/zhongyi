package com.tx.demo.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class Diagnosis {
    private Long id;
    private Long patientId;
    
    // --- 问诊字段 ---
    private String wenScores;      // 存 JSON 字符串
    private String wenConclusion;  // 问诊结论
    
    // --- 闻诊字段【新增】---
    private String wenAudioConclusion;  // 闻诊结论（体质判断）
    private String wenAudioFeatures;    // 闻诊音频特征 JSON
    private Double wenAudioConfidence;  // 闻诊置信度
    private String wenAudioTags;
    private String wenAudioUrl;// 闻诊体质标签（JSON数组）
    
    private Integer status;

    // --- 望诊字段 ---
    private String wangResult;
    private String wangImageUrl;   // 存放图片路径或 Base64
    private String wangTongueMetrics; // 舌象结构化维度(JSON)

    // --- 切诊字段 ---
    private Double qieHeartRate;
    private Double qieSpo2;
    private Double qieValidRate;        // 信号有效率（0-100）
    private Integer qieSampleCount;     // 有效采样次数
    private String qieTcmSuggestion;    // 中医建议（Python 生成）
    private String qieKeyMetricsJson;   // 关键脉诊指标JSON：hrv_rmssd_ms/rhythm_cv/perfusion_index/signal_quality/pulse_tags

    private LocalDateTime createTime;
}
