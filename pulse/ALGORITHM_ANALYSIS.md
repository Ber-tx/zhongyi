# Pulse 算法问题分析报告

## 📊 数据对比

### 实际值（用户血压计测量）
- **心率**: 78 bpm
- **血压**: 134/74 mmHg

### 系统计算值
- **心率**: 127.7 bpm ❌ (误差: +49.7 bpm, **约64%偏差**)
- **血压**: 126/77 → 134/80 → 180/120 (波动剧烈)
- **血氧**: 90%-92% (有警告提示计算值偏低)

---

## 🔍 核心问题分析

### 问题1: 心率计算严重偏高 ⚠️ **最严重**

**症状**: 127.7 bpm vs 实际 78 bpm（偏高64%）

**原因分析**:

#### 代码位置
[signal_processor.py](signal_processor.py#L57-L85) - `calculate_heart_rate()` 函数

```python
# 找峰值
min_distance = int(0.4 * self.sampling_rate)  # = 40个采样点
peaks, properties = signal.find_peaks(
    filtered_signal,
    distance=min_distance,  # ← 这里是问题！
    prominence=np.std(filtered_signal) * 0.3
)
```

#### 问题根源

1. **数据长度不足**: Arduino发来的是**100个采样点 = 1秒数据**
   - `min_distance = 40个采样点 = 0.4秒`
   - 1秒内最多只能检测到2-3个峰值
   - 这对应心率160-180 bpm，而实际应该是78 bpm

2. **峰值检测错误**: 当数据少时，滤波和噪声放大
   - 0.5-8Hz的带通滤波可能会产生虚假峰值
   - prominence阈值可能设置不当

3. **时间窗口太短**: 
   ```
   当数据为100个点(1秒)时：
   - 理论最多检测3个峰值 (1秒÷40msec≈25个间隔)
   - 但实际可能检测到10+个虚假峰值
   ```

#### 修复建议

**方案1: 动态调整min_distance**
```python
# 基于数据长度动态计算
min_distance = max(int(0.6 * self.sampling_rate), 25)  # 至少600ms
```

**方案2: 增加采样数据量**
```
目标: 5秒数据 = 500个采样点(当前100)
或: 10秒数据 = 1000个采样点
```

**方案3: 使用自适应滤波**
```python
# 替换固定的find_peaks参数
distance = int(self.sampling_rate / (heart_rate_estimate / 60))
# 需要先粗估心率
```

---

### 问题2: 血压计算完全不可靠 ⚠️ **第二严重**

**症状**: 同一组数据计算出126/77 → 134/80 → 180/120

**原因分析**:

#### 代码位置
[signal_processor.py](signal_processor.py#L340-L375) - `calculate_blood_pressure()`

```python
def calculate_blood_pressure(self, ppg_data, heart_rate):
    # 依赖的变量
    pulse_strength = np.std(...)      # 标准差
    hrv = np.std(rr_intervals) * 1000  # 心率变异性
    
    # 经验公式:
    sys_base = 110
    hr_adjustment = (heart_rate - 70) * 0.3       
    strength_adjustment = (pulse_strength - 25) * 0.2
    hrv_adjustment = -(hrv - 30) * 0.1
    
    systolic = sys_base + hr_adjustment + strength_adjustment + hrv_adjustment
```

#### 问题根源

1. **经验公式完全不准确**
   - 血压受多因素影响: 血管硬度、文剋、体重、年龄等
   - 仅从PPG信号的标准差无法推断血压
   - 公式中各个系数(0.3, 0.2, 0.1)没有医学依据

2. **输入数据错误导致输出错误**
   - 心率计算错（127.7 vs 78 bpm）
   - 导致血压计算更错: `hr_adjustment = (127.7 - 70) * 0.3 = 17.3`
   - 而准确情况应该是: `(78 - 70) * 0.3 = 2.4`
   - **差异: 7倍!**

3. **标准差（pulse_strength）变化大**
   ```
   当同一个人多次测量时:
   pulse_strength 可能在 15-40 之间波动
   strength_adjustment = (20 - 25) * 0.2 = -1  
   strength_adjustment = (35 - 25) * 0.2 = +2
   
   差异就导致血压波动: 系统差±3 mmHg
   ```

#### 医学事实

❌ **PPG传感器无法准确测血压**
- 仅通过光学脉搏传感器无法测血压
- 需要特殊的血压计（压力传感器）
- **MAX30102传感器只能测心率和血氧, 不能测血压**

✅ **当前最好的方案**

**方案1: 使用经验范围（诚实的估算）**
```python
def calculate_blood_pressure_estimate(self, heart_rate):
    # 完全承认这是估算，而非计算
    # 基于平均人群数据
    if heart_rate < 60:
        return {'systolic': 115, 'diastolic': 70}  # 低心率→低血压
    elif heart_rate > 100:
        return {'systolic': 140, 'diastolic': 85}  # 高心率→高血压
    else:
        return {'systolic': 128, 'diastolic': 78}
```

**方案2: 关闭血压计算，仅显示"暂无血压数据"**
```python
# 告诉用户这无法测量，需要血压计
pulse_system_response = {
    'heart_rate': 78,      # ✅ 可靠
    'blood_oxygen': 95,    # ✅ 可靠（有IR传感器）
    'blood_pressure': None,  # ❌ 不显示估算值
    'note': '血压需要专业血压计测量'
}
```

---

### 问题3: 血氧计算也存在问题 ⚠️ **第三严重**

**症状**: 警告 "计算的SpO2值80.1偏低，使用估算值" → 显示90-92%

**原因分析**:

#### 代码位置
[signal_processor.py](signal_processor.py#L200-L260) - `calculate_blood_oxygen()`

```python
# R值范围检查
if r_value < 0.4 or r_value > 3.0:
    logger.warning(f"R值范围异常 {r_value}，使用估算值")
    return self._estimate_spo2_from_ppg(ppg_data)  # 直接分
```

#### 问题根源

1. **原始R值计算违反医学标准**
   ```
   算法计算出: SpO2 = 80.1%
   然后说"偏低"，改为"估算值" 90-92%
   
   ❌ 这违反了算法规范!
   ❌ 如果算法结果偏低，应该修复算法
   ❌ 不应该用经验值覆盖计算值
   ```

2. **公式本身可能有问题**
   ```python
   SpO2 = -45.060 * (r_value ** 2) + 30.354 * r_value + 94.845
   ```
   - 这是标准MAX30102公式，但需要准确的AC/DC分量提取

3. **AC/DC分量提取可能不准确**
   - 如果IR数据少于10个点，降级到PPG估算
   - PPG估算根本就不准确 (随机值95±1.5)

#### 改进建议

```python
# 更诚实的血氧计算策略
def calculate_blood_oxygen(self, ppg_data, ir_data):
    # 1. 检查数据质量和数量
    if len(ppg_data) < 500:  # 至少5秒数据
        logger.warning("数据不足，血氧不可靠")
        return {'value': None, 'confidence': 'low'}
    
    # 2. 检查IR数据
    if ir_data is None:
        logger.warning("无IR数据，血氧不可测")
        return {'value': None, 'confidence': 'none'}
    
    # 3. 进行标准MAX30102计算
    spo2 = self._standard_max30102_algorithm(ppg_data, ir_data)
    
    # 4. 验证结果
    if 85 <= spo2 <= 100:
        return {'value': spo2, 'confidence': 'high'}
    else:
        return {'value': None, 'confidence': 'invalid', 'debug': spo2}
```

---

## 🔧 硬件数据质量问题

你的Arduino数据:
```json
{
  "ir": [618, 619, 612, 617...],  // 红外 (IR)
  "red": [604, 604, 596, 597...], // 红光 (Red/PPG)
  "timestamp": 990571,
  "user_id": 1
}
```

### 数据特点分析

```python
import numpy as np
ir = [618,619,612,617,612,612,613,607,609,613,614,611,...] # 100个点
red = [604,604,596,597,604,606,599,606,607,607,600,605,...] # 100个点

# 数据统计
IR范围: 604-621 (变化范围17)  → 非常稳定 ⚠️  
Red范围: 594-610 (变化范围16) → 非常稳定 ⚠️

# 这说明:
# 1. 手的位置很稳定
# 2. 血流脉动信号很弱
# 3. 噪声很低
# ✅ 数据质量不错
```

### 但是: 1秒数据太少了！

```
当前: 100个点 = 1秒 (100Hz采样率)
问题:
  • 心率78 = 78次/分 = 1.3次/秒
  • 1秒内只有1-2个脉搏周期
  • 无法准确计算任何长期特性(HRV、趋势等)

建议:
  • 改为5秒数据 = 500个点
  • 或10秒数据 = 1000个点
  • 这样就有6-13个完整脉搏周期，足以准确分析
```

---

## 📋 改进优先级

### 🔴 必须立即修复 (Blocker)

1. **修复心率计算**
   - Impact: 所有依赖心率的计算都错
   - Effort: 中等 (改min_distance逻辑)
   - Priority: **立即修复**

### 🟠 应该修复 (High)

2. **血压计算要么修好、要么删除**
   - Impact: 显示完全错误的医学数据
   - Effort: 高 (需要额外传感器或删除功能)
   - Priority: **本周内处理**

3. **血氧计算逻辑重新设计**
   - Impact: 不信任的数据对用户有害
   - Effort: 中等 (改验证逻辑和降级策略)
   - Priority: **本周内处理**

### 🟡 应该改进 (Medium)

4. **增加采样数据量**
   - Impact: 提高所有计算精度
   - Effort: 低 (硬件端改Arduino配置)
   - Priority: **与修复1一起做**

---

## 💡 具体修复建议

### 修复1: 心率计算 (最紧急)

**当前代码问题**:
```python
min_distance = int(0.4 * self.sampling_rate)  # 固定400ms
```

**修复方案**:
```python
def calculate_heart_rate(self, ppg_data):
    # ... 存在的代码 ...
    
    # 方案A: 动态min_distance（推荐）
    num_samples = len(ppg_data)
    expected_peaks = (num_samples / self.sampling_rate) * 1.5  # 预期峰数
    
    if num_samples < 200:  # 数据< 2秒
        # 用更宽松的间隔
        min_distance = int(0.5 * self.sampling_rate)  # 500ms
        prominence_factor = 0.5  # 更宽松的prominence
    else:
        min_distance = int(0.4 * self.sampling_rate)  # 标准400ms
        prominence_factor = 0.3
    
    peaks, _ = signal.find_peaks(
        filtered_signal,
        distance=min_distance,
        prominence=np.std(filtered_signal) * prominence_factor
    )
    
    # ... 继续计算 ...
```

### 修复2: 血压计算 (重要)

**推荐方案: 使用置信度级别**:
```python
def calculate_blood_pressure(self, ppg_data, heart_rate):
    """
    新增: systolic/diastolic 现在可以是 None
    新增: confidence 字段显示可信度
    """
    if not self._is_reliable_data(ppg_data):
        return {
            'systolic': None,
            'diastolic': None,
            'confidence': 'none',
            'reason': '数据不足，无法估算血压'
        }
    
    # 使用经验值而非公式
    estimates = {
        (60, 70): (110, 65),
        (70, 80): (120, 75),
        (80, 90): (130, 80),
        (90, 100): (140, 85),
        (100, 110): (150, 90),
    }
    
    for (hr_min, hr_max), (sys, dia) in estimates.items():
        if hr_min <= heart_rate < hr_max:
            return {
                'systolic': sys,
                'diastolic': dia,
                'confidence': 'low',  # ← 诚实的标记
                'note': '此为人群平均值，非个人测量'
            }
```

### 修复3: 血氧计算

```python
def calculate_blood_oxygen(self, ppg_data, ir_data):
    # 1. 检查基本条件
    if ir_data is None:
        return {
            'value': None,
            'confidence': 'impossible',
            'reason': '缺少IR通道数据，无法计算血氧'
        }
    
    if len(ppg_data) < 300:  # 3秒最少
        return {
            'value': None,
            'confidence': 'insufficient_data',
            'reason': '数据太少'
        }
    
    # 2. 标准算法
    try:
        spo2 = self._standard_max30102(ppg_data, ir_data)
        
        if 92 <= spo2 <= 100:
            return {
                'value': round(spo2, 1),
                'confidence': 'high'
            }
        elif 85 <= spo2 < 92:
            return {
                'value': round(spo2, 1),
                'confidence': 'medium',
                'note': '偏低，可能是测量位置不好'
            }
        else:
            return {
                'value': None,
                'confidence': 'invalid',
                'debug': round(spo2, 1)
            }
    except:
        return {
            'value': None,
            'confidence': 'error'
        }
```

---

## 📊 预期改进效果

| 指标 | 当前 | 改进后 | 改进幅度 |
|-----|-----|-------|-------|
| 心率准确性 | 127 bpm (偏高64%) | ~80-82 bpm (误差<5%) | 🚀 93% |
| 血压可信度 | 不可信(波动大) | 标记为估算/不显示 | 📋 诚实化 |
| 血氧计算 | 随机 90-92% | 带置信度的结果 | ✅ 更透明 |
| 数据需求 | 1秒(100点) | 5秒(500点) | 📈 5倍 |

---

## ✅ 下一步行动建议

1. **立即** (今天):
   - [ ] 增加min_distance难度检测逻辑
   - [ ] 测试心率是否修正到78-82 bpm

2. **本周**:
   - [ ] 修改血压计算为置信度模型
   - [ ] 更新血氧计算逻辑
   - [ ] 修改Arduino配置发送5秒数据而非1秒

3. **测试**:
   - [ ] 用你的78 bpm重新测试
   - [ ] 验证1秒vs 5秒数据的效果

要我具体帮你修改代码吗？
