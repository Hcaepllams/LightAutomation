"""防抖模块 - 实现状态防抖逻辑"""
from enum import Enum
from typing import Tuple


class DeviceState(Enum):
    """设备状态枚举"""
    UNKNOWN = "UNKNOWN"
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class Debouncer:
    """
    防抖器 - 实现连续检测防抖逻辑
    
    逻辑:
    - 连续 N 次在线 -> 判定为在线
    - 连续 M 次离线 -> 判定为离线
    """
    
    def __init__(self, 
                 online_threshold: int = 3,
                 offline_threshold: int = 5):
        """
        初始化防抖器
        
        Args:
            online_threshold: 连续在线次数阈值（判定为在线）
            offline_threshold: 连续离线次数阈值（判定为离线）
        """
        self.online_threshold = online_threshold
        self.offline_threshold = offline_threshold
        
        self.current_state = DeviceState.UNKNOWN
        self.consecutive_online = 0
        self.consecutive_offline = 0
    
    def update(self, ping_success: bool) -> Tuple[DeviceState, bool]:
        """
        更新检测状态
        
        Args:
            ping_success: 本次 ping 是否成功
            
        Returns:
            (当前状态, 状态是否发生变化)
        """
        previous_state = self.current_state
        
        if ping_success:
            # 在线计数 +1，离线计数清零
            self.consecutive_online += 1
            self.consecutive_offline = 0
            
            # 检查是否达到在线阈值
            if self.current_state != DeviceState.ONLINE:
                if self.consecutive_online >= self.online_threshold:
                    self.current_state = DeviceState.ONLINE
        else:
            # 离线计数 +1，在线计数清零
            self.consecutive_offline += 1
            self.consecutive_online = 0
            
            # 检查是否达到离线阈值
            if self.current_state != DeviceState.OFFLINE:
                if self.consecutive_offline >= self.offline_threshold:
                    self.current_state = DeviceState.OFFLINE
        
        # 判断是否发生状态变化
        state_changed = (previous_state != self.current_state)
        
        return self.current_state, state_changed
    
    def get_counters(self) -> Tuple[int, int]:
        """
        获取当前计数器值
        
        Returns:
            (连续在线次数, 连续离线次数)
        """
        return self.consecutive_online, self.consecutive_offline
    
    def reset(self) -> None:
        """重置状态为 UNKNOWN，计数器清零"""
        self.current_state = DeviceState.UNKNOWN
        self.consecutive_online = 0
        self.consecutive_offline = 0
    
    @classmethod
    def from_state(cls, 
                   state: str,
                   consecutive_online: int,
                   consecutive_offline: int,
                   online_threshold: int = 3,
                   offline_threshold: int = 5) -> "Debouncer":
        """
        从持久化状态恢复防抖器
        
        Args:
            state: 保存的状态字符串
            consecutive_online: 连续在线次数
            consecutive_offline: 连续离线次数
            online_threshold: 在线阈值
            offline_threshold: 离线阈值
            
        Returns:
            恢复状态的 Debouncer 实例
        """
        debouncer = cls(online_threshold, offline_threshold)
        
        try:
            debouncer.current_state = DeviceState(state)
        except ValueError:
            debouncer.current_state = DeviceState.UNKNOWN
        
        debouncer.consecutive_online = consecutive_online
        debouncer.consecutive_offline = consecutive_offline
        
        return debouncer
