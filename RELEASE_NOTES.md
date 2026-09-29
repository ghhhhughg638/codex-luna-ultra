# v1.1.0 — Dependencies and tutorial / 依赖与完整教程

This release adds dependency checks and a complete bilingual installation guide. / 本版本新增依赖检查和完整双语安装教程。

## 中文

- 首次发布 Luna Ultra profile 与本地模型目录安装器。
- 提供中英双语的多智能体计划与决策前讨论规则。
- 安装器默认只预览；应用时只写入 `$CODEX_HOME` 下的 profile 和生成目录。强制更新前会创建权限受限的备份。
- 已在 Codex CLI 0.156.1 / Termux 上验证。
- `ultra` 是本地目录选项；根代理请求是否被服务商接受取决于 provider。子代理推理强度设为 `max`，实际并发仍受运行时槽位限制。

## English

- First release of the Luna Ultra profile and local model-catalog installer.
- Includes bilingual multi-agent deliberation guidance for plans and decisions.
- The installer previews by default. Applying it writes only the profile and generated catalog under `$CODEX_HOME`; forced updates create permission-restricted backups first.
- Validated with Codex CLI 0.156.1 on Termux.
- `ultra` is a local catalog option. Whether the provider accepts the root request depends on the configured provider. Subagent effort is `max`, while actual concurrency remains limited by runtime slots.
