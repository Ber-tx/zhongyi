package com.tx.demo.controller;

import com.tx.demo.entity.Answer;
import com.tx.demo.entity.Patient;
import com.tx.demo.mapper.PatientMapper;
import com.tx.demo.service.QuestionService;
import com.tx.demo.utils.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/tcm")
public class QuestionController {

    @Autowired
    private QuestionService questionService;

    @Autowired
    private PatientMapper patientMapper;

    @PostMapping("/submit")
    public Result submit(@RequestBody Answer request) {
        System.out.println("DEBUG: 接收到的实体对象为: " + request);

        Long realId = null;

        // 第一步：先看前端有没有传 patientId (这是最快的)
        if (request.getPatientId() != null) {
            realId = request.getPatientId();
        }
        // 第二步：如果 ID 丢了，尝试用 idCard 去数据库捞
        else if (request.getIdCard() != null && !request.getIdCard().isEmpty()) {
            Patient p = patientMapper.findByIdCard(request.getIdCard());
            if (p != null) {
                realId = p.getId();
            }
        }

        // 最终检查：如果两样都没拿到，说明真没录入
        if (realId == null) {
            return Result.error("无法关联病人！请检查是否已录入信息或身份证号是否传递。");
        }

        // 校验问卷完整性
        if (request.getAnswers() == null || request.getAnswers().size() < 33) {
            return Result.error("问卷数据不完整，请重新检查！");
        }

        // 调用业务层：传入真实的 realId
        return questionService.calculateConstitution(request.getAnswers(), realId);
    }
}
