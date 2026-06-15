# architecture-analyzer

> Qoder Agent Skill — 开源项目架构分析器

系统性分析任意开源项目的代码架构，6 步方法论从全局到细节，输出可视化架构文档（Markdown + SVG）。

## 功能概览

通过 6 步递进式方法论，对陌生代码库进行完整架构分析：

| 步骤 | 名称 | 目标 |
|------|------|------|
| Step 0 | 路径探测 | 确认项目实际根目录，规避中文路径编码问题 |
| Step 1 | 鸟瞰全局 | 确定项目定位、架构模式、技术栈、模块边界 |
| Step 2 | 识别骨架 | 找到所有入口、依赖体系、配置加载流程、构建边界 |
| Step 3 | 识别模块 | 通过代码行为反向推导每个模块的职责与分层边界 |
| Step 4 | 追踪链路 | 梳理同步请求/异步任务/系统启动的完整数据流转路径 |
| Step 5 | 架构提炼 | 识别设计模式、扩展点、高可用设计、架构取舍 |
| Step 6 | 产物沉淀 | 标准化输出 4 份文档 + SVG 可视化，并做闭环校验 |

## 输出产物

分析完成后，在 `.qoder/architecture-analysis/` 目录下生成：

```
.qoder/architecture-analysis/
├── 01-architecture-layers.svg       # 架构分层图（模块+依赖+分层标注）
├── 02-directory-responsibilities.md # 目录职责清单（每个文件夹的功能说明）
├── 03-data-flow-sync.svg            # 同步请求数据流图
├── 03-data-flow-async.svg           # 异步任务数据流图
├── 03-data-flow-startup.svg         # 系统启动流程数据流图
└── 04-architecture-assessment.md    # 架构评估报告（分层规范度/扩展能力/学习难点）
```

### 架构评估报告包含

- **总体评价**：项目定位、架构模式、技术栈、总体评分
- **分层规范度评估**：违规统计（控制器直连DB、循环依赖等）
- **扩展能力评估**：SPI插件/中间件钩子/适配器/策略模式/事件总线
- **架构设计亮点**（Top 3）
- **关键架构取舍分析**
- **学习难点与建议**
- **校验结果**（对照官方文档/随机验证/循环依赖检测）

## 触发词

在 Qoder 中使用以下关键词触发本 Skill：

| 中文触发词 | 英文触发词 |
|-----------|-----------|
| 架构分析 | architecture analysis |
| 分析架构 | understand architecture |
| 项目架构 | |
| 代码架构 | |
| 分析项目结构 | |
| 分析代码库 | |
| 入职分析 | |

## 适用场景

- 分析陌生开源项目的整体架构
- 快速入职理解新项目代码结构
- 架构评审、技术选型前调研
- 代码库重构前梳理现状

## 支持的语言

| 语言 | 入口识别 | 依赖文件 | 分层约定 |
|------|----------|----------|----------|
| Python | `main()` / `app.run()` / `@app.route` | setup.py / requirements.txt / pyproject.toml | controller/service/model/dao |
| Java | `@SpringBootApplication` / `public static void main` | pom.xml / build.gradle | controller/service/dao/entity |
| Go | `func main()` / `http.ListenAndServe` | go.mod | handler/service/repository/model |
| Node.js | `index.js` / `app.listen()` | package.json | routes/controllers/services/models |
| Rust | `fn main()` / `actix_web` | Cargo.toml | handler/service/repository |

## 安装方法

### 方式一：手动安装

将本仓库克隆到 Qoder 的 skills 目录下：

```bash
# 进入 Qoder skills 目录
cd ~/.qoder/skills/   # Linux/macOS
# 或
cd %USERPROFILE%\.qoder\skills\   # Windows

# 克隆仓库
git clone https://github.com/<your-username>/architecture-analyzer.git
```

### 方式二：复制文件

将以下文件复制到 `.qoder/skills/architecture-analyzer/` 目录：

```
architecture-analyzer/
├── SKILL.md          # Skill 主文件（元数据+工作流定义）
├── methodology.md    # 详细方法论参考
├── templates.md      # 输出模板格式定义
└── scripts/
    └── scan_project.py  # 项目结构扫描辅助脚本
```

## 使用方法

### 1. 在 Qoder 中触发

在 Qoder 对话中输入触发词即可启动分析，例如：

```
分析一下这个项目的架构
```

```
帮我做一下架构分析
```

### 2. 辅助脚本（可选）

`scripts/scan_project.py` 可独立运行，用于快速收集项目基本信息：

```bash
python scan_project.py /path/to/project
```

输出 JSON 格式的项目信息摘要，包含：
- 目录结构树（带类型标记）
- 配置文件清单
- 依赖文件内容摘要
- 入口文件定位
- 语言识别

## 核心方法论

### 分层判定规则

通过代码行为反向推导模块所属层级：

| 代码特征 | 推导层 | 标记 |
|----------|--------|------|
| 路由注册、请求解析、参数校验、HTTP handler | 接入层/控制器 | 🟢 |
| 核心业务规则、校验、流程编排、领域模型 | 业务层/领域层 | 🟡 |
| 数据库 CRUD、存储交互、ORM model | 数据持久层 | 🔵 |
| 通用无业务工具、格式转换、加密 | 工具层 | ⚪ |
| 插件、钩子、扩展点、策略注册 | 扩展层 | 🟣 |
| 配置、常量、枚举、类型定义 | 配置层 | 🔘 |

### 分层调用约束

```
允许方向：接入层 🟢 → 业务层 🟡 → 持久层 🔵
禁止方向：持久层 🔵 → 业务层 🟡 ❌（反向依赖）
```

### 链路追踪覆盖

至少追踪 3 类核心链路：
1. **同步请求链路**：HTTP 请求 → 路由 → 中间件 → 控制器 → 业务 → 持久 → 响应
2. **异步任务链路**：消息消费 / 定时触发 → 任务加载 → 业务处理 → 存储/通知
3. **系统启动链路**：入口加载 → 配置初始化 → 插件注册 → 资源预加载 → 服务就绪

### 劣质项目专项策略

当文档评级为 C/D 时，自动启用：
- 从测试目录入手，用测试用例推导功能模块
- 从入口文件逐层追踪 import 链路
- 全局搜索关键字批量归类
- 检索 commit 历史，看开发者目录拆分迭代逻辑

## 特性

- **中文路径兼容**：自动检测路径编码问题，使用 PowerShell 替代方案规避编码故障
- **多语言支持**：Python / Java / Go / Node.js / Rust
- **可视化输出**：SVG 架构图 + 数据流图（通过 baoyu-diagram skill 生成）
- **闭环校验**：对照官方文档验证、随机功能验证、循环依赖检测
- **独立脚本**：`scan_project.py` 可脱离 Qoder 独立运行

## 文件结构

```
architecture-analyzer/
├── SKILL.md              # Skill 主文件：元数据定义 + 6步工作流 + 工具使用指引
├── methodology.md        # 详细方法论：每步的详细操作指南、搜索模式、校验清单
├── templates.md          # 输出模板：4份标准产物的 Markdown/SVG 模板定义
└── scripts/
    └── scan_project.py   # 辅助脚本：项目结构自动扫描，输出 JSON 摘要
```

## 依赖

- **Qoder**：本 Skill 运行于 [Qoder](https://qoder.ai/) Agent 平台
- **baoyu-diagram skill**：用于生成 SVG 架构图和数据流图（Step 6）
- **Python 3**：运行 `scan_project.py` 辅助脚本（可选）

## License

MIT
