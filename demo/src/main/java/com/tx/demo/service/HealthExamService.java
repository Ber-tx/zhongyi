package com.tx.demo.service;

import com.tx.demo.entity.HealthExam;
import com.tx.demo.mapper.HealthExamMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

@Service
public class HealthExamService {
    
    @Autowired
    private HealthExamMapper healthExamMapper;
    
    /**
     * 保存或更新体检记录
     */
    public HealthExam saveOrUpdate(HealthExam healthExam) {
        // 设置默认检查日期
        if (healthExam.getExamDate() == null) {
            healthExam.setExamDate(LocalDate.now());
        }
        
        // 保存或更新
        if (healthExam.getId() != null) {
            healthExamMapper.update(healthExam);
        } else {
            healthExamMapper.save(healthExam);
        }
        return healthExam;
    }
    
    /**
     * 查询单条记录
     */
    public HealthExam getById(Long id) {
        return healthExamMapper.selectById(id);
    }
    
    /**
     * 按身份证查询
     */
    public HealthExam getByIdCard(String idCard) {
        return healthExamMapper.selectByIdCard(idCard);
    }
    
    /**
     * 按患者ID查询所有体检记录
     */
    public List<HealthExam> getByPatientId(Long patientId) {
        return healthExamMapper.selectByPatientId(patientId);
    }
    
    /**
     * 分页查询列表（包含搜索）
     */
    public Map<String, Object> getList(int page, int size, String keyword) {
        int offset = (page - 1) * size;
        List<Map<String, Object>> list = healthExamMapper.selectList(offset, size, keyword);
        Integer total = healthExamMapper.selectCount(keyword);
        
        Map<String, Object> result = new HashMap<>();
        result.put("list", list);
        result.put("total", total);
        result.put("page", page);
        result.put("size", size);
        return result;
    }
    
    /**
     * 删除体检记录
     */
    public void delete(Long id) {
        healthExamMapper.delete(id);
    }
    
    /**
     * 计算年龄（从出生日期计算）
     */
    public Integer calculateAge(LocalDate birthday) {
        if (birthday == null) return null;
        return LocalDate.now().getYear() - birthday.getYear();
    }
}
