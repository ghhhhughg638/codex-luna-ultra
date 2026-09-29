# Codex Luna Ultra & Multi-Agent Deliberation Setup
# Codex Luna Ultra 与多智能体深度讨论配置

This repository provides a portable Codex CLI profile and an installer that adds a Luna `ultra` option to a **local** model catalog. It does not include a generated model catalog, private Codex settings, credentials, or session data.

本仓库提供可移植的 Codex CLI profile，以及一个为**本地**模型目录添加 Luna `ultra` 选项的安装器。仓库不包含生成后的模型目录、个人 Codex 配置、认证信息或会话数据。

Dependencies and the full step-by-step tutorial are in [DEPENDENCIES.md](DEPENDENCIES.md) and [TUTORIAL.md](TUTORIAL.md). The project can install the local profile and generated catalog; it cannot install Codex, GPT-6-Luna access, a provider, or credentials.

依赖和完整分步教程见 [DEPENDENCIES.md](DEPENDENCIES.md) 与 [TUTORIAL.md](TUTORIAL.md)。项目可以安装本地 profile 和生成目录，但不能安装 Codex、GPT-6-Luna 访问权、服务商或认证信息。

## What Ultra means / Ultra 的含义

The installer adds `ultra` to Luna's local reasoning menu and sets `multi_agent_reasoning_effort` to `max` for the synthetic option it creates. Existing provider-native Ultra entries and their explicit settings are preserved. The profile requests root reasoning effort `ultra` and sets default subagents to Luna `max`. This local catalog entry cannot grant provider-side model support; exact root `ultra` behavior depends on the configured provider. If the provider rejects it, select `max` instead.

安装器会把 `ultra` 加入 Luna 的本地推理菜单，并为新建的模拟档位将 `multi_agent_reasoning_effort` 设为 `max`。已有服务商原生 Ultra 档位及其设置会保留。profile 向服务商请求根代理 `ultra` 推理，并将默认子代理设为 Luna `max`。本地目录不能赋予服务商端模型能力；根代理 `ultra` 的实际行为取决于配置的服务商。如果服务商拒绝该档位，请改选 `max`。

The generated catalog contains the installed Codex model entries and built-in model instructions, so the installer keeps it in the user's Codex home and never writes it into this repository.

生成目录包含当前安装版 Codex 的模型条目和内置模型指令，因此安装器只把它保存在用户的 Codex home，不会写入本仓库。

## Install / 安装

Requirements: Codex CLI with `codex debug models` and a Luna model entry advertising multi-agent v2, Python 3, and a POSIX shell. Native Windows is not supported by this installer; use WSL2. Provider access/authentication is needed to run Luna requests, not to generate the local profile/catalog. The current format was validated with Codex CLI 0.156.1 on Termux; the installer stops when required catalog fields are incompatible or Codex rejects the generated profile.

要求：支持 `codex debug models` 且 Luna 模型条目标记多智能体 v2 的 Codex CLI、Python 3 和 POSIX shell。安装器不支持原生 Windows，请使用 WSL2。实际调用 Luna 请求需要服务商访问权和认证；生成本地 profile/目录不需要。当前格式已在 Termux 的 Codex CLI 0.156.1 上验证；必需目录字段不兼容或 Codex 拒绝生成的 profile 时，安装器会停止。

1. Clone this repository.
2. Enter the repository directory:

   ```sh
   cd codex-luna-ultra
   ```

3. Preview the install (the default; it does not modify your Codex home):

   ```sh
   python3 scripts/install.py
   ```

4. Apply the install:

   ```sh
   python3 scripts/install.py --apply
   ```

5. Start a Luna Ultra session:

   ```sh
   codex -p luna-ultra
   ```

1. 克隆本仓库。
2. 进入仓库目录：

   ```sh
   cd codex-luna-ultra
   ```

3. 先预览安装（默认行为，不修改 Codex home）：

   ```sh
   python3 scripts/install.py
   ```

4. 执行安装：

   ```sh
   python3 scripts/install.py --apply
   ```

5. 启动 Luna Ultra 会话：

   ```sh
   codex -p luna-ultra
   ```

On a fresh install, the installer writes only `luna-ultra-models.json` and `luna-ultra.config.toml` under `$CODEX_HOME` (usually `~/.codex`). It obtains a fresh catalog using a temporary isolated Codex home, validates the Luna entry, and preserves all other model entries. It does not edit `config.toml`, authentication, trust settings, `AGENTS.md`, or session state. Existing target files are never overwritten unless `--force` is supplied; forced updates also create timestamped, permission-restricted backup files first.

首次安装时，安装器只会在 `$CODEX_HOME`（通常是 `~/.codex`）下写入 `luna-ultra-models.json` 和 `luna-ultra.config.toml`。它使用临时隔离的 Codex home 获取新目录，验证 Luna 条目并保留其他模型条目。它不会改动 `config.toml`、认证信息、信任设置、`AGENTS.md` 或会话状态。默认不会覆盖同名文件；只有使用 `--force` 才会更新，并会额外创建带时间戳、权限受限的备份文件。

To use the deliberation policy globally, merge this repository's `AGENTS.md` into `$CODEX_HOME/AGENTS.md`; do not overwrite existing personal instructions. A project-local copy applies only to that project.

要全局启用深度讨论规则，请将本仓库的 `AGENTS.md` 合并到 `$CODEX_HOME/AGENTS.md`；不要覆盖已有的个人指令。放在项目中的副本只对该项目生效。

## Refresh / 更新

Preview and apply again after Codex updates its model catalog:

Codex 更新模型目录后，重新预览并应用：

```sh
python3 scripts/install.py
python3 scripts/install.py --apply --force
```

The source catalog is queried from the installed CLI in a clean temporary home. If the CLI output changes, the installer stops without writing files. Restart Codex after updating because `model_catalog_json` is loaded at startup.

安装器会在干净临时 home 中从本机 CLI 获取源目录。如果 CLI 输出格式变化，安装器会停止且不写入文件。更新后请重启 Codex，因为 `model_catalog_json` 在启动时加载。

## Deliberation behavior / 深度讨论方式

For substantive plans and decisions, the included `AGENTS.md` asks Luna Ultra to use 10–12 distinct agents when capacity allows (up to 20), conduct at least five purposeful rounds, use seven for complex work, and extend to 10–12 only for consequential unresolved disagreements. Follow-up rounds reuse the same agent threads. Actual concurrency is limited by Codex and the account/runtime; the configured ceiling does not guarantee 20 simultaneous agents. Stable context and follow-ups may help provider caching, but neither shared transcripts nor cache hits are guaranteed.

对实质性计划和决策，附带的 `AGENTS.md` 要求 Luna Ultra 在容量允许时使用 10–12 个不同代理（最多 20 个），至少进行五轮有明确目标的讨论；复杂任务按七轮安排；只有重要分歧仍未解决时才延长至 10–12 轮。后续轮次复用相同代理线程。实际并发由 Codex 与账号/运行时容量限制；配置上限不保证 20 个代理同时运行。稳定上下文和 follow-up 可能有助于服务商缓存，但不保证共享对话记录或缓存命中。

## Regression checks / 回归检查

Run the standard-library test suite from the repository root:

在仓库根目录运行标准库回归测试：

```sh
python3 -m unittest discover -s tests -v
```

## Remove / 卸载

Remove the two files created under `$CODEX_HOME`: `luna-ultra.config.toml` and `luna-ultra-models.json`. Restore a backup if you used `--force`. The installer does not modify the base config.

删除 `$CODEX_HOME` 下安装器创建的两个文件：`luna-ultra.config.toml` 和 `luna-ultra-models.json`。如果使用了 `--force`，可按需恢复备份。安装器不会改动基础配置文件。

## License / 许可证

No license is granted with this publication. / 本发布未授予许可证。
