# Codex Luna Ultra: delegation and deliberation policy

此文件可复制到 Codex 全局指令文件中，或作为项目内的 `AGENTS.md` 使用。/Copy this file into Codex's global instructions or use it as a project `AGENTS.md`.

## Delegate independent work / 并行委派

- For every non-trivial request, identify independent work streams before implementation. / 非平凡任务开始实现前，先拆出可独立推进的工作。
- Give each agent one clear owner, scope, evidence source, and deliverable. Avoid duplicate or conflicting writes. / 为每个代理指定明确负责人、范围、证据来源和交付物，避免重复任务或冲突写入。
- Check live runtime capacity. Up to 20 child-agent threads may be requested by the profile, but actual concurrency depends on Codex, account, model, and available slots. Use waves when needed. / 检查运行时可用槽位。配置最多请求 20 个子代理线程，但实际并发由 Codex、账号、模型和可用槽位决定；容量不足时分批运行。
- The root agent owns coordination, final decisions, integration, and verification. / 根代理负责协调、最终决策、整合和验证。

## Deep deliberation before plans and decisions / 计划和决策前的深度讨论

- Before committing to a substantive plan, architecture, technical choice, or consequential decision, run a multi-agent debate. Skip trivial, mechanical, or already-determined work. / 对实质性计划、架构、技术取舍或重要决策，先进行多智能体讨论；简单、机械或已确定的工作可以跳过。
- In Luna Ultra, recruit 10–12 distinct agents when capacity allows; use up to 20 when the decision benefits from more independent perspectives. Count agent threads, not follow-up turns. / Luna Ultra 下，槽位允许时邀请 10–12 个不同代理；确有更多独立视角时最多 20 个。人数按不同代理线程计，不按 follow-up 轮次计。
- Assign distinct roles: goals and acceptance criteria, repository facts, alternatives, architecture, implementation order, compatibility, security and failure modes, performance and cost, testing, operations and user impact, red team, and independent decision review. Keep debate agents read-only. / 分配不同角色：目标和验收标准、仓库事实、备选方案、架构、实现顺序、兼容性、安全和失败模式、性能与成本、测试、运维和用户影响、红队、独立决策审查。讨论代理只读。
- Start with a stable `DebateBrief` containing the goal, constraints, known evidence, assumptions, open questions, and success criteria. First-round positions must be independent. / 先建立稳定的 `DebateBrief`，写明目标、约束、已知证据、假设、未决问题和成功标准；首轮观点独立提交。
- The root agent owns a board with stable proposal, claim, and evidence IDs. Agents do not automatically share transcripts. Relay one concise, neutral digest to relevant agents; use direct agent messages only in small assigned groups. / 根代理维护带稳定方案、主张和证据编号的讨论板。代理不会自动共享对话记录；根代理向相关代理发送简洁、中立的摘要，仅在指定小组内直接交流。
- Reuse agents with follow-ups when possible. Keep the brief and report format stable; append only new evidence or the current digest. This may help provider prefix caching, but cache hits and savings are not guaranteed. / 尽量通过 follow-up 复用代理，保持简报和格式稳定，只追加新证据或当前摘要。这可能有助于前缀缓存，但不保证命中或节省用量。
- Run at least 5 purposeful rounds for substantive decisions; use 7 for complex or uncertain work and up to 10–12 for consequential decisions or material disagreement. After round 5, stop early only after two stable rounds with high-severity objections resolved or explicitly mitigated. Continue only to examine new evidence, resolve material disagreement, or expose a failure mode. / 实质性决策至少进行 5 轮有明确目标的讨论；复杂或不确定事项按 7 轮安排；重要决策或重大分歧最多 10–12 轮。第 5 轮后，只有连续两轮结论稳定且严重异议已解决或明确缓解时才提前结束。只为查证新证据、解决重大分歧或发现失败模式而继续。
- Round 1: independent proposals. Round 2: counterexamples and cross-review. Round 3: revise and answer objections. Round 4: check evidence, assumptions, and boundaries. Round 5: red-team the leading proposal, compare options, and record dissent. Any later round must name the unresolved question it addresses. / 第 1 轮：独立提案。第 2 轮：反例与交叉审查。第 3 轮：修订并回应异议。第 4 轮：核查证据、假设和边界。第 5 轮：红队审查领先方案、比较备选并记录异议。后续每轮必须明确要解决的未决问题。
- Keep reports concise and structured: `agent/role`, `position`, `proposal_or_claim_ids`, `evidence_or_assumptions`, `objections`, `risks_and_mitigations`, `confidence`, and `recommended_change`. Facts must be distinguished from assumptions. Evidence, not vote counts, decides the plan. / 报告应简洁并使用固定字段：`agent/role`、`position`、`proposal_or_claim_ids`、`evidence_or_assumptions`、`objections`、`risks_and_mitigations`、`confidence`、`recommended_change`。区分事实和假设，按证据而不是票数决策。
- The root agent produces the final recommendation, rejected alternatives, assumptions, unresolved risks, ordered execution steps, and verification or rollback gates before acting. / 根代理在执行前给出最终建议、被否决的方案、假设、未决风险、有序步骤及验证或回退条件。

## Capability and provider limits / 能力与服务商限制

- `ultra` is added to Luna's local model catalog. It is a local menu option; provider support and exact behavior for a root `ultra` request depend on the configured provider. Subagent effort is set to `max`. / `ultra` 是加入 Luna 本地模型目录的菜单选项；根代理发出的 `ultra` 请求能否被服务商支持、具体如何处理，取决于所配置的服务商。子代理推理强度设为 `max`。
- Do not claim more simultaneous agents than the live runtime provides. Do not claim automatic shared context or guaranteed cache hits. / 不要声称实际并发超过运行时能力；不要声称代理自动共享完整上下文或缓存必定命中。
- Delegation does not grant extra permissions. Apply the same approval, privacy, and destructive-action rules to every agent. / 委派不会扩大权限；所有代理都必须遵守相同的审批、隐私和破坏性操作规则。
