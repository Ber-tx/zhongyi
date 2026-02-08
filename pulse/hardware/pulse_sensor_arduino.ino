#include <Wire.h>
#include "MAX30105.h"  // SparkFun MAX30102/MAX30105库

// ===== 配置常数 =====
#define SAMPLING_RATE 100        // 采样率 100Hz
#define BUFFER_SIZE 500          // 缓冲区大小：500个样本 = 5秒数据一包 ✅ 已改进（原为100=1秒）
#define BAUD_RATE 115200         // 串口波特率

// ===== 全局变量 =====
MAX30105 sensor;
uint32_t irBuffer[BUFFER_SIZE];   // 红外通道缓冲区
uint32_t redBuffer[BUFFER_SIZE];  // 红光通道缓冲区（新增，用于准确计算SpO2）
int bufferIndex = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  delay(1000);
  
  Serial.println("\n=== 脉诊传感器初始化 (ESP32版本 v2.0) ===");
  Serial.println("BOOT OK");

  // ESP32专用I2C引脚
  Wire.begin(21, 22);  // SDA=21, SCL=22
  Serial.println("I2C STARTED (SDA:21, SCL:22)");

  Serial.println("TRY SENSOR");

  if (!sensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("错误: MAX30102传感器未检测到！");
    Serial.println("请检查连线：VCC→3.3V, GND→GND, SDA→21, SCL→22");
    while (1) delay(1000);
  }

  // 高质量PPG配置（推荐）
  byte ledBrightness = 80;    // LED亮度 60~100（根据手指厚度可调，过高会饱和）
  byte sampleAverage = 4;     // 平均4次采样（降噪）
  byte ledMode = 2;           // 2 = 红光 + 红外（必须开启两者才能准确算SpO2）
  byte sampleRate = 100;      // 采样率 100Hz
  int pulseWidth = 411;       // 最高脉宽（最高分辨率）
  int adcRange = 16384;       // 最高ADC范围（最高灵敏度）

  sensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);

  Serial.println("✓ SENSOR OK");
  Serial.println("✓ 传感器初始化成功");
  Serial.println("✓ 数据包大小: 500个样本 = 5秒数据");
  Serial.println("✓ 包含红光(Red) + 红外(IR)两个通道用于准确计算SpO2和心率");
  Serial.println("正在采集数据... (每5秒发送一包)");
  Serial.println("");
}

void loop() {
  // 同时采集红光和红外（必须两者都有才能准确算SpO2和心率）
  redBuffer[bufferIndex] = sensor.getRed();  // 红光通道
  irBuffer[bufferIndex]  = sensor.getIR();   // 红外通道

  bufferIndex++;

  // 缓冲区满（5秒数据）时发送
  if (bufferIndex >= BUFFER_SIZE) {
    sendDataToPython();
    bufferIndex = 0;
  }

  // 精确控制采样间隔 10ms
  delay(1000 / SAMPLING_RATE);
}

void sendDataToPython() {
  Serial.print("{\"ir\":[");
  for (int i = 0; i < BUFFER_SIZE; i++) {
    Serial.print(irBuffer[i]);
    if (i < BUFFER_SIZE - 1) Serial.print(",");
  }
  
  Serial.print("],\"red\":[");
  for (int i = 0; i < BUFFER_SIZE; i++) {
    Serial.print(redBuffer[i]);
    if (i < BUFFER_SIZE - 1) Serial.print(",");
  }
  
  Serial.print("],\"timestamp\":");
  Serial.print(millis());
  Serial.println(",\"user_id\":1}");
}
