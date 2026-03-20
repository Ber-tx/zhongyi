package com.tx.demo.entity;

import lombok.Data;
import java.time.LocalDateTime;

// 路径：demo/src/main/java/com/tx/demo/entity/Admin.java
@Data
public class Admin {
    private Long id;
    private String username;
    private String password;
    private LocalDateTime createTime;
}