package com.tx.demo.controller;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.tx.demo.entity.Diagnosis;
import com.tx.demo.entity.Patient;
import com.tx.demo.mapper.DiagnosisMapper;
import com.tx.demo.mapper.PatientMapper;
import com.tx.demo.utils.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.time.LocalDateTime;
import java.util.UUID;

@RestController
@RequestMapping("/api/wen")
public class WenController {

    @Autowired
    private PatientMapper patientMapper;

    @Autowired
    private DiagnosisMapper diagnosisMapper;

    // 定义临时存储路径
    private static final String UPLOAD_PATH = "E:/项目/zhongyi_uploads/tcm_temp/";

    @PostMapping("/save")
    public Result handleWenSave(
            @RequestParam("patientId") Long patientId,
            @RequestParam("idCard") String idCard,
            @RequestParam("conclusion") String conclusion,
            @RequestParam("confidence") Double confidence,
            @RequestParam(value = "tags", required = false) String tags,
            @RequestParam(value = "features", required = false) String features,
            @RequestParam(value = "file", required = false) MultipartFile file) {
        
        System.out.println("==== [DEBUG] 开始执行闻诊入库逻辑 ====");
        System.out.println("==== [DEBUG] 病人ID: " + patientId + ", 身份证: " + idCard);

        // 1. 补齐 ID 逻辑
        if (patientId == null || patientId == 0) {
            if (idCard != null && !idCard.isEmpty()) {
                Patient existing = patientMapper.findByIdCard(idCard);
                if (existing != null) {
                    patientId = existing.getId();
                    System.out.println("==== [DEBUG] 通过身份证匹配到病人 ID: " + patientId);
                } else {
                    System.out.println("==== [DEBUG] 警告：身份证 " + idCard + " 在库中不存在！");
                    return Result.error("请先完成病人信息登记再进行分析");
                }
            } else {
                System.out.println("==== [DEBUG] 警告：未能获取到有效的病人 ID ====");
                return Result.error("缺少病人ID，无法保存记录");
            }
        }

        try {
            // 2. 查找今天是否已有记录
            Diagnosis record = diagnosisMapper.findTodayRecord(patientId);

            if (record != null) {
                // 【情况A】已有记录（其他板块先开始了），直接补充闻诊结果
                System.out.println("==== [合并数据] 正在将闻诊结果更新至已有记录 ID: " + record.getId());
                
                record.setWenAudioConclusion(conclusion);
                record.setWenAudioConfidence(confidence);
                record.setWenAudioTags(tags);
                record.setWenAudioFeatures(features);

                int rows = diagnosisMapper.updateWenAudio(record);
                if (rows > 0) {
                    System.out.println("==== [成功] 闻诊数据已合并至记录 ID: " + record.getId());
                    return Result.success(record);
                } else {
                    System.out.println("==== [失败] 更新闻诊数据失败");
                    return Result.error("数据保存失败");
                }
            } else {
                // 【情况B】今天还没有任何记录，创建新记录
                System.out.println("==== [新增记录] 创建新的诊断记录");
                
                Diagnosis diagnosis = new Diagnosis();
                diagnosis.setPatientId(patientId);
                diagnosis.setStatus(0);
                diagnosis.setCreateTime(LocalDateTime.now());
                
                diagnosis.setWenAudioConclusion(conclusion);
                diagnosis.setWenAudioConfidence(confidence);
                diagnosis.setWenAudioTags(tags);
                diagnosis.setWenAudioFeatures(features);

                int rows = diagnosisMapper.insert(diagnosis);
                if (rows > 0) {
                    System.out.println("==== [成功] 闻诊数据已入库，记录 ID: " + diagnosis.getId());
                    return Result.success(diagnosis);
                } else {
                    System.out.println("==== [失败] 新建诊断记录失败");
                    return Result.error("数据保存失败");
                }
            }

        } catch (Exception e) {
            System.out.println("==== [异常] 闻诊入库异常: " + e.getMessage());
            e.printStackTrace();
            return Result.error("服务器错误: " + e.getMessage());
        }
    }

    /**
     * 备选方案：前端先调用 Python AI 服务，再调用此接口入库
     * 此方案不再需要中间调用 Python
     */
    @PostMapping("/save-direct")
    public Result saveWenDirect(
            @RequestParam("patientId") Long patientId,
            @RequestParam("idCard") String idCard,
            @RequestBody String analysisResultJson) {
        
        System.out.println("==== [DEBUG] 直接保存闻诊结果 ====");
        System.out.println("==== [DEBUG] 分析结果: " + analysisResultJson);

        try {
            // 解析前端传来的 AI 分析结果
            JSONObject analysisResult = JSON.parseObject(analysisResultJson);
            
            if (analysisResult == null || !analysisResult.containsKey("main_finding")) {
                return Result.error("分析结果格式不正确");
            }

            // 补齐 ID
            if (patientId == null || patientId == 0) {
                Patient existing = patientMapper.findByIdCard(idCard);
                if (existing != null) {
                    patientId = existing.getId();
                } else {
                    return Result.error("请先完成病人信息登记");
                }
            }

            // 查找或创建记录
            Diagnosis record = diagnosisMapper.findTodayRecord(patientId);
            
            String conclusion = analysisResult.getString("main_finding");
            Double confidence = analysisResult.getDouble("confidence");
            String tags = analysisResult.getJSONArray("constitution_tags").toJSONString();
            String features = analysisResult.getJSONObject("features").toJSONString();

            if (record != null) {
                record.setWenAudioConclusion(conclusion);
                record.setWenAudioConfidence(confidence);
                record.setWenAudioTags(tags);
                record.setWenAudioFeatures(features);
                diagnosisMapper.updateWenAudio(record);
            } else {
                Diagnosis diagnosis = new Diagnosis();
                diagnosis.setPatientId(patientId);
                diagnosis.setStatus(0);
                diagnosis.setCreateTime(LocalDateTime.now());
                diagnosis.setWenAudioConclusion(conclusion);
                diagnosis.setWenAudioConfidence(confidence);
                diagnosis.setWenAudioTags(tags);
                diagnosis.setWenAudioFeatures(features);
                diagnosisMapper.insert(diagnosis);
                record = diagnosis;
            }

            System.out.println("==== [成功] 闻诊数据已入库");
            return Result.success();

        } catch (Exception e) {
            System.out.println("==== [异常] " + e.getMessage());
            e.printStackTrace();
            return Result.error("服务器错误: " + e.getMessage());
        }
    }
}
