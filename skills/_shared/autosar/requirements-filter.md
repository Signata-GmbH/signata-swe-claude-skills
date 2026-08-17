# AUTOSAR requirements filter (by-module-filter scoping)

> Loaded when `project.type: autosar` (i.e. `requirements.scoping: by-module-filter`).
> On AUTOSAR projects the workbook has a reliable `aFunctionModule` column, so
> in-scope requirements are **filtered by module + variant** — not hand-listed.
> (The non-AUTOSAR flavor instead uses an explicit `SW_Req` ID list — see
> [../generic/requirements-scope.md](../generic/requirements-scope.md).)

## Workbook

- Path: `requirements.workbook` in `20_AI/ai_project.yaml` (e.g. `20_AI/SW_Requirements.xlsx`).
- Sheet: `Sheet1` (the only sheet in the workbook).

## Filter rule — keep only rows where ALL hold

| Column              | Condition |
| ------------------- | --------- |
| `aFunctionModule`   | equals the module — **scope differs per skill, see below** |
| `aStatusOfAnalysis` | **not** equal to `cancelled` (include `released`, `implemented`) |
| `aVariant`          | equals any entry in `requirements.variants` (from `ai_project.yaml`) |

### ⚠️ The variant-newline trap (MANDATORY)

A cell covering both variants is stored as a **two-line string with an embedded
newline** (`MQB` + `\n` + `CEA`) inside one cell — **not** space-separated. Match
the embedded newline exactly. `requirements.variants` in `ai_project.yaml` already
quotes it as `"MQB\nCEA"`; use that list verbatim.

### Scope differs per skill

- **Code Development** — `aFunctionModule == module.name` **OR** in
  `code_dev.related_modules` (manifest). Rows pulled in via a sibling must be
  flagged `(via <sibling>)` so the engineer can confirm scope. Uses
  `code_dev.expected_row_count`.
- **Code Review** — `aFunctionModule == module.name` **only** (no related
  modules). Uses `code_review.expected_row_count`. Because the scope is
  narrower, this count is normally lower than Code Dev's — they are not
  interchangeable.
- **Unit Test** — `aFunctionModule == module.name`, further narrowed by
  `unit_test.requirement_filter` (manifest) if it is a specific ID list.

## Row-count guard

State the resulting row count. Compare against the relevant `expected_row_count`
in the module manifest:
- If the manifest value is a number and the actual count **differs**, STOP and
  report it (the filter or the expected count is stale) before proceeding.
- If the manifest value is `"?"`, report the actual count and write it back as
  the learned value.
- If the count is **zero**, STOP and raise it — the filter criteria are almost
  certainly wrong, not the workbook empty.

## Columns to read from each surviving row

`ID` · `L3 software requirements` · `aTestCriteria` · `aRequirementObjectType` ·
`aC_SAF` (safety classification) · `aComment` · `aRisk` · `aVariant` ·
`aFunctionModule` · `aStatusOfAnalysis`.

## Reference filter snippet (note the real `\n` in the variant set)

```python
from openpyxl import load_workbook

# workbook + variants come from 20_AI/ai_project.yaml
wb = load_workbook("<requirements.workbook>", read_only=True, data_only=True)
ws = wb["Sheet1"]
rows = list(ws.iter_rows(values_only=True))
header = rows[0]

idx = {name: header.index(name) for name in (
    "ID", "L3 software requirements", "aTestCriteria", "aVariant",
    "aFunctionModule", "aRequirementObjectType", "aStatusOfAnalysis",
    "aComment", "aRisk", "aC_SAF",
)}

MODULE = "<module.name>"
RELATED_MODULES = set()            # code-dev only: from code_dev.related_modules
MODULE_SCOPE = {MODULE} | RELATED_MODULES
ALLOWED_VARIANTS = {"MQB", "MQB\nCEA"}   # from requirements.variants — real newline

filtered = [
    r for r in rows[1:]
    if  r[idx["aFunctionModule"]]    in MODULE_SCOPE
    and (r[idx["aStatusOfAnalysis"]] or "").lower() != "cancelled"
    and r[idx["aVariant"]] in ALLOWED_VARIANTS
]
print(f"Row count: {len(filtered)}")   # compare to expected_row_count
```
