# Desktop Light Automation

基于台式机在线状态自动触发 Apple Home 灯组开关

## 功能

- 🔍 每 30 秒检测台式机在线状态（ICMP Ping）
- 🎯 防抖设计：连续 3 次在线才判定上线，连续 5 次离线才判定下线
- 🏠 自动触发 Apple Home "到家" / "离开" 场景
- 💾 状态持久化，重启后不会重复触发
- 📝 完善的日志记录

## 快速开始

### 1. 配置

编辑 `config.json`：

```json
{
  "pc": {
    "ip": "192.168.1.100",      // 台式机 IP 地址
    "ping_interval_sec": 30,    // 检测间隔（秒）
    "online_threshold": 3,      // 判定在线的连续成功次数
    "offline_threshold": 5      // 判定离线的连续失败次数
  },
  "shortcuts": {
    "arrive": "到家",           // macOS 快捷指令名称（开灯场景）
    "leave": "离开"             // macOS 快捷指令名称（关灯场景）
  },
  "logging": {
    "level": "INFO",            // 日志级别: DEBUG/INFO/WARNING/ERROR
    "max_days": 7               // 日志保留天数
  }
}
```

### 2. 创建快捷指令

在 macOS "快捷指令" App 中创建两个自动化场景：

1. **"到家"**：触发开灯场景
2. **"离开"**：触发关灯场景

确保快捷指令名称与 `config.json` 中的配置一致。

### 3. 运行

**手动运行**：
```bash
./scripts/run.sh
```

**后台运行**：
```bash
nohup ./scripts/run.sh > /dev/null 2>&1 &
```

**停止**：
```bash
pkill -f "python3 src/monitor.py"
```

### 4. 开机自启（推荐）

macOS 开机自动启动并崩溃重启：

```bash
# 安装服务
./scripts/install-service.sh

# 查看状态
launchctl list | grep com.lightautomation.monitor

# 卸载服务
launchctl unload ~/Library/LaunchAgents/com.lightautomation.monitor.plist
rm ~/Library/LaunchAgents/com.lightautomation.monitor.plist
```

### 5. 查看日志

```bash
# 运行日志
tail -f logs/monitor.log

# 启动服务日志
tail -f logs/launchd.out.log
tail -f logs/launchd.err.log
```

## 项目结构

```
desktop-light-automation/
├── README.md
├── requirements.md       # 需求文档
├── design.md             # 设计文档
├── config.example.json   # 配置模板
├── config.json           # 配置文件（本地创建，不提交）
├── state.json            # 运行时状态（自动生成）
├── .gitignore            # Git 忽略规则
├── logs/                 # 日志目录
│   └── monitor.log
├── src/                  # 源代码
│   ├── monitor.py        # 主监控脚本
│   ├── config.py         # 配置管理
│   ├── state.py          # 状态持久化
│   ├── logger.py         # 日志配置
│   ├── pinger.py         # Ping 检测
│   ├── debouncer.py      # 防抖逻辑
│   └── trigger.py        # 场景触发
└── scripts/
    ├── run.sh                          # 启动脚本
    ├── install-service.sh              # 开机自启安装脚本
    └── com.lightautomation.monitor.plist  # launchd 配置模板
```

## 状态流转

```
UNKNOWN → 连续3次成功 → ONLINE
  ↑                         │
  └──── 连续5次失败 ─────────┘
```

## 技术栈

- Python 3.9+
- 零外部依赖（仅使用标准库）
- macOS 原生工具：`ping`, `shortcuts`

## 许可证

MIT
