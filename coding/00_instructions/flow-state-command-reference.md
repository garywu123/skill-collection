# Flow State Command Reference

`flow_state.py` 是确定性的状态与索引记录器，不是工作流编排器。它不解释业务、不选择下一个
Skill，也不授予 AI 后续权限。所有写命令均在项目根目录执行：

```text
python <flow-state-dir>/scripts/flow_state.py --root . <command> ...
```

除只读命令外，先运行 `status` 获取当前 revision；所有带 `--expect-revision` 的命令必须使用
刚读取或前一命令返回的精确 revision，不能猜测。

## 使用规则

- 每次只能对当前明确授权的一个操作写状态。
- pointer 和 artifact index 不可手工编辑。
- `ready_for_review` 是候选状态；只有带人类姓名/角色、日期、证据的决定命令才会审批。
- `ready_for_acceptance` 只用于 `feature`；`ready_for_release` 只用于 `release`。
- canonical 产品或架构事实已批准后，不能用普通命令覆盖；先走已审阅的 amendment。

## 命令总表

| 命令 | 何时使用 | 前置条件 | 写入/结果 |
|---|---|---|---|
| `init --project-id ID --profile full\|lite` | 首次启用状态跟踪 | 当前人明确授权；不存在冲突 pointer | 创建 pointer、index、SHA-256 sidecar；profile 仍为 provisional。 |
| `status` | 查看当前工作、gate、revision、允许动作 | 人明确请求状态 | 只读、无状态变化。 |
| `validate [--check-paths]` | 审核 pointer 或完整路径/索引一致性 | 人明确请求检查；`--check-paths` 用于完整一致性 | 只读；报告冲突或缺失。 |
| `start --expect-revision N --kind K --work-id ID --stage S` | 启动当前明确授权的 lifecycle operation | 前置 gate 已通过、无 pending gate、revision 精确；人明确选择该 operation | pointer 进入 `in_progress`；不调用任何 Skill。 |
| `confirm-profile --expect-revision N --profile full\|lite` | roadmap 已审批后确认 Full/Lite | roadmap 的 sizing 字段和 evidence 与 profile 一致 | profile `confirmed`。 |
| `record-output --expect-revision N --stage S --artifact role=path ...` | 当前已授权 Skill 已产生并验证自己的候选输出 | artifact 存在、角色/阶段/状态合法；当前操作有权写该 artifact | 登记候选 artifact、pending gate、索引及 sidecar。 |
| `sync-bundle --artifact root --member path ...` | canonical root 使用 `Artifact bundle: split` | 所有成员内容已最终确定；传入完整成员集合（不含 root） | 重写 root 的完整 `Approved Bundle` 哈希表；不改变 lifecycle state。 |
| `block --expect-revision N --blocker text ...` | 当前已授权操作发现具体阻断事实 | 不能有待决 gate；blocker 具体可行动 | 状态为 `blocked`，记录解除所需动作。 |
| `decide --expect-revision N --decision approved\|rejected ...` | 审批普通候选工件 | 当前 gate 是 `ready_for_review`，候选 artifact hash 未变，当前人提供 actor/date/evidence | `approved` 或 `rejected`；生成不可变 decision receipt。 |
| `record-feature-decision --decision accepted\|rejected\|changes_requested ...` | 对独立 feature acceptance 作最终人类决定 | active kind 是 feature；acceptance hash 匹配；接受时 review 为 ready/conditional 且无 blocker | 写 Feature 决定字段及 content-hashed receipt。 |
| `authorize-release --artifact readiness.md ...` | 在外部发布工具执行前记录人工授权 | active release 为 `ready_for_release`；readiness hash 匹配；review 为 ready/conditional、无 blocker | `release_authorized` 和 authorization receipt；不发布。 |
| `record-release-result --result ... --execution-evidence receipt.yaml ...` | 外部发布工具已结束后记录结果 | 已 `release_authorized`；有仓库内结构化执行 receipt；当前人确认 | `released`（仅 succeeded）或终态结果回执。 |
| `rebuild-index` | indexed 的非 canonical 工件绕过正常记录命令被改动 | pointer integrity 仍通过；没有试图重基线化已批准 canonical 内容 | 重建 index 和 sidecar；随后应执行 `validate --check-paths`。 |
| `resolve [--id ID] [--path path] [--limit N]` | 在大项目中定位所需 artifact/ID | 人明确请求定位 | 只读，返回小型 index 切片；再仅读取命中章节。 |

## 常见序列

### 初始化

```text
init → status → start（一个明确授权的 stage）→ 对应 Skill
```

`init --force` 只用于人明确要求重置且确认目标没有需要保留的状态时。不得将其当作修复冲突或覆盖
审批历史的工具。

### 候选工件的普通审批

```text
Skill 写候选工件
→ record-output
→ 人审阅
→ decide approved 或 rejected
```

若审批时在工件中补写审批字段导致字节变化，应先对同一 role/path 再次 `record-output`，再 `decide`，
以确保审批的是实际审阅版本。

### Feature 验收与发布

```text
post-implement feature
→ record-output ready_for_acceptance
→ accept-feature
→ record-feature-decision

release readiness
→ record-output ready_for_release
→ authorize-release
→ 外部发布工具（单独授权）
→ record-release-result
```

不要用 `decide` 接受 Feature，也不要用 `authorize-release` 执行发布。

## 何时不应使用命令

- 不要用 `start` 根据 `next.recommended` 自动开启下一阶段。
- 不要用 `record-output` 直接改写已批准的产品或架构真相。
- 不要用 `rebuild-index` 掩盖 canonical 文件漂移；应通过 change request/amendment 处理。
- 不要在 revision 过期时重试写入；先 `status`，理解并解决状态变化。
- 不要为方便而完整读取 `.specify/artifact-index.yaml`；使用 `resolve` 后读取需要的切片。
