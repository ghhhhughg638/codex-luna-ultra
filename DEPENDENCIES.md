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
| Shell | POSIX-compatible shell for the documented commands | Runs the examples / 执行教程命令 |
| Provider access | An account/provider that already has GPT-6-Luna access and authentication | The repository cannot grant model access / 仓库不能授予模型访问权 |

`requirements.txt` is intentionally empty of third-party packages. No `pip install` step is needed.

`requirements.txt` 没有第三方包，故不需要执行 `pip install`。

## Optional / 可选

- `git` to clone the repository; downloading the GitHub ZIP also works. / 使用 `git` 克隆仓库；下载 GitHub ZIP 也可以。
- A network connection for the installed Codex CLI to reach its configured provider. / 让已安装 Codex CLI 访问配置服务商所需的网络。

## Not included / 不包含

This project does not ship the Codex CLI binary, GPT-6-Luna model weights, a provider endpoint, API keys, authentication, session state, or a generated model catalog. The catalog is generated locally so it matches the user's installed Codex version and remains private.

本项目不包含 Codex CLI 二进制、GPT-6-Luna 模型权重、服务商地址、API 密钥、认证信息、会话状态或生成后的模型目录。目录会在用户本机生成，以匹配安装的 Codex 版本并保持私密。

## Compatibility check / 兼容性检查

Run this before installation:

安装前运行：

```sh
python3 scripts/check_dependencies.py
```

The check reports tool versions and whether the local catalog has a Luna v2 entry. It does not print credentials or raw catalog contents.

检查脚本会报告工具版本以及本地目录是否有 Luna v2 条目，不会打印认证信息或完整目录内容。
