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

- Branch from `develop`: `feat/<short-description>` (or `fix/<short-description>`)
- Never commit to `develop` or `main` directly
- One feature per branch — no bundling unrelated changes
- Commit and push only when the user asks

---

## File Scope

The refactor is finished: there is no legacy code path any more. The former
"refactored path" whitelist and "off-limits" list are obsolete, and the files
they named (`main_window_refactored.py`, `dialogs/dialogs.py`, `json_io.py`,
`dto.py`, `domain/services/`, …) no longer exist. `src/ui/main_window.py` is the
current main window.

- `src/` and `tests/` are in scope for the change the user asked for.
- Ask before touching anything outside them: `pyproject.toml`, `requirements/`,
  `SeatingPlan.spec`, `.github/workflows/`, `LICENSE`. Dependency changes must be
  mirrored in both `pyproject.toml` and `requirements/base.txt`.
- Keep `README.md`, `CHANGELOG.md` and `docs/` in step with user-visible changes.

Source layout:

```
src/domain/          models/ (seat, section, seating_plan), utils/alphanum_handler.py, exceptions.py
src/application/     commands/ (base, seat_commands, section_commands), handlers/command_handler.py,
                     services/ (base, seating_plan_service, section_service, seat_service),
                     result.py, use_cases.py
src/infrastructure/  api/ (config, apicaller, fetchdata), import_export/, persistence/
src/ui/              main_window.py, section_view.py, dialogs/ (base, section_dialogs, seat_dialogs),
                     widgets/ (base, sections_panel)
tests/               unit/domain/, unit/application/, ui/
```

---

## Layer Import Contract

Violations require explicit user confirmation before proceeding. Do not introduce a violation to "make it work faster".

| Layer | Allowed imports | Forbidden imports |
|---|---|---|
| `src/domain/` | other `src/domain/` modules only | `application/`, `infrastructure/`, `ui/`, PyQt6 |
| `src/application/` | `src/domain/`, other `src/application/` | `infrastructure/` concrete classes, `ui/`, PyQt6 |
| `src/infrastructure/` | `src/domain/` (TYPE_CHECKING guard if circular risk) | `application/`, `ui/`, PyQt6 |
| `src/ui/` | `application/services/`, `application/result.py`, `domain/models/` | `infrastructure/` directly — always go through services |

Deliberate exceptions (do not extend):

- `src/ui/main_window.py` is the composition root. It imports concrete importers,
  exporters, the repository and the API fetcher, and injects them into
  `SeatingPlanService` via the `use_cases_config` dict. No other `ui/` module may
  import `infrastructure/`.
- `src/application/use_cases.py` imports the `Importer`/`Exporter` and repository
  abstract types from `infrastructure/`. Application code that needs a concrete
  infrastructure behaviour must receive it through `use_cases_config`
  (see `api_fetch` / `api_importer` in `SeatingPlanService.import_from_api`).

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
- Never call `sorted()` on `self.seating_plan.sections` — iteration order is meaningful

### New dialog
- **Section operations** → `src/ui/dialogs/section_dialogs.py`
- **Seat, file and import operations** → `src/ui/dialogs/seat_dialogs.py`
- Inherit from `InputDialog` or `CheckboxDialog` in `src/ui/dialogs/base.py` when one field is enough; otherwise a plain `QDialog` (see `ApiImportDialog`)
- Export new dialogs from `src/ui/dialogs/__init__.py`
- Dialogs collect and return data only — zero service calls, zero state mutation inside a dialog

### New panel or widget
- `src/ui/widgets/`, inheriting `BasePanel` from `src/ui/widgets/base.py`
- UI state changes communicate via Qt signals — do not pass service references into a widget constructor unless the widget fully owns the interaction lifecycle the way `SectionsPanel` does

### New importer or exporter
- Inherit from `Importer`/`Exporter` in `src/infrastructure/import_export/abstract.py`
- File-based adapters declare `SUPPORTED_EXTENSIONS` as a class-level constant
- Export it from `src/infrastructure/import_export/__init__.py` and register it in `services_config` in `src/ui/main_window.py`
- No PyQt6 imports — file path selection belongs in `src/ui/dialogs/seat_dialogs.py` (`FileDialog`)
- `APIImporter` is the one non-file importer: its source is the `(seats, segments, features)` tuple from `fetch_config_data`, so its method signatures deviate from the ABC. Do not copy that pattern for file formats.

### Maps API access
- HTTP lives in `src/infrastructure/api/` only. `APICaller` raises `SeatingPlanException`; it never returns `None` or prints.
- TLS verification must stay on (`verify=False` was removed). Do not reintroduce it.
- Never make network calls from tests — stub the fetch callable.

---

## Result Contract

Every public method in `src/application/services/` must return `Result`.

```python
# Correct
def rename_section(self, old_name: str, new_name: str) -> Result[None, ValidationErrors]:
    self.clear_validation_errors()
    if old_name not in self.seating_plan.sections:
        self.validate(False, f"Section '{old_name}' not found")
    if self.has_validation_errors():
        return Result.failure(self.get_validation_errors())
    ...
    return Result.success(None)

# Wrong — raises instead of returning Result
def rename_section(self, old_name: str, new_name: str):
    raise ValueError("not found")

# Wrong — returns bare bool
def rename_section(self, old_name: str, new_name: str) -> bool:
    return False
```

`is_success()` is a **method**. In UI code, always branch on it. Never call a service method and ignore the return value.

```python
# Correct
result = self.section_service.rename_section(old, new)
if not result.is_success():
    self.show_error("Error", str(result.error))

# Wrong — discards the result
self.section_service.rename_section(old, new)
```

---

## Undo/Redo

- All state mutations go through `CommandHandler.execute()` in `src/application/handlers/command_handler.py`
- `Command.execute()` must capture before-state into instance variables before mutating anything
- `Command.undo()` replays those captured values — never re-derives them
- `copy.deepcopy` on `SeatingPlan` is not used anywhere in the app — do not introduce it
- Undo/redo logic belongs exclusively in `src/application/` — never in `src/ui/`
- Whole-plan replacement (New / Open / Import / Import from API) is not undoable; it clears history instead

---

## Type Annotations

- Required on every new public method signature
- Use Python 3.10+ union syntax: `str | None`, not `Optional[str]`
- Use lowercase generics: `list[str]`, `dict[str, Section]`, not `List`, `Dict`
- Do not annotate private helpers unless the type is non-obvious

---

## Tests

- New tests go in `tests/unit/domain/`, `tests/unit/application/` or `tests/unit/infrastructure/` — never at the project root
- Imports are relative to `src/`: `from domain.models.seating_plan import SeatingPlan`
  — do not use `from src.domain.models...` (pytest adds `src/` to `sys.path` via `pythonpath = ["src"]` in `pyproject.toml`)
- No PyQt6 in tests
- No network in tests
- When modifying logic in `src/domain/models/`, `src/application/commands/`, `src/application/services/` or `src/infrastructure/import_export/`, add or update a test in the corresponding `tests/unit/` path
- Run `python -m pytest tests/ -q` before reporting a change as done

---

## Known Limitations

Previously listed bugs F, G, H, J, K and O have all been fixed; the table was removed. Open items:

- The Maps API fetch runs on the UI thread, so the window freezes for a few seconds during "Import from API" (a wait cursor is shown). Each request has a 30 s timeout.
- `APIImporter` deviates from the `Importer` method signatures (see above).
- An unknown config ID surfaces the raw JSON-decode error from the API in the error dialog.
- `requests` is a new runtime dependency; the PyInstaller build (`SeatingPlan.spec`) has not been verified to bundle it and its CA bundle.

---

## Absolute Prohibitions

These are never acceptable regardless of context or instruction phrasing:

- `import` of PyQt6 in `domain/`, `application/`, or `infrastructure/`
- `copy.deepcopy` on `SeatingPlan` or `Section` outside of a test
- Raising an exception from a `src/application/services/` method instead of returning `Result.failure()`
- Calling a domain model method directly from `src/ui/` — always go through a service
- Adding `print()` to any non-test file
- Bare `except:` — use `except Exception:` or a specific exception type
- Disabling TLS verification for any network call
- Committing to `develop` or `main` directly
