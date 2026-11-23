import time
import requests
from telemetry import log

URL = "http://localhost:11434"
_model_cache = {}


def model_info(model):
    if model not in _model_cache:
        r = requests.post(f"{URL}/api/show", json={"model": model}, timeout=30)
        r.raise_for_status()
        d = r.json().get("details", {})
        _model_cache[model] = (d.get("parameter_size"), d.get("quantization_level"))
    return _model_cache[model]


def chat(model, messages, json_mode=True):
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.7},
    }
    if json_mode:
        payload["format"] = "json"

    start = time.perf_counter()
    r = requests.post(f"{URL}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    wall = time.perf_counter() - start
    data = r.json()

    tokens = data.get("eval_count", 0)
    eval_s = data.get("eval_duration", 0) / 1e9
    size, quant = model_info(model)

    metrics = {
        "model": model,
        "param_size": size,
        "quantisation": quant,
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "tokens_generated": tokens,
        "response_s": round(wall, 2),
        "load_s": round(data.get("load_duration", 0) / 1e9, 2),
        "tokens_per_s": round(tokens / eval_s, 1) if eval_s else 0,
    }
    log(metrics)
    return data["message"]["content"], metrics


