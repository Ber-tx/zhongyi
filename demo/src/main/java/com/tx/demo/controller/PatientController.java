package com.tx.demo.controller;

import com.tx.demo.entity.Patient;
import com.tx.demo.service.PatientService;
import com.tx.demo.utils.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/user")
//@CrossOrigin(origins = "*", maxAge = 3600) // 解决开发环境跨域问题
public class PatientController {

    @Autowired
    private PatientService patientService;

    @PostMapping("/save")
    public Result savePatient(@RequestBody Patient patient) {
        // 调用修改后的 Service
        Patient savedPatient = patientService.saveOrUpdateByCard(patient);

        if (savedPatient != null && savedPatient.getId() != null) {
            return Result.success(savedPatient); // 这样前端就能收到 data: { id: xxx, ... }
        } else {
            return Result.error("病人信息处理失败");
        }
    }
}