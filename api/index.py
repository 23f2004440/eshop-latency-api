from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import json
import os

app = FastAPI()

# Proper CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load telemetry safely for Vercel
BASE_DIR = os.path.dirname(__file__)
FILE_PATH = os.path.join(BASE_DIR, "..", "telemetry.json")

with open(FILE_PATH) as f:
    data = json.load(f)

df = pd.DataFrame(data)


@app.post("/")
async def analyze(payload: dict, response: Response):

    # Manually ensure header is present (extra safe for Vercel)
    response.headers["Access-Control-Allow-Origin"] = "*"

    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 0)

    results = {}

    for region in regions:
        region_df = df[df["region"] == region]

        if region_df.empty:
            continue

        results[region] = {
            "avg_latency": round(float(region_df["latency_ms"].mean()), 2),
            "p95_latency": round(float(np.percentile(region_df["latency_ms"], 95)), 2),
            "avg_uptime": round(float(region_df["uptime_pct"].mean()), 3),
            "breaches": int((region_df["latency_ms"] > threshold).sum())
        }

    return results


# Handle OPTIONS (preflight)
@app.options("/")
async def options_handler(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return {}
