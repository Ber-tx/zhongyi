-- 切诊结果补充存储字段
-- 该字段保存前端提交的脉诊关键指标 JSON，便于后续报告侧侧重切诊时直接使用。
-- JSON 内包含：心率变异性RMSSD（hrv_rmssd_ms）、节律变异系数（rhythm_cv）、
-- 灌注指数（perfusion_index）、信号质量评分（signal_quality）、脉象标签列表（pulse_tags）。
ALTER TABLE diagnosis
    ADD COLUMN qie_key_metrics_json LONGTEXT NULL COMMENT '切诊关键指标JSON：心率变异性RMSSD（hrv_rmssd_ms）、节律变异系数（rhythm_cv）、 灌注指数（perfusion_index）、信号质量评分（signal_quality）、脉象标签列表（pulse_tags）';
