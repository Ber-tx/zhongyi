package com.tx.demo.entity;


import lombok.Data;

@Data // 这是一个工具注解，帮你自动生成 get/set 方法，你不用手写了

public class Question {

    private Long id;
    private String content; // 题目内容
    // 新增字段：是否反向计分 (0:否, 1:是)
    private Integer isReverse;
    private Integer sort;            // 对应前端的索引 (0-32)
    // 新增字段：关联体质 (例如 "ph,qx")
    private String constitutionCodes;
}

