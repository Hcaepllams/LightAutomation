"""场景触发模块 - 调用 macOS 快捷指令"""
import subprocess
import logging
from typing import Tuple


class TriggerError(Exception):
    """触发错误异常"""
    pass


class SceneTrigger:
    """
    场景触发器 - 调用 macOS 快捷指令
    
    使用 `shortcuts run` 命令触发 HomeKit 场景
    """
    
    def __init__(self, 
                 arrive_shortcut: str,
                 leave_shortcut: str,
                 timeout: int = 10):
        """
        初始化场景触发器
        
        Args:
            arrive_shortcut: "到家"快捷指令名称
            leave_shortcut: "离开"快捷指令名称
            timeout: 命令执行超时时间（秒）
        """
        self.arrive_shortcut = arrive_shortcut
        self.leave_shortcut = leave_shortcut
        self.timeout = timeout
        self.logger = logging.getLogger("desktop_light")
    
    def trigger_arrive(self) -> Tuple[bool, str]:
        """
        触发"到家"场景
        
        Returns:
            (成功标志, 详细信息)
        """
        return self._run_shortcut(self.arrive_shortcut, "到家")
    
    def trigger_leave(self) -> Tuple[bool, str]:
        """
        触发"离开"场景
        
        Returns:
            (成功标志, 详细信息)
        """
        return self._run_shortcut(self.leave_shortcut, "离开")
    
    def _run_shortcut(self, shortcut_name: str, scene_name: str) -> Tuple[bool, str]:
        """
        执行快捷指令
        
        Args:
            shortcut_name: 快捷指令名称
            scene_name: 场景名称（用于日志）
            
        Returns:
            (成功标志, 详细信息)
        """
        cmd = ["shortcuts", "run", shortcut_name]
        
        try:
            self.logger.info(f"🎬 触发场景: {scene_name} (快捷指令: {shortcut_name})")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                msg = f"场景 '{scene_name}' 触发成功"
                if result.stdout.strip():
                    msg += f" | 输出: {result.stdout.strip()[:100]}"
                self.logger.info(f"✅ {msg}")
                return True, msg
            else:
                error = result.stderr.strip() or "未知错误"
                msg = f"场景 '{scene_name}' 触发失败: {error}"
                self.logger.error(f"❌ {msg}")
                return False, msg
                
        except subprocess.TimeoutExpired:
            msg = f"场景 '{scene_name}' 触发超时 ({self.timeout}秒)"
            self.logger.error(f"⏱️  {msg}")
            return False, msg
        except FileNotFoundError:
            msg = "快捷指令工具 (shortcuts) 不可用，请确认 macOS 版本支持"
            self.logger.error(f"🚫 {msg}")
            return False, msg
        except Exception as e:
            msg = f"场景 '{scene_name}' 触发异常: {str(e)}"
            self.logger.error(f"💥 {msg}")
            return False, msg
