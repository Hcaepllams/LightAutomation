"""配置管理模块 - 加载和验证配置文件"""
import json
import os
from pathlib import Path
from typing import Dict, Any


class ConfigError(Exception):
    """配置错误异常"""
    pass


class ConfigManager:
    """配置管理器 - 负责加载、验证和提供配置"""
    
    DEFAULT_CONFIG = {
        "pc": {
            "ip": "192.168.1.100",
            "ping_interval_sec": 30,
            "online_threshold": 3,
            "offline_threshold": 5
        },
        "shortcuts": {
            "arrive": "到家",
            "leave": "离开"
        },
        "logging": {
            "level": "INFO",
            "max_days": 7
        }
    }
    
    def __init__(self, config_path: str = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认使用项目目录下的 config.json
        """
        if config_path is None:
            project_dir = Path(__file__).parent.parent
            config_path = project_dir / "config.json"
        
        self.config_path = Path(config_path)
        self._config = None
    
    def load(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
            
        Raises:
            ConfigError: 配置加载或验证失败
        """
        # 检查配置文件是否存在
        if not self.config_path.exists():
            # 创建默认配置文件
            self._create_default_config()
            print(f"⚠️  配置文件不存在，已创建默认配置: {self.config_path}")
            print(f"   请编辑此文件设置正确的 IP 地址后再运行")
            raise ConfigError(f"请配置后重新运行: {self.config_path}")
        
        # 读取配置文件
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"配置文件 JSON 格式错误: {e}")
        except Exception as e:
            raise ConfigError(f"无法读取配置文件: {e}")
        
        # 合并默认配置和用户配置
        self._config = self._merge_config(self.DEFAULT_CONFIG, user_config)
        
        # 验证配置
        self._validate()
        
        return self._config
    
    def get(self, key: str = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔（如 "pc.ip"），None 返回全部
            
        Returns:
            配置值
        """
        if self._config is None:
            self.load()
        
        if key is None:
            return self._config
        
        # 支持点号分隔的键
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value
    
    def _create_default_config(self):
        """创建默认配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ConfigError(f"无法创建默认配置文件: {e}")
    
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """递归合并配置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def _validate(self):
        """验证配置有效性"""
        # 验证 IP 地址格式
        ip = self._config.get('pc', {}).get('ip', '')
        if not ip or not isinstance(ip, str):
            raise ConfigError("PC IP 地址未配置或格式错误")
        
        # 简单的 IP 格式检查
        parts = ip.split('.')
        if len(parts) != 4:
            raise ConfigError(f"IP 地址格式错误: {ip}")
        try:
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    raise ValueError()
        except ValueError:
            raise ConfigError(f"IP 地址格式错误: {ip}")
        
        # 验证阈值
        online_threshold = self._config.get('pc', {}).get('online_threshold', 0)
        offline_threshold = self._config.get('pc', {}).get('offline_threshold', 0)
        
        if not isinstance(online_threshold, int) or online_threshold < 1:
            raise ConfigError("online_threshold 必须是正整数")
        if not isinstance(offline_threshold, int) or offline_threshold < 1:
            raise ConfigError("offline_threshold 必须是正整数")
        
        # 验证快捷指令名称
        arrive = self._config.get('shortcuts', {}).get('arrive', '')
        leave = self._config.get('shortcuts', {}).get('leave', '')
        
        if not arrive or not isinstance(arrive, str):
            raise ConfigError("快捷指令 'arrive' 未配置")
        if not leave or not isinstance(leave, str):
            raise ConfigError("快捷指令 'leave' 未配置")
