package com.tx.demo.config;


//处理跨域问题和文件映射


import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    /**
     * 全局跨域配置
     */
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                // 关键修改：改用 allowedOriginPatterns 并设为 "*"
                // 或者直接用 allowedOrigins("http://localhost:5173")
                .allowedOriginPatterns("*")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);
    }

    /**
     * 静态资源映射 (关键：为后续望诊照片展示做准备)
     */
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 将 URL 以 /uploads/** 开头的请求，映射到磁盘的特定文件夹
        // 这样你访问 http://localhost:8080/uploads/test.jpg 就能看到图片了
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations("file:/usr/local/zhongyi_uploads/tcm_temp/");
    }
}
