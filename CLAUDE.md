# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 当前仓库状态

- 当前项目根目录的主线代码是 **Bing 单来源图片下载器**。
- 仓库内还存在一个演进中的 worktree：`.worktrees/multi-source-downloader/`，里面是 **多来源版本**，已经拆分出 `image_downloader/` 包、来源模型、存储与集成测试。
- 处理任务前先确认自己所在目录，不要把根目录的单来源实现和 worktree 中的多来源实现混为一谈。

## 环境与执行约定

- 当前系统的 Python 使用 `uv` 进行管理。
- 涉及 Python 运行、依赖安装、测试执行时，优先使用 `uv`。
- 根目录目前没有 `pyproject.toml`；常用方式是直接用 `uv run --with requests python ...` 运行脚本或测试。

## 常用命令

### 运行主脚本

在项目根目录运行 Bing 单来源下载器：

```bash
uv run --with requests python "scripts/bing_image_downloader.py" "cat" --limit 10 --pages 3
```

更大下载量时，按 README 中的经验值优先增加 `--pages`：

```bash
uv run --with requests python "scripts/bing_image_downloader.py" "cat" --limit 50 --pages 5
uv run --with requests python "scripts/bing_image_downloader.py" "cat" --limit 100 --pages 10
```

### 运行测试

运行当前根目录全部现有单元测试：

```bash
uv run --with requests python -m unittest tests/test_bing_image_downloader.py
```

运行单个测试文件时也使用同一命令形式：

```bash
uv run --with requests python -m unittest tests/test_bing_image_downloader.py
```

如果要运行单个测试方法，可用 `unittest` 的点路径：

```bash
uv run --with requests python -m unittest tests.test_bing_image_downloader.TestBingImageDownloader.test_collect_image_urls_across_multiple_pages
```

### 冒烟验证

```bash
uv run --with requests python "scripts/bing_image_downloader.py" "cat" --limit 10 --pages 3
```

## 根目录代码架构

### 主脚本

- `scripts/bing_image_downloader.py`
  - 这是当前根目录的入口脚本。
  - 它把流程集中在一个文件里：
    1. 请求 Bing 图片搜索页
    2. 从 HTML 的 `m` 字段里提取 `murl`
    3. 跨页去重收集候选链接
    4. 逐个下载到 `downloads/<keyword>/`
    5. 跳过失败链接并继续尝试后续候选

关键函数分工：
- `extract_image_urls()`：从 Bing 结果页 HTML 中提取原图 URL。
- `collect_image_urls()`：按页抓取搜索结果，做候选池去重，并可按 `target_count` 提前停止。
- `download_images()`：顺序下载图片并按三位编号写入本地。
- `main()`：解析 CLI 参数，组织候选收集、下载重试和最终摘要输出。

### 测试结构

- `tests/test_bing_image_downloader.py`
  - 使用 `unittest` 和 `unittest.mock`。
  - 主要覆盖：
    - HTML 中图片链接提取
    - HTML entity 场景
    - 多页候选收集与去重
    - `target_count` 提前停止
    - 下载数量限制
    - 文件编号起始位置

测试通过 `sys.path.insert(...)` 直接把 `scripts/` 加入导入路径，因此当前根目录实现仍然是“脚本中心”的结构，而不是包结构。

## README 中体现的运行规律

来自 `README.md` 的关键约定：

- 输出目录固定为 `downloads/<关键词>/`。
- 当目标数量较大时，优先增加 `--pages`，而不是先改并发。
- 常见失败通常来自第三方源站不可访问，例如：`403`、SSL 错误、超时、`404`；这不一定表示脚本主流程崩溃。

## 多来源 worktree 的额外背景

如果任务是在 `.worktrees/multi-source-downloader/` 下进行，需要注意它与根目录不是同一套实现：

- 多来源版本不再只是单脚本，已经拆分为模块化结构。
- 该版本的主流程会做：
  - source registry / source 实例化
  - 多来源候选收集
  - 去重
  - 历史索引判重与跳过
  - 下载记录持久化
  - 运行摘要统计
- 该 worktree 下的测试也比根目录更完整，除了脚本测试外，还有：
  - `test_integration_multisource.py`
  - `test_models_and_sources.py`
  - `test_storage.py`

处理 bug、补文档或跑 eval 前，先确认任务对应的是根目录主线，还是 `.worktrees/multi-source-downloader/` 中的多来源版本。

## 仓库内已确认不存在的配置

以下文件在当前根目录下未发现：

- `.cursorrules`
- `.cursor/rules/**`
- `.github/copilot-instructions.md`
- `pyproject.toml`

因此当前开发信息主要以 `README.md`、脚本源码、测试文件和项目内 worktree 结构为准。
