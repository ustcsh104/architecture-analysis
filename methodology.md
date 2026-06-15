# 架构分析详细方法论

## Step 0 路径探测 — 分析前必做（重要）

### 0.1 为什么需要路径探测

实际使用中，用户提供的项目路径经常出现以下情况：
- GitHub 克隆的仓库在本地被重命名为 `项目名--中文说明/`（如 `system-design-primer-master--系统设计面试库`）
- 工作区根目录是空壳，实际项目文件在嵌套子目录中
- 路径包含中文字符，导致 Glob/Read/Grep 工具无法正常工作

### 0.2 路径探测步骤

**Step A：快速判断路径是否可用**

```
用 Glob 扫描工作区根目录下的 README.md：
- 找到 → 工作区根 = 项目根，直接进入 Step 1
- 未找到 → 继续 Step B
```

**Step B：探测嵌套项目目录**

```powershell
# 列出工作区根的所有子目录
Get-ChildItem -Path "<workspace>" -Directory | Select-Object Name

# 寻找含 README.md 的子目录
$projDir = Get-ChildItem -Path "<workspace>" -Directory | Where-Object { $_.Name -like "<关键词>*" }
$innerDir = Join-Path $projDir.FullName "可能的嵌套目录"
Get-ChildItem -Path $innerDir -File | Where-Object { $_.Name -eq "README.md" }
```

**Step C：确认项目根并记录**

探测完成后，记录两个关键路径：
- `WORKSPACE_ROOT`：工作区根目录（产物输出基准路径）
- `PROJECT_ROOT`：项目实际根目录（分析操作基准路径）

两者可能相同，也可能不同。所有产物统一输出到 `WORKSPACE_ROOT/.qoder/architecture-analysis/`。

### 0.3 中文路径编码规避详细策略

**判断条件**：路径中包含任何非 ASCII 字符（中文、日文、韩文等）时启用规避。

| 操作 | 正常工具 | 规避替代方案 | 示例 |
|------|----------|-------------|------|
| 扫描文件 | Glob | Bash: `Get-ChildItem -Recurse` | `Get-ChildItem -Path $dir -Recurse -File -Filter "*.py"` |
| 读取文件 | Read | Bash: `Get-Content -Encoding UTF8` | `Get-Content -Path $file -Encoding UTF8` |
| 搜索内容 | Grep | Bash: `Select-String` | `Select-String -Path $files -Pattern "def main"` |
| 写入文件 | Write | Write（可靠） | 直接使用 Write 工具 |

**关键原则**：
1. **永远用 PowerShell 变量动态拼接路径**，不要硬编码中文路径字符串
2. **文件写入优先用 Write 工具**，Write 对中文路径可靠
3. **扫描结果通过 PowerShell 变量传递**，避免中文路径在命令间传递时编码丢失

```powershell
# 正确做法：用变量动态获取路径
$projDir = Get-ChildItem -Path "e:\工作区" -Directory | Where-Object { $_.Name -like "my-project*" }
$file = Join-Path $projDir.FullName "src\main.py"
Get-Content -Path $file -Encoding UTF8

# 错误做法：硬编码中文路径
# Read(file_path="e:\工作区\我的项目--中文说明\src\main.py")  ← 可能失败
```

---

## Step 1 鸟瞰全局 — 详细操作指南

### 1.1 文档扫描优先级

按以下优先级依次读取，发现即停：

1. `ARCHITECTURE.md` / `DESIGN.md` — 90% 优质项目自带架构说明
2. `README.md` — 项目定位和基本说明
3. `CONTRIBUTING.md` — 开发约定和代码规范
4. `docs/` 目录下的设计文档
5. Wiki 页面（如果是 GitHub 项目）

### 1.2 配置文件扫描清单

| 文件 | 识别内容 |
|------|----------|
| Dockerfile / docker-compose.yml | 部署方式、服务编排、端口映射 |
| Makefile / justfile | 构建目标、常用命令 |
| pom.xml / build.gradle | Java 项目：依赖、插件、打包方式 |
| package.json / tsconfig.json | Node 项目：依赖、脚本、模块系统 |
| setup.py / pyproject.toml / requirements.txt | Python 项目：依赖、入口、版本 |
| go.mod / Cargo.toml / Gemfile | Go/Rust/Ruby 依赖 |
| .env / config.yaml / application.properties | 配置文件格式 |

### 1.3 目录分类标记

生成目录树后，每个一级目录标注类型：
- `[源码]` src / lib / app / cmd / internal / pkg
- `[测试]` tests / test / spec / __tests__
- `[文档]` docs / doc / examples / examples
- `[脚本]` scripts / hack / bin
- `[部署]` deploy / k8s / docker / infra
- `[前端]` web / frontend / ui / client / public
- `[公共]` common / shared / utils / pkg / internal/common

### 1.4 完整问题清单

- 项目解决什么问题？是业务系统、工具、中间件还是框架？
- 目标用户是谁？开发者 / 运维 / 终端用户？
- 官方定义的整体架构模式？
- 核心技术栈清单（语言版本 / 框架 / DB / 缓存 / MQ）？
- 编译产物是什么？二进制 / Docker镜像 / npm包 / 库？
- 支持哪些运行环境？OS / 运行时版本？
- 是否存在官方架构图？
- 文档完备度评级？

---

## Step 2 识别骨架 — 详细操作指南

### 2.1 入口识别搜索模式

| 语言 | 搜索模式 |
|------|----------|
| Python | `def main` / `app.run` / `@app.route` / `if __name__` |
| Java | `@SpringBootApplication` / `public static void main` / `@Main` |
| Go | `func main()` / `http.ListenAndServe` / `grpc.NewServer` |
| Node.js | `app.listen` / `module.exports` / `export default` |
| Rust | `fn main()` / `actix_web::HttpServer` |

用 Grep 搜索以上模式，定位所有入口文件。

### 2.2 内部依赖分析

用 Grep 搜索 import/include/require 语句：
- Python: `import` / `from ... import`
- Java: `import` 包名
- Go: `import` 包路径
- Node.js: `require()` / `import from`
- Rust: `use` 路径

统计各目录之间的引用频率，绘制依赖矩阵：

```
模块A → 模块B (12次引用)
模块A → 模块C (3次引用)
模块B → 模块D (8次引用)
```

### 2.3 配置体系分析

追踪配置加载链路：
1. 找所有配置文件（.env / .yaml / .json / .properties / .toml）
2. 找配置加载代码（`config.load` / `os.getenv` / `@Value` / `viper`）
3. 分析加载顺序和优先级（环境变量 > 配置文件 > 默认值）
4. 检查多环境支持（dev / test / prod 配置文件区分）

### 2.4 构建边界分析

从构建文件提取：
- 哪些目录参与编译/打包？
- 哪些被排除（测试/脚本/文档）？
- 是否有多个构建目标（多模块项目）？

---

## Step 3 识别模块 — 详细操作指南

### 3.1 代码行为判定详细规则

**接入层/控制器** 🟢：
- 文件含路由注册（`@RequestMapping` / `router.get` / `@app.route`）
- 文件含请求解析（`req.body` / `request.getParameter` / `c.Request()`)
- 文件含参数校验（`validate` / `@Valid` / `schema.validate`）
- 文件含 HTTP 状态码返回（`200` / `404` / `ResponseEntity`）

**业务层/领域层** 🟡：
- 文件含业务规则校验（`if status ==` / `checkPermission`）
- 文件含流程编排（`processOrder` / `executeWorkflow`）
- 文件含领域模型（`class User` / `type Order struct`）
- 文件不含 HTTP 概念、不含 DB 操作细节

**数据持久层** 🔵：
- 文件含 CRUD 操作（`SELECT` / `INSERT` / `db.Query` / `findOne`）
- 文件含 ORM model 定义（`@Entity` / `db.Model` / `type X struct`）
- 文件含存储交互（`redis.get` / `s3.upload` / `elasticsearch.search`）

**工具层** ⚪：
- 文件无业务逻辑
- 通用工具函数（`formatDate` / `encrypt` / `parseConfig`）

**扩展层** 🟣：
- 文件含插件注册（`registerPlugin` / `@Plugin` / `Hook`）
- 文件含策略选择（`Strategy` / `Adapter` / `Factory`）
- 文件含事件监听（`@EventListener` / `subscribe` / `on_event`）

### 3.2 分层调用约束矩阵

标准分层调用约束：

```
允许调用方向：
接入层 🟢 → 业务层 🟡 → 持久层 🔵
接入层 🟢 → 工具层 ⚪
业务层 🟡 → 工具层 ⚪
业务层 🟡 → 持久层 🔵
任何层 → 配置层 🔘

禁止调用方向：
持久层 🔵 → 业务层 🟡  ❌ 反向依赖
持久层 🔵 → 接入层 🟢  ❌ 反向依赖
业务层 🟡 → 接入层 🟢  ❌ 反向依赖
```

### 3.3 跨层调用校验方法

抽样检查 3-5 个控制器文件：
- 搜索是否直接包含 SQL/DB 操作关键词
- 搜索是否直接包含 HTTP 响应关键词（在 DAO 文件中）
- 记录所有违规案例

---

## Step 4 追踪完整链路 — 详细操作指南

### 4.1 同步请求链路追踪模板

```
[客户端请求]
    ↓ URL + Method + Headers + Body
[路由层] 路由匹配 → middleware chain
    ↓ 请求对象
[中间件] 鉴权 → 日志 → 限流 → 参数校验
    ↓ 校验后的请求
[控制器] 解析参数 → 调用业务
    ↓ DTO / Command
[业务层] 规则校验 → 流程编排 → 调用持久
    ↓ Entity / Domain Model
[持久层] DB/缓存 操作
    ↓ Query/Command → ResultSet
[持久层] 返回数据模型
    ↓ Model → Entity 转换
[业务层] 组装返回 DTO
    ↓ Response DTO
[控制器] 格式化 HTTP 响应
    ↓ HTTP Response
[客户端]
```

### 4.2 异步任务链路追踪模板

```
[触发源] MQ消息 / Cron定时 / Event事件
    ↓ Message / Schedule / Event
[消费者] 消息接收 → 反序列化
    ↓ Task / Job
[任务加载] 参数校验 → 权限检查
    ↓ Validated Task
[业务处理] 核心逻辑 → 状态更新
    ↓ Entity / State Change
[持久操作] DB写入 → 缓存更新
    ↓ Commit
[通知] 结果推送 / 后续任务触发
```

### 4.3 启动链路追踪模板

```
[入口] main() / app.run() / CMD启动
    ↓
[配置加载] 优先级链：env → file → default
    ↓ Config Object
[插件注册] 扫描plugins目录 → 加载 → 初始化
    ↓ Plugin Registry
[资源预加载] DB连接池 / 缓存预热 / 路由注册
    ↓ Ready Resources
[服务就绪] HTTP监听 / MQ订阅 / Worker启动
```

### 4.4 数据结构转换记录

每步标注数据结构类型变化：
- Request → DTO（入参映射）
- DTO → Command（业务指令）
- Command → Entity（领域对象）
- Entity → Model（持久对象）
- Model → Entity（查询结果映射）
- Entity → DTO（返回映射）
- DTO → Response（HTTP响应）

---

## Step 5 架构提炼 — 详细操作指南

### 5.1 扩展点搜索关键词

| 扩展类型 | 搜索关键词 |
|----------|------------|
| SPI插件 | Plugin / Extension / Addon / Module / register |
| 中间件钩子 | Middleware / Interceptor / Filter / Handler |
| 适配器 | Adapter / Bridge / Wrapper / Proxy |
| 策略模式 | Strategy / Policy / Rule / Selector |
| 事件总线 | EventBus / PubSub / Subscribe / Observer / Listener |
| 装饰器 | Decorator / Wrapper / Enhancer / @decorator |

### 5.2 设计模式识别清单

| 模式 | 识别特征 |
|------|----------|
| 分层 | controller → service → dao 目录结构 |
| 工厂 | Factory / Create / Builder / 新建方法集中 |
| 单例 | Singleton / getInstance / 共享实例 |
| 观察者 | Observer / Listener / Callback / 事件注册 |
| 适配器 | Adapter / Bridge / 两个系统间的转换层 |
| 装饰器 | Decorator / Wrapper / 功能增强不改原类 |
| 策略 | Strategy / Policy / 算法选择器 |

### 5.3 高可用设计分析清单

- 缓存策略：本地缓存 / 分布式缓存 / 多级缓存
- 事务处理：本地事务 / 分布式事务 / Saga / TCC
- 分库分表：Sharding / Partition / 分片策略
- 限流降级：RateLimit / CircuitBreaker / Fallback
- 服务发现：Consul / Etcd / Zookeeper / DNS
- 配额管理：Quota / Throttle / Semaphore

---

## Step 6 产物沉淀 — 校验清单

### 6.0 产物路径一致性校验（重要）

所有产物**必须**输出到工作区根目录下的 `.qoder/architecture-analysis/` 目录，而非项目实际根目录。

**原因**：
- 工作区路径（`.qoder/`）由 Qoder 管控，Write 工具可稳定写入
- 项目实际路径可能含中文字符，导致写入失败或编码乱码
- 统一路径方便用户查找和管理

**校验**：Step 6 完成后，用 Bash 确认所有产物在同一目录下：
```powershell
Get-ChildItem -Path "<WORKSPACE_ROOT>\.qoder\architecture-analysis" | Select-Object Name, Length
```

如果发现产物散落在其他路径，立即用 Write 工具重新写入统一路径。

### 6.1 对照官方文档校验

| 校验项 | 方法 |
|--------|------|
| 架构模式是否一致 | 对比 ARCHITECTURE.md 中的描述 |
| 模块划分是否一致 | 对比官方架构图中的模块边界 |
| 依赖关系是否一致 | 对比官方模块依赖说明 |

### 6.2 随机验证

1. 选取一个未追踪的 API/功能
2. 快速走一遍链路（5分钟限制）
3. 确认分层逻辑是否通用
4. 如发现不一致，更新模块分层判定

### 6.3 循环依赖检测

检查内部依赖矩阵中是否存在：
- A → B → A（直接循环）
- A → B → C → A（间接循环）
- 不合理的跨层依赖（持久层调用接入层）

---

## 劣质项目专项策略 — 详细操作

### 从测试目录入手

1. 找 tests/ / test/ / __tests__/ / spec/ 目录
2. 读取测试文件名 → 推导被测功能模块
3. 读取测试用例 import → 推导内部调用链路
4. 读取测试 mock/stub → 推导外部依赖

### 关键字批量归类

全局搜索以下关键词，按出现频率归类：

```
高频搜索词：
- db / database / sql / query    → 持久层
- router / route / handler       → 接入层  
- service / business / logic     → 业务层
- config / setting / env         → 配置层
- middleware / filter / intercept → 横切层
- util / helper / common         → 工具层
- plugin / hook / extension      → 扩展层
```

### Commit 历史分析

1. 查看 git log 目录拆分历史
2. 找到项目初始 commit → 看最小架构
3. 找重大重构 commit → 看架构演进方向
4. 关注目录新增/删除 → 推导模块生命周期
