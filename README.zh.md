# Pragmatic Skills Pack — 渐进暴露版

一个实用、按阶段路由、证据优先的 coding agent skills 包。

用户正常提出任务；agent 从入口 skill 开始，先判断是否命中明确的主动直达能力，否则再 triage、选择一个主模式，并在对应阶段触发辅助 skill。用户不需要主动调用任何具体 skill。

## 用户契约

用户不需要知道内部 skill 名字，也不需要说“调用 TDD / verification / strict-change”。

正常链路是：

```text
用户任务
  -> AGENTS.md
  -> skills/using-pragmatic-skills/SKILL.md
  -> 明确的任务后 PSP 复盘？直接进入 workflow-retrospective
  -> 否则进入 skills/triage/SKILL.md
  -> 一个主模式 skill
  -> 当前阶段触发时再加载辅助 skill
```

除非用户正在设计、调试或评估这套 workflow，否则 agent 不应该问用户该用哪个 skill 或 mode。

## 一个命令安装 / 升级

从目标项目里执行：

```bash
sh /path/to/pragmatic-skills-pack/install.sh
```

或者显式指定目标项目：

```bash
sh /path/to/pragmatic-skills-pack/install.sh --target /path/to/repo
```

同一个命令可以重复执行：没有安装时会安装，已有 PSP 时会按安全策略升级。

校验解压后的包：

```bash
sh /path/to/pragmatic-skills-pack/install.sh --check
```

校验已安装项目：

```bash
sh /path/to/pragmatic-skills-pack/install.sh --verify --target /path/to/repo
```

安装后，目标项目里也会有：

```bash
python3 .psp/bin/psp.py verify --target .
```

`install.sh` 是公开入口；底层实现是无依赖的 `tools/psp.py`。

## 使用 agent 安装

也可以直接让 agent 安装。把解压后的包给 agent，然后说：

```text
请把 Pragmatic Skills Pack 安装到当前仓库。优先使用包里的 install.sh，安装后运行校验。保留 AGENTS.md 里 PSP 托管块之外的已有内容；如果有冲突，报告 .psp/conflicts/ 路径，不要静默覆盖。
```

agent 安装细则见 `AGENT-INSTALL.md` 和 `reference/AGENT-INSTALL.md`。

## 升级策略

升级安全优先：

- `AGENTS.md` 只更新 `<!-- PSP:BEGIN -->` 到 `<!-- PSP:END -->` 的托管块，不覆盖项目自己的说明。
- PSP 管理的 `skills/` 和 `reference/` 文件会记录 hash 到 `.psp/install.json`。
- 升级时只覆盖“上次安装后没被改过”的 PSP 文件。
- 用户改过的文件不会被覆盖，会生成 `.psp/conflicts/<timestamp>/REPORT.md` 和 `.new` 候选文件。
- 被替换的旧文件会备份到 `.psp/backups/<timestamp>/`。
- 不会覆盖项目自己的 README。
- 只有显式传 `--force` 才会覆盖冲突文件，而且覆盖前仍会备份。

详细说明见 `reference/INSTALL-UPGRADE.md`。

## 核心思路

```text
AGENTS.md
  -> using-pragmatic-skills
       -> triage
            -> 只打开一个主模式 skill
                 -> 需求/设计阶段命中时加载 requirements-and-design
                 -> 其他辅助 skill 仍按阶段触发
```

这样小改动不会加载完整工程规范，大改动又不会跳过测试、计划、审查和证据。


## 头脑风暴、需求确认与设计收敛

PSP 新增 `skills/requirements-and-design/SKILL.md`，负责实现前的头脑风暴、需求澄清、验收标准、方案比较与确认。

- 用户正常表达“先讨论方案、梳理需求、确认验收标准”等意图，不需要说 skill 名。
- 仍然先经过 triage：只讨论时进入 Exploration；需要实现时进入 Standard 或 Strict；然后由 mode 在需求阶段自动加载。
- `exploration` 负责发现项目事实；`requirements-and-design` 负责决定目标行为、范围、非目标、验收标准和设计方向。
- 小而明确、低风险、规格完整的任务不会强制加载，避免仪式化。
- 先查项目证据，再问用户；一次只问一个真正会改变结果的问题。
- 只有低风险、可回滚、非公开接口/安全/数据语义的细节才允许使用明确记录的安全默认值。
- 最终确认状态固定为 `confirmed`、`conditionally confirmed`、`safe assumptions used` 或 `blocked on user decision`；最后一种状态下不能进入实现。
- 需求确认和安全审批是两个独立 gate。

产出的 Requirement Brief 会传给计划、TDD、验证、审查和交付。详细规则与 eval fixtures 见 `reference/REQUIREMENTS-AND-DESIGN.md`。

## 项目 AGENTS.md 生成与重构

PSP 现在包含 `skills/project-agents-md/SKILL.md`，专门维护当前项目自己的 `AGENTS.md`。

- 主动触发：用户要求创建、更新、迁移、优化或重构 AGENTS.md / agent instructions。
- 被动触发：agent 在项目发现阶段发现没有 AGENTS.md，或者只有 PSP 通用入口块、没有项目特定说明。
- 被动触发只能询问用户是否生成，不能静默写文件。
- PSP 托管块由安装器维护；项目自己的说明写在托管块之外。

## 主动触发的工作流复盘

PSP 新增 `skills/workflow-retrospective/SKILL.md`，用于在任务完成或形成稳定阶段后，基于真实证据复盘 PSP 本身并推动整套 skills 迭代。

- 只在用户明确提出“复盘这次流程、评估 skill 触发、改进 PSP、生成迭代项”等意图时触发。
- 普通任务结束时不会自动运行，也不会例行询问用户是否复盘。
- 只使用可观察证据，并区分 observed、inferred、not observed 和 unknown。
- 每个重要改进项都必须给出优先级、置信度、准确目标文件、回归风险和 eval fixture。
- 默认只分析、不修改文件；用户同时要求落地改进时，先完成复盘，再回到 triage 执行修改。
- 普通实现总结仍由 `handoff` 负责，避免两个 skill 重复。

用户明确要求归档时，可按 `psp.retrospective/v1` 写入 `.psp/retrospectives/`。细则见 `reference/WORKFLOW-RETROSPECTIVE.md`。

## 通用命令解析

通用包不再要求在 `AGENTS.md` 里固定填写：

```text
Install / Test / Lint / Typecheck / Build / Run locally
```

不同项目的命令应该从当前仓库里发现，而不是写死在模板里。

需要命令时会加载：

```text
skills/command-discovery/SKILL.md
```

它会按优先级查找：用户明确指令、项目文档、`.psp/project-profile.md`、`package.json` scripts、`Makefile`、`justfile`、`pyproject.toml`、`tox.ini`、`Cargo.toml`、`go.mod`、`pom.xml`、`build.gradle`、CI 配置等。找不到就必须说找不到，不能编造命令。

如果具体项目想固定命令，可以复制 `reference/PROJECT-PROFILE.template.md` 到 `.psp/project-profile.md`，或者安装时加 `--profile`。

## 机器可读 metadata

每个 `SKILL.md` 顶部都有 YAML frontmatter，例如：

```yaml
schema: psp.skill/v1
name: standard-change
kind: mode
version: 1.8.0
summary: ...
triggers: [...]
loads: ...
activation: ...
outputs: [...]
```

同时有：

```text
skills/MANIFEST.json
```

工具或 agent 可以先读 manifest / frontmatter 做路由，再按需打开具体 skill 正文。

## v1.8 改动

- 新增 `skills/requirements-and-design/SKILL.md`，覆盖轻量头脑风暴、需求澄清、方案收敛、验收标准和确认状态。
- 明确拆分 `exploration`（发现事实）与 `requirements-and-design`（做需求/设计决策）。
- 给 Standard/Strict 增加按阶段触发的 requirements phase，同时保留 Fast Patch 的轻量路径。
- `writing-plans` 必须消费已确认的 Requirement Brief，存在关键未决策时不得进入实现计划。
- 将验收标准贯通到 TDD、verification、review 和 handoff。
- 新增一次一个关键问题、安全默认值边界、需求变更控制，以及 `reference/REQUIREMENTS-AND-DESIGN.md` 中的 10 个 eval fixtures。

当前版本：`1.8.0`。

## 多工具安装

PSP 现在是 shell-first，并支持 host adapter。

```bash
# 在目标仓库根目录执行
sh /path/to/pragmatic-skills-pack/install.sh

# 安装全部支持的 adapter
sh /path/to/pragmatic-skills-pack/install.sh --hosts all

# 只安装指定工具 adapter
sh /path/to/pragmatic-skills-pack/install.sh --hosts claude,codex,opencode
```

默认 `--hosts all` 会安装 `AGENTS.md`、`.agents/skills/using-pragmatic-skills` 原生入口，以及 Claude Code、OpenCode、Gemini CLI、GitHub Copilot、Cursor 等薄适配器。只想按现有项目文件检测时用 `--hosts auto`；只想装 canonical PSP、不放任何 host adapter 时用 `--no-host-adapters`。

原生 adapter 只是薄入口。真正的内部工作流仍然在 `skills/` 里，用户只需要正常提出任务。
