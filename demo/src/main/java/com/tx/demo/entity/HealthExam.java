package com.tx.demo.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 居民体检管理实体类（信息录入简化版）
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class HealthExam {
    private Long id;
    
    // 基本信息
    private String patientName;
    private String patientGender;
    private Integer patientAge;
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDate patientBirthday;
    private String patientIdCard;
    private String phone;
    private String address;
    private String occupation;
    private String marital;
    
    // 体检日期和体质
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDate examDate;
    private String constitutionType;
    
    // 生活习惯
    private String smoking;
    private String drinking;
    private String exercise;
    private String sleepQuality;
    
    // 病史信息
    private String medicalHistory;
    private String familyHistory;
    private String allergyHistory;
    
    // 体格检查项目
    private BigDecimal height;
    private BigDecimal weight;
    private BigDecimal bmi;
    private BigDecimal waistCircumference;
    private BigDecimal hipCircumference;
    private BigDecimal temperature;
    private Integer heartRate;
    private BigDecimal spo2;
    
    // 血压
    private Integer bloodPressureSystolic;
    private Integer bloodPressureDiastolic;
    
    // 体格检查结论
    private String visionLeft;
    private String visionRight;
    private String hearing;
    
    // 血糖代谢
    private BigDecimal fastingBloodGlucose;
    private BigDecimal postprandialGlucose;
    private BigDecimal hba1c;
    
    // 血脂四项
    private BigDecimal totalCholesterol;
    private BigDecimal triglycerides;
    private BigDecimal hdl;
    private BigDecimal ldl;
    
    // 肝功能
    private BigDecimal alt;
    private BigDecimal ast;
    private BigDecimal totalBilirubin;
    private BigDecimal albumin;
    
    // 肾功能
    private BigDecimal creatinine;
    private BigDecimal bun;
    private BigDecimal uricAcid;
    
    // 血常规
    private BigDecimal hemoglobin;
    private BigDecimal wbc;
    private BigDecimal rbc;
    private BigDecimal platelets;
    
    // 辅助检查
    private String chestXray;
    private String abdominalUltrasound;
    private String ecg;
    private String otherImaging;
    
    // 尿常规
    private String urineProtein;
    private String urineGlucose;
    private String urineBlood;
    
    // 综合评估
    private String healthGrade;
    private String doctorAdvice;
    private String remarks;
    
    // 系统字段
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime createTime;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime updateTime;
}
