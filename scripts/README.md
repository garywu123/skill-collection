# 部署脚本

两种作用域，各用各的脚本：

| 脚本 | 作用域 | 装到哪 |
|---|---|---|
| `Install-Skills.ps1` | 单个项目 | `<project>/.claude/skills/` |
| `Deploy-Skills.ps1` | 整台机器 | `~/.claude/skills/` 等 |

装到项目里的 skill 只在那个项目可见；装到机器上的对所有项目可见。两者可以并存，
但同名 skill 会重复出现，选一种为主。

## 整机部署配置

`Deploy-Skills.ps1` 不自动扫描仓库。它只部署本机
`deploy-skills.json` 中明确列出的 mapping：

```json
{
  "skills": [
    {
      "source": "coding/20.project-map",
      "name": "project-map"
    }
  ]
}
```

从 `deploy-skills.example.json` 复制出真实配置。真实配置已被 Git
忽略；新增 Skill 不会自动进入个人的全局环境，必须明确加入 mapping。
`source` 是仓库相对路径，`name` 必须与对应 `SKILL.md` frontmatter
一致，也是目标目录名。

目标目录仍由 `deploy-paths.json` 控制；未配置时使用
`~/.copilot/skills`、`~/.claude/skills` 和 `~/.agents/skills`。运行
`Deploy-Skills.ps1 -ListOnly` 可查看最终 Skill mapping 和目标目录，且
不会写文件。

## 项目级安装

```powershell
# 在项目根目录，链接 coding 预设的 7 个 skill
d:\code\personal-projects\skill-collection\scripts\Install-Skills.ps1

# 先看会装什么，不写任何文件
.\Install-Skills.ps1 -List

# 指定项目、只装一部分
.\Install-Skills.ps1 -ProjectPath D:\code\work-projects\wms -Preset coding-minimal

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
  "coding": ["coding/05.product-discovery-roadmap", "..."],
  "writing": ["writing/xxx"]
}
```

也可以绕过预设直接点名：

```powershell
.\Install-Skills.ps1 -Skill coding/20.project-map, coding/spec-sync
```

`targets` 里只有 `claude` 的路径是确认过的。用 `-Tool copilot` 或 `-Tool agents`
之前，先把对应路径改成你实际使用的布局。

## 数字前缀会被去掉

仓库里的目录带排序前缀，安装时自动去掉，使目录名和 `SKILL.md` 里的 `name` 一致：

```text
coding/05.product-discovery-roadmap  ->  .claude/skills/product-discovery-roadmap
```

新增 skill 时保持 `<数字>.<name>` 或直接 `<name>` 都可以。

## 操作指南不参与部署

`coding/00_instructions/` 里的六份场景指南是给人看的，留在本仓库
读即可。它们内部链接指向各 skill 的 reference 文件，复制进项目会断链，而且会在每个
项目里留下一份还在演进的文档副本。
