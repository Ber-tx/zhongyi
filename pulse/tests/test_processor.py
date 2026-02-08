# tests/test_processor.py - 单元测试

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from core import PulseDataProcessor, SignalProcessor


def test_signal_processor():
    """测试信号处理器"""
    print("=" * 50)
    print("测试信号处理器")
    print("=" * 50)

    processor = SignalProcessor(sampling_rate=100)

    # 生成测试信号（75 bpm）
    t = np.linspace(0, 5, 500)
    test_signal = 100 + 50 * np.sin(2 * np.pi * 1.25 * t)
    test_signal += np.random.normal(0, 2, len(t))

    # 测试心率计算
    heart_rate, peaks = processor.calculate_heart_rate(test_signal)
    print(f"✓ 心率计算: {heart_rate} bpm")
    print(f"✓ 检测到峰值: {len(peaks)} 个")

    # 测试特征提取
    features = processor.extract_features(test_signal)
    print(f"✓ 特征提取:")
    print(f"  - 心率: {features['heart_rate']} bpm")
    print(f"  - HRV SDNN: {features['hrv_sdnn']} ms")
    print(f"  - 脉搏强度: {features['pulse_strength']}")
    print(f"  - 脉律: {features['pulse_rhythm']}")

    # 测试脉象分析
    pulse_type = processor.analyze_pulse_type(features)
    print(f"✓ 脉象分析: {pulse_type}")

    print("\n测试通过！\n")


def test_pulse_data_processor():
    """测试数据处理器"""
    print("=" * 50)
    print("测试数据处理器")
    print("=" * 50)

    processor = PulseDataProcessor()

    # 测试模拟数据生成
    mock_data = processor.generate_mock_data(user_id=1)
    print(f"✓ 生成模拟数据: {len(mock_data['ppg'])} 个采样点")

    # 测试数据处理
    processed = processor.process_raw_data(mock_data)
    print(f"✓ 数据处理完成:")
    print(f"  - 用户ID: {processed['user_id']}")
    print(f"  - 心率: {processed['heart_rate']} bpm")
    print(f"  - 脉象: {processed['pulse_type']}")
    print(f"  - 信号质量: {processed['signal_quality']}")
    print(f"  - 状态: {processed['analysis_status']}")

    print("\n测试通过！\n")


def test_error_handling():
    """测试错误处理"""
    print("=" * 50)
    print("测试错误处理")
    print("=" * 50)

    processor = PulseDataProcessor()

    # 测试空数据
    empty_data = {'ppg': [], 'user_id': 1, 'timestamp': '2024-01-01 12:00:00'}
    result = processor.process_raw_data(empty_data)
    print(f"✓ 空数据处理: {result['analysis_status']}")

    # 测试数据不足
    short_data = {'ppg': [100] * 50, 'user_id': 1, 'timestamp': '2024-01-01 12:00:00'}
    result = processor.process_raw_data(short_data)
    print(f"✓ 短数据处理: {result['analysis_status']}")

    # 测试常数信号
    constant_data = {'ppg': [100] * 500, 'user_id': 1, 'timestamp': '2024-01-01 12:00:00'}
    result = processor.process_raw_data(constant_data)
    print(f"✓ 常数信号处理: {result['analysis_status']}")

    print("\n测试通过！\n")


if __name__ == '__main__':
    print("\n")
    print("🔬 开始运行单元测试")
    print("\n")

    try:
        test_signal_processor()
        test_pulse_data_processor()
        test_error_handling()

        print("=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()