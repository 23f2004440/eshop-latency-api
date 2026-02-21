from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import json

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry once
with open("telemetry.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)

@app.post("/api")
async def analyze(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    results = {}

    for region in regions:
        region_df = df[df["region"] == region]

        if region_df.empty:
            continue

        avg_latency = region_df["latency_ms"].mean()
        p95_latency = np.percentile(region_df["latency_ms"], 95)
        avg_uptime = region_df["uptime_pct"].mean()
        breaches = (region_df["latency_ms"] > threshold).sum()

        results[region] = {
            "avg_latency": round(float(avg_latency), 2),
            "p95_latency": round(float(p95_latency), 2),
            "avg_uptime": round(float(avg_uptime), 3),
            "breaches": int(breaches)
        }

    return results
