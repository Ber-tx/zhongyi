package com.tx.demo.mapper;

import com.tx.demo.entity.Diagnosis;
import org.apache.ibatis.annotations.*;

@Mapper
public interface DiagnosisMapper {
    // 核心查询：查找该病人今天最新的诊断记录
    @Select("SELECT * FROM diagnosis WHERE patient_id = #{patientId} " +
            "AND create_time >= CURDATE() ORDER BY create_time DESC LIMIT 1")
    Diagnosis findTodayRecord(Long patientId);

    // 基础插入：用于第一个板块开始时创建记录
    @Insert("INSERT INTO diagnosis(patient_id, status, create_time, wen_scores, wen_conclusion, wang_result, wang_image_url) " +
            "VALUES(#{patientId}, 0, NOW(), #{wenScores}, #{wenConclusion}, #{wangResult}, #{wangImageUrl})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(Diagnosis diagnosis);

    // 望诊更新方法
    @Update("UPDATE diagnosis SET wang_result = #{wangResult}, wang_image_url = #{wangImageUrl} WHERE id = #{id}")
    int updateWang(Diagnosis diagnosis);

    // 问诊更新方法
    @Update("UPDATE diagnosis SET wen_scores = #{wenScores}, wen_conclusion = #{wenConclusion} WHERE id = #{id}")
    int updateWen(Diagnosis diagnosis);
}
