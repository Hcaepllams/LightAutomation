#!/usr/bin/env python3
"""
Desktop Light Automation - 主监控脚本

基于台式机在线状态自动触发 Apple Home 灯组开关
"""
import sys
import time
import signal
import logging
from pathlib import Path

# 添加 src 到路径
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

from src.config import ConfigManager, ConfigError
from src.state import StateManager, StateError
from src.logger import Logger
from src.pinger import Pinger
from src.debouncer import Debouncer, DeviceState
from src.trigger import SceneTrigger, TriggerError


class Monitor:
    """主监控器 - 协调所有组件"""
    
    def __init__(self):
        self.config = None
        self.state_manager = None
        self.logger = None
        self.pinger = None
        self.debouncer = None
        self.trigger = None
        
        self.running = False
        self.interval = 30  # 默认检测间隔
    
    def initialize(self) -> bool:
        """
        初始化所有组件
        
        Returns:
            True 如果初始化成功，False 否则
        """
        try:
            # 1. 加载配置
            self.logger = Logger().get_logger()
            self.logger.info("🚀 启动 Desktop Light Automation")
            
            config_manager = ConfigManager()
            self.config = config_manager.load()
            self.logger.info("✅ 配置加载成功")
            
            # 2. 重新配置日志级别
            log_level = config_manager.get("logging.level")
            self.logger = Logger(level=log_level).get_logger()
            
            # 3. 加载状态
            self.state_manager = StateManager()
            saved_state = self.state_manager.load()
            self.logger.info(f"📊 状态加载：{saved_state.get('current_state', 'UNKNOWN')}")
            
            # 4. 初始化组件
            pc_ip = config_manager.get("pc.ip")
            self.interval = config_manager.get("pc.ping_interval_sec")
            
            self.pinger = Pinger(pc_ip)
            
            self.debouncer = Debouncer.from_state(
                state=saved_state.get("current_state", "UNKNOWN"),
                consecutive_online=saved_state.get("consecutive_online", 0),
                consecutive_offline=saved_state.get("consecutive_offline", 0),
                online_threshold=config_manager.get("pc.online_threshold"),
                offline_threshold=config_manager.get("pc.offline_threshold")
            )
            
            self.trigger = SceneTrigger(
                arrive_shortcut=config_manager.get("shortcuts.arrive"),
                leave_shortcut=config_manager.get("shortcuts.leave")
            )
            
            self.logger.info(f"🎯 监控目标：{pc_ip} (每 {self.interval} 秒检测)")
            return True
            
        except ConfigError as e:
            if self.logger:
                self.logger.error(f"配置错误：{e}")
            else:
                print(f"❌ 配置错误：{e}", file=sys.stderr)
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"初始化失败：{e}")
            else:
                print(f"❌ 初始化失败：{e}", file=sys.stderr)
            return False
    
    def run(self) -> None:
        """主循环"""
        self.running = True
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("🔍 开始监控循环...")
        
        try:
            while self.running:
                self._tick()
                
                # 睡眠，支持中断
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
        except Exception as e:
            self.logger.error(f"主循环异常：{e}", exc_info=True)
        finally:
            self.shutdown()
    
    def _tick(self) -> None:
        """单次检测周期"""
        try:
            # 记录上次状态
            previous_state = self.debouncer.current_state
            
            # 1. Ping 检测
            success, detail = self.pinger.ping()
            status = "🟢 在线" if success else "🔴 离线"
            self.logger.debug(f"Ping 结果：{status} ({detail})")
            
            # 2. 防抖处理
            new_state, changed = self.debouncer.update(success)
            online_cnt, offline_cnt = self.debouncer.get_counters()
            
            # 记录计数器
            self.logger.debug(
                f"计数器：连续在线={online_cnt}/{self.debouncer.online_threshold}, "
                f"连续离线={offline_cnt}/{self.debouncer.offline_threshold}"
            )
            
            # 3. 状态变化处理
            if changed:
                self.logger.info(f"📢 状态变化：{previous_state.value} → {new_state.value}")
                
                # 保存状态
                self._save_state()
                
                # 触发场景
                if new_state == DeviceState.ONLINE:
                    self.logger.info("🎬 触发场景：进入（台式机上线）")
                    self.trigger.trigger_arrive()
                elif new_state == DeviceState.OFFLINE:
                    self.logger.info("🎬 触发场景：离开（台式机下线）")
                    self.trigger.trigger_leave()
            else:
                # 定期保存计数器状态
                self._save_state()
                
        except Exception as e:
            self.logger.error(f"检测周期异常：{e}", exc_info=True)
    
    def _save_state(self) -> None:
        """保存当前状态"""
        try:
            online_cnt, offline_cnt = self.debouncer.get_counters()
            self.state_manager.set("current_state", self.debouncer.current_state.value)
            self.state_manager.set("consecutive_online", online_cnt)
            self.state_manager.set("consecutive_offline", offline_cnt)
            self.state_manager.save()
        except StateError as e:
            self.logger.error(f"状态保存失败：{e}")
    
    def _signal_handler(self, signum, frame) -> None:
        """信号处理 - 优雅退出"""
        sig_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        self.logger.info(f"📡 收到 {sig_name} 信号，准备退出...")
        self.running = False
    
    def shutdown(self) -> None:
        """关闭清理"""
        self.logger.info("🛑 正在关闭...")
        
        # 保存最终状态
        try:
            self._save_state()
            self.logger.info("💾 状态已保存")
        except Exception as e:
            self.logger.error(f"最终状态保存失败：{e}")
        
        self.logger.info("👋 已退出")


def main():
    """入口函数"""
    monitor = Monitor()
    
    if not monitor.initialize():
        sys.exit(1)
    
    monitor.run()


if __name__ == "__main__":
    main()
