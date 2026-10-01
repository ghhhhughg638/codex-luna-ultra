# Dependencies / 依赖

## Required / 必需

Install or configure Codex CLI from the official documentation first:

先通过官方文档安装或配置 Codex CLI：

- https://developers.openai.com/codex/cli/
- https://developers.openai.com/codex/quickstart/

| Component | Requirement | Why / 用途 |
| --- | --- | --- |
| Codex CLI | A version that provides `codex debug models`, `debug prompt-input`, and a Luna entry with `multi_agent_version = "v2"` and `max` | Supplies the local model catalog and loads the profile / 提供本地模型目录并加载 profile |
| Python | Python 3.9 or newer | Runs the installer; it uses only the standard library / 运行安装器，仅使用标准库 |
| Shell | POSIX-compatible shell for profile commands; PowerShell for the Windows desktop command | Runs the examples / 执行教程命令 |
| Provider access for model use | An account/provider that already has GPT-6-Luna access and authentication | Needed to run model requests, not to generate the local files / 调用模型时需要，生成本地文件不需要 |

`requirements.txt` is intentionally empty of third-party packages. No `pip install` step is needed.

`requirements.txt` 没有第三方包，故不需要执行 `pip install`。

The profile workflow is documented for POSIX environments (Linux, macOS, Termux, and WSL2). The Python installer also supports native Windows PowerShell when `--desktop` is used for the Codex desktop app.

profile 流程面向 POSIX 环境（Linux、macOS、Termux 和 WSL2）。使用 Codex 桌面版时，Python 安装器也支持原生 Windows PowerShell 的 `--desktop` 模式。

## Windows Codex desktop / Windows Codex 桌面版

The desktop app loads its model catalog from the global `$CODEX_HOME/config.toml` at startup. Install the generated catalog and opt into the desktop merge explicitly:

Windows 桌面版会在启动时从全局 `$CODEX_HOME/config.toml` 加载模型目录。请显式启用桌面合并：

```powershell
python scripts/install.py --apply --desktop --force
```

This creates a timestamped backup before updating `config.toml`, then adds the local catalog reference and `features.multi_agent = true`. Close and restart the desktop app after the command returns.

该命令会在更新 `config.toml` 前创建带时间戳的备份，然后加入本地目录引用和 `features.multi_agent = true`。命令结束后请关闭并重新打开桌面版。

## Optional / 可选

- `git` to clone the repository; downloading the GitHub ZIP also works. / 使用 `git` 克隆仓库；下载 GitHub ZIP 也可以。
- A network connection for the installed Codex CLI to reach its configured provider. / 让已安装 Codex CLI 访问配置服务商所需的网络。

## Not included / 不包含

This project does not ship the Codex CLI binary, GPT-6-Luna model weights, a provider endpoint, API keys, authentication, session state, or a generated model catalog. The catalog is generated locally so it matches the user's installed Codex version and remains private. Provider access and authentication are required to run Luna requests, not to generate the local profile/catalog.

本项目不包含 Codex CLI 二进制、GPT-6-Luna 模型权重、服务商地址、API 密钥、认证信息、会话状态或生成后的模型目录。目录会在用户本机生成，以匹配安装的 Codex 版本并保持私密。调用 Luna 请求需要服务商访问权和认证；生成本地 profile/目录不需要。

## Compatibility check / 兼容性检查

Run this before installation:

安装前运行：

```sh
python3 scripts/check_dependencies.py
```

The check reports tool versions and whether the local catalog has a Luna v2 entry. It does not print credentials or raw catalog contents.

检查脚本会报告工具版本以及本地目录是否有 Luna v2 条目，不会打印认证信息或完整目录内容。
