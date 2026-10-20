# 部署脚本

两种作用域，各用各的脚本：

| 脚本 | 作用域 | 装到哪 |
|---|---|---|
| `Install-Skills.ps1` | 单个项目 | `<project>/.claude/skills/` |
| `Deploy-Skills.ps1` | 整台机器 | `~/.copilot/skills/`、`~/.claude/skills/` 等 |

装到项目里的 skill 只在那个项目可见；装到机器上的对所有项目可见。两者可以并存，
但同名 skill 会重复出现，选一种为主。

## 整机部署配置

`Deploy-Skills.ps1` 不自动扫描仓库。它只部署
`scripts/deploy-skill/deploy-skills.json` 中明确列出的本仓库 mapping，以及由
其中 `externalSkillConfigPath` 指定（省略时默认为
`scripts/external-skills/external-skills.json`）的 public Git Skills，
并在每个目标目录中写入记录已部署名字的
`.skill-collection-deployment.json`。每个启用的目标目录由本仓库独占管理：真实部署
会先清空目录里的所有条目，包括其他来源的 Skill，再复制配置的 Skill。预览会列出
将被清空的条目。

`retiredSkillNames` 用于在预览里标出此前由本仓库管理、现在已退役的名字，不要把
Copilot、Claude、Codex 或其他仓库提供的 Skill 放进去。

```json
{
  "externalSkillConfigPath": "scripts/external-skills/external-skills.json",
  "retiredSkillNames": ["old-collection-skill"],
  "skills": [
    {
      "source": "skills/coding/10.product-brief",
      "name": "product-brief"
    }
  ]
}
```

`deploy-skills.example.json` 是提交到 Git 的模板；实际使用的
`deploy-skills.json` 是本机文件，已被 gitignore。新机器先复制模板：

```powershell
Copy-Item scripts/deploy-skill/deploy-skills.example.json scripts/deploy-skill/deploy-skills.json
```

新增 Skill 不会自动进入个人全局环境，必须明确加入本机 `deploy-skills.json`；
如果希望新机器也默认带上，同时更新模板。`source` 是仓库相对路径，`name` 必须与
对应 `SKILL.md` frontmatter 一致，也是目标目录名。

## 部署目标

本机 `deploy-skills.json` 的 `targets` 决定部署到哪些工具。没有列出的工具不部署；
每次部署会先清空所有启用的目标目录：

```json
"targets": {
  "copilot": { "enabled": true },
  "claude": { "enabled": false },
  "agents": { "enabled": false, "path": "~/.agents/skills" }
}
```

| 键 | 工具 | 默认目录 |
|---|---|---|
| `copilot` | GitHub Copilot | `~/.copilot/skills` |
| `claude` | Claude Code | `~/.claude/skills` |
| `agents` | Codex / Agents | `~/.agents/skills` |

`path` 可选，开头的 `~` 表示用户目录。路径优先级：命令行参数、旧的
`deploy-paths.json`、`targets.<tool>.path`、默认目录。配置里没有 `targets` 时，
沿用旧行为，部署到 Claude Code 和 Codex / Agents。`-Target copilot|claude|agents`
只部署指定的一个工具，忽略 `enabled`。

停用一个目标不会清理它的目录，原有 Skill 会留在那里且不再更新。如果客户端同时读取
多个目录，可能看到重复或过时的 Skill。

## Public Git Skills

Public Skills 使用独立配置和 machine-local cache：

```json
{
  "schemaVersion": 1,
  "skills": [
    {
      "name": "ponytail",
      "repository": "https://github.com/DietrichGebert/ponytail.git",
      "branch": "main",
      "skillPath": "skills/ponytail",
      "licensePath": "LICENSE"
    }
  ]
}
```

`Sync-ExternalSkills.ps1` 将仓库克隆到
`scripts/external-skills/cache/<name>/`。已有 cache 只有在 remote、branch 和配置
一致且 worktree 干净时才执行 `git pull --ff-only`；本地改动、错误 remote、错误
branch 或 non-fast-forward update 都会停止。配置删除后 cache 会保留，不会自动删除。

单独同步或只查看 cache：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/external-skills/Sync-ExternalSkills.ps1 -ListOnly
powershell -ExecutionPolicy Bypass -File scripts/external-skills/Sync-ExternalSkills.ps1
```

实际运行 `Deploy-Skills.ps1` 时会先自动同步 external Skills，再与本仓库 Skills 一起
部署。`-ListOnly` 只读取当前 cache，不 clone、不 pull、也不写目标目录。首次 cache
缺失时，可先运行上述同步脚本，再重新预览部署。配置 `licensePath` 后，上游许可证会
作为 `UPSTREAM-LICENSE` 一起复制到目标 Skill 目录。

`skills/coding/skill-deployment` 是本仓库的维护指导，不属于任何全局或项目
预设 mapping。它通过以下项目级发现路径安装，只在打开本仓库时可用：

| 平台 | 此仓库内的路径 |
|---|---|
| GitHub Copilot | `.github/skills/skill-deployment/` |
| Claude Code | `.claude/skills/skill-deployment/` |
| Codex / Agents | `.agents/skills/skill-deployment/` |

运行 `scripts/deploy-skill/Install-WorkspaceSkill.ps1` 会从
`skills/coding/skill-deployment/` 同步到这三个路径。生成目录不提交；权威源始终是
`skills/coding/skill-deployment/`。打开本仓库时，`AGENTS.md` 也会将部署请求路由到
它；离开本仓库后，它不会作为可调用的已部署 Skill 存在。

部署前先预览，确认显示的 `managed stale skill` 都属于本仓库，再执行实际同步：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-skill/Deploy-Skills.ps1 -ListOnly
powershell -ExecutionPolicy Bypass -File scripts/deploy-skill/Deploy-Skills.ps1
```

部署目标见上文"部署目标"。运行 `Deploy-Skills.ps1 -ListOnly` 可查看最终 Skill
mapping 和目标目录，且不会联网或写文件。

## 项目级安装

```powershell
# 在项目根目录，链接 coding 预设的 4 个 skill
d:\code\personal-projects\skill-collection\scripts\Install-Skills.ps1

# 先看会装什么，不写任何文件
.\Install-Skills.ps1 -List

# 指定项目、只装一部分
.\Install-Skills.ps1 -ProjectPath D:\code\work-projects\wms -Skill skills/coding/10.product-brief,skills/coding/20.feature-map

# 拆掉
.\Install-Skills.ps1 -Uninstall
```

## Link 还是 Copy

| | `-Mode Link`（默认） | `-Mode Copy` |
|---|---|---|
| 机制 | 目录 junction 指回本仓库 | 复制一份进项目 |
| 改了 skill 之后 | 所有项目立即生效 | 每个项目要重跑一次 |
| 能否提交进项目仓库 | 不能，必须 gitignore | 能，而且是固定版本 |
| 适合 | 你还在迭代这套 skill | 项目要自包含、可复现、给别人用 |

单人日常开发用 `Link`：一个源头，`git pull` 一次全部项目更新，不会出现五份互相
漂移的副本。要把某个项目冻结成可复现状态时再用 `Copy`。

用 `Link` 时把目标目录加进项目的 `.gitignore`：

```gitignore
.claude/skills/
```

## 预设

`skill-presets.json` 定义预设和各工具的目标目录。仓库以后加 `writing/`、`data/`
这类分类时，在这里加一个预设即可，安装命令不用改：

```json
"presets": {
  "coding": ["skills/coding/10.product-brief", "..."],
  "writing": ["writing/xxx"]
}
```

也可以绕过预设直接点名：

```powershell
.\Install-Skills.ps1 -Skill skills/coding/30.feature-plan,skills/coding/40.feature-delivery
```

`targets` 里只有 `claude` 的路径是确认过的。用 `-Tool copilot` 或 `-Tool agents`
之前，先把对应路径改成你实际使用的布局。

## 数字前缀会被去掉

仓库里的目录带排序前缀，安装时自动去掉，使目录名和 `SKILL.md` 里的 `name` 一致：

```text
skills/coding/10.product-brief  ->  .claude/skills/product-brief
```

新增 skill 时保持 `<数字>.<name>` 或直接 `<name>` 都可以。

## 归档内容不参与部署

`skills/coding/_obsolete/` 只保存旧流程作为历史证据。部署和项目安装都只读取显式
mapping，不会扫描或安装归档内容。
