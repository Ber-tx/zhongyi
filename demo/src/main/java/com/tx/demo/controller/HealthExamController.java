package com.tx.demo.controller;

import com.tx.demo.entity.HealthExam;
import com.tx.demo.service.HealthExamService;
import com.tx.demo.utils.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

/**
 * 居民体检管理控制器
 * API 端点：/api/health-exam
 */
@RestController
@RequestMapping("/api/health-exam")
public class HealthExamController {
    
    @Autowired
    private HealthExamService healthExamService;
    
    /**
     * 保存新增体检记录
     * POST /api/health-exam/save
     */
    /**
     * 保存新增体检记录
     * POST /api/health-exam/save
     */
    @PostMapping("/save")
    public Result save(@RequestBody HealthExam healthExam) {
        try {
            if (healthExam.getPatientName() == null || healthExam.getPatientName().trim().isEmpty()) {
                return Result.error("患者姓名不能为空");
            }
            HealthExam saved = healthExamService.saveOrUpdate(healthExam);
            return Result.success(saved, "体检档案保存成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("保存失败：" + e.getMessage());
        }
    }
    
    /**
     * 更新体检记录
     * PUT /api/health-exam/update/{id}
     */
    @PutMapping("/update/{id}")
    public Result update(@PathVariable Long id, @RequestBody HealthExam healthExam) {
        try {
            healthExam.setId(id);
            HealthExam updated = healthExamService.saveOrUpdate(healthExam);
            return Result.success(updated, "体检档案更新成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("更新失败：" + e.getMessage());
        }
    }
    
    /**
     * 查询单条体检记录
     * GET /api/health-exam/{id}
     */
    @GetMapping("/{id}")
    public Result getById(@PathVariable Long id) {
        try {
            HealthExam exam = healthExamService.getById(id);
            if (exam == null) {
                return Result.error("体检记录不存在");
            }
            return Result.success(exam);
        } catch (Exception e) {
            return Result.error("查询失败：" + e.getMessage());
        }
    }
    
    /**
     * 分页查询列表
     * GET /api/health-exam/list?page=1&size=12&keyword=
     */
    @GetMapping("/list")
    public Result getList(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "12") int size,
            @RequestParam(required = false) String keyword) {
        try {
            if (page < 1) page = 1;
            if (size < 1 || size > 100) size = 12;
            if (keyword == null) keyword = "";
            
            Map<String, Object> result = healthExamService.getList(page, size, keyword);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error("查询失败：" + e.getMessage());
        }
    }
    
    /**
     * 删除体检记录
     * DELETE /api/health-exam/{id}
     */
    @DeleteMapping("/{id}")
    public Result delete(@PathVariable Long id) {
        try {
            healthExamService.delete(id);
            return Result.success(null, "删除成功");
        } catch (Exception e) {
            return Result.error("删除失败：" + e.getMessage());
        }
    }
    
    /**
     * 按身份证查询体检记录
     * GET /api/health-exam/search?idCard=
     */
    @GetMapping("/search")
    public Result searchByIdCard(@RequestParam String idCard) {
        try {
            if (idCard == null || idCard.trim().isEmpty()) {
                return Result.error("身份证号不能为空");
            }
            HealthExam exam = healthExamService.getByIdCard(idCard);
            if (exam == null) {
                return Result.error("未找到相应体检记录");
            }
            return Result.success(exam);
        } catch (Exception e) {
            return Result.error("查询失败：" + e.getMessage());
        }
    }
}
