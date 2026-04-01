-- 舌诊结构化维度字段升级
-- 目标：替代向 LLM 传递 wang.imageUrl，改为传递 wang.tongueMetrics

ALTER TABLE diagnosis
ADD COLUMN wang_tongue_metrics TEXT NULL COMMENT '舌象结构化维度(JSON)';
