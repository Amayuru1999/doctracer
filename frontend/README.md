
# DocTracer Frontend (fixed)

React + Vite + TypeScript + Tailwind.

## Setup

```bash
npm i
# set backend API (optional, defaults to http://127.0.0.1:5001)
echo "VITE_API_URL=http://127.0.0.1:5001" > .env.local
npm run dev
```

You need a backend exposing:
- `GET /gazettes` → `[ { gazette_id, published_date } ]`
- `GET /gazettes/:id` → `[ { gazette_id, published_date, minister, departments[], laws[], functions[] } ]`
