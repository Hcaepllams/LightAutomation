"""Ping 检测模块 - 执行 ICMP ping 检测"""
import subprocess
import platform
from typing import Tuple


class Pinger:
    """
    Ping 检测器 - 执行 ICMP ping 命令
    
    支持 macOS 和 Linux
    """
    
    def __init__(self, ip: str, timeout: int = 5, count: int = 1):
        """
        初始化 Ping 检测器
        
        Args:
            ip: 目标 IP 地址
            timeout: 超时时间（秒）
            count: ping 次数
        """
        self.ip = ip
        self.timeout = timeout
        self.count = count
        self.system = platform.system()
    
    def ping(self) -> Tuple[bool, str]:
        """
        执行 ping 检测
        
        Returns:
            (成功标志，详细信息)
            - 成功：(True, "响应时间 XXms")
            - 失败：(False, 错误信息)
        """
        try:
            # 构建 ping 命令（使用绝对路径）
            if self.system == "Darwin":  # macOS
                # macOS 上 ping 通常在 /sbin/ping
                ping_path = "/sbin/ping"
                cmd = [
                    ping_path,
                    "-c", str(self.count),
                    "-W", str(self.timeout * 1000),  # macOS 使用毫秒
                    self.ip
                ]
            else:  # Linux
                cmd = [
                    "ping",
                    "-c", str(self.count),
                    "-W", str(self.timeout),
                    self.ip
                ]
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 2  # 额外缓冲时间
            )
            
            # 解析结果
            if result.returncode == 0:
                # 解析响应时间
                output = result.stdout
                if "time=" in output:
                    # 提取时间
                    time_part = output.split("time=")[1].split(" ")[0]
                    return True, f"响应时间 {time_part}"
                return True, "在线"
            else:
                return False, "无响应"
                
        except subprocess.TimeoutExpired:
            return False, "超时"
        except FileNotFoundError:
            return False, "ping 命令不可用"
        except Exception as e:
            return False, f"错误：{str(e)}"
    
    def is_reachable(self) -> bool:
        """
        快速检测是否可达
        
        Returns:
            True 如果可达，False 否则
        """
        success, _ = self.ping()
        return success
