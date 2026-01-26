package com.tx.demo.entity;

import lombok.Data;

import java.time.LocalDate;

// Patient.java
@Data // 使用 Lombok 简化代码
public class Patient {
    private Long id;
    private String name;
    private String gender;
//    private String nation;
    private LocalDate birthday;
    private String address;
    private String idCard;
}