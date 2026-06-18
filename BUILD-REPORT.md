# 构建与验收报告

- 产物：Pragmatic Skills Pack — Enhanced 2.0.1
- 版本：`2.0.1`
- 上游基线：`wyeye/pragmatic-skills@a07ef5a`
- 验收日期：`2026-06-18`
- 本地环境：Linux x86_64，Python `3.13.5`

## 2.0.1 修复范围

本修复版针对 2.0.0 复核中发现的关键缺陷进行了闭环修复：

1. 安装后写入自包含 `.psp/package.zip`，项目本地 CLI 的 `doctor`、`diff`、
   `verify-package`、重装和同版本 `upgrade` 不再依赖原解压目录或当前工作目录。
2. Manifest、Skill sidecar、宿主适配声明、Eval 案例、捕获结果和安装状态均执行
   真实 JSON Schema 实例验证，不再只检查 Schema 文件能否解析。
3. Trace 按声明类型校验证据语义；普通成功命令或文件查看不能证明测试、构建、
   审查或任务完成，通过验证也不能“洗白”不匹配的上游证据。
4. 托管区块安装、升级和卸载保留并恢复 UTF-8 BOM、CRLF/LF 换行、原始字节和
   权限模式。
5. 包校验会遍历所有已声明宿主适配资源；Trace 脱敏覆盖 DSN、连接串及 URL 内嵌
   凭据。
6. GitHub Actions 第三方步骤固定到完整提交 SHA，避免可移动大版本标签。

## 本地验收结果

| 检查 | 结果 |
|---|---|
| Skill Manifest 漂移检查 | 通过 |
| 包结构与 Schema 实例校验 | 通过：19 个 Skill，16 个 Eval 案例，全部宿主适配资源存在 |
| Python 测试套件 | 通过：58/58 |
| 结构化 Eval 自测 | 通过：16/16，最低合成得分 100 |
| JSONL Trace 评分器固定夹具 | 通过：16/16，平均分 100 |
| 全宿主适配器安装 smoke test | 通过：83 项变更、0 冲突，覆盖 8 个宿主标签 |
| 安装后完整性 | 通过：79 个托管文件、4 个托管区块 |
| 安装后本地 CLI | 通过：从任意工作目录运行 `verify/status/doctor/diff/verify-package/upgrade` |
| 幂等升级 | 通过：`diff`、dry-run upgrade、实际同版本 upgrade 均为 0 项变更 |
| 用户文件精确保真 | 通过：CRLF/LF、UTF-8 BOM、原始字节和 `0600` 权限可恢复 |
| 路径与事务安全 | 通过：路径穿越、恶意 state、符号链接逃逸、嵌入包篡改、冲突和回滚测试 |
| Trace CLI smoke test | 通过：6 个事件，声明专用证据链校验无错误 |
| Trace 脱敏 | 通过：测试 DSN/连接串中的凭据落盘为 `[REDACTED]` |
| 配置与文本校验 | 通过：49 个 JSON、9 个 YAML、185 个 UTF-8 文件；无符号链接 |
| CI 供应链引用 | 通过：所有第三方 GitHub Actions 均固定到 40 位提交 SHA |
| 确定性 ZIP | 通过：重复构建 SHA-256 一致，并执行 ZIP 完整性、解压后包校验和安装验证 |

## 覆盖重点

- 托管区块插入、替换、移除、重复标记拒绝及精确字节恢复；
- 首次安装、幂等升级、dry-run、冲突报告、显式强制恢复、卸载和回滚；
- 安装态自包含生命周期包及从任意工作目录运行本地 CLI；
- 绝对路径、路径穿越、恶意 state 路径、ZIP 路径和符号链接逃逸；
- 标准 Frontmatter、sidecar、Manifest 图可达性、Schema 实例和版本一致性；
- 所有声明宿主适配资源完整性；
- Trace 事件唯一性、证据先后、声明专用证据、验证上游证据、审批撤销/过期和验证过期；
- DSN、连接串、带凭据 URL、令牌及私钥模式脱敏；
- Eval 案例合法性、known-good 回放、负向证据案例和 JSON/Markdown/HTML 报告；
- ZIP 可重复构建、SHA-256 生成、解压后包级验证及从解压包安装。

## 不能据此推导的结论

1. 16/16 是评测框架固定夹具自测，不是真实宿主或模型基准。
2. 本地只实际运行了 Linux/Python 3.13.5；仓库配置了 Linux、macOS、Windows 与
   Python 3.9/3.11/3.13 的 CI 矩阵，但本报告不声称远程任务已经运行。
3. `compat/hosts.yaml` 只描述安装路径成熟度；在补充真实宿主版本、模型和原始
   Trace 前，不宣称跨宿主行为已被证明。
4. 上游快照没有仓库级许可证。本包按混合来源标注，仅适合私有工程评估；公开
   再分发前必须确认上游授权和最终许可条款。
5. Trace 校验验证记录的结构与内部一致性，不证明外部命令输出或远程系统绝对真实。
6. Prompt 工作流不能替代沙箱、最小权限、分支保护、人工代码审查、密钥管理和
   生产变更制度。

详细安装、Trace、Eval、回滚和许可说明见 `README.zh.md`、`reference/`、
`LICENSE` 与 `SOURCE-BASELINE.md`。
