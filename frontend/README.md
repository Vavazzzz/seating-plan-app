# Seating Plan Frontend

Vue 3 + Vite frontend for the Seating Plan API.

## Setup

```bash
cd frontend
npm install
npm run dev
```

The app will open at `http://localhost:5173`.

## Build

```bash
npm run build
```

## Features

- **Project Manager** — Create, save, load, and delete seating plans
- **Section Manager** — Create, rename, clone, and delete sections
- **Seat Manager** — Add seats individually, in bulk, or by range; delete seats/rows
- **Auto-save** — Projects saved to `projects/` folder in backend
- **Real-time Updates** — Refreshes data after each operation

## Tabs

1. **Projects** — Manage seating plans
2. **Sections** — Manage theater sections
3. **Seats** — Add/remove seats from sections

## Architecture

- `src/main.js` — Vue app entry point
- `src/App.vue` — Root component with tab navigation
- `src/api.js` — Axios service for backend calls
- `src/components/` — Feature components (ProjectManager, SectionManager, SeatManager)
- `src/style.css` — Global styles

## Prerequisites

- Backend API running at `http://localhost:8000`
- Node.js 16+
