# 快速开始指南 - 5分钟上手

> 从零到完全工作的脉诊硬件系统

## ⏱️ 预计时间
- **硬件准备**: 5分钟
- **Arduino上传**: 3分钟
- **Python配置**: 2分钟
- **系统验证**: 3分钟
- **总计**: ~13分钟

---

## 📌 前置条件

请确保你有:
- [ ] Arduino Uno 开发板
- [ ] MAX30102 传感器模块
- [ ] USB数据线（A-B 线）
- [ ] 计算机已安装Arduino IDE
- [ ] Python 3.8+ 已安装

---

## 🔌 Step 1: 硬件接线 (5分钟)

**接线对照表**:

```
MAX30102      Arduino Uno
─────────────────────────
VCC(红)  ──→  3.3V  ⚠️ 重要!
GND(黑)  ──→  GND
SDA(蓝)  ──→  A4
SCL(黄)  ──→  A5
```

**检查清单**:
- [ ] VCC 连接到 **3.3V** (不是5V!)
- [ ] GND 连接良好
- [ ] SDA 和 SCL 接线正确
- [ ] USB线已连接到电脑

---

## 📝 Step 2: 上传Arduino代码 (3分钟)

### 2.1 打开Arduino IDE

### 2.2 安装MAX30102库
```
菜单: 项目 → 加载库 → 管理库

搜索: MAX30102
作者: SparkFun Electronics
点击: 安装
```

### 2.3 打开代码并上传

```
文件 → 打开

选择: hardware/pulse_sensor_arduino.ino

工具 → 板 → Arduino Uno
工具 → 端口 → COM3 (或你的端口)

按下: 上传 (Ctrl+U)

等待: "Done uploading"
```

### 2.4 验证数据

```
工具 → 串口监视器 (Ctrl+Shift+M)

检查波特率: 115200

应该看到:
=== 脉诊传感器初始化 ===
✓ 传感器初始化成功
正在采集数据...

{"ir":[1234,1245,...],...}
```

✅ **如果看到JSON数据，说明硬件正常！**

---

## 🐍 Step 3: 配置Python环境 (2分钟)

### 3.1 安装依赖

```bash
cd e:\项目\pulse

pip install -r requirements_hardware.txt
```

### 3.2 验证安装

```bash
python -c "import serial; print('✓ pyserial 已安装')"
```

---

## 🚀 Step 4: 启动系统 (3分钟)

### 4.1 诊断硬件连接

```bash
# 先测试硬件是否正常工作
python test_hardware_connection.py

# 或指定串口
python test_hardware_connection.py --port COM3
```

**预期输出**:
```
✓ 库依赖已满足
✓ 检测到Arduino: COM3
✓ 连接成功
✓ 收到Arduino数据
✓ 数据处理成功
✓ 服务器运行正常
```

### 4.2 启动完整系统

```bash
# 方法1: 自动检测Arduino (推荐)
python main_with_hardware.py

# 方法2: 指定串口
python main_with_hardware.py --port COM3

# 方法3: 不使用硬件（纯API测试）
python main_with_hardware.py --no-hardware
```

**预期输出**:
```
==================================================
脉诊实时监测系统 v2.0
==================================================
✓ 硬件连接成功

正在采集数据...

✓ 收到硬件数据: 500 个采样点
✓ 数据处理成功: 心率=75 bpm

 * Running on http://0.0.0.0:5001
```

---

## ✅ Step 5: 验证系统 (3分钟)

### 5.1 检查健康状态

```bash
# 在另一个终端窗口运行

curl http://localhost:5001/health
```

**预期响应**:
```json
{
  "status": "healthy",
  "service": "pulse-analysis-service",
  "version": "2.0",
  "hardware_connected": true
}
```

### 5.2 检查硬件状态

```bash
curl http://localhost:5001/api/hardware/status
```

**预期响应**:
```json
{
  "connected": true,
  "port": "COM3",
  "baudrate": 115200
}
```

### 5.3 查看实时数据

打开浏览器访问:
```
http://localhost:5001/health
```

查看日志:
```bash
# 在日志中应该看到如下内容:
# ✓ 收到硬件数据: 500 个采样点
# ✓ 数据处理成功: 心率=75 bpm
```

---

## 🎉 成功标志

系统正常工作时，你应该看到:

✅ Arduino串口监视器有JSON数据
✅ Python系统启动没有错误  
✅ 日志显示收到硬件数据
✅ API端点可访问
✅ Flask应用运行在 http://localhost:5001

---

## 🔍 快速故障排除

### ❌ "MAX30102 was not found"

```
原因: 硬件接线错误
解决: 
1. 确保VCC连3.3V (不是5V!)
2. 重新检查SDA/SCL接线
3. 重启Arduino
```

### ❌ 串口乱码

```
原因: 波特率不匹配
解决:
1. 检查Arduino IDE波特率是否为115200
2. 检查硬件代码中的波特率设置
```

### ❌ "未找到Arduino设备"

```
原因: 驱动或USB问题
解决:
1. 关闭Arduino IDE
2. USB线重新插拔
3. 检查Windows设备管理器中的COM口
4. 手动指定端口: python main_with_hardware.py --port COM3
```

### ❌ Python无法导入serial

```
原因: pyserial库未安装
解决:
pip install pyserial
```

---

## 📚 详细文档

如果需要更多帮助:

| 需要帮助 | 参考文档 |
|---|---|
| 详细的接线图和原理 | [HARDWARE_INTEGRATION_GUIDE.md](HARDWARE_INTEGRATION_GUIDE.md) |
| 快速查询和常见错误 | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| 系统架构和改进总结 | [HARDWARE_INTEGRATION_SUMMARY.md](HARDWARE_INTEGRATION_SUMMARY.md) |
| 项目结构和API说明 | [README_IMPROVEMENTS.md](README_IMPROVEMENTS.md) |

---

## 🎯 下一步

系统正常工作后:

1. **连接到Spring Boot后端**
   - 修改 `config.py` 中的 `SPRING_BOOT_BASE_URL`
   - 测试数据发送

2. **优化硬件参数**
   - 调整LED亮度 (`sensor.setLedBrightness()`)
   - 调整采样频率 (SAMPLING_RATE)
   - 微调缓冲大小 (BUFFER_SIZE)

3. **测试不同用户**
   - 修改 `user_id` 值
   - 验证多用户场景

4. **性能监控**
   - 查看日志 `logs/` 目录
   - 监控数据准确率

---

## 💡 问题排查流程

```
问题出现?
    ↓
1. 查看Arduino串口输出
    - 有JSON数据吗? ✓ 转步骤2
    - 只有调试信息? → 检查硬件接线
    ↓
2. 检查Python日志
    - "收到硬件数据"吗? ✓ 转步骤3
    - "无法连接"? → 检查端口指定
    ↓
3. 测试API端点
    - /health 返回200? ✓ 完成!
    - 无法连接? → Flask未启动
    ↓
4. 查看详细文档
    → HARDWARE_INTEGRATION_GUIDE.md
```

---

## 🆘 寻求帮助

1. **查看日志**
   ```bash
   # 实时查看日志
   tail -f logs/app.log
   ```

2. **运行诊断工具**
   ```bash
   python test_hardware_connection.py --port COM3
   ```

3. **查找错误**
   - 搜索错误信息在[QUICK_REFERENCE.md](QUICK_REFERENCE.md)
   - 参考[HARDWARE_INTEGRATION_GUIDE.md](HARDWARE_INTEGRATION_GUIDE.md)的故障排除

---

## ⏮️ 重启系统

如果需要重新启动:

```bash
# 1. 关闭Flask应用 (Ctrl+C)

# 2. 关闭Arduino IDE

# 3. 拔出USB线

# 4. 等待5秒

# 5. 重新插上USB线

# 6. 重新启动系统
python main_with_hardware.py
```

---

## 📊 系统信息

| 项目 | 值 |
|---|---|
| Arduino板 | Arduino Uno |
| 传感器 | MAX30102 |
| 采样率 | 100 Hz |
| 缓冲大小 | 500点 (5秒) |
| 波特率 | 115200 bps |
| Flask端口 | 5001 |
| Python版本 | 3.8+ |

---

**🎉 祝贺！你现在拥有一个完整工作的脉诊硬件系统！**

---

*最后更新: 2026年2月6日*
