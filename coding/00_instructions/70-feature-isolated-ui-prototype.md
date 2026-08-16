# Example 7：共享 Host 下按 Feature 隔离的 UI Prototype

## 场景

一个 WMS 已经有 approved product UI structure，以及 `F101 Receive Goods`
和 `F102 Confirm Putaway` 的 approved feature wireframes。人类希望直接查看和
修改每个 feature 的 AI 理解，不希望为了进入目标页面而重复登录、选择仓库、
打开菜单或完成上游 feature。

原型因此使用一个共享 Prototype Host。Host 只统一产品 frame、tokens、术语、
Demo 首页和 feature registry；每个 feature 独立拥有 screens、presentation state、
components、fixtures 与 scenarios。Web 原型可能提供以下直接入口：

```text
/prototype                              # Demo 首页
/prototype/features/F101                # F101 初始状态
/prototype/features/F101?scenario=empty # F101 empty scenario
/prototype/features/F102?scenario=error # F102 error scenario
```

这些路径是 review entry，不要求复刻生产应用的完整导航流程。登录状态、已有 ASN、
已分配库位等前置条件由确定性的 fake scenario 建立。

## 三个模式维度

不要把 operation、source status 和 validation profile 混成一个“模式”。这些是
AI 根据请求与 repository state 解析的内部路由，不是人类每次必须声明的参数。
人类只需描述目标、范围和特殊要求；没有额外要求时，AI 使用 approved source
和 `run_only`。

| 维度 | 可选值 | 含义 |
|---|---|---|
| Operation | `bootstrap` | 首次建立共享 Host、Demo 首页、registry、scenario launcher 和一个 feature demo |
| Operation | `feature` | 在现有 Host 中增加或更新一个 feature demo；默认不修改其他 feature |
| Operation | `revise` | 根据明确的 reviewed feedback 或 approved source change 修改受影响 feature |
| Source mode | `reviewable` | 输入来源已 approved；原型可用于正式的人类 UI review，但不是 canonical product truth |
| Source mode | `exploratory` | 人类明确授权使用未批准来源；Host 和 manifest 必须明显标记 exploratory |
| Validation | `run_only` | 默认；证明 Host 能启动、目标 direct entry 能打开并完成 initial render，不创建自动化测试；仍遵守目标仓库已有的强制检查 |
| Validation | `extended` | 仅在人类明确要求额外证据时使用；在 `run_only` 基础上执行点名的额外检查或 artifacts |

`extended` 不代表生产就绪、feature acceptance 或自动授权后续实现阶段。

## 自然语言请求与自动路由

AI 先读取目标 repository guidance 和 `prototype/prototype.yaml`，再选择 operation。
不要仅因为人类没有说出 `bootstrap`、`feature` 或 `revise` 就暂停。

| 请求与当前状态 | AI 自动选择 |
|---|---|
| “为 F101 创建 prototype”，当前没有 Host/manifest | `bootstrap`，同一次建立 Host 和 F101；不要求随后再调用 `feature F101` |
| “为 F102 创建 prototype”，Host 已存在但 registry 没有 F102 | `feature`，隔离增加 F102 |
| “按这轮反馈修改 F101”，manifest 已有 F101 | `revise` |
| “打开/看看 F101 prototype”，manifest 已有 F101，且没有 change | 启动或报告现有 direct entry，不伪造 `revise` |

如果人类只说“根据 approved roadmap 帮我先创建一个 prototype”，AI 按 roadmap
顺序选择第一个 UI surface 适用且 required UI sources 已批准的 feature，说明选择
结果并继续。只有 roadmap 没有顺序、候选项并列，或者没有 feature 具备必要来源时，
才询问真正阻塞选择的问题。

显式 operation 名称仍可作为 override 或排错工具，但不是正常使用的前提。AI 默认
完成一个 bounded feature demo 后停止供人评审，不因为 roadmap 中还有其他 feature
就自动继续构建。

## 使用案例

### 1. Bootstrap：建立 Host 和第一个 Feature

自然语言请求示例：

```text
请根据 approved product UI structure 和 F101 wireframes，帮我为 F101 创建一个
可以直接运行和查看的 UI prototype。不要创建自动化测试；能启动并打开 F101
初始页面后就交给我评审。
```

AI 发现没有 `prototype/prototype.yaml` 或 Host，因此内部选择 `bootstrap`，默认
validation 为 `run_only`。人类不需要先要求 bootstrap，再要求创建 F101。

AI 只读取产品 shell、目标 stack evidence、F101 来源和必要的 shared patterns。
典型产物为：

```text
prototype/
  prototype.yaml
  src/
    shared/
      shell/
      tokens/
      feature-registry.*
    features/
      F101/
        screens/
        components/
        scenarios/
        fixtures/
```

完成点是 Demo 首页与 F101 direct entry 可运行，manifest 记录实际命令和
`human_review: pending`。AI 不继续构建 F102，也不宣布 F101 accepted。

### 2. Feature：隔离增加第二个 Feature

自然语言请求示例：

```text
请根据 F102 的 approved wireframes，把 F102 prototype 加到现有 Demo 首页。
我希望能直接进入 F102，不要为了模拟完整流程实现登录、菜单或 F101，也不要
修改与 F102 无关的部分。能运行后交给我评审。
```

AI 从 manifest 发现 Host 已存在、F102 尚未注册，因此内部选择 `feature` 和默认
`run_only`。

AI 先读取 `prototype/prototype.yaml`，然后只读取 F102 roadmap/wireframe anchors
和受影响代码。F102 所需的“已有待上架库存”由 F102 fake scenario 建立，不通过
执行 F101 获得。若 shared frame 确实必须改变，报告修改位置和现有 consumers，
但不要顺便重构其他 feature。

完成点是 F101 仍可从 Demo 首页进入、F102 有独立 direct entry、F102 initial
render 成功，并且 manifest 只增加或更新对应记录。F101 的交互回归由人类决定
是否检查；`run_only` 不自动扩大为跨 feature 测试。

### 3. Revise：根据评审只修改一个 Feature

自然语言请求示例：

```text
根据本轮 reviewed feedback 修改 F101：把 quantity validation 改为 inline
message，并保留提交后的 confirmation。只修改受影响的 F101 内容，能运行后
交给我重新评审。
```

AI 从 manifest 发现 F101 已存在，并且请求包含明确 change，因此内部选择
`revise` 和默认 `run_only`。

AI 不重读完整 PRD、Roadmap 或全部 app tree，也不把人类反馈静默写回 canonical
wireframes。若反馈改变了 approved behavior、safety rule 或 operator-visible result，
停止并指出需要先修订的 authoritative source。

完成点是修改后的 F101 initial entry 可运行，manifest 记录 feedback/source anchor、
实际 smoke result 和仍待人类验证的内容。

## Exploratory 与 Extended 变体

当 wireframes 尚未批准，但人类想先比较概念时，可以明确调用：

```text
F101 wireframes 还没有批准，但我想先做一个探索性 prototype 比较概念。请基于
这个 draft 建立隔离 demo，并明显标记它不是正式设计。
```

AI 从“探索性”和“尚未批准”解析出用户已明确授权 `exploratory`；若 Host 不存在，
同时自动选择 `bootstrap`。

Exploratory 原型不能自动转成 `reviewable`。来源批准后，人类另行调用 `revise`，
由 AI 对照 approved anchors 更新原型与 manifest。

只有需要额外证据时才使用 `extended`，并点名范围，例如：

```text
修改 F101 后，除了确认它能启动和打开，请再运行现有 typecheck，并截图 success
与 error scenario。不要新增自动化测试。
```

AI 从额外 typecheck 和截图要求解析出 `extended`，并根据 manifest 与 change
内容自动选择 `revise`。

如果人类明确要求某个 navigation 或 safeguard 自动化测试，`extended` 才包含该
测试。没有明确授权时，AI 只能建议测试，不能自行增加。

## 每次调用的停止点

每个 operation 都更新 `prototype/prototype.yaml`，报告 Host、feature、scenario IDs、
direct entry、实际命令、smoke-open 结果、未请求或实际执行的自动化检查，以及下一步
人类 review。随后停止；不实现 backend、不修改 canonical product artifacts、不推进
feature lifecycle，也不自动调用下一个 operation。
