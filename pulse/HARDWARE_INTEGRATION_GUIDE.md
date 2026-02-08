# 硬件集成指南 - MAX30102脉诊传感器

> 本指南说明如何将MAX30102硬件集成到脉诊实时监测系统中

## 📌 目录
1. [硬件简介](#硬件简介)
2. [接线说明](#接线说明)
3. [Arduino代码配置](#arduino代码配置)
4. [Python后端配置](#python后端配置)
5. [数据验证](#数据验证)
6. [故障排除](#故障排除)

---

## 硬件简介

**MAX30102** 是一个集成式脉搏血氧仪传感器芯片，具有：
- 📊 **PPG传感器**: 采集反射光强度曲线
- 🫀 **心率计算**: 通过PPG峰值检测提取心率
- 🧬 **光谱特性**: 红光(660nm) + 红外光(880nm)
- ⚡ **采样率**: 最高200Hz（本项目使用100Hz）

---

## 接线说明

### Arduino Uno 与 MAX30102 连接

```
┌─────────────────┬──────────────┬─────────────┬──────────┐
│ MAX30102 引脚   │ Arduino 引脚 │ 颜色标记    │ 说明     │
├─────────────────┼──────────────┼─────────────┼──────────┤
│ VCC (3.3V)      │ 3.3V         │ 红色        │ 必须用3.3V│
│ GND             │ GND          │ 黑色        │ 地线     │
│ SCL             │ A5 (SCL)     │ 黄色        │ I2C时钟  │
│ SDA             │ A4 (SDA)     │ 蓝色        │ I2C数据  │
│ INT (可选)      │ 未连接       │ 紫色        │ 中断脚   │
└─────────────────┴──────────────┴─────────────┴──────────┘
```

### 引脚对应关系

| 不同Arduino板型 | SDA | SCL | 说明 |
|---|---|---|---|
| Arduino Uno | A4 | A5 | 标准模拟引脚 |
| Arduino Nano | A4 | A5 | 与Uno相同 |
| Arduino Mega | 20 | 21 | 额外I2C端口 |
| Arduino Due | 20 | 21 | 类似Mega |

### ⚠️ 重要注意

1. **必须使用3.3V电源**
   - ❌ 错误: 5V → 会烧坏传感器
   -  正确: 3.3V Arduino引脚或稳压模块

2. **可选的上拉电阻**
   ```
   SDA → 1kΩ → 3.3V
   SCL → 1kΩ → 3.3V
   ```
   大多数Arduino已内置，通常不需要额外添加。

3. **接线稳定性**
   - 使用杜邦线或焊接
   - 避免虚接触不良
   - 定期检查接线

---

## Arduino代码配置

### 1️⃣ 安装库

库管理器搜索并安装:
- **SparkFun MAX30102** (作者: SparkFun Electronics)

步骤:
```
Arduino IDE → 项目 → 加载库 → 管理库 → 搜索 "MAX30102" → 安装
```

### 2️⃣ 上传代码

```bash
# 位置: hardware/pulse_sensor_arduino.ino
# 步骤:
1. 用USB线连接Arduino
2. Arduino IDE中选择正确的板型和串口
3. 打开 pulse_sensor_arduino.ino
4. 点击上传按钮
5. 看到"Done uploading"表示成功
```

### 3️⃣ 监控串口输出

打开 Arduino IDE 的 "串口监视器":
```
工具 → 串口监视器 (Ctrl+Shift+M)
波特率: 115200
```

应该看到:
```
=== 脉诊传感器初始化 ===
✓ 传感器初始化成功
正在采集数据...

{"ir":[1234,1245,1256,...,9876],"timestamp":5000,"user_id":1}
```

---

## Python后端配置

### 方式1: 自动硬件连接 (推荐)

```bash
# 启动系统，自动检测Arduino
python main_with_hardware.py

# 或指定串口
python main_with_hardware.py --port COM3      # Windows
python main_with_hardware.py --port /dev/ttyUSB0  # Linux
```

### 方式2: 手动API模式

```bash
# 不使用硬件连接，仅提供API
python main_with_hardware.py --no-hardware
```

### 方式3: 原始API模式

```bash
# 使用原始的Flask应用（无硬件支持）
python main.py
```

---

## 数据验证

### 1. 检查Arduino输出

串口监视器应该看到JSON数据:
```json
{
  "ir": [1234, 1245, 1256, ...],    // 500个采样点 (5秒)
  "timestamp": 5000,                  // 毫秒时间戳
  "user_id": 1
}
```

### 2. 检查Python后端

日志应该显示:
```
✓ 收到硬件数据: 500 个采样点
✓ 数据处理成功: 心率=75 bpm
```

### 3. 测试API端点

```bash
# 检查硬件连接状态
curl http://localhost:5001/api/hardware/status

# 响应示例:
{
  "connected": true,
  "port": "COM3",
  "baudrate": 115200
}
```

---

## 故障排除

### ❌ 问题1: 传感器未检测到

**症状**: Arduino输出 "MAX30102 was not found"

**原因和解决**:
1. ✅ 检查接线是否正确
   - VCC连接3.3V（不是5V）
   - GND和地线相连
   - SDA/SCL接对了引脚

2. ✅ 检查I2C通信
   ```c
   // 在Arduino中运行I2C扫描程序，确认传感器地址是0x57
   ```

3. ✅ 重启Arduino
   - 断开USB线，等待2秒，重新连接

4. ✅ 检查库版本
   - 确保安装了最新版本的SparkFun MAX30102库

---

### ❌ 问题2: 串口乱码

**症状**: 串口监视器显示乱码或乱字符

**解决**:
1. ✅ 检查波特率是否为 **115200**
2. ✅ 确认Arduino中的波特率设置
   ```c
   Serial.begin(115200);  // 必须为115200
   ```
3. ✅ 更新驱动程序
   - Windows: 更新CH340或FTDI驱动

---

### ❌ 问题3: Python无法连接硬件

**症状**: "未找到Arduino设备" 或 "端口占用"

**解决**:
1. ✅ 确认USB线已连接
2. ✅ 查看串口号
   ```bash
   # Windows:
   Get-Content \\.\COM3 -Wait  # 测试COM3
   
   # Linux:
   ls /dev/ttyUSB*
   ```

3. ✅ 关闭其他串口监视器
   - Arduino IDE 的串口监视器、PuTTY等会占用端口

4. ✅ 手动指定端口
   ```bash
   python main_with_hardware.py --port COM3
   ```

5. ✅ 安装pyserial库
   ```bash
   pip install pyserial
   ```

---

### ❌ 问题4: 数据处理失败

**症状**: "PPG数据不足" 或 "信号质量不佳"

**原因和解决**:
1. ✅ 确保采样点足够 (最少100个)
   ```python
   # 检查config.py
   WINDOW_SIZE = 500  # 5秒的数据
   ```

2. ✅ 检查传感器是否接触到皮肤
   - 将手指轻轻放在传感器红光照射区域
   - 保持静止不动

3. ✅ 调整LED亮度 (Arduino代码)
   ```c
   sensor.setLedBrightness(60);  // 范围 0-255，尝试不同值
   ```

---

## 📊 数据流示意图

```
┌─────────────┐
│  MAX30102   │   → 采集PPG信号 (100Hz)
├─────────────┤
│   Arduino   │   → JSON 数据格式
├─────────────┤
│   USB串口   │   → 波特率 115200
├─────────────┤
│   Python    │   → SerialDataReceiver 接收
├─────────────┤
│  数据处理   │   → 计算心率、血氧、血压
├─────────────┤
│  Flask API  │   → RESTful 接口
├─────────────┤
│ Spring Boot │   → 后端存储和展示
└─────────────┘
```

---

## 🔧 配置速查表

| 配置项 | 值 | 位置 |
|---|---|---|
| 采样率 | 100 Hz | `config.py` |
| 波特率 | 115200 | `hardware/pulse_sensor_arduino.ino` |
| 缓冲区大小 | 500 (5秒) | `hardware/pulse_sensor_arduino.ino` |
| I2C地址 | 0x57 | MAX30102引出 |
| 数据格式 | JSON | Arduino → Python |

---

## 📝 快速启动清单

- [ ] 硬件已连接 (VCC、GND、SDA、SCL)
- [ ] Arduino库已安装 (SparkFun MAX30102)
- [ ] Arduino代码已上传
- [ ] 串口监视器可看到JSON数据
- [ ] Python环境已安装 pyserial
- [ ] config.py 采样率设置为 100Hz
- [ ] Flask应用启动成功
- [ ] API端点可访问

---

## 相关文件

| 文件 | 说明 |
|---|---|
| `hardware/pulse_sensor_arduino.ino` | Arduino硬件代码 |
| `utils/serial_receiver.py` | Python串口接收模块 |
| `main_with_hardware.py` | 集成硬件的Flask应用 |
| `config.py` | 系统配置 |

---

## 支持

如有问题:
1. 查看串口监视器的具体错误信息
2. 检查日志文件 (`logs/`)
3. 参考故障排除部分
4. 重新上传Arduino代码

---

*最后更新: 2026年2月*
