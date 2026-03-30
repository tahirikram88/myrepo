#!/usr/bin/env python3
"""
Mock pre-check orchestrator for 300 SnapMirror relationships.

Usage:
  python3 netapp_cutover_precheck.py --mock --output sample_output_precheck.csv
  python3 netapp_cutover_precheck.py --input sample_snapmirror_status.json --output report.csv

This version is intentionally interview-friendly:
- readable
- idempotent
- easy to explain
- supports mock execution without a live NetApp cluster
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any


GREEN_MAX_LAG_MINUTES = 30
AMBER_MAX_LAG_MINUTES = 120


@dataclass
class VolumeStatus:
    volume: str
    svm: str
    state: str
    healthy: bool
    lag_minutes: int
    last_transfer_type: str
    last_transfer_end: str
    last_error: str
    rag_status: str
    reason: str


def evaluate(item: Dict[str, Any]) -> VolumeStatus:
    state = item.get("state", "unknown")
    healthy = bool(item.get("healthy", False))
    lag_minutes = int(item.get("lag_minutes", 999999))
    last_error = item.get("last_error", "").strip()

    rag = "GREEN"
    reason = "Replication healthy"

    if state.lower() != "snapmirrored":
        rag = "RED"
        reason = f"Unexpected state: {state}"
    elif not healthy:
        rag = "RED"
        reason = "Relationship unhealthy"
    elif last_error:
        rag = "RED"
        reason = f"Last transfer error: {last_error}"
    elif lag_minutes > AMBER_MAX_LAG_MINUTES:
        rag = "RED"
        reason = f"Lag {lag_minutes}m exceeds hard stop threshold"
    elif lag_minutes > GREEN_MAX_LAG_MINUTES:
        rag = "AMBER"
        reason = f"Lag {lag_minutes}m exceeds green threshold"

    return VolumeStatus(
        volume=item["volume"],
        svm=item["svm"],
        state=state,
        healthy=healthy,
        lag_minutes=lag_minutes,
        last_transfer_type=item.get("last_transfer_type", "unknown"),
        last_transfer_end=item.get("last_transfer_end", ""),
        last_error=last_error,
        rag_status=rag,
        reason=reason,
    )


def overall_decision(results: List[VolumeStatus]) -> str:
    critical_reds = [r for r in results if r.rag_status == "RED" and r.volume.startswith(("eng-", "prod-", "core-"))]
    if critical_reds:
        return "NO-GO"
    reds = [r for r in results if r.rag_status == "RED"]
    if reds:
        return "NO-GO"
    return "GO"


def load_mock_data() -> List[Dict[str, Any]]:
    return [
        {"volume": "eng-home-01", "svm": "svm_eng", "state": "SnapMirrored", "healthy": True, "lag_minutes": 8, "last_transfer_type": "incremental", "last_transfer_end": "2026-03-30T21:10:00Z", "last_error": ""},
        {"volume": "prod-build-02", "svm": "svm_prod", "state": "SnapMirrored", "healthy": True, "lag_minutes": 42, "last_transfer_type": "incremental", "last_transfer_end": "2026-03-30T20:55:00Z", "last_error": ""},
        {"volume": "archive-legacy-77", "svm": "svm_archive", "state": "BrokenOff", "healthy": False, "lag_minutes": 999, "last_transfer_type": "incremental", "last_transfer_end": "2026-03-29T09:00:00Z", "last_error": "snapmirror state broken"},
    ]


def write_csv(results: List[VolumeStatus], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(results[0]).keys()) if results else [
        "volume", "svm", "state", "healthy", "lag_minutes", "last_transfer_type",
        "last_transfer_end", "last_error", "rag_status", "reason"
    ]
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(asdict(row))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Use built-in mock data")
    parser.add_argument("--input", help="JSON input file containing SnapMirror relationship data")
    parser.add_argument("--output", required=True, help="CSV output path")
    args = parser.parse_args()

    if not args.mock and not args.input:
        print("Choose either --mock or --input", file=sys.stderr)
        return 2

    if args.mock:
        raw = load_mock_data()
    else:
        raw = json.loads(Path(args.input).read_text(encoding="utf-8"))

    results = [evaluate(item) for item in raw]
    write_csv(results, Path(args.output))

    go_no_go = overall_decision(results)
    greens = sum(1 for r in results if r.rag_status == "GREEN")
    ambers = sum(1 for r in results if r.rag_status == "AMBER")
    reds = sum(1 for r in results if r.rag_status == "RED")

    print(f"Volumes checked: {len(results)}")
    print(f"GREEN: {greens}  AMBER: {ambers}  RED: {reds}")
    print(f"OVERALL DECISION: {go_no_go}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
