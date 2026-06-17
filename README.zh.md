# Pragmatic Skills Pack v1.2

一个面向 coding agent 的实用派、阶段路由、证据优先 skill pack。

用户只需要正常描述任务，不需要知道、选择或手动调用具体 skill。agent 从很薄的入口开始，经过 triage 选择一个主模式，再在执行到对应阶段时加载 support skill。

## 项目身份

```text
正式名：Pragmatic Skills Pack
简称：PSP
仓库名：pragmatic-skills
包 ID：pragmatic-skills-pack
Manifest ID：psp
版本：1.2.0
入口 skill：skills/using-pragmatic-skills/SKILL.md
```

## 核心思路

```text
AGENTS.md
  -> skills/using-pragmatic-skills/SKILL.md
       -> skills/triage/SKILL.md
            -> 只选择一个主模式：fast-patch | exploration | standard-change | strict-change
                 -> 当前阶段触发时再加载 support skill
```

这样小改动不会加载完整工程规范，大改动又不会跳过计划、测试、验证、审查和证据。

## 用户使用方式

用户不用说：

```text
请调用 tdd skill
请调用 review skill
请调用 command-discovery skill
请切到 strict-change
```

用户只要提出任务。agent 应该从入口 skill 开始，经过 triage 选择模式，再在执行到对应阶段时自动加载内部 support skill。

只有当用户在设计、调试、评估或修改这套 workflow 本身时，才需要讨论具体 skill 名称。

## 通用命令解析

通用包里不再写固定占位：

```text
Install / Test / Lint / Typecheck / Build / Run locally
```

原因是 PSP 应该能安装到任意项目。不同项目的命令应该从当前仓库里发现，而不是写死在模板里。

需要命令时会加载：

```text
skills/command-discovery/SKILL.md
```

它会按优先级查找：用户明确指令、项目文档、`package.json` scripts、`Makefile`、`justfile`、`pyproject.toml`、`tox.ini`、`Cargo.toml`、`go.mod`、`pom.xml`、`build.gradle`、CI 配置等。找不到就必须说找不到，不能编造命令。

安装命令和会修改依赖状态的命令不会因为存在就自动运行。

## 机器可读 metadata

每个 `SKILL.md` 顶部都有 YAML frontmatter，并包含 `routing` / `activation` 字段。例如：

```yaml
schema: psp.skill/v1
name: standard-change
kind: mode
version: 1.2.0
summary: ...
triggers: [...]
loads: ...
outputs: [...]
routing:
  user_exposed: false
  user_invocation_required: false
  activation: router-selected-mode
  invoked_by:
    - skills/triage/SKILL.md
  contract: Selected internally; users do not invoke this skill directly.
activation:
  automatic: true
  entrypoint: false
  user_direct: false
```

工具或 agent 可以先读 `skills/MANIFEST.json` / frontmatter 做路由，再按需打开具体 skill 正文。

## 安装

把 `AGENTS.md` 和 `skills/` 放到项目根目录：

```bash
cp -R pragmatic-skills-pack/AGENTS.md pragmatic-skills-pack/skills .
```

可选：如果想保留说明文档，也复制 `reference/`：

```bash
cp -R pragmatic-skills-pack/reference .
```

然后告诉 coding agent：

```text
Follow AGENTS.md. Use progressive skill loading. Do not preload all skills.
Route internally from the entry skill; do not ask the user which skill to invoke.
```

## 项目级定制

大多数项目只需要定制 `.psp/project-profile.md` 或 `AGENTS.md` 里的本地 section。

适合放进去的内容包括：精确 test/lint/typecheck/build 命令、generated files、禁止自动编辑的区域、项目特有 Strict Change 触发条件、依赖策略、部署/审批策略。

## v1.2 改动

- 项目正式改名为 Pragmatic Skills Pack。
- 入口 skill 改为 `skills/using-pragmatic-skills/SKILL.md`。
- 统一更新 manifest、README、TREE、user contract、schema example 和内部路径。
- 移除入口文件里残留的通用命令占位。
- 统一补强每个 skill 的机器可读 `activation` metadata。
