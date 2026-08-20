#!/usr/bin/env python3
"""Validate completeness and semantic coverage of hi3861-dev-skill."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "references"
INDEX = REFS / "indexes"
REQUIRED_TOPICS = [
    "i2c", "spi", "pwm", "adc", "gpio", "uart", "timer", "liteos",
    "wifi", "network", "mqtt", "storage", "ota", "security", "power",
]
CORE_EVIDENCE = {
    "i2c": {"api": "hi_i2c_init", "config": "CONFIG_I2C_SUPPORT", "driver": "/platform/drivers/i2c/"},
    "spi": {"api": "hi_spi_init", "config": "CONFIG_SPI_SUPPORT", "driver": "/platform/drivers/spi/"},
    "pwm": {"api": "hi_pwm_start", "config": "CONFIG_PWM_SUPPORT", "driver": "/platform/drivers/pwm/"},
    "adc": {"api": "hi_adc_read", "driver": "/platform/drivers/adc/"},
    "gpio": {"api": "hi_gpio_init", "driver": "/app/demo/src/app_demo_io_gpio.c"},
    "uart": {"api": "hi_uart_init", "config": "CONFIG_UART0_SUPPORT", "driver": "/platform/drivers/uart/"},
    "timer": {"api": "hi_timer_create", "driver": "/app/demo/src/app_demo_timer_systick.c"},
}
LITEOS_APIS = {
    "LOS_TaskCreate", "LOS_QueueCreate", "LOS_SemCreate", "LOS_MuxCreate", "LOS_EventInit", "LOS_SwtmrCreate",
}


def load(name: str):
    return json.loads((INDEX / name).read_text(encoding="utf-8"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-checksums", action="store_true", help="Hash every mirrored file instead of a deterministic sample")
    args = parser.parse_args()

    failures: list[str] = []
    require((ROOT / "SKILL.md").is_file(), "SKILL.md missing", failures)
    require((ROOT / "agents/openai.yaml").is_file(), "agents/openai.yaml missing", failures)
    require((REFS / "source/sdk").is_dir(), "SDK mirror missing", failures)
    require(not (REFS / "source/puzhong-guide").exists(), "External Puzhong guide must not be bundled", failures)
    require(not (REFS / "source/liteos-kernel-guide").exists(), "External LiteOS CHM must not be bundled", failures)
    require(not (REFS / "pdf-text").exists(), "Extracted PDF content must not be bundled", failures)

    required_indexes = ["metadata.json", "source-manifest.json", "api-symbols.json", "examples.json", "configs.json", "documents.json"]
    for name in required_indexes:
        require((INDEX / name).is_file(), f"Index missing: {name}", failures)
    if failures:
        print("\n".join(f"FAIL: {item}" for item in failures))
        return 1

    metadata = load("metadata.json")
    manifest = load("source-manifest.json")
    symbols = load("api-symbols.json")
    examples = load("examples.json")
    configs = load("configs.json")
    docs = load("documents.json")
    runnable_examples = [item for item in examples if item.get("kind", "runnable") == "runnable"]

    require(len(manifest) > 20000, f"Too few mirrored files: {len(manifest)}", failures)
    require(len({item['symbol'] for item in symbols}) > 500, "API symbol coverage below 500", failures)
    require(len(runnable_examples) >= 80, f"Too few runnable demos: {len(runnable_examples)}", failures)
    require(len(configs) >= 100, f"Too few indexed configs: {len(configs)}", failures)
    require(len(docs) >= 100, f"Too few indexed documents: {len(docs)}", failures)
    require(len(list((REFS / "source/sdk").rglob("*.pdf"))) >= 15, "SDK PDF snapshot is incomplete", failures)

    evidence_blob = json.dumps({"symbols": symbols, "examples": runnable_examples, "configs": configs, "docs": docs}, ensure_ascii=False).lower()
    for topic in REQUIRED_TOPICS:
        require(topic in evidence_blob, f"No evidence found for topic: {topic}", failures)

    symbol_names = {item["symbol"] for item in symbols if item.get("kind") == "function"}
    config_names = {item["config"] for item in configs}
    manifest_paths = [item["path"].lower() for item in manifest]
    for topic, expected in CORE_EVIDENCE.items():
        api_records = [
            item for item in symbols
            if item["symbol"] == expected["api"]
            and item.get("kind") == "function"
            and item.get("source_scope") == "public-api"
        ]
        require(bool(api_records), f"No public Hi3861 function evidence for {topic}: {expected['api']}", failures)
        require(
            any(topic in item.get("topics", []) for item in runnable_examples),
            f"No runnable SDK/Vendor example evidence for topic: {topic}",
            failures,
        )
        require(
            any(expected["driver"] in path for path in manifest_paths),
            f"No Hi3861 driver/native-demo evidence for topic: {topic}",
            failures,
        )
        if "config" in expected:
            require(expected["config"] in config_names, f"Config evidence missing: {expected['config']}", failures)

    missing_liteos = sorted(LITEOS_APIS - symbol_names)
    require(not missing_liteos, f"LiteOS public APIs missing: {', '.join(missing_liteos)}", failures)

    pz_demos = [item for item in runnable_examples if item["board"] == "pz-hi3861"]
    pz_containers = [item for item in examples if item["board"] == "pz-hi3861" and item.get("kind") == "container"]
    require(len(pz_demos) == 43, f"Expected exactly 43 runnable PZ demos, found {len(pz_demos)}", failures)
    require(len(pz_containers) == 1, f"Expected one PZ demo dispatcher container, found {len(pz_containers)}", failures)
    require(metadata.get("default_board") == "pz-hi3861", "Default board is not pz-hi3861", failures)
    require(metadata.get("schema_version") == 2, "Index schema is not version 2", failures)

    for item in manifest:
        path = ROOT / item["path"]
        require(path.is_file(), f"Manifest path missing: {item['path']}", failures)
        if path.is_file():
            require(path.stat().st_size == item["size"], f"Manifest size mismatch: {item['path']}", failures)
    sample_step = 1 if args.full_checksums else max(1, len(manifest) // 25)
    for item in manifest[::sample_step]:
        path = ROOT / item["path"]
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            require(digest == item["sha256"], f"Manifest checksum mismatch: {item['path']}", failures)

    for item in symbols:
        require((ROOT / item["path"]).is_file(), f"API evidence missing: {item['path']}", failures)
    for item in examples:
        require((ROOT / item["path"]).exists(), f"Example evidence missing: {item['path']}", failures)

    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for link in re.findall(r"\]\((references/[^)]+)\)", skill_text):
        require((ROOT / link).exists(), f"SKILL.md reference missing: {link}", failures)

    query = ROOT / "scripts/query_index.py"
    for topic in REQUIRED_TOPICS:
        result = subprocess.run([sys.executable, str(query), "--topic", topic, "--json"], capture_output=True, text=True)
        require(result.returncode == 0, f"Query failed for {topic}: {result.stderr}", failures)
        if result.returncode == 0:
            payload = json.loads(result.stdout)
            require(bool(payload["api"] or payload["examples"]), f"Empty query result for {topic}", failures)
            require(
                not any(
                    "third_party/u-boot" in json.dumps(item).lower()
                    for section in ("configs", "documents")
                    for item in payload[section]
                ),
                f"Default query leaked U-Boot-only evidence for {topic}",
                failures,
            )

    if failures:
        print("\n".join(f"FAIL: {item}" for item in failures))
        return 1
    print(json.dumps({
        "status": "ok",
        "files": len(manifest),
        "symbols": len({item['symbol'] for item in symbols}),
        "examples": len(examples),
        "runnable_examples": len(runnable_examples),
        "pz_examples": len(pz_demos),
        "documents": len(docs),
        "sdk_pdfs": len(list((REFS / "source/sdk").rglob("*.pdf"))),
        "checksum_mode": "full" if args.full_checksums else "sampled",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
