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

只部署一端时使用 `-Target claude` 或 `-Target agents`。不确定目录里是否有其他内容时，不要直接运行真实部署。部署安装 Skill 的代码和指令，不会自动生成目标 repo 的 `.cross-agent/config.toml`，也不会替项目初始化 Git；项目配置由下一节的 `initiate` 创建。

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
Producer 使用 Claude 默认模型，effort 为 high；Reviewer 使用 Codex 默认模型，effort 为 high。
后续任务是先规划、再执行行为不变的重构，请据此选择验证命令。
这次只初始化并报告有效配置和缺少的前置条件。
```

Orch 会读取项目证据，确定 `allowed_commands`、`delivery_checks` 和必要的 `extra_dirs`，再由 CLI 校验和写入。没有可靠的验证命令时会报告“验证未配置”，不会按语言凭空猜测试。命令选择有实质歧义或需要扩大权限时才询问你。你不必自己复制 PowerShell 模板或创建 `$PROFILE`。

默认配置位置为当前项目根目录的 `.cross-agent/config.toml`，与 Codex 自身的配置文件不同。每个 repo 独立保存设置；CLI 不向父目录搜索，也不回退读取旧的 `~/.cross-agent/config.toml`。从哪个项目根目录运行，就使用哪个根目录的配置。新建配置使用 `[projects."."]`，因此移动 checkout 后不必修改绝对路径。

已有配置、注释和角色默认值会保留，仅追加缺少的当前项目分区。已有分区保持原样，包括省略的字段；返回 `unchanged`，并用 `proposed_differences` 和 `proposed_role_differences` 报告命令与角色建议的差异。要修改现有设置，请明确提出配置修改请求，重复初始化不会覆盖它们。初始化会使用 Git 的本地 exclude 忽略 `.cross-agent/`，不用修改项目的 `.gitignore`。没有配置文件时仍可使用内置默认值，但缺少文件不会自动触发初始化。

底层命令如下；`--producer` 和 `--reviewer` 在新文件中保存当前 repo 的角色、模型和 effort。`codex::high` 保留默认模型但指定 effort，`codex:<指定模型>:high` 同时指定两者。Orch 只传你明确指定的值，省略角色参数时新文件使用内置角色默认值：

```powershell
python $crossAgentCli init --input '<JSON文件绝对路径>' --producer claude::high --reviewer codex::high
```

Orch 将输入放在工作树外的临时文件中，完成后删除；JSON 只接受以下三个字段，省略的字段使用空列表：

```json
{
  "allowed_commands": ["python -m unittest"],
  "delivery_checks": ["python -m unittest discover -s tests -v"],
  "extra_dirs": []
}
```

这些命令适用于本教程案例，应以你的项目证据为准。CLI 不会执行项目检查，也不验证登录和模型权限；`providers_on_path` 只表示能否找到可执行程序。初始化成功表示配置语法和结构有效，不表示项目测试通过或所有运行前提齐全。

`init` 会执行只读的 `codex --version`，并向 npm registry 查询 `@openai/codex` 的 `latest` 发布版本。结果在 `codex_version` 中包含已安装版本、最新版本、来源和状态：`current` 表示相同，`update-available` 表示安装的稳定版较旧，`ahead` 表示比该发布版新。未安装时是 `not-installed`，网络失败、版本无法识别或安装预发布版时是 `unknown`，不能报告成“已是最新”。两个查询都有超时，检测失败不会阻止配置创建；初始化不自动升级 CLI。只有明确要求跳过检测时才使用 `--skip-version-check`，此时返回 `skipped`。

如需手动理解或调整设置，参见 [完整配置示例](../cross-agent/assets/config.example.toml)。下面是本案例的完整设置示意；初始化写入角色默认值和项目分区，其他键省略时使用内置默认值：

```toml
max_reviews = 2
timeout_minutes = 30
rotate_at_tokens = 350000
backlog_rejected = true
max_diff_kb = 200

[defaults]
producer = "claude::high"
reviewer = "codex::high"

[projects."."]
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

`[projects."."]` 表示当前项目根目录；始终从同一项目根目录调用 CLI，进入子目录会使用另一份配置路径。旧的绝对路径分区仍可解析，但用户目录文件不会自动加载。如需继续使用旧文件，通过 `CROSS_AGENT_CONFIG` 显式指定；也可在新建 repo 配置时明确提供旧设置，初始化不会自动迁移或修改旧文件。即使是写计划的 `general` 阶段也会运行 `delivery_checks`，所以本例先确保基线测试存在且能通过。

角色格式为 `<provider>[:<model>[:<effort>]]`。`claude` / `codex` 使用对应 CLI 的默认值；如需指定，填入该 CLI 和账号实际支持的模型与 effort。`codex::high` 表示保留默认模型并请求 `high` effort，不是对所有模型兼容性的保证。Codex 的 effort 通过 `model_reasoning_effort` 传给 CLI，可用程度依模型和客户端而定，见 [OpenAI 官方配置说明](https://learn.chatgpt.com/docs/config-file/config-reference)。新配置的 `[defaults]` 只属于当前 repo；后续任务中指定的角色通过 `start --producer` / `--reviewer` 覆盖该次 run 的默认值，不会改写配置文件。

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

### 3.3 共享 workspace 配置与 CLI 路径

多个项目可以各自保留 `.cross-agent/config.toml` 入口，只含一行指针，例如：

```toml
config_file = "../../workspace/.cross-agent/config.toml"
```

路径从入口文件所在目录解析，只允许一层指针。共享文件保存角色和设置，各项目以
明确的根目录键分别配置命令与 `extra_dirs`；run 状态仍留在发起项目中。无需重复 init
或删除旧 history。共享文件中的 CLI 选择示例：

```toml
[cli]
codex = "C:/Tools/Codex/codex.exe"
claude = "C:/Tools/Claude/claude.exe"
```

使用实际安装的绝对路径。省略某一项时该 provider 使用 PATH；指定路径无效时会失败，
不会回退到另一份安装。CLI 路径在每次 worker 调用时读取，因此现有 run 的恢复也使用
新选择；保存的角色、命令、timeout 和 review 预算保持原样。

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
| `failed` | `automatic_recovery_available` 为 true 时调用一次 `next`；否则报告原因并暂停。 |
| `blocked` | 等待用户解决 blocker，再用 `answer` 传递决定。 |

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

`feature-map`、`feature-plan`、`feature-delivery` 现在允许根据用户请求自动选择；共用 `SKILL.md`，分别用 Claude frontmatter 和 Codex `agents/openai.yaml` 声明策略。其他生命周期 Skills 和 Orch 保持显式调用。Cross-agent 不依赖模型碰巧选择正确 Skill：CLI 将指定阶段的完整正文注入 prompt，并显示路径、hash 和加载方式；引用的资源仍按需读取。自动选择不会扩大用户授权或解除 Reviewer 的只读角色。

## 7. 常见问题

- **项目命令没有生效**：核对当前项目根目录和 `status` 返回的配置路径；本地配置使用 `[projects."."]`。CLI 不向父目录搜索，也不自动加载用户目录旧配置；自定义环境变量必须传到实际启动进程。
- **再次 initiate 没有更新命令或角色**：已有设置会保留，建议分别在 `proposed_differences` 和 `proposed_role_differences` 中报告。明确要求修改现有配置，不能把重复初始化当作覆盖操作。
- **版本显示 unknown**：查看 `codex_version.reason`，可能是网络、超时、不可识别的输出或预发布版。它不表示最新，也不表示版本必然过旧；恢复检测条件后可再次初始化，不会覆盖配置。
- **初始化成功但不能运行 worker**：初始化只校验配置；继续核对 CLI 安装、登录、模型权限、所用阶段的 Skill 和真实检查结果。`checks_configured` 不代表 `checks_executed`。
- **找不到阶段 Skill**：默认从 `cross-agent` 的同级目录寻找。完整部署后应有对应目录；特殊布局可在配置中设置 `[stages.feature-plan]` 的 `skill` 为正确 `SKILL.md` 路径。
- **配置了命令但仍被拒绝**：允许规则不能覆盖 provider 的安全边界。缩小命令、改用普通测试文件或请求明确授权；不要关闭保护来强行通过。
- **context / effort / subagent 数字缺失**：provider 不一定提供。context 是最近一次父会话用量测量，不是持续精确的剩余容量；只有观察到窗口上限才能计算占比。
- **什么时候换人或压缩**：阶段/独立工作项之间、计划 checkpoint 后新开会话；其他调用优先 resume，只有 context 超阈值或 session 明确失效才替换。timeout 保留最后可用的 parent context 测量，旧 session 留在历史中。provider 自身压缩与 CLI 换会话分别报告。
- **换了 Orch 对话后怎样继续**：回到同一个项目根目录，显式调用 Skill，让 Orch 先运行 `status`。已有 run 的状态可读取；原对话的多阶段授权和审批门槛需要你重新提供，不能只凭文件推断。
- **可以直接修改 `.cross-agent/` 吗**：运行状态在 `.cross-agent/runs/`，只能通过 `status`、`next`、`decide`、`answer`、`close` 管理。`.cross-agent/config.toml` 是配置，明确的配置修改任务可以编辑它；阶段 worker 不修改配置，配置变更不影响已打开 run 的设置。

首次使用时，把目标、输入、输出、验证命令和停止点讲清楚即可。之后你看到的应该是一个持续汇报、在授权范围内推进的 Orch，而不是需要你手动传递每轮结果的两个聊天窗口。


## 执行阶段、进度和恢复

Feature Plan 提前评估可验证的功能区域、依赖、阶段验收与交接，并决定串行还是值得
委派。小功能保持单阶段；较大 Feature 在同一份 Plan 中安排执行 segment，预留验证和
checkpoint 时间。30 分钟是单次 worker 调用的硬上限，规划不能保证所有测试都在限时内。
Producer 最多同时三个 sub-agent；共享接口、schema、整合与整体回归留在父会话。

`next --stream` 的 `skill-loaded` 表示完整正文已注入本次 prompt，`method` 为
`prompt-injected`，附路径和 SHA-256；不是声称调用了原生 Skill 工具。worker 就绪后
`skill-started` 显示 Producer 执行阶段或 Reviewer 只读判定阶段。运行数据缺失时为
`null`，不能报作零。示例状态包括 Skill 加载、Feature/阶段开始、模型/effort 和实际
sub-agent 活动；有心跳不代表验收通过。

完成一个计划 segment 且后续工作仍在授权范围内时，Producer 返回 `status: checkpoint`。
`summary` 必须包含完成段、真实验收/检查证据、稳定契约、下一段未完成工作和限制；
`questions`、`outcomes` 为空，`blocker` 为 null。下一次 `next` 创建新 Producer session
继续，不提前送审。每 run 最多八个 checkpoint；原始 baseline、Feature ID、findings、
待传递回答与总 review 预算保持原样，全部完成后才执行整体验证并交给 Reviewer。

Producer timeout 或明确瞬态连接/限流错误会自动恢复一次，每 run 共用这个上限，包括
升级 CLI 后的旧 failed run。默认优先 resume 之前的 Producer；context 超阈值才换新。
恢复前先检查现有 diff、Plan 结果和交接，避免重复已经完成的工作。第二次失败停在
failed；修复外部原因并授权后，可以显式重试：

```powershell
python $crossAgentCli retry-producer --run '<run-id>'
python $crossAgentCli next --run '<run-id>' --stream
```

显式重试只启动下一次调用，不追加自动重试；不会关闭 run 或删除 session。Reviewer
执行失败仍用 `retry-review`，保留 Producer，让之后的 feedback 返回它。没有结构化
输出、schema 校验失败、Reviewer 写文件等 guard 失败都不能通过 retry 绕过；用户
问题与 Producer blocker 仍等待真实回答。更新/部署 CLI 不需要重新 init，也不移动或
清理项目配置和 run 历史。


本次执行机制的自动化验证运行 `python -B -m unittest discover -s
skills/coding/cross-agent/scripts/tests`：70 项通过，覆盖假 provider 的恢复、feedback
回路、checkpoint、只读/schema guard、CLI 选择和真实子进程的硬 timeout。安装后另以
`status`、`start --dry-run` 与文件 hash 核对两端副本及旧 run 兼容性。模型原生的自动
Skill 选择、真实 Claude/Codex 的 checkpoint 和失效 session 恢复尚需实际运行验证；
本轮部署没有启动、关闭或修改现有 F05 run。

## 失败 Delivery 转回 Feature Plan

用户要求重新规划时，用 `park --run <delivery-id> --reason "<原因>"` 释放 artifact 锁；
run、原始 baseline、findings、剩余预算以及已有 session 全部保留。新版 Feature Plan
更新同一计划、拆分验收 session 后，另起 `feature-plan` run 审阅。只有它以
`independently-passed` 完成，才可 `resume-delivery --run <delivery-id>
--plan-run <plan-id> --request "<分段交接>"`。随后关闭已完成的 Plan run，再调用 Delivery
`next --stream`；Producer 会以新 session 开始，原交付审阅边界与预算不重置。
旧 diff size guard 可用 `--max-diff-kb <更大值>` 明确增加容量；schema、只读、snapshot
校验失败不可通过该入口恢复。30 分钟硬 timeout 不变。

验证记录：本次交接与 Windows 原子写入修复后，CLI 回归共 74 项通过。实机验证了
失败 Delivery 暂存、同一 Plan 的 Codex 独立审阅通过、恢复时新开 Producer、
S1/S2/S3 checkpoint 连续换新 session，以及原始交付 baseline 与 0/2 审阅预算保留。
原 run 的命令权限仍为启动时的快照；更新共享配置只影响新 run 的命令权限，
`[cli]` 路径仍实时读取，旧 run 的 review 容量只通过显式 handoff 参数增加。
被旧权限拒绝的 Workspace validator 由 Orch 执行并记录真实结果，不把拒绝算作通过。
