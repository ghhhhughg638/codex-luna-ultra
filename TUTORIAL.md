# Codex Luna Ultra tutorial / Codex Luna Ultra 完整教程

This guide is intentionally bilingual. It installs the local profile and catalog patch while preserving the user's existing Codex configuration.

本教程中英双语，安装本地 profile 和目录补丁，同时保留用户已有 Codex 配置。

## 1. Prerequisites / 前置依赖

Install or configure Codex CLI first. The account/provider must already have access to GPT-6-Luna. The repository cannot provide a model, account, provider, or login.

先安装并配置 Codex CLI。账号和服务商必须已经有 GPT-6-Luna 访问权。本仓库不会提供模型、账号、服务商或登录凭据。

Run the dependency check:

运行依赖检查：

```sh
python3 scripts/check_dependencies.py
```

The check requires Python 3.9+, `codex` on `PATH`, `codex debug models`, and a Luna v2 catalog entry. There are no third-party Python dependencies.

检查要求 Python 3.9+、`PATH` 中有 `codex`、支持 `codex debug models`，且目录中存在 Luna v2 条目。不需要第三方 Python 依赖。

## 2. Download / 下载

```sh
git clone https://github.com/ghhhhughg638/codex-luna-ultra.git
cd codex-luna-ultra
```

没有 Git 时也可以下载 GitHub ZIP 后进入解压目录。

## 3. Preview, then install / 先预览再安装

Preview never writes the Codex home:

预览不会写入 Codex home：

```sh
python3 scripts/install.py
```

Apply to the default `$CODEX_HOME` (usually `~/.codex`):

写入默认 `$CODEX_HOME`（通常是 `~/.codex`）：

```sh
python3 scripts/install.py --apply
```

Use an explicit absolute Codex home when needed:

需要时指定绝对 Codex home：

```sh
python3 scripts/install.py --apply --code-home /absolute/path/to/.codex
```

The installer creates only `luna-ultra-models.json` and `luna-ultra.config.toml`, mode `0600`. It obtains the current catalog in an isolated temporary home, adds Luna Ultra, and does not copy credentials or edit the base config.

安装器只创建权限 `0600` 的 `luna-ultra-models.json` 和 `luna-ultra.config.toml`。它在隔离临时 home 中获取当前目录、添加 Luna Ultra，不会复制凭据或修改基础配置。

If the targets already exist, preview first and then use `--force` to update. Backups are created before replacement:

如果目标文件已存在，先预览，再用 `--force` 更新；替换前会先创建备份：

```sh
python3 scripts/install.py
python3 scripts/install.py --apply --force
```

## 4. Start and verify / 启动和验证

Restart Codex, then start the profile:

重启 Codex，然后启动 profile：

```sh
codex -p luna-ultra
```

In More Reasoning, Luna should list `ultra` after the generated catalog loads. A non-network profile check is:

生成目录加载后，在 More Reasoning 中应看到 Luna 的 `ultra`。可用以下命令检查 profile：

```sh
codex --profile luna-ultra debug prompt-input "installation check"
```

## 5. Enable the deep-deliberation rules / 启用深度讨论规则

The installer deliberately does not overwrite your global instructions. To use the included debate policy globally, inspect it and merge it into `$CODEX_HOME/AGENTS.md`; back up your existing file first and avoid duplicate appends. A project-local `AGENTS.md` affects only that project.

安装器不会覆盖全局指令。要全局使用附带的辩论规则，请先审阅，再备份已有文件并合并到 `$CODEX_HOME/AGENTS.md`，避免重复追加。项目内的 `AGENTS.md` 只影响该项目。

```sh
codex_home="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$codex_home"
if [ -f "$codex_home/AGENTS.md" ]; then
  backup="$codex_home/AGENTS.md.$(date -u +%Y%m%dT%H%M%SZ).bak"
  cp "$codex_home/AGENTS.md" "$backup"
  printf 'Backed up existing AGENTS.md to %s\n' "$backup"
fi
cat AGENTS.md >> "$codex_home/AGENTS.md"
```

Review and deduplicate the file after merging. The policy asks for 10–12 distinct agents when capacity permits, purposeful multi-round debate, and up to 20 configured threads; runtime/account slots still control actual concurrency.

合并后请审阅并去重。规则要求容量允许时使用 10–12 个不同代理进行有目标的多轮讨论，配置最多 20 个线程；实际并发仍由运行时和账号槽位决定。

## 6. Refresh after a Codex update / Codex 更新后刷新

```sh
python3 scripts/check_dependencies.py
python3 scripts/install.py
python3 scripts/install.py --apply --force
```

完全重启 Codex。安装器会在目录格式不兼容时停止且不写文件。

Restart Codex completely. The installer stops without writing if the catalog format is incompatible.

## 7. Roll back or uninstall / 回滚或卸载

Close Codex first. For a new installation, remove the two generated files:

先关闭 Codex。全新安装可删除两个生成文件：

```sh
codex_home="${CODEX_HOME:-$HOME/.codex}"
rm -f "$codex_home/luna-ultra.config.toml" "$codex_home/luna-ultra-models.json"
```

For a forced update, list the timestamped `.bak` files and restore the desired pair after confirming their timestamps. Do not delete `auth.json`, session databases, or the base `config.toml`.

强制更新后，请先列出带时间戳的 `.bak` 文件，确认时间后恢复需要的一对文件。不要删除 `auth.json`、会话数据库或基础 `config.toml`。

## 8. Troubleshooting / 故障排查

- `codex not found`: install Codex CLI or fix `PATH`. / 找不到 `codex`：安装 Codex CLI 或修复 `PATH`。
- Luna v2 or max missing: update/configure the provider; the installer fails closed. / 缺少 Luna v2 或 max：更新或配置服务商，安装器会安全停止。
- Provider rejects root Ultra: choose `max` in More Reasoning or edit the profile's root effort to `max`; subagents remain `max`. / 服务商拒绝根代理 Ultra：在 More Reasoning 选择 `max`，或把 profile 根推理改为 `max`；子代理仍为 `max`。
- Existing targets: use dry-run, then `--apply --force`; backups are created. / 目标已存在：先预览，再 `--apply --force`，安装器会创建备份。
- Permission/path errors: use an absolute, non-symlink `--code-home`. / 权限或路径错误：使用绝对且非符号链接的 `--code-home`。
- More Reasoning has no Ultra: restart Codex after installation and check `codex debug models`. / More Reasoning 没有 Ultra：安装后重启 Codex，并检查 `codex debug models`。

The project adds a local catalog option and reusable instructions. It does not create model access, provider capabilities, credentials, guaranteed cache hits, or guaranteed 20-agent concurrency.

本项目添加本地目录选项和可复用指令，不会创建模型访问权、服务商能力、凭据，也不保证缓存命中或 20 个代理并发。
