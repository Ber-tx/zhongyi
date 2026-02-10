package com.tx.demo.controller;

import com.tx.demo.service.QieService;
import com.tx.demo.utils.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/detect")
@CrossOrigin // 允许跨域
public class QieController {

    @Autowired
    private QieService qieService;

    @PostMapping("/qie/save")
    public Result saveQie(@RequestBody Map<String, Object> payload) {
        // 控制层只负责转发，没有任何业务逻辑，极其干净
        return qieService.saveAndAnalyze(payload);
    }
}
