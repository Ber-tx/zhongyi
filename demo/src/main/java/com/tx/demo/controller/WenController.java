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
import java.time.LocalDateTime;
import java.util.UUID;

@RestController
@RequestMapping("/api/wen")
public class WenController {

    @Autowired
    private PatientMapper patientMapper;

    @Autowired
    private DiagnosisMapper diagnosisMapper;

    // 音频存储路径（与望诊分开目录，便于管理）
    // 改成
    private static final String UPLOAD_PATH =
        System.getenv("UPLOAD_PATH") != null ?
        System.getenv("UPLOAD_PATH") + "audio/" : "E:/项目/zhongyi_uploads/audio/";
    // =====================================================================
    // 分析 + 入库（一步完成，与 WangController 结构完全一致）
    // =====================================================================
    @PostMapping("/analyze")
    public Result handleWen(
            @RequestParam(value = "patient_id", required = false) Long patientId,
            @RequestParam(value = "patient_idcard", required = false) String idCard,
            @RequestParam("file") MultipartFile file) {

        System.out.println("==== [闻诊] 开始执行业务逻辑 ====");
        System.out.println("==== [闻诊] 患者ID: " + patientId + ", 身份证: " + idCard);

        // ---- 1. 补齐病人 ID（与 WangController 逻辑完全一致）----
        if (patientId == null || patientId == 0) {
            if (idCard != null && !idCard.isEmpty()) {
                Patient existing = patientMapper.findByIdCard(idCard);
                if (existing != null) {
                    patientId = existing.getId();
                    System.out.println("==== [闻诊] 通过身份证匹配到患者 ID: " + patientId);
                } else {
                    System.out.println("==== [闻诊] 警告：身份证 " + idCard + " 在库中不存在！");
                    return Result.error("请先完成病人信息登记再进行分析");
                }
            } else {
                System.out.println("==== [闻诊] 警告：未能获取到有效的病人 ID");
                return Result.error("缺少病人ID，无法保存记录");
            }
        }

        // ---- 2. 保存音频文件到本地（与望诊保存图片逻辑一致）----
        File tempDir = new File(UPLOAD_PATH);
        if (!tempDir.exists()) tempDir.mkdirs();

        String originalFilename = file.getOriginalFilename();
        String suffix = (originalFilename != null && originalFilename.contains("."))
                ? originalFilename.substring(originalFilename.lastIndexOf("."))
                : ".webm";
        String fileName = UUID.randomUUID().toString() + suffix;
        File destFile = new File(UPLOAD_PATH + fileName);

        try {
            file.transferTo(destFile);
            System.out.println("==== [闻诊] 音频文件已保存: " + destFile.getAbsolutePath());
        } catch (IOException e) {
            return Result.error("音频文件保存失败: " + e.getMessage());
        }

        // ---- 3. 调用 Python 闻诊分析服务 ----
        RestTemplate restTemplate = new RestTemplate();
        String pythonUrl = "http://localhost:5000/wen/analyze";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();

        body.add("file", new FileSystemResource(destFile));
        body.add("patient_id", String.valueOf(patientId));      // 新增
        body.add("patient_idcard", idCard != null ? idCard : ""); // 新增

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        try {
            System.out.println("==== [闻诊] 正在请求 Python 接口: " + pythonUrl);
            String responseStr = restTemplate.postForObject(pythonUrl, requestEntity, String.class);

            // ---- 4. 解析 Python 返回结果 ----
            JSONObject json = JSON.parseObject(responseStr);

            if (json != null && Boolean.TRUE.equals(json.getBoolean("success"))) {

                JSONObject data       = json.getJSONObject("data");
                String mainFinding    = data.getString("main_finding");
                Double confidence     = data.getDouble("confidence");
                String tags           = data.getJSONArray("constitution_tags") != null
                        ? data.getJSONArray("constitution_tags").toJSONString() : null;
                String features       = data.getJSONObject("features") != null
                        ? data.getJSONObject("features").toJSONString() : null;
                String localPath      = destFile.getAbsolutePath();

                System.out.println("==== [闻诊] 分析结果: " + mainFinding + "，置信度: " + confidence);

                // ---- 5. 入库（与 WangController 完全一致的合并/新建逻辑）----
                Diagnosis record = diagnosisMapper.findTodayRecord(patientId);

                if (record != null) {
                    // 情况A：今天已有记录，补充闻诊字段
                    System.out.println("==== [闻诊][合并] 更新至已有记录 ID: " + record.getId());
                    record.setWenAudioConclusion(mainFinding);
                    record.setWenAudioConfidence(confidence);
                    record.setWenAudioTags(tags);
                    record.setWenAudioFeatures(features);

                    diagnosisMapper.updateWenAudio(record);
                } else {
                    // 情况B：闻诊是今天第一个板块，新建记录
                    System.out.println("==== [闻诊][新建] 闻诊作为首个板块开始执行");
                    Diagnosis newOne = new Diagnosis();
                    newOne.setPatientId(patientId);
                    newOne.setWenAudioConclusion(mainFinding);
                    newOne.setWenAudioConfidence(confidence);
                    newOne.setWenAudioTags(tags);
                    newOne.setWenAudioFeatures(features);
                    newOne.setWenAudioUrl(localPath);
                    newOne.setCreateTime(LocalDateTime.now());
                    newOne.setStatus(0);
                    diagnosisMapper.insert(newOne);
                }

                // ---- 6. 把分析结果透传给前端展示 ----
                return Result.success(data);

            } else {
                String msg = (json != null) ? json.getString("msg") : "AI 服务返回空值";
                System.out.println("==== [闻诊] 分析失败: " + msg);
                return Result.error("分析失败: " + msg);
            }

        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("算法服务访问失败，请检查 Python 后端状态");
        }
    }
}
