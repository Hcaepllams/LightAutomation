"""日志配置模块 - 设置日志记录"""
import logging
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler


class Logger:
    """日志管理器 - 配置和控制日志输出"""
    
    def __init__(self, 
                 log_dir: str = None,
                 level: str = "INFO",
                 max_days: int = 7):
        """
        初始化日志管理器
        
        Args:
            log_dir: 日志目录，默认使用项目目录下的 logs/
            level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
            max_days: 日志保留天数
        """
        if log_dir is None:
            project_dir = Path(__file__).parent.parent
            log_dir = project_dir / "logs"
        
        self.log_dir = Path(log_dir)
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.max_days = max_days
        self.logger = None
    
    def setup(self) -> logging.Logger:
        """
        设置日志系统
        
        Returns:
            配置好的 logger 实例
        """
        # 确保日志目录存在
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建 logger
        self.logger = logging.getLogger("desktop_light")
        self.logger.setLevel(self.level)
        
        # 清除已有 handler
        self.logger.handlers = []
        
        # 文件 handler - 按天轮转
        log_file = self.log_dir / "monitor.log"
        file_handler = TimedRotatingFileHandler(
            log_file,
            when="midnight",
            interval=1,
            backupCount=self.max_days,
            encoding="utf-8"
        )
        file_handler.setLevel(self.level)
        
        # 控制台 handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        
        # 格式化
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加 handler
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        return self.logger
    
    def get_logger(self) -> logging.Logger:
        """获取 logger 实例"""
        if self.logger is None:
            return self.setup()
        return self.logger
