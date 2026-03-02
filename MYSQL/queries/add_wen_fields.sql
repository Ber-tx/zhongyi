-- 闻诊数据库字段添加脚本
-- 执行此脚本为 diagnosis 表添加闻诊相关字段

-- 添加闻诊结论字段
ALTER TABLE diagnosis ADD COLUMN wen_audio_conclusion VARCHAR(500) COMMENT '闻诊结论（体质判断）';

-- 添加闻诊音频特征字段 (JSON格式)
ALTER TABLE diagnosis ADD COLUMN wen_audio_features LONGTEXT COMMENT '闻诊音频特征 JSON';

-- 添加闻诊置信度字段
ALTER TABLE diagnosis ADD COLUMN wen_audio_confidence DECIMAL(3,2) COMMENT '闻诊置信度 (0-1)';

-- 添加闻诊体质标签字段 (JSON数组格式)
ALTER TABLE diagnosis ADD COLUMN wen_audio_tags VARCHAR(500) COMMENT '闻诊体质标签（JSON数组）';

-- 验证脚本（可选）
-- SELECT * FROM diagnosis WHERE wen_audio_conclusion IS NOT NULL;
