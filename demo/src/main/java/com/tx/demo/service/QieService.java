package com.tx.demo.service;
import com.tx.demo.utils.Result;
import java.util.Map;

public interface QieService {
    Result saveAndAnalyze(Map<String, Object> payload);
}
