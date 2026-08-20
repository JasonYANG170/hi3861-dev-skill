#!/usr/bin/env python3
"""Build deterministic searchable indexes for the bundled Hi3861 knowledge base."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFS = SKILL_ROOT / "references"
SOURCE = REFS / "source"
SDK = SOURCE / "sdk"
INDEX = REFS / "indexes"

TEXT_SUFFIXES = {
    ".c", ".h", ".cpp", ".cc", ".s", ".S", ".mk", ".gn", ".gni",
    ".json", ".md", ".txt", ".config", ".py", ".sh", ".bat", ".cmake",
}
SYMBOL_RE = re.compile(r"\b(?:hi_[A-Za-z0-9_]+|IoT[A-Za-z0-9_]+|IOT_[A-Z0-9_]+|HI_[A-Z0-9_]+|LOS_[A-Za-z0-9_]+)\b")
ENTRY_RE = re.compile(r"\b(?:APP_FEATURE_INIT|SYS_RUN|SYS_SERVICE_INIT)\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)")
PIN_RE = re.compile(r"\b(?:HI_IO_NAME_GPIO_|HI_GPIO_IDX_|GPIO_)(\d+)\b")
CONFIG_RE = re.compile(r"\bCONFIG_[A-Z0-9_]+\b")
TARGET_RE = re.compile(r"(?:static_library|lite_component|executable|group)\s*\(\s*[\"']([^\"']+)")

TOPICS = {
    "gpio": ["gpio", "led", "button", "key", "interrupt", "exti", "中断", "按键"],
    "i2c": ["i2c", "iic", "aht20", "nfc", "ssd1306", "pcf8574", "sht20", "ap3216"],
    "spi": ["spi", "gyro", "flash"],
    "pwm": ["pwm", "breath", "motor", "servo", "蜂鸣", "电机"],
    "adc": ["adc", "light_sense", "smoke", "raindrop", "采样"],
    "uart": ["uart", "serial", "串口"],
    "timer": ["timer", "hrtimer", "systick", "定时"],
    "liteos": ["task", "queue", "sem", "semaphore", "mux", "mutex", "event", "swtmr", "kernel", "liteos"],
    "wifi": ["wifi", "wlan", "hotspot", "sta", "softap"],
    "network": ["tcp", "udp", "http", "socket", "lwip", "sntp", "coap"],
    "mqtt": ["mqtt", "paho", "iotda", "cloud_oc"],
    "storage": ["flash", "nv", "filesystem", "file_system", "partition"],
    "ota": ["ota", "upgrade", "upg", "boot"],
    "security": ["cipher", "tls", "dtls", "mbedtls", "efuse", "security"],
    "power": ["lowpower", "low_power", "sleep", "watchdog", "功耗"],
}


def rel(path: Path) -> str:
    return path.relative_to(SKILL_ROOT).as_posix()


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except (UnicodeDecodeError, OSError):
            continue
    return ""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify_topics(text: str) -> list[str]:
    lower = text.lower()
    matches = []
    for name, words in TOPICS.items():
        for word in words:
            if any(ord(char) > 127 for char in word):
                found = word in lower
            else:
                found = re.search(rf"(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])", lower) is not None
            if found:
                matches.append(name)
                break
    return sorted(matches)


def board_from_path(path: Path) -> str:
    value = path.as_posix().lower()
    if "/pzkj/pz_hi3861/" in value:
        return "pz-hi3861"
    if "/hqyj/fs_hi3861/" in value:
        return "fs-hi3861"
    if "/bearpi/bearpi_hm_nano/" in value:
        return "bearpi-hm-nano"
    if "/hihope/hispark_pegasus/" in value:
        return "hispark-pegasus"
    if "/hisilicon/hispark_m1/" in value:
        return "hispark-m1"
    if "/hisilicon/hispark_pegasus/" in value:
        return "hispark-pegasus-sdk"
    return "generic-hi3861"


def source_scope(path: Path) -> str:
    value = path.as_posix().lower()
    if "/third_party/u-boot/" in value:
        return "third-party-u-boot"
    if "/third_party/" in value:
        return "third-party"
    if "/sdk_liteos/include/" in value or "/interfaces/kits/" in value:
        return "public-api"
    if "/kernel/liteos" in value or "/huawei_liteos/kernel/" in value:
        return "liteos-kernel"
    if "/vendor/" in value:
        return "vendor"
    return "hi3861-sdk"


def build_manifest() -> list[dict]:
    records = []
    for path in sorted(p for p in SOURCE.rglob("*") if p.is_file()):
        stat = path.stat()
        records.append({
            "path": rel(path),
            "size": stat.st_size,
            "sha256": sha256(path),
            "kind": path.suffix.lower().lstrip(".") or "file",
        })
    return records


def build_symbols() -> list[dict]:
    records: dict[tuple[str, str], dict] = {}
    roots = [
        SDK / "device/hisilicon/hispark_pegasus/sdk_liteos/include",
        SDK / "device/hisilicon/hispark_pegasus/sdk_liteos/platform/os/Huawei_LiteOS/kernel/include",
        SDK / "base/iot_hardware/peripheral/interfaces/kits",
        SDK / "kernel/liteos_m",
    ]
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.h")):
            for lineno, line in enumerate(read_text(path).splitlines(), 1):
                for symbol in sorted(set(SYMBOL_RE.findall(line))):
                    stripped = line.strip()
                    if stripped.startswith(("//", "/*", "*")):
                        continue
                    if stripped.startswith("#define"):
                        kind = "macro"
                    elif "typedef" in stripped:
                        kind = "type"
                    elif re.search(rf"\b{re.escape(symbol)}\s*\(", stripped):
                        kind = "function"
                    elif re.search(rf"}}\s*{re.escape(symbol)}\s*;", stripped):
                        kind = "type"
                    else:
                        kind = "symbol"
                    record = {
                        "symbol": symbol,
                        "kind": kind,
                        "path": rel(path),
                        "line": lineno,
                        "declaration": stripped[:500],
                        "topics": classify_topics(symbol + " " + path.name),
                        "source_scope": source_scope(path),
                    }
                    key = (symbol, record["path"])
                    previous = records.get(key)
                    kind_rank = {"function": 0, "type": 1, "macro": 2, "symbol": 3}
                    if previous is None or kind_rank[kind] < kind_rank[previous["kind"]]:
                        records[key] = record
    return sorted(records.values(), key=lambda item: (item["symbol"], item["path"]))


def build_demos() -> list[dict]:
    records = []
    vendor = SDK / "vendor"
    if not vendor.exists():
        return records
    for build_file in sorted(vendor.rglob("BUILD.gn")):
        demo_dir = build_file.parent
        if "demo" not in [part.lower() for part in demo_dir.parts]:
            continue
        files = sorted(p for p in demo_dir.rglob("*") if p.is_file())
        code_files = [p for p in files if p.suffix in {".c", ".h", ".cpp", ".cc"}]
        build_text = read_text(build_file)
        active_build_text = "\n".join(line for line in build_text.splitlines() if not line.lstrip().startswith("#"))
        is_container = "lite_component(" in active_build_text and not re.search(
            r"\b(?:static_library|executable)\s*\(", active_build_text
        )
        if is_container:
            code_files = []
        combined_parts = [demo_dir.name, active_build_text]
        entries: set[str] = set()
        pins: set[int] = set()
        configs: set[str] = set(CONFIG_RE.findall(active_build_text))
        symbols: set[str] = set()
        for path in code_files:
            text = read_text(path)
            combined_parts.extend((path.name, " ".join(SYMBOL_RE.findall(text))))
            entries.update(ENTRY_RE.findall(text))
            pins.update(int(value) for value in PIN_RE.findall(text))
            configs.update(CONFIG_RE.findall(text))
            symbols.update(SYMBOL_RE.findall(text))
        combined = " ".join(combined_parts)
        primary_topics = classify_topics(demo_dir.name + " " + " ".join(TARGET_RE.findall(build_text)))
        secondary_topics = sorted(set(classify_topics(combined)) - set(primary_topics))
        records.append({
            "name": demo_dir.name,
            "board": board_from_path(demo_dir),
            "path": rel(demo_dir),
            "build_file": rel(build_file),
            "targets": sorted(set(TARGET_RE.findall(build_text))),
            "entries": sorted(entries),
            "pins": sorted(pins),
            "configs": sorted(configs),
            "symbols": sorted(symbols),
            "kind": "container" if is_container else "runnable",
            "primary_topics": primary_topics,
            "secondary_topics": secondary_topics,
            "topics": sorted(set(primary_topics) | set(secondary_topics)),
            "file_count": len(files),
        })

    native_demo = SDK / "device/hisilicon/hispark_pegasus/sdk_liteos/app/demo/src"
    if native_demo.exists():
        for path in sorted(native_demo.glob("app_demo_*.c")):
            text = read_text(path)
            symbols = sorted(set(SYMBOL_RE.findall(text)))
            primary_topics = classify_topics(path.name)
            secondary_topics = sorted(set(classify_topics(" ".join(symbols))) - set(primary_topics))
            records.append({
                "name": path.stem,
                "board": "hispark-pegasus-sdk",
                "path": rel(path),
                "build_file": "references/source/sdk/device/hisilicon/hispark_pegasus/sdk_liteos/app/demo/SConscript",
                "targets": [],
                "entries": sorted(set(ENTRY_RE.findall(text))),
                "pins": sorted({int(value) for value in PIN_RE.findall(text)}),
                "configs": sorted(set(CONFIG_RE.findall(text))),
                "symbols": symbols,
                "kind": "runnable",
                "primary_topics": primary_topics,
                "secondary_topics": secondary_topics,
                "topics": sorted(set(primary_topics) | set(secondary_topics)),
                "file_count": 1,
            })
    return records


def build_configs() -> list[dict]:
    hits: dict[str, list[dict]] = {}
    for path in sorted(p for p in SDK.rglob("*") if p.is_file() and p.suffix in TEXT_SUFFIXES):
        text = read_text(path)
        if "CONFIG_" not in text:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for name in set(CONFIG_RE.findall(line)):
                bucket = hits.setdefault(name, [])
                if len(bucket) < 50:
                    bucket.append({
                        "path": rel(path),
                        "line": lineno,
                        "text": line.strip()[:300],
                        "source_scope": source_scope(path),
                    })
    return [{"config": name, "occurrences": values} for name, values in sorted(hits.items())]


def build_docs() -> list[dict]:
    records = []
    for path in sorted(p for p in SOURCE.rglob("*") if p.is_file()):
        if path.suffix.lower() not in {".md", ".pdf", ".chm", ".html", ".htm", ".txt"}:
            continue
        records.append({
            "path": rel(path),
            "title": path.stem,
            "topics": classify_topics(path.as_posix()),
            "size": path.stat().st_size,
            "source_scope": source_scope(path),
        })
    return records


def write_json(name: str, value: object) -> None:
    INDEX.mkdir(parents=True, exist_ok=True)
    destination = INDEX / name
    temporary = INDEX / f".{name}.tmp"
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-checksums", action="store_true", help="Skip full file hashes for a faster development pass")
    args = parser.parse_args()
    if not SDK.exists():
        raise SystemExit(f"SDK mirror not found: {SDK}")

    symbols = build_symbols()
    demos = build_demos()
    configs = build_configs()
    docs = build_docs()
    manifest_path = INDEX / "source-manifest.json"
    if args.skip_checksums and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = build_manifest()
    write_json("api-symbols.json", symbols)
    write_json("examples.json", demos)
    write_json("configs.json", configs)
    write_json("documents.json", docs)
    write_json("source-manifest.json", manifest)
    metadata = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "default_board": "pz-hi3861",
        "counts": {
            "source_files": len(manifest) if manifest else sum(1 for p in SOURCE.rglob("*") if p.is_file()),
            "api_records": len(symbols),
            "unique_api_symbols": len({item["symbol"] for item in symbols}),
            "examples": len(demos),
            "runnable_examples": sum(item.get("kind") == "runnable" for item in demos),
            "configs": len(configs),
            "documents": len(docs),
        },
    }
    write_json("metadata.json", metadata)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
