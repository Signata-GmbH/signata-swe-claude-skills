# Module location — resolve `module.path`, never assume `layout.app_root`

> Loaded by every skill that touches a module's source. The layer a module lives
> in (application, BSW, CDD, MCAL, ...) is **not** derivable from the module name
> or from the requirements workbook, and `layout.app_root` is only the application
> root. Resolve the module's own folder once, record it in the manifest as
> `module.path` (repo-relative; the folder that owns the module's files), and use it for
> every later read or write. Applies to **both** flavors (`project.type: autosar`
> and `nonautosar`); only the folder shape differs (below).

## Folder shape by flavor

`module.path` is the folder that **owns** the module's files, whatever the shape:
- **autosar** — `<module.path>/inc/<MODULE>.h`, `<module.path>/src/<MODULE>.c`
  (+ `mak/`); `module.path` is the folder *above* `inc/`/`src/`.
- **nonautosar** — typically `<MODULE>.c`, `<MODULE>.h`, `<MODULE>_cfg.h` together
  (flat, or with its own `inc/`/`src/`); `module.path` is the folder holding them.
  Do not require `inc/`/`src/` to exist.

## Resolution order

1. **Manifest** — `module.path` already set → use it; confirm it exists on disk.
2. **Search the repo** for an existing implementation: glob
   for `<MODULE>.c` / `<MODULE>.h` at any depth (e.g. `**/<MODULE>.c`,
   `**/<MODULE>/**/<MODULE>.c`), then derive `module.path` per the shape above.
   Non-AUTOSAR names carry a project prefix (`SAPF_<Module>`) — also try the
   bare module name and the prefixed form. Exclude test,
   output and generated trees (`00_SW/06_Test/**`, `00_SW/05_Output/**`,
   `10_Test/**`, `Polyspace/**`, `ECU_Extract/**`, `*.drs`, and stub folders such
   as `layout.stubs`). Also try a case-insensitive match
   on the folder name — workbook names and folder names can differ in case or
   prefix (e.g. `CDD_ECUStateHandler` vs `CDD_EcuStateHandler`) — and **list every
   near match**. Exactly one hit → the module. Several → ask which.
3. **Not found** → behaviour depends on the skill:
   - **Creating skills (`code-dev`)** — **ask the engineer for the path** where
     the module is to be created. Never fall back silently to `layout.app_root`.
     Offer a **suggestion only**, derived by pattern from where sibling modules
     live (a `CDD_` prefix → the folder holding the other `CDD_*` modules; a name
     matching a folder under the app root → that root; non-AUTOSAR: `layout.app_root`,
     e.g. `00_SW/01_APPL`, when sibling `SAPF_*` modules sit there), show the evidence, and let
     the engineer accept or type another path. Nothing inferable → ask with no
     suggestion.
   - **Skills that need existing code (`code-fix`, `code-review`, `unit-test`,
     `integration-test`)** — ask the engineer for the existing path (offer the
     near matches). If they confirm there is no implementation, stop: `code-fix`
     routes to `/code-dev`; the others cannot proceed without code.

Record the confirmed `module.path` in the manifest and in the gate summary.

## Existing implementation

When code already exists at the resolved path, a creating skill must **not**
create a new module or overwrite files: it evaluates the current version against
the requirements and other inputs and proposes targeted changes
(`task_mode: feature-or-update`). A from-scratch regenerate needs an explicit
engineer request and confirmation, and is never the default.
