# Unreleased — Windows Codex desktop integration / Windows Codex 桌面版接入

## 中文

- 新增可选的 `--desktop` 安装模式，接入 Windows Codex 桌面版的全局模型目录。
- 安全合并 `model_catalog_json` 和 `features.multi_agent`，更新前备份已有配置、profile 和目录文件。
- 更新中英文依赖、教程和刷新说明，明确桌面版需要完全重启才能加载目录。

## English

- Adds an opt-in `--desktop` installation mode for the Windows Codex desktop app's global model catalog.
- Safely merges `model_catalog_json` and `features.multi_agent`, backing up existing config, profile, and catalog files before replacement.
- Updates the bilingual dependency, tutorial, and refresh documentation with the required full desktop restart.

## Capability boundary / 能力边界

`ultra` remains a local catalog option. Provider acceptance of root Ultra and actual parallel-agent capacity depend on the configured provider, account, and Codex runtime. This project does not include the model, provider credentials, or model-service entitlement.

# v1.2.0 — QA hardening and regression suite / 测试加固与回归套件

## 中文

- 增加 15 项 Python 标准库回归测试，覆盖目录补丁、畸形输入、备份唯一性和事务回滚。
- 修复畸形模型目录导致 traceback、快速重复强制更新备份重名、备份中途失败遗留文件等问题。
- 预检使用隔离 Codex home 且不转发 API 密钥环境变量；格式校验与安装器保持一致。
- 新增 Ultra 描述并保留目录中已有的服务商原生 Ultra 设置。
- 修正全局 AGENTS 教程的符号链接防护、依赖边界和平台说明。
- 已在 Codex CLI 0.156.1 / Python 3.14.6 / Termux 上验证。

## English

- Adds 15 standard-library regression tests for catalog patching, malformed inputs, unique backups, and transactional rollback.
- Fixes tracebacks on malformed catalogs, same-second forced-update backup collisions, and orphaned backups after preflight failures.
- Runs dependency probes in an isolated Codex home without forwarding API-key environment variables; catalog checks now match installer validation.
- Adds a truthful synthetic Ultra description while preserving provider-native Ultra metadata already present in a catalog.
- Hardens the global AGENTS tutorial against symlinks and clarifies provider and platform boundaries.
- Validated with Codex CLI 0.156.1, Python 3.14.6, and Termux.

## Capability boundary / 能力边界

`ultra` remains a local catalog option. Provider acceptance of root Ultra and actual parallel-agent capacity depend on the configured provider, account, and Codex runtime. This project does not include the model, provider credentials, or model-service entitlement.
