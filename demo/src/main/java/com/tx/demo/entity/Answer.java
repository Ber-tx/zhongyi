package com.tx.demo.entity;

import lombok.Data;
import java.util.List;

@Data
public class Answer {
    private List<Integer> answers; // 长度为33的整数数组
    private String idCard;
    private Double bmi;
    private Long patientId;
}