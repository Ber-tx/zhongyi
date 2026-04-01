package com.tx.demo.controller;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.tx.demo.entity.Diagnosis;
import com.tx.demo.entity.Patient;
import com.tx.demo.mapper.DiagnosisMapper;
import com.tx.demo.mapper.PatientMapper;
import com.tx.demo.utils.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime; // 必须使用这个，匹配你的实体类
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/detect")
public class WangController {

    @Autowired
    private PatientMapper patientMapper;

    @Autowired
    private DiagnosisMapper diagnosisMapper;

    // 定义临时存储路径
    private static final String UPLOAD_PATH = "E:/项目/zhongyi_uploads/tcm_temp/";

    @PostMapping("/wang")
    public Result handleWang(
            Patient patient,
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "diagnosisId", required = false) Long diagnosisId) {
        System.out.println("==== [DEBUG] 开始执行业务逻辑 ====");
        System.out.println("==== [DEBUG] 接收到的原始数据: " + patient.toString());

        // 1. 【核心逻辑】解决重新分析传入 null 的问题
        // 如果 ID 为空但身份证不为空，尝试通过身份证补齐 ID
        // 1. 补齐 ID 逻辑
        if (patient.getId() == null && patient.getIdCard() != null) {
            Patient existing = patientMapper.findByIdCard(patient.getIdCard());
            if (existing != null) {
                patient.setId(existing.getId());
                System.out.println("==== [DEBUG] 匹配到已有病人 ID: " + patient.getId());
            } else {
                // --- 重点改这里 ---
                // 说明库里根本没这个人，可能是前端传错了或者没先录入
                System.out.println("==== [DEBUG] 警告：身份证 " + patient.getIdCard() + " 在库中不存在！");
                return Result.error("请先完成病人信息登记再进行分析");
            }
        }

        // 再次校验 ID
        if (patient.getId() == null) {
            System.out.println("==== [DEBUG] 警告：未能获取到有效的病人 ID ====");
            return Result.error("缺少病人ID，无法保存记录");
        }

        // 2. 将上传的文件保存到本地临时目录
        File tempDir = new File(UPLOAD_PATH);
        if (!tempDir.exists()) tempDir.mkdirs();

        String originalFilename = file.getOriginalFilename();
        String suffix = originalFilename.substring(originalFilename.lastIndexOf("."));
        String fileName = UUID.randomUUID().toString() + suffix;
        File destFile = new File(UPLOAD_PATH + fileName);

        try {
            file.transferTo(destFile);
        } catch (IOException e) {
            return Result.error("文件保存失败: " + e.getMessage());
        }

        // 3. 通过 HTTP 调用 Python Flask 接口
        RestTemplate restTemplate = new RestTemplate();
        String pythonUrl = "http://localhost:5000/tongue/detect";

        // 设置请求头
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        // 设置请求体
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new FileSystemResource(destFile));

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        try {
            System.out.println("==== [DEBUG] 正在请求 Python 接口... ====");
            String responseStr = restTemplate.postForObject(pythonUrl, requestEntity, String.class);
            // System.out.println("==== [DEBUG] Python 返回内容: " + responseStr);

            // 4. 解析结果
            JSONObject json = JSON.parseObject(responseStr);

            if (json != null && json.getBoolean("success")) {


                JSONObject data = json.getJSONObject("data");


                String chartImg = data.getString("chart_img");
                Double confidence = data.getDouble("confidence");
                JSONObject scores = data.getJSONObject("scores");
                String mainResult = data.getString("main_result");//要存入的数据
                String localPath=destFile.getAbsolutePath();
                String tongueMetricsJson = scores != null ? scores.toJSONString() : null;
                // 【业务拦截】如果识别结果无效，不写入数据库，方便用户重测
                if (mainResult.contains("未检测到") || mainResult.contains("不佳")) {
                    System.out.println("==== [DEBUG] AI 识别无效，拦截入库操作 ====");
                    return Result.error("分析失败: " + mainResult);
                }

                // --- 识别成功：封装 Diagnosis 对象并存入数据库 ---
                // 【第一步】寻找今天是否已经产生了任何板块的记录
                Diagnosis record = null;
                if (diagnosisId != null && diagnosisId > 0) {
                    record = diagnosisMapper.findById(diagnosisId);
                    if (record != null && !patient.getId().equals(record.getPatientId())) {
                        return Result.error("诊断会话与患者不匹配");
                    }
                }
                if (record == null) {
                    record = diagnosisMapper.findTodayRecord(patient.getId());
                }

                if (record != null) {
                    // 【第二步：情况A】已有记录（说明其他板块先开始了），直接把望诊结果补进去
                    System.out.println("==== [合并数据] 正在将望诊结果更新至已有记录 ID: " + record.getId());
                    record.setWangResult(mainResult);
                    record.setWangImageUrl(localPath);
                    record.setWangTongueMetrics(tongueMetricsJson);
                    diagnosisMapper.updateWang(record);
                } else {
                    // 【第二步：情况B】完全没记录（说明望诊是第一个开始的），新建一行
                    System.out.println("==== [新建记录] 望诊作为首个板块开始执行 ====");
                    Diagnosis newOne = new Diagnosis();
                    newOne.setPatientId(patient.getId());
                    newOne.setWangResult(mainResult);
                    newOne.setWangImageUrl(localPath);
                    newOne.setWangTongueMetrics(tongueMetricsJson);
                    newOne.setCreateTime(LocalDateTime.now());
                    newOne.setStatus(0); // 0表示进行中，等所有板块齐了可以设为1
                    diagnosisMapper.insert(newOne);
                }





                // 准备返回前端展示的数据
                Map<String, Object> resultMap = new HashMap<>();
                resultMap.put("main_result", mainResult);
                resultMap.put("chart_img",chartImg );

                if(json.containsKey("data_depth")){
                    resultMap.put("details", json.getJSONObject("data_depth"));
                }

                return Result.success(resultMap);
            } else {
                String msg = (json != null) ? json.getString("main_result") : "算法分析返回空值";
                return Result.error("分析失败: " + msg);
            }

        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("算法服务访问失败，请检查 Python 后端状态");
        }
    }
}
