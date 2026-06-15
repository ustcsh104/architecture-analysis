# system-design-primer 目录职责清单

> 生成日期：2026-06-15
> 文档规范度：B 级（单 README + 架构图 + 解答代码说明，缺失独立 ARCHITECTURE.md）

---

## 一级目录概览

| 目录 | 类型标记 | 职责 | 关键文件数 |
|------|----------|------|-----------|
| images/ | 🟡展示层 | README 引用图片，36 张架构图/示例图 | 36 |
| resources/ | 🔵资源层 | 辅助学习资源：Anki 卡组 + 学习导图 | 5 |
| solutions/system_design/ | 🟢业务层 | 系统设计面试解答，8 个完整案例 | ~60 |
| solutions/object_oriented_design/ | 🟢业务层 | OOP 设计面试解答，6 个完整案例 | 18 |
| .github/ | ⚪配置层 | GitHub PR 模板 | 1 |
| architecture-analysis/ | 🟣扩展层 | 架构分析产物（本次生成） | 4 |

---

## 详细目录说明

### README.md — 🟢业务/知识层
- **职责**：项目主入口知识库，约 1800 行，涵盖全部系统设计面试核心知识点
- **包含文件**：
  - `README.md` — 英文主文档（最完整版）
  - `README-zh-Hans.md` — 中文简体翻译版
  - `README-zh-TW.md` — 中文繁体版
  - `README-ja.md` — 日文版
- **知识块**：系统设计基础 → 基础设施层 → 数据库 → 缓存 → 异步 → 通信 → 安全 → 登录

### images/ — 🟡展示层
- **职责**：README 文档引用的架构图、示例图，Markdown 图片链接指向此目录
- **无承载逻辑**，纯静态资源
- **删除影响**：README 中图片链接全部失效

### resources/ — 🔵资源/辅助层
- **职责**：辅助学习材料
- **包含文件**：
  - `flash_cards/System Design.apkg` — 系统设计核心的 Anki 卡组
  - `flash_cards/System Design Exercises.apkg` — 系统设计练习卡组
  - `flash_cards/OO Design.apkg` — OOP 设计卡组
  - `study_guide.png` — 学习导图
  - `study_guide.graffle` — 学习导图源文件（macOS 专用）

### solutions/system_design/ — 🟢业务层（系统设计解答）
- **职责**：8 个系统设计面试案例解答，每题独立目录
- **子模块**：
  - `pastebin/` — 粘贴服务设计（键值存储）
  - `twitter/` — Twitter 时间线设计（高并发）
  - `web_crawler/` — 网页爬虫设计（分布式）
  - `mint/` — 个人理财系统设计（中间件）
  - `social_graph/` — 社交图谱数据结构设计（图存储）
  - `query_cache/` — 查询缓存 KV 存储设计（缓存）
  - `sales_rank/` — Amazon 销量排名设计（排序）
  - `scaling_aws/` — AWS 扩展用户设计（实战型）
  - `template/` — 架构图模板（贡献者专用）
- **每个子目录典型包含**：README.md（英文）+ README-zh-Hans.md（中文）+ __init__.py + .py 代码片段 + .graffle 架构图源文件 + .png 架构图 + *_basic.graffle/png 基础架构图

### solutions/object_oriented_design/ — 🟢业务层（OOP 解答）
- **职责**：6 个 OOP 设计面试案例解答，代码驱动
- **子模块**：
  - `hash_table/` — HashMap 实现
  - `lru_cache/` — LRU 缓存实现
  - `call_center/` — 呼叫中心模拟
  - `deck_of_cards/` — 扑克牌设计
  - `parking_lot/` — 停车场设计
  - `online_chat/` — 在线聊天服务
- **每个子目录典型包含**：__init__.py + .py 主代码 + .ipynb Jupyter 笔记本

### 根目录配置文件 — ⚪配置层
- `.gitignore` — Git 忽略规则
- `.gitattributes` — Git 属性配置
- `CONTRIBUTING.md` — 贡献指南
- `TRANSLATIONS.md` — 翻译说明
- `LICENSE.txt` — CC BY 4.0 开源许可证
- `epub-metadata.yaml` — EPUB 电子书元数据
- `generate-epub.sh` — EPUB 生成脚本
