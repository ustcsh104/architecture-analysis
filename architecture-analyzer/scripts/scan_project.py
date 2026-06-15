#!/usr/bin/env python3
"""
项目结构扫描辅助脚本
自动收集项目基本信息，辅助架构分析 Step 1 和 Step 2

用法：
    python scan_project.py <项目根目录路径>

输出：
    JSON 格式的项目信息摘要，包含：
    - 目录结构树
    - 配置文件清单
    - 依赖文件内容摘要
    - 入口文件定位
    - 语言识别
"""

import json
import os
import re
import sys
from pathlib import Path


# ============================================================
# 配置常量
# ============================================================

CONFIG_FILES = {
    # Docker / 部署
    "Dockerfile": "docker",
    "docker-compose.yml": "docker",
    "docker-compose.yaml": "docker",
    "docker-compose.override.yml": "docker",
    # 构建
    "Makefile": "build",
    "justfile": "build",
    "pom.xml": "build_java",
    "build.gradle": "build_java",
    "build.gradle.kts": "build_java",
    "package.json": "build_node",
    "tsconfig.json": "build_node",
    "setup.py": "build_python",
    "setup.cfg": "build_python",
    "pyproject.toml": "build_python",
    "requirements.txt": "build_python",
    "Pipfile": "build_python",
    "go.mod": "build_go",
    "Cargo.toml": "build_rust",
    "CMakeLists.txt": "build_c",
    # 配置
    ".env": "config",
    ".env.example": "config",
    "config.yaml": "config",
    "config.yml": "config",
    "config.json": "config",
    "application.properties": "config",
    "application.yml": "config",
    # CI/CD
    ".github/workflows": "cicd",
    "Jenkinsfile": "cicd",
    ".travis.yml": "cicd",
    ".gitlab-ci.yml": "cicd",
}

DIR_TYPE_MARKS = {
    "src": "[源码]",
    "lib": "[源码]",
    "app": "[源码]",
    "cmd": "[源码]",
    "internal": "[源码]",
    "pkg": "[源码]",
    "main": "[源码]",
    "core": "[源码]",
    "tests": "[测试]",
    "test": "[测试]",
    "spec": "[测试]",
    "__tests__": "[测试]",
    "docs": "[文档]",
    "doc": "[文档]",
    "examples": "[文档]",
    "scripts": "[脚本]",
    "hack": "[脚本]",
    "bin": "[脚本]",
    "deploy": "[部署]",
    "k8s": "[部署]",
    "docker": "[部署]",
    "infra": "[部署]",
    "web": "[前端]",
    "frontend": "[前端]",
    "ui": "[前端]",
    "client": "[前端]",
    "public": "[前端]",
    "static": "[前端]",
    "common": "[公共]",
    "shared": "[公共]",
    "utils": "[公共]",
    "config": "[配置]",
    "configs": "[配置]",
    "conf": "[配置]",
    "migrations": "[数据库]",
    "db": "[数据库]",
    "seeds": "[数据库]",
}

ENTRY_PATTERNS = {
    "python": [
        r"def\s+main\s*\(",
        r"app\.run\s*\(",
        r"if\s+__name__\s*==\s*['\"]__main__['\"]",
        r"@app\.route",
        r"flask\.run",
    ],
    "java": [
        r"@SpringBootApplication",
        r"public\s+static\s+void\s+main",
        r"public\s+class\s+Main",
    ],
    "go": [
        r"func\s+main\s*\(",
        r"http\.ListenAndServe",
        r"grpc\.NewServer",
    ],
    "node": [
        r"app\.listen\s*\(",
        r"module\.exports",
        r"export\s+default",
        r"createServer\s*\(",
    ],
    "rust": [
        r"fn\s+main\s*\(",
        r"actix_web::HttpServer",
        r"warp::serve",
    ],
}

LANG_BY_FILE = {
    "pom.xml": "java",
    "build.gradle": "java",
    "build.gradle.kts": "java",
    "package.json": "node",
    "tsconfig.json": "node",
    "setup.py": "python",
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "Pipfile": "python",
    "go.mod": "go",
    "Cargo.toml": "rust",
    "CMakeLists.txt": "c/c++",
}


# ============================================================
# 扫描函数
# ============================================================


def detect_languages(root: Path) -> list:
    """通过配置文件和源码文件扩展名检测项目语言"""
    langs = set()
    for fname, lang in LANG_BY_FILE.items():
        if (root / fname).exists():
            langs.add(lang)
    # 源码文件扩展名统计
    ext_counts = {}
    for f in root.rglob("*"):
        if f.is_file() and not f.name.startswith("."):
            ext = f.suffix.lower()
            if ext in (".py", ".java", ".go", ".js", ".ts", ".rs", ".c", ".cpp", ".jsx", ".tsx", ".rb", ".php"):
                ext_counts[ext] = ext_counts.get(ext, 0) + 1
    ext_lang = {
        ".py": "python", ".java": "java", ".go": "go",
        ".js": "javascript", ".ts": "typescript", ".rs": "rust",
        ".c": "c", ".cpp": "c++", ".jsx": "javascript",
        ".tsx": "typescript", ".rb": "ruby", ".php": "php",
    }
    for ext, count in sorted(ext_counts.items(), key=lambda x: -x[1]):
        if ext in ext_lang:
            langs.add(ext_lang[ext])
    return sorted(langs)


def scan_config_files(root: Path) -> dict:
    """扫描根目录配置文件"""
    configs = {}
    for fname, category in CONFIG_FILES.items():
        fpath = root / fname
        if fname == ".github/workflows":
            wf_dir = root / ".github" / "workflows"
            if wf_dir.exists():
                configs[str(wf_dir.relative_to(root))] = {
                    "category": category,
                    "exists": True,
                    "files": [f.name for f in wf_dir.iterdir() if f.is_file()],
                }
        elif fpath.exists():
            configs[fname] = {"category": category, "exists": True}
    return configs


def build_dir_tree(root: Path, max_depth: int = 3) -> dict:
    """构建带类型标记的目录树"""
    tree = {}
    for item in sorted(root.iterdir()):
        if item.name.startswith(".") or item.name in ("node_modules", "__pycache__", ".git"):
            continue
        if item.is_dir():
            mark = DIR_TYPE_MARKS.get(item.name, "[其他]")
            sub = {}
            if max_depth > 1:
                sub = build_dir_tree(item, max_depth - 1)
            tree[f"{item.name} {mark}"] = sub
        else:
            tree[item.name] = None
    return tree


def find_entry_files(root: Path, langs: list) -> dict:
    """定位程序入口文件"""
    entries = {}
    for lang in langs:
        lang_key = lang.split("/")[0].split("+")[0]
        if lang_key not in ENTRY_PATTERNS:
            continue
        patterns = ENTRY_PATTERNS[lang_key]
        for pattern in patterns:
            for fpath in root.rglob("*"):
                if not fpath.is_file():
                    continue
                ext_map = {
                    "python": ".py", "java": ".java", "go": ".go",
                    "node": ".js", "javascript": ".js", "rust": ".rs",
                }
                expected_ext = ext_map.get(lang_key)
                if expected_ext and fpath.suffix != expected_ext:
                    continue
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    if re.search(pattern, content):
                        rel = str(fpath.relative_to(root))
                        entries.setdefault(lang_key, []).append({
                            "file": rel,
                            "pattern": pattern,
                        })
                except Exception:
                    pass
    return entries


def read_dependency_summary(root: Path, langs: list) -> dict:
    """读取依赖文件摘要"""
    deps = {}
    dep_files = {
        "python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
        "java": ["pom.xml", "build.gradle"],
        "node": ["package.json"],
        "go": ["go.mod"],
        "rust": ["Cargo.toml"],
    }
    for lang in langs:
        lang_key = lang.split("/")[0].split("+")[0]
        for fname in dep_files.get(lang_key, []):
            fpath = root / fname
            if fpath.exists():
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    deps[fname] = content[:2000]  # 最多取前2000字符
                except Exception:
                    deps[fname] = "(读取失败)"
    return deps


def main():
    if len(sys.argv) < 2:
        print("用法: python scan_project.py <项目根目录路径>")
        sys.exit(1)

    root = Path(sys.argv[1])
    if not root.exists() or not root.is_dir():
        print(f"错误: {root} 不是有效的目录")
        sys.exit(1)

    # Windows 中文路径编码容错：确保 stdout 使用 UTF-8
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print(f"正在扫描项目: {root}")
    print("=" * 60)

    langs = detect_languages(root)
    print(f"\n[语言识别] 检测到的语言: {', '.join(langs)}")

    configs = scan_config_files(root)
    print(f"\n[配置文件] 发现 {len(configs)} 个配置文件:")
    for name, info in configs.items():
        print(f"  - {name} ({info['category']})")

    tree = build_dir_tree(root, max_depth=3)
    print(f"\n[目录结构] 一级目录概览:")
    for name, sub in tree.items():
        if sub is not None:
            sub_count = len(sub)
            print(f"  - {name} ({sub_count} 项)")
        else:
            print(f"  - {name} (文件)")

    entries = find_entry_files(root, langs)
    print(f"\n[入口文件] 发现的入口点:")
    for lang, findings in entries.items():
        print(f"  [{lang}]")
        for item in findings:
            print(f"    - {item['file']} (匹配: {item['pattern']})")

    deps = read_dependency_summary(root, langs)
    print(f"\n[依赖摘要] 读取了 {len(deps)} 个依赖文件")
    for name, content in deps.items():
        print(f"  - {name} ({len(content)} 字符)")

    # 保存完整 JSON 结果
    # 输出路径统一到工作区的 .qoder/architecture-analysis/ 目录
    # 如果脚本在工作区根目录执行，输出到 .qoder/architecture-analysis/scan-result.json
    # 如果脚本在项目实际根目录执行，输出到 .qoder/architecture-analysis/scan-result.json
    result = {
        "project_root": str(root),
        "languages": langs,
        "config_files": configs,
        "directory_tree": tree,
        "entry_files": entries,
        "dependency_summary": deps,
    }

    output_path = root / ".qoder" / "architecture-analysis" / "scan-result.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n完整结果已保存到: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
