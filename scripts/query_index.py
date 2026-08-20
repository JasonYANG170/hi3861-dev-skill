#!/usr/bin/env python3
"""Query Hi3861 APIs, examples, configs, and documentation with evidence paths."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
INDEX = SKILL_ROOT / "references" / "indexes"
ALIASES = {
    "iic": "i2c", "serial": "uart", "串口": "uart", "模数": "adc",
    "中断": "gpio", "任务": "liteos", "队列": "liteos", "信号量": "liteos",
    "互斥锁": "liteos", "事件": "liteos", "低功耗": "power", "升级": "ota",
}
BOARD_ALIASES = {
    "pz": "pz-hi3861", "普中": "pz-hi3861", "pzkj": "pz-hi3861",
    "fs": "fs-hi3861", "bearpi": "bearpi-hm-nano", "pegasus": "hispark-pegasus",
    "m1": "hispark-m1", "all": "all",
}
CORE_SYMBOLS = {
    "i2c": ["hi_i2c_init", "hi_i2c_write", "hi_i2c_read", "hi_i2c_writeread", "hi_i2c_deinit"],
    "spi": ["hi_spi_init", "hi_spi_host_write", "hi_spi_host_read", "hi_spi_host_writeread", "hi_spi_deinit"],
    "pwm": ["hi_pwm_init", "hi_pwm_start", "hi_pwm_stop", "hi_pwm_set_clock", "hi_pwm_deinit"],
    "adc": ["hi_adc_read", "hi_adc_convert_to_voltage"],
    "gpio": ["hi_gpio_init", "hi_gpio_set_dir", "hi_gpio_set_ouput_val", "hi_gpio_get_input_val"],
    "uart": ["hi_uart_init", "hi_uart_write", "hi_uart_read", "hi_uart_deinit"],
    "timer": ["hi_timer_create", "hi_timer_start", "hi_timer_stop", "hi_timer_delete"],
    "liteos": ["LOS_TaskCreate", "LOS_QueueCreate", "LOS_SemCreate", "LOS_MuxCreate", "LOS_EventInit", "LOS_SwtmrCreate"],
}


def load(name: str):
    return json.loads((INDEX / name).read_text(encoding="utf-8"))


def scope_rank(scope: str) -> int:
    return {
        "public-api": 0,
        "liteos-kernel": 1,
        "hi3861-sdk": 2,
        "vendor": 3,
        "third-party": 8,
        "third-party-u-boot": 9,
    }.get(scope, 5)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--board", default="pz-hi3861")
    parser.add_argument("--symbol")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--include-third-party", action="store_true", help="Include U-Boot and other third-party-only evidence")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    topic = ALIASES.get(args.topic.lower(), args.topic.lower())
    board = BOARD_ALIASES.get(args.board.lower(), args.board.lower())
    symbols = load("api-symbols.json")
    examples = load("examples.json")
    configs = load("configs.json")
    documents = load("documents.json")

    if args.symbol:
        symbol_matches = [item for item in symbols if args.symbol.lower() in item["symbol"].lower()]
    else:
        symbol_matches = [item for item in symbols if topic in item.get("topics", [])]
    core_order = {name.lower(): order for order, name in enumerate(CORE_SYMBOLS.get(topic, []))}
    symbol_matches.sort(key=lambda item: (
        core_order.get(item["symbol"].lower(), 999),
        {"function": 0, "type": 1, "macro": 2, "symbol": 3}.get(item["kind"], 4),
        scope_rank(item.get("source_scope", "")),
        Path(item["path"]).name.lower() != f"hi_{topic}.h",
        not item["symbol"].lower().startswith(f"hi_{topic}"),
        item["symbol"],
        item["path"],
    ))

    candidates = [
        item for item in examples
        if item.get("kind", "runnable") == "runnable" and topic in item.get("topics", [])
    ]
    candidates.sort(key=lambda item: (
        0 if board != "all" and item["board"] == board else 1 if item["board"] == "hispark-pegasus-sdk" else 2,
        topic not in item.get("primary_topics", []),
        topic not in item["name"].lower(),
        topic not in item["path"].lower(),
        item["board"],
        item["name"],
    ))

    config_matches = [item for item in configs if topic in item["config"].lower()]
    if not args.include_third_party:
        config_matches = [
            item for item in config_matches
            if any(not occurrence.get("source_scope", "").startswith("third-party") for occurrence in item.get("occurrences", []))
        ]
    for item in config_matches:
        item["occurrences"] = sorted(
            item.get("occurrences", []),
            key=lambda occurrence: (scope_rank(occurrence.get("source_scope", "")), occurrence.get("path", ""), occurrence.get("line", 0)),
        )
    config_matches.sort(key=lambda item: (
        item["config"] != f"CONFIG_{topic.upper()}_SUPPORT",
        not item["config"].endswith("_SUPPORT"),
        min((scope_rank(occurrence.get("source_scope", "")) for occurrence in item["occurrences"]), default=9),
        item["config"],
    ))
    document_matches = [item for item in documents if topic in item.get("topics", [])]
    if not args.include_third_party:
        document_matches = [
            item for item in document_matches
            if not item.get("source_scope", "").startswith("third-party")
        ]
    document_matches.sort(key=lambda item: (
        scope_rank(item.get("source_scope", "")),
        topic not in item["title"].lower(),
        item["path"],
    ))
    result = {
        "query": {"topic": topic, "board": board, "symbol": args.symbol},
        "api": symbol_matches[: args.limit],
        "examples": candidates[: args.limit],
        "configs": config_matches[: args.limit],
        "documents": document_matches[: args.limit],
        "evidence_note": "Paths are relative to the hi3861-dev-skill directory; third-party-only evidence is hidden unless --include-third-party is used.",
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Topic: {topic}  Board: {board}")
        for section in ("api", "examples", "configs", "documents"):
            print(f"\n[{section.upper()}]")
            for item in result[section]:
                if section == "api":
                    print(f"- {item['symbol']} ({item['kind']}): {item['path']}:{item['line']}")
                elif section == "examples":
                    print(f"- {item['board']} / {item['name']}: {item['path']}")
                elif section == "configs":
                    first = item["occurrences"][0] if item["occurrences"] else {}
                    print(f"- {item['config']}: {first.get('path', '')}:{first.get('line', '')}")
                else:
                    print(f"- {item['title']}: {item['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
