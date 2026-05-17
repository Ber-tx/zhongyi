package com.tx.demo.config;


//处理跨域问题和文件映射


import com.tx.demo.interceptor.AdminInterceptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Autowired
    private AdminInterceptor adminInterceptor;

    @Value("${app.paths.upload-root:./zhongyi_uploads}")
    private String uploadRoot;

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
        String normalized = uploadRoot.replace("\\", "/");
        if (!normalized.endsWith("/")) {
            normalized = normalized + "/";
        }
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations("file:" + normalized);
    }
    @Override

    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(adminInterceptor)
                .addPathPatterns("/api/admin/**")
                .excludePathPatterns("/api/admin/login")
                // 只读接口，普通用户可以访问
                .excludePathPatterns("/api/admin/diagnoses-with-patient")
                .excludePathPatterns("/api/admin/diagnoses")
                .excludePathPatterns("/api/admin/stats")
                .excludePathPatterns("/api/admin/constitution-stats");
    }


}
