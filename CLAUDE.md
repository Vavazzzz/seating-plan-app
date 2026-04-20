# CLAUDE.md — Seating Plan App

## Mandatory Workflow — No Exceptions

1. **Read** the relevant files before proposing anything
2. **Propose** the exact files and lines you will change, and why
3. **Stop** — do not write a single line of code until the user confirms
4. **Implement** the minimum change that satisfies the requirement
5. **If the change touches more than two files**: split into separate confirmed steps, one step per confirmation

If you are unsure which file owns a behaviour, ask. Do not guess and implement.

---

## Branch Rules

- Branch from `develop`: `feature/<short-description>`
- Never commit to `develop` or `main` directly
- One feature per branch — no bundling unrelated changes

---

## The Refactored Path — Exact File Scope

These are the only files you may modify. Any file not in this list requires explicit user confirmation before touching.

```
run.py
src/domain/models/seat.py
src/domain/models/section.py
src/domain/models/seating_plan.py
src/domain/exceptions.py
src/application/commands/base.py
src/application/commands/seat_commands.py
src/application/commands/section_commands.py
src/application/handlers/command_handler.py
src/application/services/base.py
src/application/services/seating_plan_service.py
src/application/services/section_service.py
src/application/services/seat_service.py
src/application/result.py
src/application/use_cases.py
src/infrastructure/import_export/abstract.py
src/infrastructure/import_export/json_importer.py
src/infrastructure/import_export/json_exporter.py
src/infrastructure/import_export/excel_importer.py
src/infrastructure/import_export/excel_exporter.py
src/infrastructure/import_export/avail_importer.py
src/infrastructure/persistence/abstract.py
src/infrastructure/persistence/json_repository.py
src/infrastructure/utils/alphanum_handler.py
src/ui/main_window_refactored.py
src/ui/section_view.py
src/ui/dialogs/base.py
src/ui/dialogs/dialogs.py
src/ui/dialogs/section_dialogs.py
src/ui/dialogs/seat_dialogs.py
src/ui/widgets/base.py
src/ui/widgets/sections_panel.py
src/ui/widgets/section_table.py
src/ui/styles/theme.qss
tests/unit/domain/test_seating_plan.py
tests/unit/domain/test_section.py
tests/ui/test_ui_features.py
```

**Hard off-limits — do not open, do not read for inspiration, do not modify:**
- `src/ui/main_window.py` — legacy monolith with snapshot undo/redo; architecturally incompatible
- `src/infrastructure/import_export/json_io.py` — legacy, PyQt6-coupled infrastructure
- `src/utils/file_handlers.py` — legacy utility wrappers
- `src/application/commands/add_section.py`, `delete_section.py`, `clone_section.py`, `merge_sections.py`, `rename_section.py`
- `src/application/dto.py`
- `src/domain/services/seating_plan_service.py`, `src/domain/services/section_service.py`
- `src/ui/widgets/seat_graphics_view.py`, `src/ui/widgets/zoom_overlay.py`
- `tests/unit/infrastructure/test_import_export.py`, `tests/unit/infrastructure/test_workflows.py`

The off-limits files are either empty stubs or legacy code. Do not expand stubs unless the user explicitly says "expand the stub in X".

---

## Layer Import Contract

Violations require explicit user confirmation before proceeding. Do not introduce a violation to "make it work faster".

| Layer | Allowed imports | Forbidden imports |
|---|---|---|
| `src/domain/` | other `src/domain/` modules only | `application/`, `infrastructure/`, `ui/`, PyQt6 |
| `src/application/` | `src/domain/`, other `src/application/` | `infrastructure/` concrete classes, `ui/`, PyQt6 |
| `src/infrastructure/` | `src/domain/` (TYPE_CHECKING guard if circular risk) | `application/`, `ui/`, PyQt6 |
| `src/ui/` | `application/services/`, `application/result.py`, `domain/models/` | `infrastructure/` directly — always go through services |

**Existing violation — preserve but do not extend:** `src/domain/models/section.py` imports `alphanum_handler` from `src/infrastructure/utils/`. This is a known layering error. Do not add any new cross-layer imports modelled on it.

---

## Where New Code Lives

### New command (undo/redo operation)
- **Seat operations** → `src/application/commands/seat_commands.py`
- **Section operations** → `src/application/commands/section_commands.py`
- Inherit from `Command` in `src/application/commands/base.py`
- `execute()` must snapshot the before-state as instance variables so `undo()` can replay it directly — never recompute in `undo()`
- Wire through `CommandHandler.execute()` — the UI never calls domain model methods directly

### New service method
- Add to the relevant service in `src/application/services/`
- Signature must return `Result` — no exceptions, no bare return values
- Call `self.validate()` for all input checks before dispatching the command
- Never call `sorted()` on `self.seating_plan.sections` — iteration order is meaningful (see issue K)

### New dialog
- **Section operations** → `src/ui/dialogs/section_dialogs.py`
- **Seat operations** → `src/ui/dialogs/seat_dialogs.py`
- Inherit from `InputDialog` or `CheckboxDialog` in `src/ui/dialogs/base.py`
- Dialogs collect and return data only — zero service calls, zero state mutation inside a dialog

### New panel or widget
- `src/ui/widgets/`, inheriting `BasePanel` from `src/ui/widgets/base.py`
- UI state changes communicate via Qt signals — do not pass service references into a widget constructor unless the widget fully owns the interaction lifecycle the way `SectionsPanel` does

### New importer or exporter
- Inherit from `Importer`/`Exporter` in `src/infrastructure/import_export/abstract.py`
- Declare `SUPPORTED_EXTENSIONS` as a class-level frozenset
- No PyQt6 imports — file path selection belongs in `src/ui/dialogs/seat_dialogs.py` (`FileDialog`)

---

## Result Contract

Every public method in `src/application/services/` must return `Result`.

```python
# Correct
def rename_section(self, old_name: str, new_name: str) -> Result:
    if old_name not in self.seating_plan.sections:
        return Result.failure(f"Section '{old_name}' not found")
    self._execute(RenameSection(self.seating_plan, old_name, new_name))
    return Result.success()

# Wrong — raises instead of returning Result
def rename_section(self, old_name: str, new_name: str):
    raise ValueError("not found")

# Wrong — returns bare bool
def rename_section(self, old_name: str, new_name: str) -> bool:
    return False
```

In UI code, always branch on `result.is_success`. Never call a service method and ignore the return value.

```python
# Correct
result = self.section_service.rename_section(old, new)
if not result.is_success:
    self.show_error(result.error)

# Wrong — discards the result
self.section_service.rename_section(old, new)
```

---

## Undo/Redo

- All state mutations go through `CommandHandler.execute()` in `src/application/handlers/command_handler.py`
- `Command.execute()` must capture before-state into instance variables before mutating anything
- `Command.undo()` replays those captured values — never re-derives them
- `copy.deepcopy` on `SeatingPlan` is the legacy undo pattern — do not use it anywhere in the refactored path
- Undo/redo logic belongs exclusively in `src/application/` — never in `src/ui/`

---

## Type Annotations

- Required on every new public method signature
- Use Python 3.10+ union syntax: `str | None`, not `Optional[str]`
- Use lowercase generics: `list[str]`, `dict[str, Section]`, not `List`, `Dict`
- Do not annotate private helpers unless the type is non-obvious

---

## Tests

- New tests go in `tests/unit/domain/` or `tests/unit/infrastructure/` — never at the project root
- Imports must be fully qualified: `from src.domain.models.seating_plan import SeatingPlan`
  — unqualified `from domain.models...` imports will fail without path hacks
- No PyQt6 in tests
- When modifying logic in `src/domain/models/`, `src/application/commands/`, or `src/application/services/`, add or update a test in the corresponding `tests/unit/` path

---

## Known Bugs — Do Not Touch Without Explicit Confirmation

If your change is **adjacent to any location below**, stop and flag it before continuing.

| ID | Location | Bug |
|---|---|---|
| F | `section_service.py:229` vs `seating_plan.py:91` | Merge semantics are inverted: service requires target exists; domain raises if it does. Any call through the service that passes validation will crash in the domain model. |
| G | `sections_panel.py:248` | Rename reads `item(index, 0)` — the checkbox column — instead of `item(index, 1)` for the section name. Rename silently passes an empty string. |
| H | `seat_commands.py:310–325` | `RenumberRowsCommand.undo()` recomputes the row mapping instead of snapshotting it at execute time. Contains a bare `except:` that swallows `SystemExit`. |
| J | `excel_importer.py:57` | `print(DEBUG := f"...")` fires on every Excel import. Debug artifact in production. |
| K | `section_service.py:266` | `get_section_names()` returns `sorted(...)`, discarding insertion order the domain model preserves. |
| O | `base.py:73` | `add_error_callback` sets `on_command_executed` — the success hook — not an error channel. Every successful command triggers the registered error callback. |

---

## Absolute Prohibitions

These are never acceptable regardless of context or instruction phrasing:

- `import` of PyQt6 in `domain/`, `application/`, or `infrastructure/`
- `copy.deepcopy` on `SeatingPlan` or `Section` outside of a test
- Raising an exception from a `src/application/services/` method instead of returning `Result.failure()`
- Calling a domain model method directly from `src/ui/` — always go through a service
- Adding `print()` to any non-test file
- Bare `except:` — use `except Exception:` or a specific exception type
- Modifying any off-limits file listed above
- Committing to `api/develop` or `main` directly
