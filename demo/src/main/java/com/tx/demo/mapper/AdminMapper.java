package com.tx.demo.mapper;

import com.tx.demo.entity.Admin;
import org.apache.ibatis.annotations.*;
import java.util.List;
import java.util.Map;

// 路径：demo/src/main/java/com/tx/demo/mapper/AdminMapper.java
@Mapper
public interface AdminMapper {

    // ========== 管理员账户 ==========

    @Select("SELECT * FROM admin WHERE username = #{username}")
    Admin findByUsername(String username);


    // ========== 患者查询 ==========

    @Select("<script>" +
            "SELECT id, name, gender, birthday, address, id_card as idCard " +
            "FROM patients " +
            "<where>" +
            "  <if test='keyword != null and keyword != \"\"'>" +
            "    name LIKE CONCAT('%',#{keyword},'%') OR id_card LIKE CONCAT('%',#{keyword},'%')" +
            "  </if>" +
            "</where>" +
            "ORDER BY id DESC " +
            "LIMIT #{offset}, #{size}" +
            "</script>")
    List<Map<String, Object>> listPatients(@Param("keyword") String keyword,
                                           @Param("offset") int offset,
                                           @Param("size") int size);

    @Select("<script>" +
            "SELECT COUNT(*) FROM patients " +
            "<where>" +
            "  <if test='keyword != null and keyword != \"\"'>" +
            "    name LIKE CONCAT('%',#{keyword},'%') OR id_card LIKE CONCAT('%',#{keyword},'%')" +
            "  </if>" +
            "</where>" +
            "</script>")
    int countPatients(@Param("keyword") String keyword);

    @Delete("DELETE FROM patients WHERE id = #{id}")
    int deletePatient(Long id);

    @Delete("DELETE FROM diagnosis WHERE patient_id = #{patientId}")
    int deleteDiagnosesByPatient(Long patientId);


    // ========== 诊断记录查询 ==========

    @Select("SELECT d.id, d.patient_id as patientId, d.create_time as createTime, d.status, " +
            "d.wang_result as wangResult, " +
            "d.wen_conclusion as wenConclusion, " +
            "d.wen_audio_conclusion as wenAudioConclusion, " +
            "d.qie_heart_rate as qieHeartRate, d.qie_spo2 as qieSpo2, " +
            "d.qie_tcm_suggestion as qieTcmSuggestion, " +
            "d.qie_valid_rate as qieValidRate, d.qie_sample_count as qieSampleCount, " +
            "d.wen_scores as wenScores, " +
            "p.name as patientName, p.id_card as patientIdCard, p.gender as patientGender " +
            "FROM diagnosis d LEFT JOIN patients p ON d.patient_id = p.id " +
            "ORDER BY d.create_time DESC " +
            "LIMIT #{offset}, #{size}")
    List<Map<String, Object>> listDiagnoses(@Param("offset") int offset, @Param("size") int size);

    @Select("SELECT COUNT(*) FROM diagnosis")
    int countDiagnoses();

    @Select("SELECT COUNT(*) FROM diagnosis WHERE DATE(create_time) = CURDATE()")
    int countTodayDiagnoses();

    @Select("SELECT COUNT(*) FROM patients")
    int countAllPatients();
}