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
    public Result calculateConstitution(List<Integer> answers, Long patientId) {
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

        // 4. 判定主结论
        String mainCode = "ph";
        int maxScore = 0;
        for (String code : codes) {
            if (code.equals("ph")) continue;
            if (scoreMap.get(code) > maxScore) {
                maxScore = scoreMap.get(code);
                mainCode = code;
            }
        }
        if (maxScore < 11) mainCode = "ph";

        String conclusion = getTypeName(mainCode);
        String scoresJson;
        try {
            scoresJson = objectMapper.writeValueAsString(scoreMap);
        } catch (Exception e) {
            scoresJson = "{}";
        }

        // --- 修复后的入库逻辑 ---

        // 1. 先声明一个变量用来存储最终的 ID
        Long finalDiagnosisId;

        // 2. 尝试从数据库获取今天该病人的记录
        Diagnosis todayRecord = diagnosisMapper.findTodayRecord(patientId);

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

        return Result.success(result);

    }

    private String getTypeName(String code) {
        Map<String, String> names = new HashMap<>();
        names.put("ph", "平和质"); names.put("qx", "气虚质"); names.put("yx1", "阳虚质");
        names.put("yx0", "阴虚质"); names.put("ts", "痰湿质"); names.put("sr", "湿热质");
        names.put("xy", "血瘀质"); names.put("qy", "气郁质"); names.put("tb", "特禀质");
        return names.getOrDefault(code, "未知体质");
    }
}