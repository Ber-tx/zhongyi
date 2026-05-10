package com.tx.demo.controller;

import com.tx.demo.entity.Answer;
import com.tx.demo.entity.Diagnosis;
import com.tx.demo.entity.Patient;
import com.tx.demo.mapper.DiagnosisMapper;
import com.tx.demo.mapper.PatientMapper;
import com.tx.demo.service.QuestionService;
import com.tx.demo.utils.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/tcm")
public class QuestionController {

    @Autowired
    private QuestionService questionService;

    @Autowired
    private PatientMapper patientMapper;

    @Autowired
    private DiagnosisMapper diagnosisMapper;

    @PostMapping("/submit")
    public Result submit(@RequestBody Answer request) {
        System.out.println("DEBUG: 接收到的实体对象为: " + request);

        Long realId = null;

        // 第一步：先看前端有没有传 patientId 
        if (request.getPatientId() != null) {
            realId = request.getPatientId();
        }
        // 第二步：如果 ID 丢了，尝试用 idCard 去数据库捞
        else if (request.getIdCard() != null && !request.getIdCard().isEmpty()) {
            Patient p = patientMapper.findByIdCard(request.getIdCard());
            if (p != null) {
                realId = p.getId();
            }
        }

        // 最终检查：都没拿到，没录入
        if (realId == null) {
            return Result.error("无法关联病人！请检查是否已录入信息或身份证号是否传递。");
        }

        String templateCode = request.getTemplateCode() == null || request.getTemplateCode().trim().isEmpty()
                ? "original"
                : request.getTemplateCode().trim();

        // 校验问卷完整性：原始版本要求 33 题，专项模板允许按各自题数提交
        if (request.getAnswers() == null || request.getAnswers().isEmpty()) {
            return Result.error("问卷数据不完整，请重新检查！");
        }
        if ("original".equalsIgnoreCase(templateCode) && request.getAnswers().size() < 33) {
            return Result.error("原始问卷数据不完整，请重新检查！");
        }

        // 调用业务层：传入真实的 realId
        return questionService.calculateConstitution(
                request.getAnswers(),
                realId,
                request.getDiagnosisId(),
                templateCode,
                request.getTemplateTitle(),
                request.getTemplateResult()
        );
    }

    @PostMapping("/reset-wen")
    public Result resetWen(@RequestBody Map<String, Object> request) {
        Long diagnosisId = parseLong(request.get("diagnosisId"));
        Long patientId = parseLong(request.get("patientId"));

        if (diagnosisId == null) {
            return Result.error("缺少诊断会话ID，无法清空问诊结果");
        }

        Diagnosis diagnosis = diagnosisMapper.findById(diagnosisId);
        if (diagnosis == null) {
            return Result.error("诊断会话不存在");
        }

        if (patientId != null && diagnosis.getPatientId() != null && !patientId.equals(diagnosis.getPatientId())) {
            return Result.error("诊断会话与患者不匹配");
        }

        diagnosis.setWenScores(null);
        diagnosis.setWenConclusion(null);
        diagnosisMapper.updateWen(diagnosis);
        return Result.success("问诊结果已清空");
    }

    private Long parseLong(Object value) {
        if (value == null) return null;
        if (value instanceof Number) return ((Number) value).longValue();
        String str = String.valueOf(value).trim();
        if (str.isEmpty()) return null;
        try {
            return Long.parseLong(str);
        } catch (NumberFormatException e) {
            return null;
        }
    }
}
