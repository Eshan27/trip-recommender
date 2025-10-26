# AI Trip Recommender

**AI Trip Recommender** is a lightweight trip-planning backend + Chrome extension MVP that takes an origin, destination, dates, budget and user preferences and returns a structured, day-by-day itinerary (hotels, restaurants, attractions, travel time estimates). The system is optimized for free / low-cost services, uses only open-data sources by default, and integrates an instruction-tuned small LLM for human-friendly itinerary generation.

---

## Key Features

* Generate multi-day itineraries from origin → destination and a budget
* Uses open-data POI sources (OpenTripMap / OpenStreetMap) to find hotels, restaurants and attractions
* Uses an LLM to assemble a readable day-by-day plan from structured POI data
* Caching of POI and AI outputs to minimize API calls and cost
* Minimal, stateless Chrome extension UI (no user accounts required)

---

## Tech Stack

* **Frontend (client):** Chrome Extension (vanilla JS or React) + Leaflet (for optional map visualization) + OpenStreetMap tiles
* **Backend:** Python + Flask
* **Deployment (serverless-first):** AWS Lambda + API Gateway (via Serverless Framework + `serverless-wsgi`) or AWS Lambda container
* **Caching / Storage:** Amazon DynamoDB (key-value cache with TTL) and Amazon S3 (static assets / optional exports)
* **POI / Geodata:** OpenTripMap, OpenStreetMap (Nominatim), OpenRouteService (for routing/distance)
* **AI / LLM:** Hugging Face Inference API (or local open-source LLM for zero API cost)
* **CI/CD:** GitHub Actions (build & deploy)
* **Monitoring:** AWS CloudWatch + AWS Budgets (alerts)

---

## Architecture (high-level)

```
Chrome Extension (UI)
        ↓ HTTPS
API Gateway (HTTP API)
        ↓
Lambda (Flask app)
  ├─ POI fetcher (OpenTripMap / OSM) + cache (DynamoDB)
  ├─ Distance/route calls (OpenRouteService)
  ├─ LLM call (Hugging Face) for itinerary assembly
  └─ S3 for exports (optional)
```

Notes:

* DynamoDB is used as a key-value cache for POI responses and generated itineraries (TTL configured).
* LLM outputs and expensive external API calls must be cached aggressively.

---

## Repository layout (suggested)

```
ai-trip-recommender/
├─ extension/                # Chrome extension source (manifest, popup, background)
├─ backend/
│  ├─ app.py                 # Flask application
│  ├─ requirements.txt
│  ├─ modules/
│  │  ├─ poi_fetcher.py      # wrappers for OpenTripMap / OSM
│  │  ├─ routing.py          # OpenRouteService helpers
│  │  ├─ llm.py              # abstraction to call HF or local model
│  │  └─ cache.py            # DynamoDB get/set TTL helpers
│  └─ serverless.yml         # Serverless Framework config
├─ infra/                    # Optional IaC (Terraform/SAM templates)
├─ docs/
└─ README.md
```

---

## Endpoints (minimal)

* `POST /generate-itinerary` — Generate itinerary

  * Input JSON: `{ origin, destination, start_date, end_date, budget, preferences }`
  * Output JSON: structured itinerary (days, POIs, hotels, est. costs, coords)

* `GET /poi?lat={lat}&lon={lon}&type={type}` — Cached POI lookup

* `GET /health` — Health check

---

## Cache strategy

* Use a single DynamoDB `cache` table with fields: `cache_key` (PK), `payload` (JSON), `type`, `created_at`, `ttl`.
* Generate cache keys with a deterministic hash, e.g. `sha256("gen|origin|dest|start|end|budget|prefs")`.
* Recommended TTLs:

  * POI data: 24 hours – 7 days
  * Itineraries (LLM outputs): 7–30 days
  * LLM prompts/outputs: 30 days

---

## Env / Config (example .env variables)

```
# POI / Geocoding
OPENTRIPMAP_KEY=your_opentripmap_key
NOMINATIM_URL=https://nominatim.openstreetmap.org

# Routing
OPENROUTESERVICE_KEY=your_openrouteservice_key

# AI
HF_API_URL=https://api-inference.huggingface.co/models/your-model
HF_API_KEY=your_hf_key

# AWS
AWS_REGION=us-east-1
DYNAMO_TABLE_CACHE=ai_trip_cache
S3_BUCKET_EXPORTS=ai-trip-exports

# Misc
CACHE_TTL_POI=86400
CACHE_TTL_ITINERARY=604800
```

---

## Local development

1. Clone repo
2. Create a Python virtualenv and install `requirements.txt`
3. Create `.env` from example and populate keys
4. Run Flask locally: `flask run` (or `python -m flask run --port 5000`)
5. Use Postman or the extension dev build to call `POST /generate-itinerary`

---

## Deployment (quick notes)

* Serverless Framework with `serverless-wsgi` is recommended to package Flask for Lambda + API Gateway.
* Use GitHub Actions to automate `sls deploy` on push to `main`.
* Create AWS Budget alert immediately to avoid surprise charges.

---

## Security & Cost Controls

* Require an API key in the extension to limit casual abuse; rotate keys if needed.
* Rate-limit on API Gateway or inside the Flask app (basic token bucket per IP/key).
* Cache aggressively to reduce external API & LLM calls.
* Set AWS Budget alert at a low threshold (e.g., $1–5) early.

---

## Next steps (recommended)

1. Generate a minimal Flask skeleton with endpoints and a mock `llm` function.
2. Create the Chrome extension manifest and a simple popup UI that calls the `generate-itinerary` endpoint.
3. Implement the `poi_fetcher` using OpenTripMap and DynamoDB caching.
