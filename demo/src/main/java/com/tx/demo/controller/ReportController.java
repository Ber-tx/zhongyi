package com.tx.demo.controller;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.tx.demo.entity.Diagnosis;
import com.tx.demo.entity.Patient;
import com.tx.demo.mapper.DiagnosisMapper;
import com.tx.demo.mapper.PatientMapper;
import com.tx.demo.utils.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;

@RestController
@RequestMapping("/api/report")
public class ReportController {

    @Autowired
    private PatientMapper patientMapper;

    @Autowired
    private DiagnosisMapper diagnosisMapper;

    @Autowired
    private RestTemplate restTemplate;

    @Value("${app.services.python-base-url:http://localhost:5000}")
    private String pythonBaseUrl;

    /**
     * 请求体类
     */
    public static class ReportRequest {
        public Long patientId;
        public String idCard;
        public Long caseId;
        // AI辅助生成：Gemini 3 Flash, 2025-12-30
        // 前端传入的已完成板块，用于分阶段报告生成与提示词拼装
        public String completedTypes; // 逗号分隔如 "wang,wen_audio,wen_questionnaire"
        public String customPromptTemplate;
        public String focusMode;

        // 无参构造函数（用于 JSON 反序列化）
        public ReportRequest() {
        }

        public ReportRequest(Long patientId, String idCard) {
            this.patientId = patientId;
            this.idCard = idCard;
        }

        public ReportRequest(Long patientId, String idCard, String completedTypes) {
            this.patientId = patientId;
            this.idCard = idCard;
            this.completedTypes = completedTypes;
        }

        public Long getPatientId() {
            return patientId;
        }

        public void setPatientId(Long patientId) {
            this.patientId = patientId;
        }

        public String getIdCard() {
            return idCard;
        }

        public void setIdCard(String idCard) {
            this.idCard = idCard;
        }

        public Long getCaseId() {
            return caseId;
        }

        public void setCaseId(Long caseId) {
            this.caseId = caseId;
        }

        public String getCompletedTypes() {
            return completedTypes;
        }

        public void setCompletedTypes(String completedTypes) {
            this.completedTypes = completedTypes;
        }

        public String getCustomPromptTemplate() {
            return customPromptTemplate;
        }

        public void setCustomPromptTemplate(String customPromptTemplate) {
            this.customPromptTemplate = customPromptTemplate;
        }

        public String getFocusMode() {
            return focusMode;
        }

        public void setFocusMode(String focusMode) {
            this.focusMode = focusMode;
        }

        @Override
        public String toString() {
            return "ReportRequest{" +
                    "patientId=" + patientId +
                    ", idCard='" + idCard + '\'' +
                    ", caseId=" + caseId +
                    ", completedTypes='" + completedTypes + '\'' +
                    ", customPromptTemplate='" + customPromptTemplate + '\'' +
                    ", focusMode='" + focusMode + '\'' +
                    '}';
        }
    }

    /**
        * 生成综合四诊报告（支持部分板块完成）
        * 这里承接前端的 completedTypes / focusMode / customPromptTemplate，统一转成报告生成上下文。
     * POST /api/report/generate
     */
    @PostMapping("/generate")
    public Result generateReport(@RequestBody ReportRequest request) {

        System.out.println("==== [DEBUG] 开始生成综合四诊报告 ====");
        System.out.println("==== [DEBUG] 请求体: " + request);
        System.out.println("==== [DEBUG] 患者ID: " + (request != null ? request.getPatientId() : "null") + 
                           ", 身份证: " + (request != null ? request.getIdCard() : "null") +
                           ", 已完成类型: " + (request != null ? request.getCompletedTypes() : "null"));

        try {
            // 验证请求是否为空
            if (request == null) {
                System.out.println("==== [ERROR] 请求体为空 ====");
                return Result.error("请求体为空");
            }

            Long patientId = request.getPatientId();
            String idCard = request.getIdCard();
            Long caseId = request.getCaseId();
            String completedTypes = request.getCompletedTypes();
            String customPromptTemplate = request.getCustomPromptTemplate();
            String focusMode = request.getFocusMode();

            System.out.println("==== [DEBUG] 提取数据 - patientId: " + patientId + ", idCard: " + idCard + 
                               ", completedTypes: " + completedTypes);

            // 1. 补齐患者ID
            if (patientId == null || patientId == 0) {
                System.out.println("==== [DEBUG] 患者ID为空或为0，尝试用身份证匹配 ====");
                if (idCard != null && !idCard.isEmpty()) {
                    Patient existing = patientMapper.findByIdCard(idCard);
                    if (existing != null) {
                        patientId = existing.getId();
                        System.out.println("==== [DEBUG] 通过身份证匹配到患者 ID: " + patientId);
                    } else {
                        System.out.println("==== [DEBUG] 身份证在库中不存在: " + idCard);
                        return Result.error("患者不存在，请先完成病人信息登记");
                    }
                } else {
                    System.out.println("==== [ERROR] 患者ID和身份证都为空 ====");
                    return Result.error("缺少患者ID，无法生成报告");
                }
            }

            System.out.println("==== [DEBUG] 最终使用的患者ID: " + patientId);

            // 2. 获取患者基本信息
            Patient patient = patientMapper.selectById(patientId);
            if (patient == null) {
                System.out.println("==== [ERROR] 患者信息不存在: " + patientId);
                return Result.error("找不到该患者信息");
            }

            // 3. 获取今天的诊断记录
            Diagnosis diagnosis = resolveDiagnosisRecord(patientId, caseId);
            if (diagnosis == null) {
                return Result.error("未找到该患者的诊断记录，请先完成四诊操作");
            }

            // 4. 验证四诊完整性（修改：现在只需要至少1个板块完成）
            if (!hasCompletedDiagnosis(diagnosis)) {
                return Result.error("诊断未完成，请完成至少一个诊断板块后生成报告");
            }

            // 5. 构建诊断信息对象
            Map<String, Object> diagnosisInfo = buildDiagnosisInfo(
                    patient,
                    diagnosis,
                    completedTypes,
                    customPromptTemplate,
                    focusMode
            );

            // 6. 调用LLM生成综合建议
            String synthesisResult = callLlmForSynthesis(diagnosisInfo);
            if (synthesisResult == null) {
                return Result.error("调用AI服务失败，请重试");
            }

            // 7. 构建报告
            Map<String, Object> report = new LinkedHashMap<>();
            report.put("reportId", System.currentTimeMillis());
            report.put("caseId", diagnosis.getId());
            report.put("patientInfo", extractPatientInfo(patient));
            report.put("diagnosis", extractDiagnosisInfo(diagnosis));
            report.put("synthesis", synthesisResult);
            report.put("createdAt", System.currentTimeMillis());

            System.out.println("==== [成功] 报告生成完成 ====");
            return Result.success(report);

        } catch (Exception e) {
            System.out.println("==== [异常] 报告生成异常: " + e.getMessage());
            e.printStackTrace();
            return Result.error("服务器错误: " + e.getMessage());
        }
    }

    @PostMapping(value = "/generate/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter generateReportStream(@RequestBody ReportRequest request) {
        SseEmitter emitter = new SseEmitter(300000L);

        Executors.newSingleThreadExecutor().execute(() -> {
            try {
                Long patientId = request.getPatientId();
                Long caseId = request.getCaseId();
                if (patientId == null || patientId == 0) {
                    if (request.getIdCard() != null && !request.getIdCard().isEmpty()) {
                        Patient existing = patientMapper.findByIdCard(request.getIdCard());
                        if (existing != null) {
                            patientId = existing.getId();
                        }
                    }
                }

                Patient patient = patientMapper.selectById(patientId);
                Diagnosis diagnosis = resolveDiagnosisRecord(patientId, caseId);
                if (patient == null || diagnosis == null || !hasCompletedDiagnosis(diagnosis)) {
                    emitter.send(SseEmitter.event().data("{\"error\": \"患者不存在或未完成诊断\"}"));
                    emitter.send(SseEmitter.event().data("[DONE]"));
                    emitter.complete();
                    return;
                }

                Map<String, Object> reportMeta = new HashMap<>();
                reportMeta.put("reportId", System.currentTimeMillis());
                reportMeta.put("caseId", diagnosis.getId());
                reportMeta.put("patientInfo", extractPatientInfo(patient));
                reportMeta.put("diagnosis", extractDiagnosisInfo(diagnosis));
                reportMeta.put("createdAt", System.currentTimeMillis());

                Map<String, Object> metaWrapper = new HashMap<>();
                metaWrapper.put("meta", reportMeta);
                emitter.send(SseEmitter.event().data(JSON.toJSONString(metaWrapper)));

                Map<String, Object> diagnosisInfo = buildDiagnosisInfo(
                        patient,
                        diagnosis,
                        request.getCompletedTypes(),
                        request.getCustomPromptTemplate(),
                        request.getFocusMode()
                );
                String pythonUrl = pythonBaseUrl + "/api/synthesis/llm/stream";
                URL url = new URL(pythonUrl);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json");
                conn.setRequestProperty("Accept", "text/event-stream");
                conn.setDoOutput(true);
                conn.setConnectTimeout(15000);
                conn.setReadTimeout(300000);

                try (OutputStream os = conn.getOutputStream()) {
                    byte[] input = JSON.toJSONString(diagnosisInfo).getBytes(StandardCharsets.UTF_8);
                    os.write(input, 0, input.length);
                }

                int statusCode = conn.getResponseCode();
                if (statusCode < 200 || statusCode >= 300) {
                    emitter.send(SseEmitter.event().data("{\"error\": \"AI 服务不可用，请稍后重试\"}"));
                    emitter.send(SseEmitter.event().data("[DONE]"));
                    emitter.complete();
                    return;
                }

                try (BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), StandardCharsets.UTF_8))) {
                    String line;
                    while ((line = br.readLine()) != null) {
                        if (!line.startsWith("data:")) {
                            continue;
                        }
                        String data = line.substring(5).trim();
                        if ("[DONE]".equals(data)) {
                            emitter.send(SseEmitter.event().data("[DONE]"));
                            break;
                        }
                        emitter.send(SseEmitter.event().data(data));
                    }
                }
                emitter.complete();
            } catch (Exception e) {
                try {
                    emitter.send(SseEmitter.event().data("{\"error\": \"流式生成中断，请重试\"}"));
                    emitter.send(SseEmitter.event().data("[DONE]"));
                    emitter.complete();
                } catch (Exception ignored) {
                    emitter.completeWithError(e);
                }
            }
        });

        return emitter;
    }

    /**
     * 获取诊断记录（前端刷新报告时调用）
     * GET /api/report/get-diagnosis
     */
    @GetMapping("/get-diagnosis")
    public Result getDiagnosis(
            @RequestParam(value = "patientId", required = false) Long patientId,
            @RequestParam(value = "caseId", required = false) Long caseId,
            @RequestParam(value = "idCard", required = false) String idCard) {

        System.out.println("==== [DEBUG] GET /api/report/get-diagnosis ====");
        System.out.println("==== [DEBUG] patientId: " + patientId + ", caseId: " + caseId + ", idCard: " + idCard);

        try {
            // 补齐ID
            if (patientId == null || patientId == 0) {
                System.out.println("==== [DEBUG] 患者ID为空，尝试用身份证匹配 ====");
                if (idCard != null && !idCard.isEmpty()) {
                    Patient existing = patientMapper.findByIdCard(idCard);
                    if (existing != null) {
                        patientId = existing.getId();
                        System.out.println("==== [DEBUG] 通过身份证匹配到患者 ID: " + patientId);
                    } else {
                        System.out.println("==== [ERROR] 患者不存在: " + idCard);
                        return Result.error("患者不存在");
                    }
                } else {
                    System.out.println("==== [ERROR] 缺少患者ID");
                    return Result.error("缺少患者ID");
                }
            }

            System.out.println("==== [DEBUG] 最终使用的患者ID: " + patientId);

            // 获取患者和诊断信息
            Patient patient = patientMapper.selectById(patientId);
            Diagnosis diagnosis = resolveDiagnosisRecord(patientId, caseId);

            if (patient == null || diagnosis == null) {
                System.out.println("==== [ERROR] 找不到患者或诊断记录 ====");
                return Result.error("找不到患者或诊断记录");
            }

            Map<String, Object> response = new LinkedHashMap<>();
            response.put("patient", extractPatientInfo(patient));
            response.put("diagnosis", extractDiagnosisInfo(diagnosis));

            System.out.println("==== [SUCCESS] 成功获取诊断记录 ====");
            return Result.success(response);

        } catch (Exception e) {
            System.out.println("==== [异常] " + e.getMessage());
            e.printStackTrace();
            return Result.error("服务器错误");
        }
    }

    // ===== 辅助方法 =====

    /**
     * 检查是否至少有一个诊断完成（修改：支持部分板块）
     */
    private Diagnosis resolveDiagnosisRecord(Long patientId, Long caseId) {
        if (caseId != null && caseId > 0) {
            Diagnosis byCase = diagnosisMapper.findById(caseId);
            if (byCase != null && patientId != null && patientId.equals(byCase.getPatientId())) {
                return byCase;
            }
            return null;
        }
        return diagnosisMapper.findTodayRecord(patientId);
    }

    private boolean hasCompletedDiagnosis(Diagnosis diagnosis) {
        if ((diagnosis.getWangResult() != null && !diagnosis.getWangResult().isEmpty()) ||
                (diagnosis.getWangTongueMetrics() != null && !diagnosis.getWangTongueMetrics().isEmpty())) {
            return true;
        }
        if (diagnosis.getWenAudioConclusion() != null && !diagnosis.getWenAudioConclusion().isEmpty()) {
            return true;
        }
        if (diagnosis.getWenConclusion() != null && !diagnosis.getWenConclusion().isEmpty()) {
            return true;
        }
        if (diagnosis.getQieHeartRate() != null) {
            return true;
        }
        return false;
    }

    /**
     * 检查四诊是否完整（仅用于向后兼容）
     */
    private boolean isIncomplete(Diagnosis diagnosis) {
        // 这个方法现在只是检查至少有一个诊断完成
        return !hasCompletedDiagnosis(diagnosis);
    }

    /**
     * 构建诊断信息（用于LLM提示词）- 支持部分板块
     */
    private Map<String, Object> buildDiagnosisInfo(Patient patient, Diagnosis diagnosis, String completedTypes,
                                                   String customPromptTemplate, String focusMode) {
        Map<String, Object> info = new LinkedHashMap<>();

        // 患者基本信息
        info.put("patientName", patient.getName());
        info.put("gender", patient.getGender());
        // 优先使用 birthday 计算年龄；若缺失，尝试从 idCard 解析出生日期
        Integer age = calculateAge(patient.getBirthday());
        if (age == null) {
            String idCard = patient.getIdCard();
            if (idCard != null) {
                try {
                    String ymd = null;
                    if (idCard.length() == 18) {
                        ymd = idCard.substring(6, 14); // yyyyMMdd
                    } else if (idCard.length() == 15) {
                        ymd = "19" + idCard.substring(6, 12); // 19yyMMdd
                    }
                    if (ymd != null) {
                        LocalDate bd = LocalDate.parse(ymd, DateTimeFormatter.ofPattern("yyyyMMdd"));
                        age = calculateAge(bd);
                        System.out.println("==== [DEBUG] 从身份证解析出生日期并计算年龄: " + age);
                    }
                } catch (Exception e) {
                    System.out.println("==== [WARN] 无法从身份证解析出生日期: " + e.getMessage());
                }
            }
        }
        info.put("age", age == null ? 0 : age);
        info.put("idCard", patient.getIdCard());

        // 记录已完成的诊断类型
        if (completedTypes != null && !completedTypes.isEmpty()) {
            info.put("completedTypes", completedTypes);
        }
        if (customPromptTemplate != null && !customPromptTemplate.trim().isEmpty()) {
            info.put("customPromptTemplate", customPromptTemplate.trim());
        }
        if (focusMode != null && !focusMode.trim().isEmpty()) {
            info.put("focusMode", focusMode.trim());
        }

        // 四诊信息
        Map<String, Object> diagnoses = new LinkedHashMap<>();

        // 望诊
        if ((diagnosis.getWangResult() != null && !diagnosis.getWangResult().isEmpty()) ||
            (diagnosis.getWangTongueMetrics() != null && !diagnosis.getWangTongueMetrics().isEmpty())) {
            Map<String, Object> wang = new LinkedHashMap<>();
            wang.put("result", diagnosis.getWangResult());
            Object tongueMetrics = parseJsonOrRaw(diagnosis.getWangTongueMetrics());
            if (tongueMetrics != null) {
                wang.put("tongueMetrics", tongueMetrics);
            }
            diagnoses.put("wang", wang);
        }

        // 闻诊（音频）
        if (diagnosis.getWenAudioConclusion() != null && !diagnosis.getWenAudioConclusion().isEmpty()) {
            Map<String, Object> wen = new LinkedHashMap<>();
            wen.put("conclusion", diagnosis.getWenAudioConclusion());
            wen.put("confidence", diagnosis.getWenAudioConfidence());
            if (diagnosis.getWenAudioTags() != null) {
                try {
                    wen.put("tags", JSON.parse(diagnosis.getWenAudioTags()));
                } catch (Exception e) {
                    wen.put("tags", diagnosis.getWenAudioTags());
                }
            }
            Object audioFeatures = parseJsonOrRaw(diagnosis.getWenAudioFeatures());
            if (audioFeatures != null) {
                wen.put("features", audioFeatures);
            }
            diagnoses.put("wen_audio", wen);
        }

        // 问诊（问卷）
        if (diagnosis.getWenConclusion() != null && !diagnosis.getWenConclusion().isEmpty()) {
            Map<String, Object> wenQuestionnaire = new LinkedHashMap<>();
            wenQuestionnaire.put("conclusion", diagnosis.getWenConclusion());
            if (diagnosis.getWenScores() != null) {
                try {
                    wenQuestionnaire.put("scores", JSON.parse(diagnosis.getWenScores()));
                } catch (Exception e) {
                    wenQuestionnaire.put("scores", diagnosis.getWenScores());
                }
            }
            Object profile = buildQuestionnaireProfile(diagnosis.getWenScores());
            if (profile != null) {
                wenQuestionnaire.put("constitutionProfile", profile);
            }
            diagnoses.put("wen_questionnaire", wenQuestionnaire);
        }

        // 切诊（脉搏）
        if (diagnosis.getQieHeartRate() != null) {
            Map<String, Object> qie = new LinkedHashMap<>();
            qie.put("heartRate", diagnosis.getQieHeartRate());
            qie.put("spo2", diagnosis.getQieSpo2());
            qie.put("validRate", diagnosis.getQieValidRate());
            qie.put("sampleCount", diagnosis.getQieSampleCount());
            qie.put("tcmSuggestion", diagnosis.getQieTcmSuggestion());
            qie.put("qualityLevel", determineQieQualityLevel(diagnosis.getQieValidRate(), diagnosis.getQieSampleCount()));
            qie.put("heartRateBand", determineHeartRateBand(diagnosis.getQieHeartRate()));
            qie.put("spo2Band", determineSpo2Band(diagnosis.getQieSpo2()));
            if ("qie".equalsIgnoreCase(String.valueOf(focusMode)) &&
                    diagnosis.getQieKeyMetricsJson() != null &&
                    !diagnosis.getQieKeyMetricsJson().trim().isEmpty()) {
                Object keyMetrics = parseJsonOrRaw(diagnosis.getQieKeyMetricsJson());
                if (keyMetrics != null) {
                    qie.put("keyMetrics", keyMetrics);
                }
            }
            diagnoses.put("qie", qie);
        }

        info.put("diagnoses", diagnoses);
        info.put("llmContext", buildLlmContext());
        return info;
    }

    /**
     * 构建诊断信息（用于LLM提示词）- 兼容旧版本
     */
    private Map<String, Object> buildDiagnosisInfo(Patient patient, Diagnosis diagnosis) {
        return buildDiagnosisInfo(patient, diagnosis, null, null, null);
    }

    /**
     * 提取患者信息（用于报告返回）
     */
    private Map<String, Object> extractPatientInfo(Patient patient) {
        Map<String, Object> info = new LinkedHashMap<>();
        info.put("id", patient.getId());
        info.put("name", patient.getName());
        info.put("gender", patient.getGender());
        info.put("age", calculateAge(patient.getBirthday()));
        info.put("birthday", patient.getBirthday());
        info.put("address", patient.getAddress());
        info.put("idCard", maskIdCard(patient.getIdCard()));
        return info;
    }

    /**
     * 提取诊断信息（用于报告返回）
     */
    private Map<String, Object> extractDiagnosisInfo(Diagnosis diagnosis) {
        Map<String, Object> info = new LinkedHashMap<>();

        // 望诊
        if (diagnosis.getWangResult() != null || diagnosis.getWangTongueMetrics() != null) {
            Map<String, Object> wang = new LinkedHashMap<>();
            wang.put("result", diagnosis.getWangResult());
            wang.put("imageUrl", diagnosis.getWangImageUrl());
            Object tongueMetrics = parseJsonOrRaw(diagnosis.getWangTongueMetrics());
            if (tongueMetrics != null) {
                wang.put("tongueMetrics", tongueMetrics);
            }
            info.put("wang", wang);
        }

        // 闻诊（音频）
        if (diagnosis.getWenAudioConclusion() != null) {
            Map<String, Object> wen = new LinkedHashMap<>();
            wen.put("conclusion", diagnosis.getWenAudioConclusion());
            wen.put("confidence", diagnosis.getWenAudioConfidence());
            if (diagnosis.getWenAudioTags() != null) {
                try {
                    wen.put("tags", JSON.parse(diagnosis.getWenAudioTags()));
                } catch (Exception e) {
                    wen.put("tags", diagnosis.getWenAudioTags());
                }
            }
            Object audioFeatures = parseJsonOrRaw(diagnosis.getWenAudioFeatures());
            if (audioFeatures != null) {
                wen.put("features", audioFeatures);
            }
            info.put("wen_audio", wen);
        }

        // 问诊
        if (diagnosis.getWenConclusion() != null) {
            Map<String, Object> wenQuestionnaire = new LinkedHashMap<>();
            wenQuestionnaire.put("conclusion", diagnosis.getWenConclusion());
            if (diagnosis.getWenScores() != null) {
                Object scores = parseJsonOrRaw(diagnosis.getWenScores());
                if (scores != null) {
                    wenQuestionnaire.put("scores", scores);
                }
            }
            Object profile = buildQuestionnaireProfile(diagnosis.getWenScores());
            if (profile != null) {
                wenQuestionnaire.put("constitutionProfile", profile);
            }
            info.put("wen_questionnaire", wenQuestionnaire);
        }

        // 切诊
        if (diagnosis.getQieHeartRate() != null) {
            Map<String, Object> qie = new LinkedHashMap<>();
            qie.put("heartRate", diagnosis.getQieHeartRate());
            qie.put("spo2", diagnosis.getQieSpo2());
            qie.put("validRate", diagnosis.getQieValidRate());
            qie.put("sampleCount", diagnosis.getQieSampleCount());
            qie.put("tcmSuggestion", diagnosis.getQieTcmSuggestion());
            qie.put("qualityLevel", determineQieQualityLevel(diagnosis.getQieValidRate(), diagnosis.getQieSampleCount()));
            qie.put("heartRateBand", determineHeartRateBand(diagnosis.getQieHeartRate()));
            qie.put("spo2Band", determineSpo2Band(diagnosis.getQieSpo2()));
            Object keyMetrics = parseJsonOrRaw(diagnosis.getQieKeyMetricsJson());
            if (keyMetrics != null) {
                qie.put("keyMetrics", keyMetrics);
            }
            info.put("qie", qie);
        }

        return info;
    }

    /**
     * 调用LLM进行综合诊断
     * 返回综合诊断建议（支持多个LLM服务）
     */
    private String callLlmForSynthesis(Map<String, Object> diagnosisInfo) {
        try {
            // 先尝试调用本地Python AI服务的LLM接口
            String result = callPythonLlmService(diagnosisInfo);
            if (result != null) {
                return result;
            }

            // 备选：调用外部LLM API（Gemini/GPT/Doubao）
            // result = callExternalLlm(diagnosisInfo);
            // if (result != null) {
            //     return result;
            // }

            // 如果LLM调用失败，返回基于规则的合成结果
            return generateRuleBasedSynthesis(diagnosisInfo);

        } catch (Exception e) {
            System.out.println("==== [警告] LLM调用异常: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }

    /**
     * 调用本地Python AI服务的LLM接口
     */
    private String callPythonLlmService(Map<String, Object> diagnosisInfo) {
        try {
            String pythonUrl = pythonBaseUrl + "/api/synthesis/llm";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            String jsonBody = JSON.toJSONString(diagnosisInfo);
            HttpEntity<String> entity = new HttpEntity<>(jsonBody, headers);

            // 调用Python接口
            String response = restTemplate.postForObject(pythonUrl, entity, String.class);
            System.out.println("==== [DEBUG] Python LLM服务响应: " + response);

            if (response != null) {
                JSONObject jsonResponse = JSON.parseObject(response);
                if (jsonResponse.getInteger("code") == 200) {
                    return jsonResponse.getString("synthesis");
                }
            }

        } catch (Exception e) {
            System.out.println("==== [警告] 调用Python LLM服务失败: " + e.getMessage());
        }

        return null;
    }

    /**
     * 基于规则的合成诊断（LLM不可用时的备选方案）
     */
    private String generateRuleBasedSynthesis(Map<String, Object> diagnosisInfo) {
        StringBuilder synthesis = new StringBuilder();

        synthesis.append("## 综合四诊诊断建议\n\n");

        @SuppressWarnings("unchecked")
        Map<String, Object> diagnoses = (Map<String, Object>) diagnosisInfo.get("diagnoses");

        // 分析舌象
        if (diagnoses.containsKey("wang")) {
            @SuppressWarnings("unchecked")
            Map<String, Object> wang = (Map<String, Object>) diagnoses.get("wang");
            synthesis.append("**舌象分析：** ").append(wang.get("result")).append("\n\n");
        }

        // 分析声音
        if (diagnoses.containsKey("wen_audio")) {
            @SuppressWarnings("unchecked")
            Map<String, Object> wen = (Map<String, Object>) diagnoses.get("wen_audio");
            synthesis.append("**声音诊断：** ").append(wen.get("conclusion")).append("\n\n");
        }

        // 分析问卷
        if (diagnoses.containsKey("wen_questionnaire")) {
            @SuppressWarnings("unchecked")
            Map<String, Object> wenQ = (Map<String, Object>) diagnoses.get("wen_questionnaire");
            synthesis.append("**问诊结论：** ").append(wenQ.get("conclusion")).append("\n\n");
        }

        // 分析脉搏
        if (diagnoses.containsKey("qie")) {
            @SuppressWarnings("unchecked")
            Map<String, Object> qie = (Map<String, Object>) diagnoses.get("qie");
            Double heartRate = (Double) qie.get("heartRate");
            Double spo2 = (Double) qie.get("spo2");
            String suggestion = (String) qie.get("tcmSuggestion");

            synthesis.append("**脉搏诊断：** 心率 ").append(heartRate)
                    .append(" bpm, 血氧 ").append(spo2)
                    .append("%\n");

            if (suggestion != null && !suggestion.isEmpty()) {
                synthesis.append(suggestion).append("\n\n");
            }
        }

        synthesis.append("### 建议\n");
        synthesis.append("1. 建议定期复诊，监测体质变化\n");
        synthesis.append("2. 根据诊断结果调整生活起居和饮食\n");
        synthesis.append("3. 遵循医生建议进行调理\n");

        return synthesis.toString();
    }

    // 辅助方法

    /**
     * 计算年龄（根据生日）
     */
    private Integer calculateAge(LocalDate birthday) {
        if (birthday == null) return null;
        return (int) ChronoUnit.YEARS.between(birthday, LocalDate.now());
    }

    /**
     * 隐藏身份证号
     */
    private String maskIdCard(String idCard) {
        if (idCard == null || idCard.length() < 10) {
            return "****";
        }
        return idCard.substring(0, 3) + "****" + idCard.substring(idCard.length() - 4);
    }

    private Object parseJsonOrRaw(String raw) {
        if (raw == null || raw.trim().isEmpty()) {
            return null;
        }
        try {
            return JSON.parse(raw);
        } catch (Exception e) {
            return raw;
        }
    }

    private Object buildQuestionnaireProfile(String scoresRaw) {
        Object parsed = parseJsonOrRaw(scoresRaw);
        if (!(parsed instanceof JSONObject)) {
            return null;
        }

        JSONObject scores = extractQuestionnaireScoreMap((JSONObject) parsed);
        if (scores == null || scores.isEmpty()) {
            return null;
        }
        List<Map<String, Object>> ranking = new ArrayList<>();
        for (String key : scores.keySet()) {
            Object value = scores.get(key);
            Double numericScore = parseNumericScore(value);
            if (numericScore == null) {
                continue;
            }
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("code", key);
            row.put("name", constitutionCodeToName(key));
            row.put("score", numericScore);
            ranking.add(row);
        }

        ranking.sort((a, b) -> Double.compare((Double) b.get("score"), (Double) a.get("score")));
        if (ranking.size() > 3) {
            ranking = new ArrayList<>(ranking.subList(0, 3));
        }

        Map<String, Object> profile = new LinkedHashMap<>();
        profile.put("topConstitutions", ranking);
        return profile;
    }

    private JSONObject extractQuestionnaireScoreMap(JSONObject payload) {
        if (payload == null) {
            return null;
        }
        Object templateResult = payload.get("templateResult");
        if (templateResult instanceof JSONObject) {
            JSONObject templateJson = (JSONObject) templateResult;
            Object scoreMap = templateJson.get("scoreMap");
            if (scoreMap instanceof JSONObject) {
                return (JSONObject) scoreMap;
            }
            Object nestedScores = templateJson.get("scores");
            if (nestedScores instanceof JSONObject) {
                return (JSONObject) nestedScores;
            }
        }
        Object innerScores = payload.get("scores");
        if (innerScores instanceof JSONObject) {
            return (JSONObject) innerScores;
        }
        return payload;
    }

    private Double parseNumericScore(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        try {
            return Double.parseDouble(String.valueOf(value));
        } catch (Exception ignored) {
            return null;
        }
    }

    private Map<String, Object> buildLlmContext() {
        Map<String, Object> context = new LinkedHashMap<>();
        context.put("version", "llm_context_v1");
        context.put("fieldGlossary", buildFieldGlossary());
        context.put("algorithmNotes", buildAlgorithmNotes());
        context.put("diagnosisRules", buildDiagnosisRules());
        return context;
    }

    private Map<String, Object> buildFieldGlossary() {
        Map<String, Object> glossary = new LinkedHashMap<>();

        Map<String, Object> wang = new LinkedHashMap<>();
        wang.put("result", "望诊算法输出的主结论文本，属于算法结论层。可用于提炼舌象证据。");
        wang.put("tongueMetrics", "舌像结构化维度，0-100 分。推荐按 mean 解释强度：0-30 低，30-70 中，70-100 高。std 表示波动/不确定性。");
        glossary.put("wang", wang);

        Map<String, Object> wenAudio = new LinkedHashMap<>();
        wenAudio.put("conclusion", "闻诊算法主结论文本，属于算法结论层。");
        wenAudio.put("confidence", "闻诊模型置信度，0-1，越高越可信。");
        wenAudio.put("tags", "闻诊体质/证候标签集合，供辨证映射参考。");
        wenAudio.put("features", "音频特征摘要，属于信号层，不等同于诊断结论。");
        glossary.put("wen_audio", wenAudio);

        Map<String, Object> wenQuestionnaire = new LinkedHashMap<>();
        wenQuestionnaire.put("conclusion", "问卷算法主结论文本。");
        wenQuestionnaire.put("scores", "各体质原始得分，分值越高表示该体质倾向越明显。");
        wenQuestionnaire.put("constitutionProfile", "体质排名摘要，topConstitutions 为高分体质 Top 列表。");
        glossary.put("wen_questionnaire", wenQuestionnaire);

        Map<String, Object> qie = new LinkedHashMap<>();
        qie.put("heartRate", "心率（bpm）。");
        qie.put("spo2", "血氧饱和度（%）。");
        qie.put("validRate", "有效采样率（%），反映采集质量。");
        qie.put("sampleCount", "采样点数量，数量越高一般稳定性越好。");
        qie.put("qualityLevel", "切诊质量等级（高/中/低），由 validRate 与 sampleCount 共同推断。");
        qie.put("heartRateBand", "心率分段标签（偏低/正常/偏高等）。");
        qie.put("spo2Band", "血氧分段标签（偏低/临界/正常）。");
        qie.put("tcmSuggestion", "切诊算法建议文本，可作为调理建议参考但需与其他板块交叉验证。");
        qie.put("keyMetrics", "切诊关键指标JSON：hrv_rmssd_ms=RMSSD(ms)，rhythm_cv=节律变异系数，perfusion_index=灌注指数，signal_quality=信号质量评分，pulse_tags=脉象标签列表；仅在切诊侧重时重点参考。");
        glossary.put("qie", qie);

        return glossary;
    }

    private Map<String, Object> buildAlgorithmNotes() {
        Map<String, Object> notes = new LinkedHashMap<>();

        Map<String, Object> wang = new LinkedHashMap<>();
        wang.put("name", "舌像结构化评估");
        wang.put("inputs", "舌面图像");
        wang.put("outputs", "result + tongueMetrics");
        wang.put("interpretation", "tongueMetrics 为规则映射后的结构化指标，适合做证据链，不可单独替代临床诊断。");
        notes.put("wang", wang);

        Map<String, Object> wenAudio = new LinkedHashMap<>();
        wenAudio.put("name", "音频特征融合评估");
        wenAudio.put("inputs", "语音片段");
        wenAudio.put("outputs", "conclusion + confidence + tags + features");
        wenAudio.put("interpretation", "features 为声学测量值，conclusion/tags 为模型解释层。需避免把单一声学指标直接等价为证型。");
        notes.put("wen_audio", wenAudio);

        Map<String, Object> wenQuestionnaire = new LinkedHashMap<>();
        wenQuestionnaire.put("name", "体质问卷评分");
        wenQuestionnaire.put("inputs", "问卷答案");
        wenQuestionnaire.put("outputs", "scores + conclusion + constitutionProfile");
        wenQuestionnaire.put("interpretation", "scores 反映倾向强弱，需结合望闻切共同判断。");
        notes.put("wen_questionnaire", wenQuestionnaire);

        Map<String, Object> qie = new LinkedHashMap<>();
        qie.put("name", "脉搏采样统计评估");
        qie.put("inputs", "脉搏信号采样");
        qie.put("outputs", "heartRate/spo2/validRate/sampleCount + band/quality + keyMetrics");
        qie.put("interpretation", "qualityLevel 低时应降低切诊结论置信度，并给出复测建议。");
        notes.put("qie", qie);

        return notes;
    }

    private List<String> buildDiagnosisRules() {
        List<String> rules = new ArrayList<>();
        rules.add("区分三层信息：事实数据层、算法结论层、中医推断层。");
        rules.add("优先使用 fieldGlossary 理解字段，不得臆造字段含义。");
        rules.add("当 confidence 较低或 qualityLevel=低 时，必须降低结论强度并建议补采。");
        rules.add("侧重板块可加长分析，但不得忽略其余板块的冲突证据。");
        return rules;
    }

    private String constitutionCodeToName(String code) {
        if (code == null) {
            return "未知";
        }
        switch (code.toLowerCase()) {
            case "ph":
                return "平和质";
            case "qx":
            case "qixu":
                return "气虚质";
            case "xy":
            case "xueyu":
                return "血瘀质";
            case "yx0":
            case "yinxu":
                return "阴虚质";
            case "yx1":
            case "yangxu":
                return "阳虚质";
            case "ts":
            case "tanshi":
                return "痰湿质";
            case "sr":
            case "shire":
                return "湿热质";
            case "qy":
            case "qiyu":
                return "气郁质";
            case "tb":
            case "tebing":
                return "特禀质";
            default:
                return code;
        }
    }

    private String determineQieQualityLevel(Double validRate, Integer sampleCount) {
        if (validRate == null) {
            return "未知";
        }
        if (validRate >= 85 && sampleCount != null && sampleCount >= 80) {
            return "高";
        }
        if (validRate >= 70) {
            return "中";
        }
        return "低";
    }

    private String determineHeartRateBand(Double heartRate) {
        if (heartRate == null) {
            return "未知";
        }
        if (heartRate < 60) {
            return "偏慢";
        }
        if (heartRate <= 100) {
            return "正常范围";
        }
        return "偏快";
    }

    private String determineSpo2Band(Double spo2) {
        if (spo2 == null) {
            return "未知";
        }
        if (spo2 >= 95) {
            return "正常范围";
        }
        if (spo2 >= 90) {
            return "轻度下降";
        }
        return "偏低";
    }
}
