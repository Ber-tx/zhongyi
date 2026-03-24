package com.tx.demo.mapper;

import com.tx.demo.entity.Diagnosis;
import org.apache.ibatis.annotations.*;

@Mapper
public interface DiagnosisMapper {

    /**
     * 核心查询：查找该病人今天最新的诊断记录
     */
    @Select("SELECT * FROM diagnosis WHERE patient_id = #{patientId} " +
            "AND DATE(create_time) = CURDATE() ORDER BY create_time DESC LIMIT 1")
    Diagnosis findTodayRecord(Long patientId);

    /**
     * 基础插入：创建新记录
     */
    @Insert("INSERT INTO diagnosis(patient_id, status, create_time, " +
            "wen_scores, wen_conclusion, wen_audio_conclusion, wen_audio_features, wen_audio_confidence, wen_audio_tags,wen_audio_url, " +
            "wang_result, wang_image_url, " +
            "qie_heart_rate, qie_spo2, qie_valid_rate, qie_sample_count, qie_tcm_suggestion) " +
            "VALUES(#{patientId}, 0, NOW(), " +
            "#{wenScores}, #{wenConclusion}, #{wenAudioConclusion}, #{wenAudioFeatures}, #{wenAudioConfidence}, #{wenAudioTags},#{wenAudioUrl}, " +
            "#{wangResult}, #{wangImageUrl}, " +
            "#{qieHeartRate}, #{qieSpo2}, #{qieValidRate}, #{qieSampleCount}, #{qieTcmSuggestion})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(Diagnosis diagnosis);

    /**
     * 望诊更新
     */
    @Update("UPDATE diagnosis SET wang_result = #{wangResult}, wang_image_url = #{wangImageUrl} WHERE id = #{id}")
    int updateWang(Diagnosis diagnosis);

    /**
     * 问诊更新
     */
    @Update("UPDATE diagnosis SET wen_scores = #{wenScores}, wen_conclusion = #{wenConclusion} WHERE id = #{id}")
    int updateWen(Diagnosis diagnosis);

    /**
     * 闻诊更新【新增】
     */
    @Update("UPDATE diagnosis SET " +
            "wen_audio_conclusion = #{wenAudioConclusion}, " +
            "wen_audio_features = #{wenAudioFeatures}, " +
            "wen_audio_confidence = #{wenAudioConfidence}, " +
            "wen_audio_tags = #{wenAudioTags}, " +
            "wen_audio_url = #{wenAudioUrl} "+
            "WHERE id = #{id}")
    int updateWenAudio(Diagnosis diagnosis);

    /**
     * 切诊更新（优化后：只存统计数据，不存原始波形）
     */
    @Update("UPDATE diagnosis SET " +
            "qie_heart_rate = #{qieHeartRate}, " +
            "qie_spo2 = #{qieSpo2}, " +
            "qie_valid_rate = #{qieValidRate}, " +
            "qie_sample_count = #{qieSampleCount}, " +
            "qie_tcm_suggestion = #{qieTcmSuggestion} " +
            "WHERE id = #{id}")
    int updateQie(Diagnosis diagnosis);
}
