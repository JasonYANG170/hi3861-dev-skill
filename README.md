[简体中文](README.md) | [English](README_en.md)

# hi3861-dev-skill

HiSilicon Hi3861V100 / OpenHarmony / LiteOS-M 固件开发 Skill，支持 Codex。仓库内置完整 SDK 快照和由该快照生成的检索索引，可用于外设开发、RTOS、联网、云接入、存储、升级、安全、低功耗以及构建调试。

## 支持范围

- 默认板卡：普中 PZ-Hi3861
- 其他板卡：HiSpark Pegasus/M1、BearPi-HM Nano、FS-Hi3861
- 外设：GPIO/中断、I2C/IIC、SPI、PWM、ADC、UART、I2S、Timer、DMA、Flash/NV、Watchdog
- LiteOS：任务、队列、信号量、互斥锁、事件、软件定时器、内存与中断
- 网络与云：Wi-Fi AP/STA、TCP/UDP、HTTP、MQTT、CoAP、IoTDA、TLS/DTLS
- 平台能力：文件系统、分区、OTA/Boot、安全、低功耗、AT 命令与故障诊断

当前索引覆盖 25,806 个 SDK 文件、2,486 个唯一 API 符号和 191 个可运行例程，其中包括普中 PZ-Hi3861 的 43 个编号例程。最新统计以 [`references/indexes/metadata.json`](references/indexes/metadata.json) 为准。

## 内容边界

知识库只包含 SDK 原始内容及其派生索引，不包含外部博客、外部 CHM 或额外提取的 PDF 文本。SDK 内原有许可证、NOTICE、文档和目录结构均被保留。

回答和生成代码时采用以下证据优先级：

1. 用户项目及实际板卡配置
2. SDK 公共头文件、源码和构建文件
3. 同板卡例程
4. SDK 原生例程或其他板卡例程（明确说明适配差异）
5. SDK 自带文档

找不到 SDK 证据的 API、引脚或配置会标记为“未验证”，不会根据通用嵌入式经验编造。

## 安装

将仓库克隆到 Codex Skills 目录：

```powershell
git clone https://github.com/JasonYANG170/hi3861-dev-skill.git "$env:USERPROFILE\.codex\skills\hi3861-dev-skill"
```

Linux/macOS：

```bash
git clone https://github.com/JasonYANG170/hi3861-dev-skill.git ~/.codex/skills/hi3861-dev-skill
```

重新打开 Codex 任务后，可以显式调用：

```text
使用 $hi3861-dev-skill 为 PZ-Hi3861 编写一个 I2C 传感器程序
```

该 Skill 也允许根据 Hi3861 开发请求自动触发。

## 索引查询

脚本仅依赖 Python 3.9+ 标准库。在仓库根目录运行：

```bash
python scripts/query_index.py --topic iic --board pz
python scripts/query_index.py --topic spi --symbol hi_spi_init
python scripts/query_index.py --topic adc --board bearpi
python scripts/query_index.py --topic liteos --json
```

默认查询优先返回 Hi3861 公共 API、原生例程和目标板卡例程，并隐藏仅来自 U-Boot/第三方目录的噪声。需要检查完整第三方结果时增加 `--include-third-party`。

## 开发输出

使用本 Skill 创建或修改固件时，应同时给出：

- 应用源文件与入口函数
- `BUILD.gn` 接线
- 必要的 `CONFIG_*` 开关
- 引脚复用、上下拉和方向配置
- 初始化顺序与返回值处理
- 编译、串口和硬件验证方法

构建命令必须以项目实际结构为准：标准 OpenHarmony 产品通常使用 `hb set` / `hb build`，部分旧 HiSpark/HiHope 例程使用 `python build.py wifiiot`。

## 更新 SDK 快照

显式指定新的 Hi3861 SDK `src` 根目录：

```bash
python scripts/sync_sources.py --sdk-root <Hi3861-SDK-src>
```

同步脚本会排除 `out`、`build_tmp`、对象文件和缓存，使用暂存目录替换快照，重建索引并执行验证；失败时自动回滚。

## 验证

```bash
python scripts/validate_hi3861_skill.py
python scripts/validate_hi3861_skill.py --full-checksums
```

验证器检查 SDK 镜像、索引路径、公共 API、配置、驱动/原生例程、43 个普中例程、主题覆盖和文件校验和。它不等同于固件编译；实际编译仍需要匹配的 Hi3861 RISC-V 工具链和烧录环境。

## 目录结构

```text
hi3861-dev-skill/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── query_index.py
│   ├── build_indexes.py
│   ├── sync_sources.py
│   └── validate_hi3861_skill.py
└── references/
    ├── indexes/
    ├── source/sdk/
    └── *.md
```

## 许可证

SDK 镜像中的代码、文档和第三方组件继续适用其各自原始许可证及 NOTICE。本仓库保留这些文件，不对 SDK 或第三方内容重新授权；使用和分发前请检查对应目录中的许可证条款。
