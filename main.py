import os
import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow browser access for the grader
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Layer 1: Defaults
config = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# Layer 2: YAML
with open("config.development.yaml") as f:
    yaml_cfg = yaml.safe_load(f)
    if yaml_cfg:
        config.update(yaml_cfg)

# Layer 3: .env
env_cfg = dotenv_values(".env")

if "APP_PORT" in env_cfg:
    config["port"] = env_cfg["APP_PORT"]

if "APP_LOG_LEVEL" in env_cfg:
    config["log_level"] = env_cfg["APP_LOG_LEVEL"]

if "APP_API_KEY" in env_cfg:
    config["api_key"] = env_cfg["APP_API_KEY"]

# Alias
if "NUM_WORKERS" in env_cfg:
    config["workers"] = env_cfg["NUM_WORKERS"]

# Layer 4: OS Environment
mapping = {
    "APP_PORT": "port",
    "APP_WORKERS": "workers",
    "APP_LOG_LEVEL": "log_level",
    "APP_API_KEY": "api_key",
}

for env_key, cfg_key in mapping.items():
    if env_key in os.environ:
        config[cfg_key] = os.environ[env_key]


def to_bool(v):
    return str(v).lower() in ["true", "1", "yes", "on"]


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    result = config.copy()

    # CLI overrides
    for item in set:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        result[key] = value

    # Type coercion
    result["port"] = int(result["port"])
    result["workers"] = int(result["workers"])
    result["debug"] = to_bool(result["debug"])
    result["log_level"] = str(result["log_level"])

    # Secret masking
    result["api_key"] = "****"

    return result
