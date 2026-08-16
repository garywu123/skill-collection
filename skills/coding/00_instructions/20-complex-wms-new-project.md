# Example 2：新建复杂 WMS

## Discovery 阶段就识别 domain

对话描述了 ASN 收货、上架策略、库位库存、分配、拣选、复核、装运、审计追踪和外部 ERP/设备集成。Discovery 先建立共同词汇，并把可能的 domain 作为待验证边界，例如：

- `inbound-receiving`
- `putaway`
- `inventory`
- `allocation`
- `picking`
- `shipping`
- `integration`（若它确实拥有业务行为；纯技术连接仍属于 Architecture）

这些是 discovery hypothesis，不是已批准 Roadmap。PRD 批准产品行为后，`draft-roadmap` 才为 cohesive features 分配 F-ID。

## 顺序、模式与产物

| Step | 人类调用 | AI 判断/模式 | 主要产物 |
|---|---|---|---|
| 1 | `$project-map init` | profile 暂缺 | routing-only map/guidance |
| 2 | `$product-discovery-roadmap discover` | 单 discovery；按 domain 批次收敛 | discovery notes + 必要的 `doc/domain/*.md` |
| 3 | `draft-prd` | Full；需求多或 domain 可并行时 split | PRD root + domain requirement members |
| 4 | `approve-prd` | 人类审批 | approved PRD bundle |
| 5 | `draft-roadmap` | Full；先拆 domain-sized 候选，再按 domain split bundle | roadmap root + `doc/roadmap/<domain>.md` |
| 6 | `approve-roadmap` | 人类审批 | approved feature boundaries/order |
| 7 | `$architecture-baseline create` | Full；多 domain/deployable、外部合同与一致性决策需要 ADR | baseline root、domain details、proposed ADRs |
| 8 | `approve`，再 `$project-map refresh` | 记录 profile/path/state | refreshed map/guidance |
| 9 | `$feature-implementation-plan plan F0XX` | 通常仍是 compact | 该 feature 的 plan + checklist |

Full 主要增加的是必要的 domain member files 与 ADR；它不要求每个 feature 都创建 Spec Kit 文件。即使 WMS 很大，只要 `F0XX` 是一个 cohesive outcome，仍可采用 compact。

## 典型输出树

```text
doc/
  product-discovery-notes.md
  domain/warehouse-terms.md
  general-product-requirement.md          # PRD root
  requirements/inbound.md
  requirements/putaway.md
  requirements/inventory.md
  feature-roadmap.md                      # control rows + Domain Registry
  roadmap/inbound-receiving.md
  roadmap/putaway.md
  roadmap/inventory.md
  architecture-baseline.md
  architecture/putaway.md
  architecture/integration.md
  adr/0001-inventory-consistency.md
specs/F0XX-confirm-putaway/
  implementation-plan.md
  checklist.md
```

Roadmap root 只拥有 routing、domain、requirement ownership、dependency、delivery/UI 控制字段；domain member 只拥有 feature description 与 acceptance，避免重复。
