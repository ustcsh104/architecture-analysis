---
name: architecture-analyzer
description: 开源项目架构分析技能。6步方法论系统性分析项目架构：鸟瞰全局→识别骨架→识别模块→追踪链路→架构提炼→产物沉淀。生成架构分层图、目录职责清单、数据流图、架构评估报告（Markdown+SVG可视化）。适用于分析开源项目、理解陌生代码库、架构评审、入职学习等场景。触发词：架构分析、分析架构、项目架构、代码架构、分析项目结构、architecture analysis、understand architecture、分析代码库、入职分析。
---

# 开源项目架构分析器

## 适用场景

- 分析陌生开源项目的整体架构
- 快速入职理解新项目代码结构
- 架构评审、技术选型前调研
- 代码库重构前梳理现状

## 工作流总览

按以下 6 步顺序执行，每步完成后更新进度追踪器：

```
架构分析进度：
- [ ] Step 1: 鸟瞰全局
- [ ] Step 2: 识别骨架
- [ ] Step 3: 识别模块
- [ ] Step 4: 追踪链路
- [ ] Step 5: 架构提炼
- [ ] Step 6: 产物沉淀+校验
```

## Step 1: 鸟瞰全局

**目标**：确定项目定位、架构模式、技术栈、模块边界、文档完备度

**操作**：
1. 读取 README.md / ARCHITECTURE.md / CONTRIBUTING.md 等顶层文档
2. 扫描根目录全部配置文件：Dockerfile、docker-compose、Makefile、pom.xml / setup.py / package.json / go.mod、tsconfig、CMakeLists 等
3. 用 Bash 生成完整目录树（`tree -L 3` 或 PowerShell `Get-ChildItem -Recurse -Name`）
4. 标记一级目录分类：源码、测试、文档、脚本、部署、前端、公共依赖

**必须回答的问题**：
- 项目解决什么问题？（业务系统 / 工具 / 中间件 / 框架）
- 官方定义的整体架构模式？（MVC / DDD / 插件化 / 微服务 / 单体）
- 技术栈？（语言、框架、数据库、中间件）
- 编译产物、部署方式、支持环境？
- 是否存在官方架构图、模块划分说明？
- 文档完备度评级（A/B/C/D）

**文档完备度评级标准**：
- A：有 ARCHITECTURE.md + 架构图 + 设计文档 + API 文档
- B：有 README + 架构图 + 基本设计说明
- C：只有 README，内容中等
- D：README 简陋或缺失

## Step 2: 识别骨架

**目标**：找到程序所有入口、依赖体系、配置加载全流程、构建边界

**操作**：
1. 找运行时入口：main 函数、CLI 入口、启动脚本、容器启动命令、cron 配置
2. 分析依赖两层：
   - **三方依赖**：从依赖文件提取第三方组件（缓存/ORM/MQ/Web框架/DB驱动）
   - **内部依赖**：用 Grep 搜索 import/include/require 语句，绘制模块依赖简图
3. 配置体系全流程：配置文件路径、加载顺序、多环境区分（dev/test/prod）、默认配置
4. 构建边界：通过构建文件确认哪些目录参与打包，哪些是测试/脚本不参与
5. 模块导出规则：`__init__.py`、包导出、对外暴露 API

**必须回答的问题**：
- 有多少种启动入口？（HTTP / 定时任务 / CLI / 后台任务 / 消息消费）
- 三方依赖核心组件清单？（Web框架/DB/缓存/MQ/日志/配置）
- 内部模块依赖关系简图？
- 配置加载优先级？是否有热更新？
- 哪些模块是公共基础包，全项目复用？

## Step 3: 识别模块

**目标**：定义每个文件夹/子模块的职责、分层边界、调用约束

**核心原则**：先不依赖目录名，通过代码行为反向推导职责

**分层判定规则**：
| 代码特征 | 推导层 | 标记 |
|----------|--------|------|
| 路由注册、请求解析、参数校验、HTTP handler | 接入层/控制器 | 🟢 |
| 核心业务规则、校验、流程编排、领域模型 | 业务层/领域层 | 🟡 |
| 数据库 CRUD、存储交互、ORM model | 数据持久层 | 🔵 |
| 通用无业务工具、格式转换、加密 | 工具层 | ⚪ |
| 插件、钩子、扩展点、策略注册 | 扩展层 | 🟣 |
| 配置、常量、枚举、类型定义 | 配置层 | 🔘 |

**操作**：
1. 抽样每个子目录 3-5 个文件，通过代码特征判定所属层
2. 记录分层调用约束（允许跨层、禁止反向调用）
3. 拆分横切通用模块：日志、监控、异常、鉴权、缓存
4. 区分独立子模块 / 公共依赖模块 / 业务隔离模块

**必须回答的问题**：
- 目录命名是行业通用约定还是项目自定义规范？
- 各模块允许依赖哪些上层/下层模块？禁止依赖哪些？
- 哪些模块属于横向通用基础设施，贯穿全项目？
- 是否存在违规跨层调用？（如控制器直接操作 DB）

## Step 4: 追踪完整链路

**目标**：梳理数据/指令完整流转路径，覆盖全场景

**至少追踪 3 类链路**：
1. **同步请求链路**：HTTP 请求 → 路由 → 中间件 → 控制器 → 业务 → 持久 → 响应
2. **异步任务链路**：消息消费 / 定时触发 → 任务加载 → 业务处理 → 存储/通知
3. **系统启动链路**：入口加载 → 配置初始化 → 插件注册 → 资源预加载 → 服务就绪

**操作**：
1. 用 SearchCodebase + Grep 找到链路关键节点
2. 用 SearchSymbol 追踪函数调用链
3. 记录每一步数据结构传递（DTO/实体/DB模型转换）
4. 标注链路中的横切拦截点（鉴权/日志/缓存/限流）

**校验**：
- 链路流转是否严格遵循分层？
- 是否存在逻辑越层跳转？

## Step 5: 架构提炼与扩展机制

**目标**：看懂项目核心设计、扩展能力、设计模式、架构取舍

**操作**：
1. 寻找扩展点：SPI 插件、中间件钩子、适配器、策略模式、事件总线
2. 识别核心设计模式：分层、工厂、单例、观察者、适配器、装饰器
3. 分析分布式/高可用设计：缓存策略、事务处理、分库分表、限流降级
4. 梳理横切能力实现方案（AOP / 拦截器 / 中间件 / 装饰器）

**输出**：
- 项目核心架构设计亮点（top 3）
- 扩展性优缺点评估
- 关键架构设计取舍分析

## Step 6: 产物沉淀 + 结论校验

**目标**：标准化输出 4 份文档 + SVG 可视化，形成闭环

**4 份标准产物**（详见 [templates.md](templates.md)）：
1. **架构分层图**（SVG）：模块 + 依赖关系 + 分层标注
2. **目录职责清单**（Markdown）：每个文件夹、核心文件的功能说明
3. **典型数据流图**（SVG）：至少 3 条核心链路流转图
4. **架构评估报告**（Markdown）：分层规范度、代码腐化点、扩展能力、学习难点

**校验动作**：
1. 对照官方 ARCHITECTURE.md 验证推导是否一致
2. 随机选取未追踪功能，快速走链路验证分层逻辑
3. 检查是否存在循环依赖、不合理跨层

## 劣质项目专项策略

当文档评级为 C/D 时，启用以下策略：
1. 从测试目录入手：测试用例是最直观的功能调用示例
2. 从入口文件逐层追踪 import 链路
3. 全局搜索关键字（db / router / service / config / middleware）批量归类
4. 检索 commit 历史，看开发者目录拆分迭代逻辑
5. 用 SearchCodebase 语义搜索替代文档阅读

## 工具使用指引

| 步骤 | 首选工具 | 用途 |
|------|----------|------|
| 路径探测 | Bash (PowerShell) | 探测项目实际根目录，规避中文路径 |
| Step 1 | Read + Glob / Bash | 读取文档和扫描目录（中文路径用 Bash） |
| Step 2 | Grep + SearchSymbol / Bash | 找入口和追踪依赖（中文路径用 Bash Select-String） |
| Step 3 | Read + Grep + SearchCodebase / Bash | 代码特征分析 |
| Step 4 | SearchSymbol + Grep / Bash | 追踪调用链 |
| Step 5 | SearchCodebase + Read / Bash | 语义搜索设计模式 |
| Step 6 | baoyu-diagram Skill + Write | 生成 SVG 架构图 + 写入产物文件 |

**SVG 架构图生成**：Step 6 中使用 `baoyu-diagram` skill 生成架构分层图和数据流图，输出 .svg 文件。

**产物统一写入**：Step 6 中所有 Markdown 产物用 Write 工具写入，SVG 产物由 baoyu-diagram 生成后确认路径。统一输出到 `.qoder/architecture-analysis/` 目录。

## 多语言识别规则

| 语言 | 入口特征 | 依赖文件 | 分层约定 |
|------|----------|----------|----------|
| Python | `main()` / `app.run()` | setup.py / requirements.txt / pyproject.toml | controller/service/model/dao |
| Java | `@SpringBootApplication` / `public static void main` | pom.xml / build.gradle | controller/service/dao/entity |
| Go | `func main()` / `http.ListenAndServe` | go.mod | handler/service/repository/model |
| Node.js | `index.js` / `app.listen()` | package.json | routes/controllers/services/models |
| Rust | `fn main()` / `actix_web` | Cargo.toml | handler/service/repository |

## 路径解析策略（重要）

分析开始前，**必须先确认项目实际根目录**。常见情况：

1. **标准情况**：工作区路径 = 项目根目录，直接使用
2. **嵌套目录**：工作区下有子目录（如 `system-design-primer-master/system-design-primer-master/`）
3. **中文后缀目录**：GitHub 下载的仓库可能被重命名为 `项目名--中文说明/`，导致路径含中文字符

**路径探测流程**（Step 1 前执行）：

```
1. 用 Glob 扫描工作区根目录下的 README.md
   - 如果找到 → 工作区根 = 项目根
   - 如果未找到 → 进入步骤 2

2. 用 Bash (PowerShell) 列出工作区根目录的子目录：
   Get-ChildItem -Path "<workspace>" -Directory | Select-Object Name
   
3. 识别可能的嵌套项目目录：
   - 与仓库名前缀匹配的目录（如 system-design-primer-master--*）
   - 含 README.md 的子目录
   
4. 用 Bash 动态解析实际路径：
   $projDir = Get-ChildItem -Path "<workspace>" -Directory | Where-Object { $_.Name -like "<关键词>*" }
   $actualRoot = Join-Path $projDir.FullName "<子目录>"
```

**⚠️ 中文路径编码规避规则**：

| 工具 | 中文路径可用性 | 规避策略 |
|------|---------------|----------|
| Glob | ❌ 不可靠 | 用 Bash `Get-ChildItem -Recurse` 替代 |
| Read | ❌ 不可靠 | 用 Bash `Get-Content -Encoding UTF8` 替代 |
| Grep | ❌ 不可靠 | 用 Bash `Select-String` 替代 |
| Write | ✅ 可靠 | 优先使用，确保输出路径统一 |
| Bash | ✅ 可靠 | 用 PowerShell 变量动态拼接路径，避免硬编码中文 |

**判断是否需要规避**：如果工作区路径包含非 ASCII 字符（中文、日文等），直接启用规避规则。如果全为 ASCII 路径，正常使用 Glob/Read/Grep。

## 详细方法论参考

完整的 6 步方法论详细说明、问题清单、校验标准见 [methodology.md](methodology.md)。

输出模板格式和示例见 [templates.md](templates.md)。
