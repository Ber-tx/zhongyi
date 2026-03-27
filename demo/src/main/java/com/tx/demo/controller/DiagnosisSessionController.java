package com.tx.demo.controller;

import com.tx.demo.entity.Diagnosis;
import com.tx.demo.entity.Patient;
import com.tx.demo.mapper.DiagnosisMapper;
import com.tx.demo.mapper.PatientMapper;
import com.tx.demo.utils.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/diagnosis")
public class DiagnosisSessionController {

    @Autowired
    private DiagnosisMapper diagnosisMapper;

    @Autowired
    private PatientMapper patientMapper;

    public static class StartSessionRequest {
        private Long patientId;
        private String idCard;

        public Long getPatientId() {
            return patientId;
        }

        public void setPatientId(Long patientId) {
            this.patientId = patientId;
        }

        public String getIdCard() {
            return idCard;
        }

        public void setIdCard(String idCard) {
            this.idCard = idCard;
        }
    }

    @PostMapping("/session/start")
    public Result startSession(@RequestBody StartSessionRequest request) {
        try {
            Long patientId = request.getPatientId();
            if ((patientId == null || patientId == 0) && request.getIdCard() != null && !request.getIdCard().isEmpty()) {
                Patient existing = patientMapper.findByIdCard(request.getIdCard());
                if (existing != null) {
                    patientId = existing.getId();
                }
            }

            if (patientId == null || patientId == 0) {
                return Result.error("缺少患者ID，无法创建诊断会话");
            }

            Diagnosis session = new Diagnosis();
            session.setPatientId(patientId);
            session.setStatus(0);
            session.setCreateTime(LocalDateTime.now());
            diagnosisMapper.insert(session);

            if (session.getId() == null) {
                return Result.error("创建诊断会话失败");
            }

            String archiveNo = buildArchiveNo(patientId, session.getCreateTime(), session.getId());
            Map<String, Object> data = new HashMap<>();
            data.put("caseId", session.getId());
            data.put("archiveNo", archiveNo);
            data.put("patientId", patientId);
            data.put("createdAt", session.getCreateTime());
            return Result.success(data);
        } catch (Exception e) {
            return Result.error("创建诊断会话异常: " + e.getMessage());
        }
    }

    private String buildArchiveNo(Long patientId, LocalDateTime ts, Long caseId) {
        String timePart = ts != null
                ? ts.format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"))
                : LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        return "DA-" + patientId + "-" + timePart + "-" + caseId;
    }
}

