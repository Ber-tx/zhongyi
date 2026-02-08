# test_hardware_connection.py - 硬件连接测试脚本

"""
快速硬件诊断工具
用途: 在启动完整系统前，快速测试Arduino连接和数据通信
"""

import sys
import json
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports():
    """测试必要的Python库是否已安装"""
    print("\n" + "=" * 60)
    print("测试1: Python库依赖")
    print("=" * 60)
    
    required_packages = {
        'serial': 'pyserial',
        'numpy': 'numpy',
        'flask': 'Flask'
    }
    
    all_ok = True
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✓ {package:<20} 已安装")
        except ImportError:
            print(f"✗ {package:<20} 未安装 ❌")
            print(f"   请运行: pip install {package}")
            all_ok = False
    
    return all_ok


def test_serial_ports():
    """列出所有可用的串口"""
    print("\n" + "=" * 60)
    print("测试2: 可用的串口设备")
    print("=" * 60)
    
    try:
        import serial.tools.list_ports as list_ports
        
        ports = list_ports.comports()
        
        if not ports:
            print("⚠️  未检测到任何串口设备")
            print("   请检查:")
            print("   1. Arduino是否已通过USB连接")
            print("   2. USB线是否接触良好")
            print("   3. 设备管理器中是否有COM口")
            return None
        
        print(f"检测到 {len(ports)} 个设备:\n")
        
        arduino_port = None
        for port in ports:
            status = "✓" if "Arduino" in port.description or "CH340" in port.description else "○"
            print(f"{status} {port.device:<10} - {port.description}")
            
            if not arduino_port and ("Arduino" in port.description or "CH340" in port.description):
                arduino_port = port.device
        
        if arduino_port:
            print(f"\n检测到Arduino: {arduino_port}")
        else:
            print("\n⚠️  未识别到Arduino设备")
            print("   如果Arduino已连接，可能需要安装CH340驱动")
        
        return arduino_port
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def test_serial_connection(port=None):
    """测试串口连接"""
    print("\n" + "=" * 60)
    print("测试3: 串口连接")
    print("=" * 60)
    
    import serial
    
    if not port:
        print("⚠️  未指定串口，跳过此测试")
        print("   用法: python test_hardware_connection.py COM3")
        return False
    
    try:
        print(f"连接到 {port}...")
        
        ser = serial.Serial(port, 115200, timeout=2)
        print(f"✓ 连接成功")
        print(f"  波特率: 115200")
        print(f"  超时: 2秒")
        
        # 尝试读取数据
        print("\n等待Arduino数据（15秒超时）...")
        print("-" * 60)
        
        data_received = False
        timeout_counter = 0
        max_wait = 15  # 15秒
        
        while timeout_counter < max_wait:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line:
                    print(f"[{timeout_counter:2d}s] 收到: {line[:80]}")
                    
                    # 尝试解析为JSON
                    try:
                        data = json.loads(line)
                        print(f"      ✓ JSON格式有效")
                        print(f"      采样点数: {len(data.get('ir', []))}")
                        print(f"      时间戳: {data.get('timestamp')}")
                        data_received = True
                        break
                    except json.JSONDecodeError:
                        print(f"      ⚠️  JSON解析失败 (可能是调试信息)")
                        
            timeout_counter += 1
            import time
            time.sleep(1)
        
        ser.close()
        
        if data_received:
            print("-" * 60)
            print("✓ 数据接收成功！")
            return True
        else:
            print("-" * 60)
            print("❌ 未收到有效的JSON数据")
            print("\n可能的原因:")
            print("1. Arduino代码未成功上传")
            print("2. MAX30102传感器未连接或未初始化")
            print("3. 通信线（SDA/SCL）接触不良")
            return False
            
    except serial.SerialException as e:
        print(f"❌ 串口错误: {e}")
        print("\n可能的原因:")
        print("1. 当前已有程序占用此串口（关闭Arduino IDE）")
        print("2. USB驱动未安装")
        print("3. USB线接触不良")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_data_processing(sample_data=None):
    """测试数据处理"""
    print("\n" + "=" * 60)
    print("测试4: 数据处理（离线测试）")
    print("=" * 60)
    
    try:
        from core import PulseDataProcessor
        
        processor = PulseDataProcessor()
        
        # 使用示例数据
        if sample_data is None:
            sample_data = {
                "ppg": list(range(100, 600)),  # 500个采样点
                "ir": list(range(100, 600)),
                "user_id": 1,
                "timestamp": 1706000000
            }
        
        print("处理测试数据...")
        result = processor.process_raw_data(sample_data, mode='simple')
        
        if result['status'] == 'success':
            print(f"✓ 数据处理成功")
            print(f"  心率: {result['data'].get('heart_rate', 'N/A')} bpm")
            if 'blood_oxygen' in result['data']:
                print(f"  血氧: {result['data']['blood_oxygen']} %")
            if 'blood_pressure' in result['data']:
                bp = result['data']['blood_pressure']
                print(f"  血压: {bp['sys']}/{bp['dia']} mmHg")
            if 'pulse_type' in result['data']:
                print(f"  脉象: {result['data']['pulse_type']}")
            return True
        else:
            print(f"❌ 数据处理失败: {result['message']}")
            return False
            
    except ImportError as e:
        print(f"⚠️  无法导入处理模块: {e}")
        print("   请确保已安装所有依赖")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_flask_server():
    """测试Flask服务器"""
    print("\n" + "=" * 60)
    print("测试5: Flask API服务器")
    print("=" * 60)
    
    try:
        import requests
        from config import config
        
        url = f"http://{config.HOST}:{config.PORT}/health"
        
        print(f"测试连接: {url}")
        
        try:
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 服务器运行正常")
                print(f"  状态: {data['status']}")
                print(f"  版本: {data.get('version', 'N/A')}")
                print(f"  硬件: {'已连接' if data.get('hardware_connected') else '未连接'}")
                return True
            else:
                print(f"⚠️  服务器返回异常状态: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 无法连接到服务器")
            print(f"   请先启动Flask应用:")
            print(f"   python main_with_hardware.py")
            return False
            
    except ImportError:
        print("⚠️  requests库未安装，跳过此测试")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """主测试函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='硬件连接测试工具')
    parser.add_argument('--port', type=str, default=None, help='指定Arduino串口号')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    args = parser.parse_args()
    
    print("\n")
    print(" " * 20 + "脉诊系统 - 硬件诊断工具")
    print(" " * 20 + "=" * 45)
    
    results = {}
    
    # 测试1: 库依赖
    results['库依赖'] = test_imports()
    
    if not results['库依赖']:
        print("\n❌ 请先安装依赖:")
        print("   pip install -r requirements_hardware.txt")
        return False
    
    # 测试2: 串口设备
    arduino_port = test_serial_ports()
    
    if not arduino_port and not args.port:
        port_to_test = None
    else:
        port_to_test = args.port or arduino_port
    
    # 测试3: 串口连接
    if port_to_test:
        results['串口连接'] = test_serial_connection(port_to_test)
    else:
        print("\n⚠️  跳过串口测试（未找到设备或未指定端口）")
        results['串口连接'] = None
    
    # 测试4: 数据处理
    results['数据处理'] = test_data_processing()
    
    # 测试5: Flask服务器
    results['Flask API'] = test_flask_server()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, result in results.items():
        if result is None:
            status = "⊘ 跳过"
        elif result:
            status = "✓ 通过"
        else:
            status = "✗ 失败"
        print(f"{status:<10} {name}")
    
    # 下一步建议
    print("\n" + "=" * 60)
    print("建议的下一步")
    print("=" * 60)
    
    if results.get('库依赖'):
        print("✓ 库依赖已满足")
    else:
        print("❌ 请先安装依赖:  pip install -r requirements_hardware.txt")
    
    if results.get('串口连接'):
        print("✓ 硬件连接正常，可以启动系统")
    elif results.get('串口连接') is False:
        print("❌ 硬件连接失败，请检查:")
        print("   1. 参考 HARDWARE_INTEGRATION_GUIDE.md")
        print("   2. 检查接线是否正确（特别是VCC 3.3V）")
        print("   3. 尝试更新Arduino驱动")
    elif port_to_test is None:
        print("⚠️  未测试串口连接，请:")
        print(f"   python test_hardware_connection.py --port COM3")
    
    if results.get('数据处理'):
        print("✓ 数据处理正常")
    else:
        print("⚠️  数据处理失败，请检查依赖")
    
    if results.get('Flask API'):
        print("✓ Flask服务器已启动")
    else:
        print("⚠️  Flask服务器未启动或未连接，请运行:")
        print("   python main_with_hardware.py")
    
    print("\n启动完整系统:")
    if port_to_test:
        print(f"   python main_with_hardware.py --port {port_to_test}")
    else:
        print(f"   python main_with_hardware.py  (自动检测)")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
