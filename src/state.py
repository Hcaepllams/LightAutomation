"""状态管理模块 - 持久化当前检测状态"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class StateError(Exception):
    """状态错误异常"""
    pass


class StateManager:
    """
    状态管理器 - 负责读写状态文件
    
    使用原子写入策略防止文件损坏
    """
    
    def __init__(self, state_path: str = None):
        """
        初始化状态管理器
        
        Args:
            state_path: 状态文件路径，默认使用项目目录下的 state.json
        """
        if state_path is None:
            project_dir = Path(__file__).parent.parent
            state_path = project_dir / "state.json"
        
        self.state_path = Path(state_path)
        self._state = None
    
    def load(self) -> Dict[str, Any]:
        """
        加载状态文件
        
        Returns:
            状态字典，如果不存在返回默认状态
        """
        if not self.state_path.exists():
            # 返回默认状态
            self._state = self._get_default_state()
            return self._state
        
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                self._state = json.load(f)
        except json.JSONDecodeError:
            # 文件损坏，重置为默认状态
            self._state = self._get_default_state()
        except Exception as e:
            raise StateError(f"无法读取状态文件: {e}")
        
        # 确保必要字段存在
        default = self._get_default_state()
        for key, value in default.items():
            if key not in self._state:
                self._state[key] = value
        
        return self._state
    
    def save(self, state: Dict[str, Any] = None) -> None:
        """
        保存状态到文件（原子写入）
        
        Args:
            state: 要保存的状态，None 使用当前缓存的状态
        """
        if state is not None:
            self._state = state
        
        if self._state is None:
            self._state = self._get_default_state()
        
        # 更新时间戳
        self._state['last_updated'] = datetime.now().isoformat()
        
        # 原子写入：先写入临时文件，再重命名
        temp_path = self.state_path.with_suffix('.tmp')
        
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self._state, f, ensure_ascii=False, indent=2)
            
            # 原子重命名
            os.replace(temp_path, self.state_path)
        except Exception as e:
            # 清理临时文件
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
            raise StateError(f"无法保存状态文件: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取状态值
        
        Args:
            key: 状态键
            default: 默认值
            
        Returns:
            状态值
        """
        if self._state is None:
            self.load()
        
        return self._state.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        设置状态值
        
        Args:
            key: 状态键
            value: 状态值
        """
        if self._state is None:
            self.load()
        
        self._state[key] = value
    
    def _get_default_state(self) -> Dict[str, Any]:
        """获取默认状态"""
        return {
            "current_state": "UNKNOWN",
            "consecutive_online": 0,
            "consecutive_offline": 0,
            "last_updated": datetime.now().isoformat()
        }
