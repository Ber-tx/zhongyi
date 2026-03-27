package com.tx.demo.mapper;

import com.tx.demo.entity.HealthExam;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface HealthExamMapper {
    
    /**
     * 保存体检记录
     */
    void save(HealthExam healthExam);
    
    /**
     * 更新体检记录
     */
    void update(HealthExam healthExam);
    
    /**
     * 查询单条体检记录
     */
    HealthExam selectById(Long id);
    
    /**
     * 按身份证查询体检记录
     */
    HealthExam selectByIdCard(String idCard);
    
    /**
     * 分页查询体检记录列表
     */
    List<Map<String, Object>> selectList(@Param("offset") int offset, 
                                          @Param("limit") int limit,
                                          @Param("keyword") String keyword);
    
    /**
     * 查询总数
     */
    Integer selectCount(@Param("keyword") String keyword);
    
    /**
     * 根据患者ID查询所有体检记录
     */
    List<HealthExam> selectByPatientId(Long patientId);
    
    /**
     * 删除体检记录
     */
    void delete(Long id);
}
