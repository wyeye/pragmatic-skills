# Pragmatic Skills Pack — 增强版 2.0.2

一个面向 Coding Agent 的阶段路由、证据优先工作流包，并配套安全安装器、
可审计本地 Trace、确定性工作流 Eval 和发布检查。

本压缩包是用于**私有工程评估**的增强派生版本，基于
`SOURCE-BASELINE.md` 记录的上游快照制作，不是上游官方发布。公开分发前请先
阅读 `LICENSE`。

## 它解决什么问题

PSP 只向 Agent 暴露一个入口，然后在内部完成任务分流：

```text
using-pragmatic-skills
  -> triage
    -> fast-patch | exploration | standard-change | strict-change
      -> 按阶段加载支持 Skill
         需求、计划、TDD、安全审批、验证、审查、交付
```

目标是让小改动保持轻量，同时在范围、歧义或风险增加时，逐步增强计划、审批、
证据和验证要求。

## 增强版 2.0.2 的主要补强

- **跨系统行为建模：**针对平台、本地、设备、客户端/H5、同步及查询可见性等多入口状态变更，被动生成基于证据的行为/状态矩阵；对规格完整的本地单路径任务保持负向边界，不误触发。
- **跨系统行为建模：**当删除、同步、对账、生命周期或可见性语义跨越多个入口或状态权威时，需求阶段自动生成行为/状态矩阵，并把每个变更行贯通到计划、测试、验证和审查。
- **事务化安装器：**路径边界校验、符号链接拒绝、操作锁、staging、原子替换、
  备份、冲突报告、回滚、卸载、doctor、diff、dry-run 和 JSON 输出。
- **可移植 Skill 元数据：**标准 `SKILL.md` frontmatter，外加机器可读
  `psp.skill.json` sidecar 和自动生成的依赖 Manifest。
- **证据 Trace：**可选 JSONL 追加日志、扩展凭据脱敏、声明类型与证据语义
  匹配、带范围/有效期的审批校验，以及“修改后验证失效”检测。
- **可执行 Eval：**18 个确定性案例，覆盖路由、安全、证据、修改范围、重新分流
  和负向控制。
- **发布工程：**单元、集成、对抗、Trace、Eval、打包及 CI 检查；Python 工具
  仅使用标准库，GitHub Actions 均固定到不可变的完整提交 SHA。

## 环境要求

- Python 3.9 或更高版本
- 对目标项目有创建 `.psp/`、Skill 文件及所选宿主适配文件的权限

不需要安装第三方 Python 依赖。

## 安装

在解压后的目录执行：

```sh
sh install.sh --target /path/to/your/repository
```

Windows 下可直接调用 Python 入口：

```powershell
py -3 tools\psp.py install --target C:\path\to\repository
```

宿主选择默认为 `auto`：安装器会安装通用 `agents` 入口，并根据目标项目标记追加相关宿主适配器。也可显式覆盖：

```sh
sh install.sh --target /path/to/repository --hosts all
sh install.sh --target /path/to/repository --hosts minimal
sh install.sh --target /path/to/repository --hosts none
sh install.sh --target /path/to/repository --hosts agents,claude,opencode
```

常用安全选项：

```sh
# 展示完整计划，但不写文件
sh install.sh --target /path/to/repository --dry-run --json

# 目标不存在项目画像时安装模板
sh install.sh --target /path/to/repository --profile

# 仅在检查过备份和变更计划后，显式覆盖被修改的托管文件
sh install.sh --target /path/to/repository --force
```

安装状态保存在 `.psp/install.json`。安装器会保留 PSP 托管区块以外的用户内容；
除非显式使用 `--force`，否则不会覆盖被用户修改的托管文件。对新插入的托管区块，
安装器会保留原文件的 UTF-8 BOM、换行风格和权限模式，并在卸载时恢复精确原始字节。
许可与来源说明会安装到 `.psp/legal/`，确保被托管的 Skill 副本仍携带来源上下文。

## 管理已安装项目

项目本地 CLI 位于 `.psp/bin/psp.py`。安装时还会生成确定性的自包含生命周期包
`.psp/package.zip`，因此 `doctor`、`diff`、`verify-package`、重装和同版本
`upgrade` 不依赖调用时所在目录，也不依赖最初解压的压缩包：

```sh
python3 .psp/bin/psp.py verify --target .
python3 .psp/bin/psp.py status --target .
python3 .psp/bin/psp.py doctor --target .
```

使用项目内嵌包比较或重新应用当前版本：

```sh
python3 .psp/bin/psp.py diff --target .
python3 .psp/bin/psp.py upgrade --target . --dry-run
python3 .psp/bin/psp.py upgrade --target .
```

升级到更新的解压包时，可运行新包中的 CLI，或通过 `--package-root` 指定新包目录。 嵌入归档会按安装状态校验哈希，并限制条目数、展开大小、路径、重复项和符号链接。

安全卸载或恢复事务快照：

```sh
python3 .psp/bin/psp.py uninstall --target . --dry-run
python3 .psp/bin/psp.py uninstall --target .

python3 .psp/bin/psp.py rollback --target . --list
python3 .psp/bin/psp.py rollback --target .
python3 .psp/bin/psp.py rollback --target . --to <完整备份ID>
```

回滚会恢复某次操作前的精确快照，并在恢复前先为当前状态创建安全快照。

## 可选执行 Trace

Trace 是保存在 `.psp/runs/<run-id>/events.jsonl` 的本地追加记录。正常使用 Skill
并不依赖它，但它能让完成声明、审批和验证更容易审计。

```sh
python3 .psp/bin/psp.py trace start \
  --target . \
  --metadata '{"task":"修复解析器校验"}'

python3 .psp/bin/psp.py trace emit mode_selected \
  --target . \
  --data '{"mode":"standard-change"}'

python3 .psp/bin/psp.py trace emit command_finished \
  --target . \
  --event-id cmd-tests \
  --data '{"command":"pytest -q","exit_code":0,"purpose":"tests","evidence_id":"tests-ok"}'

python3 .psp/bin/psp.py trace emit verification_finished \
  --target . \
  --event-id verify-tests \
  --data '{"status":"passed","scope":"tests","evidence":["tests-ok"],"evidence_id":"verified-tests"}'

python3 .psp/bin/psp.py trace emit claim \
  --target . \
  --data '{"claim":"tests_passed","evidence":["verified-tests"]}'

python3 .psp/bin/psp.py trace finish --target . --status completed
python3 .psp/bin/psp.py trace verify --target .
```

`trace verify` 会拒绝重复事件 ID、引用不存在或未来证据的声明、没有成功上游证据
的通过验证、声明与证据类型不匹配、缺少先前匹配且未过期审批的高风险动作，以及在
文件再次变化后已经失效的验证。普通成功命令或文件查看不能再冒充测试、构建通过。
敏感键、带凭据 URL、DSN 和连接串会在落盘前脱敏，但 Trace 仍应视作敏感运维记录。

## 行为 Eval

校验案例定义和确定性评分器：

```sh
python3 tools/psp.py eval validate --target .
python3 tools/psp.py eval self-test --target .
python3 tools/eval_runner.py --self-test --output-dir build/eval --summary
```

评分真实宿主运行记录：

```sh
python3 tools/eval_runner.py \
  --trace-dir path/to/captured-traces \
  --output-dir build/eval
```

Self-test 只能证明案例、合成通过样本和评分器彼此一致，**不能**证明真实模型或宿主
通过了工作流。真正的兼容性结论必须记录宿主、版本、模型、日期、案例集和原始运行
Trace。

## Skill 元数据模型

每个 `SKILL.md` 只保留可移植的顶层字段：

```yaml
---
name: standard-change
description: Execute a bounded repository change through planning, implementation, verification, and handoff.
license: Mixed-origin; see repository LICENSE
compatibility: Agent Skills-compatible host or a PSP adapter.
metadata:
  psp-schema: psp.skill/v2
  psp-kind: mode
  psp-version: 2.0.2
---
```

PSP 自有的路由图数据放在相邻的 `psp.skill.json` 中。自动生成的
`skills/MANIFEST.json` 记录文件哈希，并校验单一入口、引用存在和所有 Skill 可达。

## 开发与验证本增强包

```sh
make check
make test
make eval
make package
```

对应的直接命令：

```sh
python3 -m compileall -q tools
python3 tools/build_manifest.py --check
python3 tools/psp.py verify-package --target .
python3 -m unittest discover -s tests -v
python3 tools/psp.py eval validate --target .
python3 tools/psp.py eval self-test --target .
python3 tools/eval_runner.py --self-test --summary
```

`verify-package` 检查目录结构、声明的适配器资源、Manifest、JSON Schema 实例、
sidecar、捕获结果结构和 Eval 案例语法。它是包完整性检查，不是 Agent 行为已经可靠
的证明。

## 目录结构

```text
skills/       核心工作流 Skill 与 sidecar
adapters/     宿主发现入口适配器
reference/    运维与工作流文档
schemas/      Trace、Eval、Manifest、sidecar、安装状态 Schema
evals/        可执行案例、fixture、runner 和确定性评分器
tools/        安装、Trace、Eval、Manifest、发布 CLI
tests/        单元、集成、对抗、Trace、Eval 和打包测试
.github/      CI 与贡献模板
```

## 已知边界

- 除非宿主提供运行时强制 API，否则路由本质上仍由模型按提示词执行。
- 不同模型和宿主版本对同一 Skill 的遵循行为可能不同。
- 安装完整性检查不能证明 Agent 真正遵循了工作流。
- Trace 可以增强审计，但不能独立证明所有外部命令或环境事实都真实。
- 在发布真实宿主运行结果前，`compat/hosts.yaml` 中的兼容标签保持保守。

## 许可与来源

本包属于混合来源。被审查的上游快照没有仓库级许可证，因此本增强包**不会**把
上游派生材料重新许可。新编写增强内容仅在贡献者确实拥有许可权的范围内按
Apache-2.0 提供。详见 `LICENSE`、`LICENSE-APACHE-2.0`、`NOTICE` 和
`SOURCE-BASELINE.md`。
