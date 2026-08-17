# non-AUTOSAR requirements scope (explicit-id-list)

> Loaded when `project.type: nonautosar` (i.e. `requirements.scoping:
> explicit-id-list`). On non-AUTOSAR projects the workbook's metadata columns
> (`aSubsystem`, `aFunctionModule`, `aFeature`, …) are **not standardised** — you
> **cannot** reliably filter a module by column. Scope is given explicitly.
> (The AUTOSAR flavor instead filters by module + variant — see
> [../autosar/requirements-filter.md](../autosar/requirements-filter.md).)

## Workbook

- Path: `requirements.workbook` in `20_AI/ai_project.yaml` (e.g. `20_AI/SW_Requirements.xlsx`).
- Each row has an `ID` column (`SW_Req-<n>`) and a `Requirements` column
  (section-numbered text). It is binary `.xlsx` — read it with `openpyxl` (via the
  project venv if one is configured), not a plain file reader.

## Scope source (from the manifest)

Use exactly what the manifest provides for the workflow section, in this order:

1. **`sw_req_ids`** — an explicit list of in-scope `SW_Req` IDs. Treat exactly
   those rows as the complete, authoritative set. Look each ID up and read its
   full text. **If a listed ID is not found in the sheet, that is a blocking
   Phase-1 question** — do not silently drop it.
2. **`release_filter`** (when IDs are not hand-enumerated) — e.g.
   `aRequiredForRelease == "B0-Sample"`. **Confirm the exact string first** (dump
   the column's distinct values — it is hyphenated `"B0-Sample"`, not
   `"B0_Sample"`). Then narrow to the module with a **code-grounding cross-check**:
   does the module's `.c` actually implement what the requirement describes?
   **Report the derived ID list in Phase 1 for confirmation** — never treat a
   derived list as pre-approved.

## Requirements-vs-code gaps

A row tagged to the module whose behaviour has **no corresponding implementation**
in the current `.c` is a real requirement-vs-code gap — **flag it in Phase 1**
rather than authoring a placeholder/fabricated artifact, unless the engineer asks
for one.

## German signal shorthand

Requirements may name signals in German (`SollPos`, `NLF`, `BF`, `RF`, `SHB`,
`Spulen`, …). Map each to its LDF signal + generated accessor explicitly and show
the mapping in Phase 1 (per [project-context.md](project-context.md) grounding).

## Columns to read from each in-scope row

`ID` · `Requirements` (the spec text) · plus any populated acceptance-criteria /
comment column the row carries. Record the ID for traceability; the metadata
columns are informational only (not a filter).
