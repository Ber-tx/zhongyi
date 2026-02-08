# utils/spring_boot_client.py - Spring Boot API客户端

import requests
import logging
from typing import Dict, Any
from config import config

logger = logging.getLogger(__name__)


class SpringBootClient:
    """Spring Boot后端API客户端"""

    def __init__(self):
        """初始化客户端"""
        self.base_url = config.SPRING_BOOT_BASE_URL
        self.pulse_endpoint = self.base_url + config.PULSE_DATA_ENDPOINT
        self.timeout = 10  # 请求超时时间（秒）

        logger.info(f"Spring Boot客户端初始化 - 目标地址: {self.base_url}")

    def send_pulse_data(self, pulse_data: Dict[str, Any]) -> bool:
        """
        发送脉诊数据到Spring Boot后端

        Args:
            pulse_data: 处理后的脉诊数据

        Returns:
            是否成功
        """
        try:
            logger.info(f"发送脉诊数据到Spring Boot - 用户ID: {pulse_data.get('user_id')}")

            response = requests.post(
                self.pulse_endpoint,
                json=pulse_data,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                logger.info("数据发送成功")
                return True
            else:
                logger.error(f"数据发送失败 - 状态码: {response.status_code}, 响应: {response.text}")
                return False

        except requests.exceptions.Timeout:
            logger.error(f"请求超时 - 目标地址: {self.pulse_endpoint}")
            return False

        except requests.exceptions.ConnectionError:
            logger.error(f"连接失败 - 请确认Spring Boot服务是否启动: {self.pulse_endpoint}")
            return False

        except Exception as e:
            logger.error(f"发送数据异常: {e}", exc_info=True)
            return False

    def test_connection(self) -> bool:
        """
        测试与Spring Boot的连接

        Returns:
            连接是否正常
        """
        try:
            # 可以添加一个健康检查端点
            health_url = f"{self.base_url}/actuator/health"
            response = requests.get(health_url, timeout=5)

            if response.status_code == 200:
                logger.info("Spring Boot连接正常")
                return True
            else:
                logger.warning(f"Spring Boot连接异常 - 状态码: {response.status_code}")
                return False

        except Exception as e:
            logger.warning(f"无法连接到Spring Boot: {e}")
            return False