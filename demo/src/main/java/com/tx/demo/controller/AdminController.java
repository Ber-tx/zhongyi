package com.tx.demo.controller;

import com.tx.demo.entity.Admin;
import com.tx.demo.mapper.AdminMapper;
import com.tx.demo.utils.JwtUtils;
import com.tx.demo.utils.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.*;

// 路径：demo/src/main/java/com/tx/demo/controller/AdminController.java


@RestController
@RequestMapping("/api/admin")
public class AdminController {

    @Autowired
    private AdminMapper adminMapper;

    @Autowired
    private JwtUtils jwtUtils;

    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();


    // ==================== 登录 ====================

    /**
     * POST /api/admin/login
     * Body: { "username": "admin", "password": "admin123" }
     */
    @PostMapping("/login")
    public Result login(@RequestBody Map<String, String> body) {
        String username = body.get("username");
        String password = body.get("password");

        if (username == null || password == null) {
            return Result.error("用户名或密码不能为空");
        }

        Admin admin = adminMapper.findByUsername(username);
        if (admin == null) {
            return Result.error("用户名不存在");
        }

        if (!passwordEncoder.matches(password, admin.getPassword())) {
            return Result.error("密码错误");
        }

        String token = jwtUtils.generateToken(username);

        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("username", username);
        return Result.success(data);
    }


    // ==================== 统计概览 ====================

    /**
     * GET /api/admin/stats
     * 返回：患者总数、今日诊断数、历史诊断总数
     */
    @GetMapping("/stats")
    public Result getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalPatients", adminMapper.countAllPatients());
        stats.put("totalDiagnoses", adminMapper.countDiagnoses());
        stats.put("todayDiagnoses", adminMapper.countTodayDiagnoses());
        return Result.success(stats);
    }


    // ==================== 患者管理 ====================

    /**
     * GET /api/admin/patients?page=1&size=10&keyword=张三
     */
    @GetMapping("/patients")
    public Result listPatients(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "") String keyword) {

        int offset = (page - 1) * size;
        List<Map<String, Object>> list = adminMapper.listPatients(keyword, offset, size);
        int total = adminMapper.countPatients(keyword);

        Map<String, Object> result = new HashMap<>();
        result.put("list", list);
        result.put("total", total);
        result.put("page", page);
        result.put("size", size);
        return Result.success(result);
    }

    /**
     * DELETE /api/admin/patient/{id}
     * 级联删除患者及其所有诊断记录
     */
    @DeleteMapping("/patient/{id}")
    public Result deletePatient(@PathVariable Long id) {
        adminMapper.deleteDiagnosesByPatient(id);  // 先删关联记录
        int rows = adminMapper.deletePatient(id);
        if (rows > 0) {
            return Result.success("患者及其诊断记录已删除");
        }
        return Result.error("患者不存在");
    }


    // ==================== 诊断记录 ====================

    /**
     * GET /api/admin/diagnoses?page=1&size=10
     */
    @GetMapping("/diagnoses")
    public Result listDiagnoses(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {

        int offset = (page - 1) * size;
        List<Map<String, Object>> list = adminMapper.listDiagnoses(offset, size);
        int total = adminMapper.countDiagnoses();

        Map<String, Object> result = new HashMap<>();
        result.put("list", list);
        result.put("total", total);
        result.put("page", page);
        result.put("size", size);
        return Result.success(result);
    }
}
