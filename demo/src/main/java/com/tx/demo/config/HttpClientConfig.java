package com.tx.demo.config;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;

/**
 * HTTP 客户端配置
 * 用于调用外部服务（如 x86 读卡服务）
 */
@Configuration
public class HttpClientConfig {

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
                // 连接超时 5 秒
                .setConnectTimeout(Duration.ofSeconds(5))
                // 读超时 10 秒
                .setReadTimeout(Duration.ofSeconds(10))
                .build();
    }
}
