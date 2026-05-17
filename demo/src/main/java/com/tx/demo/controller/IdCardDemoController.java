package com.tx.demo.controller;

import com.tx.demo.utils.Result;
import com.tx.demo.vo.IdCardInfoVO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;

/**
 * 身份证读卡器集成控制器
 * 
 * 负责调用本地 x86 读卡服务 (127.0.0.1:9009)
 * 并将结果转换为应用内部格式
 */
@RestController
@RequestMapping("/api/idcard")
public class IdCardDemoController {

    private static final Logger logger = LoggerFactory.getLogger(IdCardDemoController.class);

    @Value("${app.software-mode:false}")
    private boolean softwareMode;

    @Value("${app.services.idcard-base-url:http://127.0.0.1:9009/api/idcard}")
    private String readerServiceUrl;

    @Autowired
    private RestTemplate restTemplate;

    /**
     * 读取身份证信息
     * GET /api/idcard/read
     * 调用 x86 读卡服务进行读卡
     */
    @GetMapping("/read")
    public Result readIdCard() {
        logger.info("收到读卡请求");
        if (softwareMode) {
            return Result.error("软件模式下已关闭身份证读卡功能");
        }
        
        try {
            // 调用本地 x86 读卡服务
            String url = readerServiceUrl + "/read";
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);

            if (response != null && (Boolean) response.getOrDefault("success", false)) {
                Map<String, Object> data = (Map<String, Object>) response.get("data");
                
                // 转换为 VO 对象
                IdCardInfoVO idCardInfo = convertToIdCardInfoVO(data);
                
                logger.info("读卡成功: " + idCardInfo.getName() + " (" + idCardInfo.getIdNumber() + ")");
                return Result.success(idCardInfo);
            } else {
                String message = (String) response.getOrDefault("message", "未知错误");
                logger.warn("读卡失败: " + message);
                return Result.error("读卡失败: " + message);
            }
        } catch (Exception e) {
            logger.error("读卡异常: " + e.getMessage(), e);
            
            // 检查读卡服务是否可用
            if (e.getMessage().contains("Connection refused")) {
                return Result.error("读卡服务不可用，请检查读卡服务是否已启动 (" + readerServiceUrl + ")");
            }
            
            return Result.error("读卡异常: " + e.getMessage());
        }
    }

    /**
     * 检查读卡器状态
     * GET /api/idcard/status
     */
    @GetMapping("/status")
    public Result checkReaderStatus() {
        if (softwareMode) {
            return Result.error("软件模式下已关闭身份证读卡功能");
        }
        try {
            String url = readerServiceUrl + "/status";
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);

            if (response != null && (Boolean) response.getOrDefault("success", false)) {
                Map<String, Object> data = (Map<String, Object>) response.get("data");
                return Result.success(data);
            } else {
                return Result.error((String) response.getOrDefault("message", "状态检查失败"));
            }
        } catch (Exception e) {
            logger.error("状态检查异常: " + e.getMessage());
            return Result.error("读卡服务不可用");
        }
    }

    /**
     * 健康检查
     * GET /api/idcard/health
     */
    @GetMapping("/health")
    public Result healthCheck() {
        if (softwareMode) {
            Map<String, Object> result = new HashMap<>();
            result.put("mainService", "运行正常");
            result.put("readerService", "软件模式已禁用");
            return Result.success(result);
        }
        try {
            String url = readerServiceUrl + "/health";
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            
            Map<String, Object> result = new HashMap<>();
            result.put("mainService", "运行正常");
            result.put("readerService", (Boolean) response.getOrDefault("success", false) ? "运行正常" : "故障");
            
            return Result.success(result);
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("mainService", "运行正常");
            result.put("readerService", "离线");
            return Result.success(result);
        }
    }

    /**
     * 释放读卡器资源
     * POST /api/idcard/release
     */
    @PostMapping("/release")
    public Result releaseReader() {
        if (softwareMode) {
            return Result.error("软件模式下已关闭身份证读卡功能");
        }
        try {
            String url = readerServiceUrl + "/release";
            Map<String, Object> response = restTemplate.postForObject(url, null, Map.class);

            if (response != null && (Boolean) response.getOrDefault("success", false)) {
                return Result.success("读卡器已释放");
            } else {
                return Result.error((String) response.getOrDefault("message", "释放失败"));
            }
        } catch (Exception e) {
            logger.error("释放资源异常: " + e.getMessage());
            return Result.error("释放失败: " + e.getMessage());
        }
    }

    /**
     * 转换身份证信息为 VO 对象
     */
    private IdCardInfoVO convertToIdCardInfoVO(Map<String, Object> data) {
        IdCardInfoVO vo = new IdCardInfoVO();
        
        vo.setIdNumber((String) data.getOrDefault("idNumber", ""));
        vo.setName((String) data.getOrDefault("name", ""));
        vo.setGender((String) data.getOrDefault("gender", ""));
        vo.setNationality((String) data.getOrDefault("nationality", ""));
        vo.setDateOfBirth((String) data.getOrDefault("dateOfBirth", ""));
        vo.setAddress((String) data.getOrDefault("address", ""));
        vo.setIssuingAuthority((String) data.getOrDefault("issuingAuthority", ""));
        vo.setValidFrom((String) data.getOrDefault("validFrom", ""));
        vo.setValidTo((String) data.getOrDefault("validTo", ""));
        vo.setPhotoBase64((String) data.getOrDefault("photoBase64", null));
        vo.setIdCardImageBase64((String) data.getOrDefault("idCardImageBase64", null));
        
        return vo;
    }
}
