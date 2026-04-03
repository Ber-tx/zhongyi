package com.tx.demo.service;

import com.tx.demo.utils.Result;

import java.util.List;
import java.util.Map;

public interface QuestionService {
    /**
     * 根据 33 道题的答案计算体质结果
     * @param answers 前端提交的 1-5 分数列表
     * @return 包含主体质和各项分数的 Map
     */

    Result calculateConstitution(List<Integer> answers, Long patientId, Long diagnosisId,
                                 String templateCode, String templateTitle, Map<String, Object> templateResult);
}
