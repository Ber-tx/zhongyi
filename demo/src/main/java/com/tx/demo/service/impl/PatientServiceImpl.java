package com.tx.demo.service.impl;

import com.tx.demo.entity.Patient;
import com.tx.demo.mapper.PatientMapper;
import com.tx.demo.service.PatientService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class PatientServiceImpl implements PatientService {
    @Autowired
    private PatientMapper patientMapper;

    @Override
    public Patient saveOrUpdateByCard(Patient patient) {
        System.out.println("==== [DEBUG] 开始执行业务逻辑 ====");
        System.out.println("==== [DEBUG] 接收到的数据: " + patient + " ====");
        // 先检查身份证是否存在，实现“增量更新”
        Patient existing = patientMapper.findByIdCard(patient.getIdCard());
        if (existing != null) {
            // 已存在：更新信息
            patient.setId(existing.getId()); // 把查到的 ID 赋给当前对象
            patientMapper.update(patient);
            System.out.println("==== [DEBUG] 更新病人信息，ID: " + patient.getId());
        } else {
            // 不存在：插入新记录
            // 因为 XML 配置了 useGeneratedKeys，执行 insert 后 patient.id 会自动被填充
            patientMapper.insert(patient);
            System.out.println("==== [DEBUG] 插入新病人，生成 ID: " + patient.getId());
        }

        // 关键：返回携带 ID 的对象，而不是布尔值
        return patient;
    }
}
