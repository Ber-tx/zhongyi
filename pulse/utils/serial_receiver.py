# utils/serial_receiver.py - Arduino串口数据接收器

import serial
import json
import logging
import threading
from typing import Callable, Optional
from queue import Queue

logger = logging.getLogger(__name__)


class SerialDataReceiver:
    """
    Arduino串口数据接收器
    
    功能: 从Arduino设备接收JSON格式的PPG传感器数据
    """

    def __init__(self, port: str = None, baudrate: int = 115200):
        """
        初始化串口接收器
        
        Args:
            port: 串口号 (如 'COM3' 或 '/dev/ttyUSB0')
                  如果为None，自动检测
            baudrate: 波特率 (默认115200，与Arduino配置对应)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.running = False
        self.receive_thread = None
        self.data_queue = Queue()  # 数据队列
        self.on_data_received = None  # 数据回调函数

    def connect(self) -> bool:
        """
        连接到Arduino设备
        
        Returns:
            bool: 连接成功返回True
        """
        try:
            # 如果未指定端口，自动检测
            actual_port = self.port or self._auto_detect_port()
            
            if not actual_port:
                logger.error("未找到Arduino设备，请检查硬件连接")
                return False

            # 打开串口
            self.serial = serial.Serial(actual_port, self.baudrate, timeout=1)
            logger.info(f"✓ 已连接到Arduino: {actual_port}")
            return True

        except Exception as e:
            logger.error(f"串口连接失败: {e}")
            return False

    def start_receiving(self, callback: Optional[Callable] = None):
        """
        启动接收线程
        
        Args:
            callback: 数据接收回调函数，签名为 callback(data: dict)
        """
        if not self.serial or not self.serial.is_open:
            logger.error("串口未连接，请先调用 connect()")
            return

        self.on_data_received = callback
        self.running = True
        
        # 启动后台接收线程
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        logger.info("✓ 串口接收线程已启动")

    def _receive_loop(self):
        """
        接收循环（在后台线程中运行）
        """
        while self.running:
            try:
                if self.serial.in_waiting > 0:
                    # 读取一行数据
                    line = self.serial.readline().decode('utf-8').strip()
                    
                    if not line:
                        continue
                    
                    # 尝试解析JSON
                    try:
                        data = json.loads(line)
                        self.data_queue.put(data)
                        
                        # 触发回调函数
                        if self.on_data_received:
                            self.on_data_received(data)
                        
                        logger.debug(f"✓ 接收到数据: {len(data.get('ir', []))} 个采样点")
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON解析失败: {line[:50]}...")
                        
            except Exception as e:
                logger.error(f"接收错误: {e}")

    def stop_receiving(self):
        """停止接收"""
        self.running = False
        if self.receive_thread:
            self.receive_thread.join(timeout=2)
        logger.info("✓ 串口接收已停止")

    def disconnect(self):
        """断开连接"""
        self.stop_receiving()
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info("✓ 串口已关闭")

    def get_data(self, timeout: float = 1.0) -> Optional[dict]:
        """
        获取队列中的数据（阻塞）
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            dict: 数据字典，或None（超时）
        """
        try:
            return self.data_queue.get(timeout=timeout)
        except:
            return None

    def _auto_detect_port(self) -> Optional[str]:
        """
        自动检测Arduino连接的串口
        
        Returns:
            str: 串口号，或None（未找到）
        """
        try:
            import serial.tools.list_ports as list_ports
            
            ports = list_ports.comports()
            logger.info(f"检测到的串口设备: {len(ports)} 个")
            
            for port in ports:
                logger.info(f"  - {port.device}: {port.description}")
                # 通常Arduino设备描述包含"Arduino"或"CH340"
                if "Arduino" in port.description or "CH340" in port.description:
                    logger.info(f"✓ 自动选择: {port.device}")
                    return port.device
            
            # 如果无特殊标记，返回第一个可用端口
            if ports:
                logger.warning(f"未识别Arduino设备，使用第一个端口: {ports[0].device}")
                return ports[0].device
                
        except ImportError:
            logger.warning("serial.tools.list_ports 不可用，请手动指定端口")
        
        return None


# ===== 使用示例 =====
if __name__ == "__main__":
    import logging
    from config import config
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建接收器
    receiver = SerialDataReceiver(port='COM3')  # Windows: COM3, Linux: /dev/ttyUSB0
    
    # 定义数据处理回调
    def on_data(data: dict):
        print(f"收到数据: {len(data['ir'])} 个采样点")
    
    # 连接并启动接收
    if receiver.connect():
        receiver.start_receiving(callback=on_data)
        
        # 持续接收数据
        try:
            while True:
                data = receiver.get_data(timeout=5)
                if data:
                    print(f"处理数据: {data}")
        except KeyboardInterrupt:
            pass
        finally:
            receiver.disconnect()
