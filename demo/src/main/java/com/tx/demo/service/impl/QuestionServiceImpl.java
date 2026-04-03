package com.tx.demo.service.impl;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tx.demo.entity.Diagnosis;
import com.tx.demo.entity.Question;
import com.tx.demo.mapper.DiagnosisMapper;
import com.tx.demo.mapper.QuestionMapper;
import com.tx.demo.service.QuestionService;
import com.tx.demo.utils.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;

@Service
public class QuestionServiceImpl implements QuestionService {

    @Autowired
    private QuestionMapper questionMapper;
    @Autowired
    private DiagnosisMapper diagnosisMapper;
    @Autowired
    private ObjectMapper objectMapper;

    @Override
    public Result calculateConstitution(List<Integer> answers, Long patientId, Long diagnosisId,
                                        String templateCode, String templateTitle, Map<String, Object> templateResult) {
        String normalizedTemplateCode = normalizeTemplateCode(templateCode);
        if (!"original".equals(normalizedTemplateCode)) {
            return calculateTemplateQuestionnaire(
                    answers,
                    patientId,
                    diagnosisId,
                    normalizedTemplateCode,
                    templateTitle,
                    templateResult
            );
        }

        return calculateOriginalConstitution(answers, patientId, diagnosisId);
    }

    private Result calculateOriginalConstitution(List<Integer> answers, Long patientId, Long diagnosisId) {
        // 1. 获取题目规则
        List<Question> questions = questionMapper.selectAllQuestions();

        // 2. 初始化分数桶
        String[] codes = {"ph", "qx", "xy", "yx0", "ts", "sr", "qy", "tb","yx1"};
        Map<String, Integer> scoreMap = new HashMap<>();
        for (String code : codes) scoreMap.put(code, 0);

        // 3. 计算分数
        for (int i = 0; i < questions.size(); i++) {
            if (i >= answers.size()) break;
            Question q = questions.get(i);
            int rawScore = answers.get(i);

            // 正反向处理 (1为反向)
            int finalScore = (q.getIsReverse() != null && q.getIsReverse() == 1)
                    ? (6 - rawScore) : rawScore;

            String field = q.getConstitutionCodes();
            // 【关键点】处理一道题对应多个体质的情况
            if (field != null && !field.trim().isEmpty()) {
                // 支持英文逗号和中文逗号，防止录入错误
                String[] relatedCodes = field.split("[,，]");

                for (String c : relatedCodes) {
                    String cleanCode = c.trim().toLowerCase();
                    if (scoreMap.containsKey(cleanCode)) {
                        // 在原有分数基础上累加
                        scoreMap.put(cleanCode, scoreMap.get(cleanCode) + finalScore);
                    }
                }

            }
        }
        //  scoreMap 已经存满了各体质的总分
        System.out.println(">>> 计分完成，最终得分明细: " + scoreMap);

        // 4. 判定主结论与候选体质
        List<ConstitutionCandidate> candidates = buildOriginalCandidates(scoreMap);
        String conclusion = candidates.isEmpty() ? "平和质" : buildConclusionText(candidates);
        String scoresJson;
        try {
            Map<String, Object> payload = new LinkedHashMap<>();
            payload.put("scores", scoreMap);
            payload.put("candidateConstitutions", candidates);
            payload.put("mainConstitution", conclusion);
            scoresJson = objectMapper.writeValueAsString(payload);
        } catch (Exception e) {
            scoresJson = "{}";
        }

        // --- 修复后的入库逻辑 ---

        // 1. 先声明一个变量用来存储最终的 ID
        Long finalDiagnosisId;

        // 2. 尝试从数据库获取今天该病人的记录
        Diagnosis todayRecord = null;
        if (diagnosisId != null && diagnosisId > 0) {
            todayRecord = diagnosisMapper.findById(diagnosisId);
            if (todayRecord != null && !patientId.equals(todayRecord.getPatientId())) {
                return Result.error("诊断会话与患者不匹配");
            }
        }
        if (todayRecord == null) {
            todayRecord = diagnosisMapper.findTodayRecord(patientId);
        }

        if (todayRecord != null) {
            // 情况 A: 记录来自数据库
            System.out.println("==== 发现已有记录 ID: " + todayRecord.getId() + "，准备更新问诊数据 ====");

            todayRecord.setWenScores(scoresJson);
            todayRecord.setWenConclusion(conclusion);

            // 执行更新
            diagnosisMapper.updateWen(todayRecord);

            // 记录 ID
            finalDiagnosisId = todayRecord.getId();
        } else {
            // 情况 B: 新建记录
            System.out.println("==== 未发现记录，准备新建诊断行 ====");

            Diagnosis newRecord = new Diagnosis();
            newRecord.setPatientId(patientId);
            newRecord.setWenScores(scoresJson);
            newRecord.setWenConclusion(conclusion);
            newRecord.setStatus(0);
            newRecord.setCreateTime(LocalDateTime.now());

            // 执行插入
            diagnosisMapper.insert(newRecord);

            // 获取自增生成的 ID (MyBatis 会回填到对象中)
            finalDiagnosisId = newRecord.getId();
        }

        // 7. 返回给前端结果

        Map<String, Object> result = new HashMap<>();
        result.put("diagnosisId", finalDiagnosisId);
        result.put("mainType", conclusion);
        result.put("scores", scoreMap);
        result.put("candidateConstitutions", candidates);

        return Result.success(result);

    }

    private Result calculateTemplateQuestionnaire(List<Integer> answers, Long patientId, Long diagnosisId,
                                                  String templateCode, String templateTitle,
                                                  Map<String, Object> templateResult) {
        Map<String, Object> normalizedResult = normalizeTemplateResult(templateCode, templateTitle, templateResult, answers);
        String conclusion = String.valueOf(normalizedResult.getOrDefault("title", templateTitle != null ? templateTitle : "专项问诊结论"));

        String scoresJson;
        try {
            Map<String, Object> payload = new LinkedHashMap<>();
            payload.put("templateCode", templateCode);
            payload.put("templateTitle", templateTitle);
            payload.put("templateResult", normalizedResult);
            payload.put("answers", answers);
            scoresJson = objectMapper.writeValueAsString(payload);
        } catch (Exception e) {
            scoresJson = "{}";
        }

        Long finalDiagnosisId;
        Diagnosis todayRecord = null;
        if (diagnosisId != null && diagnosisId > 0) {
            todayRecord = diagnosisMapper.findById(diagnosisId);
            if (todayRecord != null && !patientId.equals(todayRecord.getPatientId())) {
                return Result.error("诊断会话与患者不匹配");
            }
        }
        if (todayRecord == null) {
            todayRecord = diagnosisMapper.findTodayRecord(patientId);
        }

        if (todayRecord != null) {
            todayRecord.setWenScores(scoresJson);
            todayRecord.setWenConclusion(conclusion);
            diagnosisMapper.updateWen(todayRecord);
            finalDiagnosisId = todayRecord.getId();
        } else {
            Diagnosis newRecord = new Diagnosis();
            newRecord.setPatientId(patientId);
            newRecord.setWenScores(scoresJson);
            newRecord.setWenConclusion(conclusion);
            newRecord.setStatus(0);
            newRecord.setCreateTime(LocalDateTime.now());
            diagnosisMapper.insert(newRecord);
            finalDiagnosisId = newRecord.getId();
        }

        Map<String, Object> result = new HashMap<>();
        result.put("diagnosisId", finalDiagnosisId);
        result.put("mainType", conclusion);
        result.put("templateCode", templateCode);
        result.put("templateResult", normalizedResult);
        result.put("scores", normalizedResult);
        result.put("candidateConstitutions", normalizedResult.get("candidateConstitutions"));

        return Result.success(result);
    }

    private List<ConstitutionCandidate> buildOriginalCandidates(Map<String, Integer> scoreMap) {
        List<ConstitutionCandidate> candidates = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : scoreMap.entrySet()) {
            String code = entry.getKey();
            if ("ph".equals(code)) {
                continue;
            }
            int score = entry.getValue() == null ? 0 : entry.getValue();
            candidates.add(new ConstitutionCandidate(code, getTypeName(code), score, getBiasLevel(score)));
        }
        candidates.sort((a, b) -> Integer.compare(b.getScore(), a.getScore()));

        int maxScore = candidates.isEmpty() ? 0 : candidates.get(0).getScore();
        List<ConstitutionCandidate> topCandidates = new ArrayList<>();
        for (ConstitutionCandidate candidate : candidates) {
            if (candidate.getScore() == maxScore) {
                topCandidates.add(candidate);
            }
        }

        if (scoreMap.getOrDefault("ph", 0) >= 11 && candidates.stream().allMatch(c -> c.getScore() < 9)) {
            return Collections.singletonList(new ConstitutionCandidate("ph", "平和质", scoreMap.getOrDefault("ph", 0), getBiasLevel(scoreMap.getOrDefault("ph", 0))));
        }

        if (topCandidates.size() >= 2 && Math.abs(topCandidates.get(0).getScore() - topCandidates.get(1).getScore()) <= 1) {
            return topCandidates.subList(0, 2);
        }

        if (!topCandidates.isEmpty()) {
            return Collections.singletonList(topCandidates.get(0));
        }

        return Collections.singletonList(new ConstitutionCandidate("ph", "平和质", scoreMap.getOrDefault("ph", 0), getBiasLevel(scoreMap.getOrDefault("ph", 0))));
    }

    private String buildConclusionText(List<ConstitutionCandidate> candidates) {
        if (candidates == null || candidates.isEmpty()) {
            return "平和质";
        }
        if (candidates.size() == 1) {
            return candidates.get(0).getName();
        }
        return candidates.get(0).getName() + "、" + candidates.get(1).getName();
    }

    private String getBiasLevel(int score) {
        if (score >= 19) return "重度偏颇";
        if (score >= 13) return "中度偏颇";
        if (score >= 7) return "轻微偏颇";
        return "无明显偏颇";
    }

    private Map<String, Object> normalizeTemplateResult(String templateCode, String templateTitle,
                                                        Map<String, Object> templateResult, List<Integer> answers) {
        Map<String, Object> normalized = new LinkedHashMap<>();
        if (templateResult != null) {
            normalized.putAll(templateResult);
        }

        if (!normalized.containsKey("title") || normalized.get("title") == null) {
            normalized.put("title", templateTitle != null && !templateTitle.trim().isEmpty()
                    ? templateTitle
                    : getTemplateDisplayName(templateCode));
        }
        if (!normalized.containsKey("summary") || normalized.get("summary") == null) {
            normalized.put("summary", "问诊已完成，请结合生活方式与线下检查进一步评估。");
        }
        if (!normalized.containsKey("diet")) {
            normalized.put("diet", new ArrayList<>());
        }
        if (!normalized.containsKey("avoid")) {
            normalized.put("avoid", new ArrayList<>());
        }
        if (!normalized.containsKey("suggestions")) {
            normalized.put("suggestions", new ArrayList<>());
        }
        normalized.putIfAbsent("badge", getTemplateDisplayName(templateCode));
        normalized.putIfAbsent("templateCode", templateCode);
        normalized.putIfAbsent("templateTitle", templateTitle);
        normalized.putIfAbsent("answerCount", answers == null ? 0 : answers.size());
        normalized.putIfAbsent("candidateConstitutions", buildTemplateCandidates(normalized));
        return normalized;
    }

    private List<Map<String, Object>> buildTemplateCandidates(Map<String, Object> normalized) {
        List<Map<String, Object>> candidates = new ArrayList<>();
        Object constitutionScores = normalized.get("constitutionScores");
        if (constitutionScores instanceof List<?>) {
            for (Object item : (List<?>) constitutionScores) {
                if (item instanceof Map<?, ?>) {
                    Map<?, ?> map = (Map<?, ?>) item;
                    Map<String, Object> candidate = new LinkedHashMap<>();
                    candidate.put("name", map.get("name"));
                    candidate.put("score", map.get("score"));
                    candidate.put("level", map.get("level"));
                    candidates.add(candidate);
                }
            }
        }
        if (!candidates.isEmpty()) {
            candidates.sort((a, b) -> Integer.compare(
                    parseIntSafe(b.get("score")),
                    parseIntSafe(a.get("score"))
            ));
        }
        return candidates;
    }

    private int parseIntSafe(Object value) {
        if (value == null) return 0;
        if (value instanceof Number) return ((Number) value).intValue();
        try {
            return Integer.parseInt(String.valueOf(value));
        } catch (Exception e) {
            return 0;
        }
    }

    private String normalizeTemplateCode(String templateCode) {
        String raw = templateCode == null ? "" : templateCode.trim().toLowerCase(Locale.ROOT);
        return raw.isEmpty() ? "original" : raw;
    }

    private String getTemplateDisplayName(String templateCode) {
        Map<String, String> names = new HashMap<>();
        names.put("original", "原始问卷");
        names.put("hypertension", "高血压专项问诊");
        names.put("diabetes", "糖尿病专项问诊");
        names.put("children", "儿童体质辨识");
        names.put("fivepersonality", "五态人格测评");
        names.put("five_personality", "五态人格测评");
        return names.getOrDefault(templateCode, "专项问诊");
    }

    private String getTypeName(String code) {
        Map<String, String> names = new HashMap<>();
        names.put("ph", "平和质"); names.put("qx", "气虚质"); names.put("yx1", "阳虚质");
        names.put("yx0", "阴虚质"); names.put("ts", "痰湿质"); names.put("sr", "湿热质");
        names.put("xy", "血瘀质"); names.put("qy", "气郁质"); names.put("tb", "特禀质");
        return names.getOrDefault(code, "未知体质");
    }

    public static class ConstitutionCandidate {
        private final String code;
        private final String name;
        private final int score;
        private final String level;

        public ConstitutionCandidate(String code, String name, int score, String level) {
            this.code = code;
            this.name = name;
            this.score = score;
            this.level = level;
        }

        public String getCode() {
            return code;
        }

        public String getName() {
            return name;
        }

        public int getScore() {
            return score;
        }

        public String getLevel() {
            return level;
        }
    }
}
