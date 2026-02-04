React + Konva Seating Plan (first draft)

Setup

1. Node.js (16+ recommended) and npm installed.
2. From repository root run:

```powershell
cd frontend-react
npm install
npm run dev
```

The dev server proxies `/api` to `http://localhost:8000` (see `vite.config.js`).

Dependencies to install (created in package.json):
- react, react-dom, axios
- zustand (state), immer (immutable updates)
- konva, react-konva
- vite + @vitejs/plugin-react

Folder structure (important files):

- frontend-react/
  - index.html
  - package.json
  - vite.config.js
  - src/
    - main.jsx
    - App.jsx
    - api.js            # thin wrapper around existing FastAPI endpoints
    - store/store.js   # zustand store + undo/redo history
    - components/
      - CanvasStage.jsx    # core react-konva canvas and seat renderer
      - SectionList.jsx    # list/create/select sections
      - RowRangeDialog.jsx # row-range dialog mirroring Qt features

State store design

- `sections`: array of section metadata (name, is_ga)
- `selectedSection`: string
- `sectionData`: full section with `rows: [{row_number, seats:[{seat_number}]}]`
- `past` / `future` stacks: JSON snapshots of `sectionData` for undo/redo

Actions:
- `loadSections()`, `selectSection(name)`
- `addSeat(row, seat)`, `deleteSeat(row, seat)` — call API and update local state
- `addRowRange(payload)` — POST `/sections/{name}/rows/range`
- `snapshot()` called before mutating ops; `undo()`, `redo()` manipulate `past`/`future`

Component breakdown

- `App.jsx` — layout, loads sections
- `SectionList.jsx` — create and select sections
- `CanvasStage.jsx` — Seat grid rendering using `react-konva` (cells drawn with `Rect` + `Text`)
- `RowRangeDialog.jsx` — UI for row range options (parity, prefix/suffix, continuous, unnumbered)

Seat rendering strategy

- Compute unique sorted seat numbers across all rows to form columns.
- Rows form vertical axis. Position = `x = padding + colIndex * CELL`, `y = padding + rowIndex * CELL`.
- Each seat is a `Group` containing a `Rect` and `Text`.
- Click toggles selection; double-click adds seat if missing.

Selection algorithm blueprint

- Simple selection by cell key `row-seat` stored in a Set.
- Rubber-band selection can be implemented with an overlay `Rect` during drag and an intersection test (box vs cell bounds).
- For performance, compute cell bounding boxes on render (they're regular grid, so bounds arithmetic is O(1)).

Undo/Redo design for web

- Use `past`/`future` stacks storing deep-cloned `sectionData` snapshots.
- Before any mutating API call, push current `sectionData` to `past` and clear `future`.
- `undo()` pops last snapshot from `past` and pushes current to `future`, then replaces `sectionData` locally (optionally syncs with server via a full save endpoint).
- `redo()` pops from `future` to `past` symmetrically.

Migration plan from Qt

1. Audit Qt dialogs & flows (already done). Identify features to port: row-range options, renumbering, move seats.
2. Map GUI widgets to React components: dialogs -> modal components, graphics view -> `CanvasStage` + Konva.
3. Port logic: reuse existing backend logic where possible. Calls from Qt that mutate model map to API calls (sectionsAPI, seatsAPI).
4. Add missing backend endpoints only when necessary (batch-mutate, full-save) — current backend already supports row-range.
5. Implement undo/redo: server-side snapshot endpoints (optional) or client-only snapshots (current draft uses client snapshots).

Notes & next steps

- This is a minimal working draft; rubber-band selection and keyboard shortcuts are partially implemented in `CanvasStage` and can be extended.
- If you want, I can: add Redux DevTools-compatible store, implement full rubber-band selection, add keyboard listeners globally, and implement an efficient diff-based undo/redo that sends reverse API operations to the backend.

