package com.tx.demo.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class Diagnosis {
    private Long id;
    private Long patientId;
    private String wenScores;      // 存 JSON 字符串
    private String wenConclusion;  // 问诊结论
    private Integer status;

    // 存放 Python 返回的诊断文字结果
    private String wangResult;
    private String wangImageUrl;   // 存放图片路径或 Base64

    // --- 切诊字段 ---
    private Double qieHeartRate;
    private Double qieSpo2;
    private Double qieValidRate;        // 【新增】信号有效率（0-100）
    private Integer qieSampleCount;     // 【新增】有效采样次数
    private String qieTcmSuggestion;    // 【新增】中医建议（Python 生成）

    private LocalDateTime createTime;
}
