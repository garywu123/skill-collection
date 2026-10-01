# Cross-agent 使用教程：从重构计划到交付

本教程以一个小型 Python 项目为例：你在 Codex 对话里调用 Orch，让 Claude Code 写重构计划，Codex 独立评审，通过后再由新的 Claude 会话实现、新的 Codex 会话评审。你主要管理目标、边界和必要决策，不必手动转发两边的对话。

本文是操作教程，不是新的流程规范。行为以 [Cross-agent Skill](../cross-agent/SKILL.md) 为准；生命周期文档的职责见 [Coding 集合说明](../README.md)。

## 1. 先理解三个角色

| 角色 | 在哪里运行 | 负责什么 |
|---|---|---|
| Orchestrator（Orch） | 你当前调用 Skill 的对话 | 理解目标、安排阶段、分派工作、裁决 findings、汇报进度、处理审批 |
| Producer | CLI 启动的 Claude Code 或 Codex 会话 | 当前阶段的详细设计、文档、代码和测试；有必要且允许时才开 subagent |
| Reviewer | CLI 启动的另一个只读会话 | 根据请求、权威输入、变更和测试证据提出问题；不改文件、不再委派 |

本例的顺序是：

```text
你给 Orch 一个包含规划和执行的请求
  -> run A：Claude 写计划 -> Codex 评审 -> Orch 裁决并关闭 run A
  -> run B：新的 Claude 按计划实现 -> 新的 Codex 评审 -> Orch 汇报并关闭 run B
```

一个 run 只负责一个阶段和一个中心 artifact；它不是整个项目。多阶段议程由当前 Orch 对话维护。CLI 不是常驻的自动调度服务：每次 `next` 推进一步，Orch 负责持续调用和判断下一步。

## 2. 一次性准备

### 2.1 准备命令行环境

需要 Python 3.11+、Git，以及本次角色使用的 Claude Code / Codex CLI。Cross-agent 的 Python 脚本使用标准库，不需要额外 `pip install`。

在准备运行项目的同一个终端环境中检查：

```powershell
python --version
git --version
claude --version
codex --version
```

先分别完成所用 CLI 的安装、登录和项目访问设置。Codex 可从项目目录运行 `codex`，按提示登录；安装与认证细节以 [Codex CLI 官方指南](https://learn.chatgpt.com/docs/codex/cli) 和 [认证说明](https://learn.chatgpt.com/docs/auth) 为准。Claude Code 同样需要事先在其自身 CLI 中完成登录。

Cross-agent 不替你登录，也不安装这些 CLI。版本检查成功只代表命令可用，不代表网络、账号额度或模型权限一定可用。不要把密钥放进下面的 TOML、请求文本或仓库。

### 2.2 部署 Skills

在 Skill Collection 仓库根目录，先阅读 [部署 Skill](../skill-deployment/SKILL.md)，再预览：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/external-skills/Sync-ExternalSkills.ps1 -ListOnly
powershell -ExecutionPolicy Bypass -File scripts/deploy-skill/Deploy-Skills.ps1 -ListOnly
```

当前脚本的默认目标是 `~/.claude/skills` 和 `~/.agents/skills`。真实部署会更新配置的外部 Skill 缓存，并清空所选目标目录后重新复制；包括非部署清单中的条目也会被移除。只有确认目标目录由本仓库独占管理、预览里的清理范围可接受后，才执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-skill/Deploy-Skills.ps1
```

只部署一端时使用 `-Target claude` 或 `-Target agents`。不确定目录里是否有其他内容时，不要直接运行真实部署。部署不会自动生成 `~/.cross-agent/config.toml`，也不会替项目初始化 Git。

部署后确认实际使用的 Skill 路径。后文 PowerShell 示例采用 Codex / Agents 的默认安装位置：

```powershell
$crossAgentCli = Join-Path $env:USERPROFILE '.agents/skills/cross-agent/scripts/cross_agent.py'
Test-Path -LiteralPath $crossAgentCli
python $crossAgentCli --help
```

如果只部署到 Claude，改用 `.claude/skills/cross-agent/scripts/cross_agent.py`；如果配置了自定义部署路径，使用实际路径。Skill 未出现在当前客户端时，新开会话重新发现，或明确附上其 `SKILL.md` 文件。

## 3. 初始化项目和配置

### 3.1 选择项目根目录

以下路径 `D:/code/examples/name-cleaner` 是示例，请替换成自己的项目。进入项目根目录，而不是 Skill Collection 仓库或已安装 Skill 的目录：

```powershell
Set-Location D:/code/examples/name-cleaner
git rev-parse --show-toplevel
```

项目必须在 Git 工作树中，因为 CLI 用 Git 快照隔离本次变更。只有确认是新项目、尚未处于 Git 工作树中时，才运行 `git init`。Cross-agent 不自动 commit。

项目应有适用的 `AGENTS.md`，写清边界和真实验证命令。运行过程中不要让其他人或其他会话同时修改该工作树；不同 artifact 的 run 也不代表文件系统隔离。

Cross-agent 的 `initiate` 模式负责按项目证据准备配置，底层调用 CLI 的 `init` 子命令。它不初始化 Git、不创建 run、不启动 worker；首个 `start` 才创建运行状态。只有初始化的请求会在配置报告后结束；明确要求“初始化后执行任务”时，Orch 才继续已授权的任务。

### 3.2 用 initiate 自动初始化配置

在目标项目的对话中显式选择或附上 `cross-agent` Skill，发送：

```text
使用 cross-agent initiate，根据当前项目的 AGENTS.md 和已有构建、测试定义初始化配置。
后续任务是先规划、再执行行为不变的重构，请据此选择验证命令。
这次只初始化并报告有效配置和缺少的前置条件。
```

Orch 会读取项目证据，确定 `allowed_commands`、`delivery_checks` 和必要的 `extra_dirs`，再由 CLI 校验和写入。没有可靠的验证命令时会报告“验证未配置”，不会按语言凭空猜测试。命令选择有实质歧义或需要扩大权限时才询问你。你不必自己复制 PowerShell 模板或创建 `$PROFILE`。

默认配置位置为 `~/.cross-agent/config.toml`，与 Codex 自身的配置文件不同。已有配置会保留全局设置、注释和其他项目，仅追加缺少的当前项目分区。若当前项目分区已经存在，整个分区保持原样，包括省略的字段；返回 `unchanged` 并报告 `proposed_differences`。要修改现有设置，请明确提出配置修改请求，重复初始化不会覆盖它们。没有配置文件时也能使用内置默认值，但缺少文件不会自动触发初始化。

底层命令是 `python $crossAgentCli init --input <JSON文件绝对路径>`。Orch 将输入放在工作树外的临时文件中，完成后删除；JSON 只接受以下三个字段，省略的字段使用空列表：

```json
{
  "allowed_commands": ["python -m unittest"],
  "delivery_checks": ["python -m unittest discover -s tests -v"],
  "extra_dirs": []
}
```

这些命令适用于本教程案例，应以你的项目证据为准。CLI 不会执行这些命令，也不验证登录和模型权限；`providers_on_path` 只表示能否找到可执行程序。初始化成功表示配置语法和结构有效，不表示项目测试通过或所有运行前提齐全。

如需手动理解或调整设置，参见 [完整配置示例](../cross-agent/assets/config.example.toml)。下面是本案例的完整设置示意；初始化只需写入项目分区，其他键省略时使用内置默认值：

```toml
max_reviews = 2
timeout_minutes = 30
rotate_at_tokens = 350000
backlog_rejected = true
max_diff_kb = 200

[defaults]
producer = "claude"
reviewer = "codex"

[projects."D:/code/examples/name-cleaner"]
allowed_commands = ["python -m unittest"]
delivery_checks = ["python -m unittest discover -s tests -v"]
extra_dirs = []
```

关键设置的含义：

| 设置 | 使用时要知道的事 |
|---|---|
| `max_reviews` | 每个 run 的独立评审次数上限，不是整个任务的次数。用完后可能交由 Orch 作有限收尾，不能另开 run 刷新预算。 |
| `timeout_minutes` | 单次 worker 调用或一条验证命令的超时，不是整个任务时限。 |
| `rotate_at_tokens` | 上次调用测得的 context 超过阈值时，下次调用换新会话。`0` 关闭该轮换；不是模型的窗口大小，也不在调用中途触发。默认值未必适合你使用的模型。 |
| `backlog_rejected` | 关闭 run 时是否把被拒绝的 findings 也写进 backlog。 |
| `max_diff_kb` | 一次评审允许读取的变更体积上限。 |
| `allowed_commands` | 当前 Claude Producer 适配器用它生成命令允许规则；不等于所有 provider 的通用沙箱，也不能覆盖平台的拒绝规则。 |
| `delivery_checks` | CLI 在 `general` / `feature-delivery` Producer 完成后实际执行的检查；空列表不表示测试通过。只填写你信任、适合当前阶段的命令。 |
| `extra_dirs` | 额外目录，Producer 可写、Reviewer 可读；不要为了方便授予无关目录。 |

`[projects."..."]` 按运行 CLI 的项目根目录匹配。进入子目录运行可能匹配不到你配置的命令。即使是写计划的 `general` 阶段也会运行 `delivery_checks`，所以本例先确保基线测试存在且能通过。

角色格式为 `<provider>[:<model>[:<effort>]]`。`claude` / `codex` 使用对应 CLI 的默认值；如需指定，填入该 CLI 和账号实际支持的模型与 effort。`codex::high` 表示保留默认模型并请求 `high` effort，不是对所有模型兼容性的保证。初始化继承已有全局或内置角色默认值，不为一个项目修改全局角色；后续任务中指定的角色通过 `start --producer` / `--reviewer` 覆盖默认值。

配置控制 worker，不会改变当前 Orch 对话自己的模型或 effort。每个 run 会保存启动时的设置；修改配置不会改变已经打开的 run。

若要使用其他配置文件，必须让启动 CLI 的进程继承该变量：

```powershell
$env:CROSS_AGENT_CONFIG = 'D:/local-config/cross-agent-demo.toml'
```

这只是当前 PowerShell 及其子进程的设置，不会自动传给已经打开的桌面客户端。也不要把真实机器路径或私人配置提交进仓库。

### 3.3 检查是否就绪

在项目根目录执行：

```powershell
python $crossAgentCli status
```

检查 `config_path`、`config_exists`、`project_root`、`project_configured`、`project`、`defaults`、`settings` 和 `open_runs`。`project` 显示当前目录匹配到的有效命令和额外目录；`project_configured: false` 表示没有匹配的项目分区。空的 `delivery_checks` 表示没有配置验证，不表示测试通过。如果相同 artifact 已有打开的 run，应恢复它或明确决定放弃，不要直接创建第二个。

## 4. 主案例：先规划，再执行重构

### 4.1 案例起点

假设项目已经有 `names.py` 和 `tests/test_names.py`，`clean_name(value)` 用循环拼接 `value.split()` 的结果。原有测试覆盖空字符串、混合空白和 Unicode / 大小写保持，以下命令已经能通过：

```powershell
python -m unittest discover -s tests -v
```

你想简化实现，但保留现有行为，包括异常行为。它是独立重构，不需要为了调用 Orch 临时创建 Product Brief、Feature Map 或 Feature ID。

### 4.2 给 Orch 一次完整授权

在项目的 Codex 对话中显式选择或附上 `cross-agent` Skill，发送：

```text
使用 cross-agent。你作为 Orch，Claude Code 作为 Producer，Codex 作为 Reviewer，
模型和 effort 使用配置默认值。

目标：行为不变地简化 names.py 中的 clean_name。
先让 Producer 读取 AGENTS.md、names.py 和现有测试，写 docs/refactor-plan.md；
计划必须说明行为边界、最小修改、正常与异常路径测试，规划阶段不要改生产代码。

计划独立评审通过后，自动开启新的执行阶段，按已审计划实现并再次独立评审。
保留现有测试，必要时增加普通 unittest 测试文件；重构前后都运行
python -m unittest discover -s tests -v。
不加依赖、不扩展产品范围、不 commit。这个小案例不需要 subagent。
只有确实需要我决定范围或行为时才停下来询问。

请在当前对话汇报阶段、模型/effort、可观测的 context 和 subagent 状态，
说明每次交接和新会话的原因。结束时报告测试与最终状态。
```

这条请求同时授权“计划”和“实现”，但实现以计划的独立评审通过为门槛。如果你要自己审批，把相应句子改成：“计划评审结束后停下来，等我批准，暂不实现。”不要同时保留两种相反要求。

### 4.3 Orch 应怎样推进

Orch 先在对话里列出两个阶段及验收条件，再检查配置和已有 run：

1. `general` / `docs/refactor-plan.md`：Claude 产出计划，Codex 只读评审，Orch 裁决。通过并关闭后，才进入下一阶段。
2. `general` / `names.py`：新的 Claude 读取已审计划，补测试并修改实现；CLI 执行配置的检查；新的 Codex 评审最终变更。

发现有效的范围内重大问题时，Orch 接受 finding 并让 Producer 修订；可选建议不自动扩张任务。涉及行为、范围或权威方向变化的决定仍需你回答。详细裁决规则以 Skill 为准。

下面是状态汇报的示意格式，不是固定数值，也不表示本机一定能观察到所有字段：

```text
阶段 2/2：执行重构。Producer 已启动，新会话 generation 1。
Provider：Claude；配置：默认模型/effort；实际模型：已观测值；实际 effort：未知。
最近 parent context：约 34k；窗口上限：未知；轮换阈值：350k。
Subagents：请求 2，已确认启动 2，活跃 1。当前正在处理测试；尚无通过结论。
```

本案例明确禁止 subagent，所以不应出现上述“2 个”的情况；该行仅说明较大任务中的汇报方式。未知应显示“未知”，不能显示 `0`。收到工具活动或 heartbeat 只说明有活动或进程仍在运行，不代表任务成功。

### 4.4 如何判断完成

正常完成报告应说明产物、实际测试结果、使用的评审/修订次数、遗留项，以及最终状态：

- `independently-passed`：独立评审后没有待处理的 accepted finding；仍需结合实际检查结果和已披露的未决项理解，不等于形式化证明无缺陷。
- `completed-by-orchestrator`：预算结束后由 Orch 完成有限收尾，没有再次独立评审；不能冒充前一种状态。
- `needs-user-decision`、`blocked` 或 `failed`：不能报告为完整交付。

上述小型重构曾用于真实跨模型验证：计划和执行各通过一次独立评审，执行后的 10 项 unittest 通过。过程中遇到内联命令权限限制，改成普通测试文件后完成；这不是保证以后每次都无阻塞。多 subagent 并发和 context 压满后的自动压缩不属于这次真实测试覆盖。

## 5. 想看底层命令时

日常使用让 Orch 操作即可。本节用于理解和排障，不要与正在运行的 Orch 同时操作同一个 run。

先在项目根目录预览计划阶段，不启动 worker、不创建 run：

```powershell
python $crossAgentCli start --stage general --artifact docs/refactor-plan.md --first produce --request 'Plan a behavior-preserving simplification of names.py; read AGENTS.md and tests; write only docs/refactor-plan.md. Do not implement or commit.' --producer claude --reviewer codex --dry-run
```

确认预览后，去掉 `--dry-run` 才会创建 run。记录返回的真实 `run_id`，例如保存为变量，再逐步运行：

```powershell
$crossAgentRun = '<替换为返回的 run_id>'
python $crossAgentCli next --run $crossAgentRun --stream
```

每次命令结束都读取最后的 `event: result`，不要无条件循环 `next`：

| 返回的 `phase` | 下一步 |
|---|---|
| `produce` / `review` | 上一步已结束后，继续 `next --stream`。 |
| `awaiting-decision` | Orch 阅读证据、逐条裁决，再用 `decide --input` 提交；JSON 文件放工作树外。 |
| `awaiting-answer` | 等你明确回答，再通过 `answer --text` 转交。 |
| `finalizing` | 由 Orch 完成 Skill 允许的一次有限收尾，再 `next` 记录结果。 |
| `done` | 先读 `final_status` 和报告；满足门槛后才关闭并进入已授权的下一阶段。 |
| `failed` / `blocked` | 报告原因并暂停，不无限重试、不自行新建 run 刷预算。 |

只读查看状态和正常关闭：

```powershell
python $crossAgentCli status --run $crossAgentRun
# 仅在确认已经结束且报告已记录后执行：
python $crossAgentCli close --run $crossAgentRun
```

`close` 清理运行状态和记录的 worker 会话，保留项目产物，并按设置追加 backlog。它不是撤销代码，也不是“完成开发”的快捷方式。未完成的 run 只有你明确放弃后才关闭，必要时使用 `--abandon`。关闭后不能再恢复这个 run，因此先保存你需要的结果报告。

计划关闭且门槛满足后，执行阶段创建另一个 run，明确把已审计划作为输入：

```powershell
python $crossAgentCli start --stage general --artifact names.py --first produce --request 'Implement the independently reviewed docs/refactor-plan.md. Preserve behavior and existing tests; add unittest coverage as needed. Run python -m unittest discover -s tests -v before and after the change. Record actual results in the plan. No dependencies, subagents, scope changes, or commits.'
```

随后仍按上述状态逐步推进。`general` 没有自动附加生命周期 Skill，`--request` 就是工作范围的主要依据，不能只写“继续”。

## 6. 换成 Feature Map、架构或 Roadmap

初始化方式相同，改变的是输入、阶段和停止点。例如在显式调用 `cross-agent` 后说：

```text
完成 docs/feature-map.md 中 F03、F04 的计划和交付，按依赖顺序处理。
使用 feature-plan 和 feature-delivery；已有计划先核对，缺失前提先报告。
不要执行其他 Features。每个 Feature / 阶段使用新 worker，会话交接在这里汇报。
```

或者：

```text
为现有系统提出模块拆分设计与分阶段迁移 Roadmap，明确职责、依赖、风险、
验收和回退方案。先检查现有权威设计；适用时使用 feature-map 的 General Design /
Roadmap 结构，否则作为有明确产物的 general 设计任务。评审后等我批准，不改生产代码。
```

CLI 当前只有 `feature-map`、`feature-plan`、`feature-delivery`、`general` 四种 stage，不存在 `roadmap` 或 `refactor` 子命令。`general` 不应被用来绕过本来适用的生命周期前提。

不用为了这条链路把所有 Skills 的自动调用全部打开：生命周期阶段的 worker prompt 会明确指定要读取的 Skill 文件。这里区分的是“你授权 Orch 后显式分派阶段”和“模型看到文件就自行扩展流程”，不是一个全局自动开发开关。

## 7. 常见问题

- **项目命令没有生效**：核对当前目录与 `[projects."..."]`，以及 `status` 返回的配置路径。配置文件不会通过项目向上搜索；自定义环境变量必须传到实际启动进程。
- **再次 initiate 没有更新命令**：已有项目分区会完整保留，新的建议在 `proposed_differences` 中报告。明确要求修改现有配置，不能把重复初始化当作覆盖操作。
- **初始化成功但不能运行 worker**：初始化只校验配置；继续核对 CLI 安装、登录、模型权限、所用阶段的 Skill 和真实检查结果。`checks_configured` 不代表 `checks_executed`。
- **找不到阶段 Skill**：默认从 `cross-agent` 的同级目录寻找。完整部署后应有对应目录；特殊布局可在配置中设置 `[stages.feature-plan]` 的 `skill` 为正确 `SKILL.md` 路径。
- **配置了命令但仍被拒绝**：允许规则不能覆盖 provider 的安全边界。缩小命令、改用普通测试文件或请求明确授权；不要关闭保护来强行通过。
- **context / effort / subagent 数字缺失**：provider 不一定提供。context 是最近一次父会话用量测量，不是持续精确的剩余容量；只有观察到窗口上限才能计算占比。
- **什么时候换人或压缩**：阶段/独立工作项之间新开会话；同阶段按已保存 context 在调用间判断轮换。provider 自身压缩与 CLI 换会话是两回事，Orch 只能报告观察到的事件。
- **换了 Orch 对话后怎样继续**：回到同一个项目根目录，显式调用 Skill，让 Orch 先运行 `status`。已有 run 的状态可读取；原对话的多阶段授权和审批门槛需要你重新提供，不能只凭文件推断。
- **可以直接修改 `.cross-agent/` 吗**：不要。通过 `status`、`next`、`decide`、`answer`、`close` 管理运行；运行中也不要旁路修改项目文件。

首次使用时，把目标、输入、输出、验证命令和停止点讲清楚即可。之后你看到的应该是一个持续汇报、在授权范围内推进的 Orch，而不是需要你手动传递每轮结果的两个聊天窗口。
