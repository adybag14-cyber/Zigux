#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


ROOT = repo_root()
FIXTURE_REL = "zigux/tests/fixtures/phase1_closure_validator_surface.json"
TARGET_REL = "scripts/zigux/validate-phase1-closure.py"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_fixture(path: Path) -> dict[str, object]:
    return json.loads(read_text(path))


def audit(target_text: str, fixture: dict[str, object]) -> list[str]:
    missing: list[str] = []
    snippets = fixture.get("required_snippets", [])
    if not isinstance(snippets, list):
        raise ValueError("fixture:required_snippets must be a list")
    for item in snippets:
        if not isinstance(item, dict):
            raise ValueError("fixture:required_snippets entries must be objects")
        item_id = item.get("id")
        snippet = item.get("snippet")
        if not isinstance(item_id, str) or not isinstance(snippet, str):
            raise ValueError("fixture:required_snippets entries need string id and snippet")
        if snippet not in target_text:
            missing.append(item_id)
    return missing


def run(target_path: Path, fixture_path: Path, strict: bool) -> int:
    fixture = load_fixture(fixture_path)
    missing = audit(read_text(target_path), fixture)
    if missing:
        print("PHASE1_CLOSURE_VALIDATOR_SURFACE=needs_update")
        print("MISSING_PHASE1_CLOSURE_VALIDATOR_SURFACE_START")
        for item_id in missing:
            print(item_id)
        print("MISSING_PHASE1_CLOSURE_VALIDATOR_SURFACE_END")
        return 1 if strict else 0

    print("PHASE1_CLOSURE_VALIDATOR_SURFACE=aligned")
    print(f"PHASE1_CLOSURE_VALIDATOR_SURFACE_TARGET_COUNT={len(fixture['required_snippets'])}")
    return 0


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def self_test() -> int:
    fixture = {
        "required_snippets": [
            {"id": "required_file_review_checklist", "snippet": '"Documentation/zigux/review-checklist.md",'},
            {"id": "required_file_tests_root", "snippet": '"zigux/tests/README.md",'},
            {"id": "required_file_bitmap_checker", "snippet": '"scripts/zigux/check-phase1-bitmap-validator-anchors.py",'},
            {"id": "review_checklist_marker", "snippet": '"- if the change touches the closed Phase 1 host-helper packet, do `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-bitmap-validator-anchors.py`, `scripts/zigux/check-phase1-find-bit-validator-anchors.py`, `scripts/zigux/check-phase1-route-summary-counts.py`, `scripts/zigux/check-phase1-validation-route-inventory.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/phase1_helpers.zig`, and `zigux/tests/phase1_bench.zig` still agree on the same closed helper inventory, validator-first replay path, and fail-closed checker stack?",'},
            {"id": "workflow_route_inventory_exact_count", "snippet": '"workflow_phase1_route_inventory_count",'},
            {"id": "makefile_route_inventory_exact_count", "snippet": '"makefile_phase1_route_inventory_count",'},
        ]
    }
    full_target = "\n".join(
        [
            '"Documentation/zigux/review-checklist.md",',
            '"zigux/tests/README.md",',
            '"scripts/zigux/check-phase1-bitmap-validator-anchors.py",',
            '"- if the change touches the closed Phase 1 host-helper packet, do `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-bitmap-validator-anchors.py`, `scripts/zigux/check-phase1-find-bit-validator-anchors.py`, `scripts/zigux/check-phase1-route-summary-counts.py`, `scripts/zigux/check-phase1-validation-route-inventory.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/phase1_helpers.zig`, and `zigux/tests/phase1_bench.zig` still agree on the same closed helper inventory, validator-first replay path, and fail-closed checker stack?",',
            '"workflow_phase1_route_inventory_count",',
            '"makefile_phase1_route_inventory_count",',
        ]
    )
    missing_target = "\n".join(
        [
            '"zigux/tests/README.md",',
            '"scripts/zigux/check-phase1-bitmap-validator-anchors.py",',
            '"makefile_phase1_route_inventory_count",',
        ]
    )

    with tempfile.TemporaryDirectory(prefix="phase1-closure-validator-surface-") as tmp:
        root = Path(tmp)
        fixture_path = root / FIXTURE_REL
        target_path = root / TARGET_REL
        write(fixture_path, json.dumps(fixture, indent=2) + "\n")
        write(target_path, full_target + "\n")

        if run(target_path, fixture_path, strict=False) != 0:
            raise AssertionError("expected aligned target to report success")
        if run(target_path, fixture_path, strict=True) != 0:
            raise AssertionError("expected aligned target to pass strict mode")

        write(target_path, missing_target + "\n")
        if run(target_path, fixture_path, strict=False) != 0:
            raise AssertionError("expected report mode to stay non-failing")
        if run(target_path, fixture_path, strict=True) != 1:
            raise AssertionError("expected strict mode to fail on missing snippets")

    print("PHASE1_CLOSURE_VALIDATOR_SURFACE_SELF_TEST=pass")
    print("PHASE1_CLOSURE_VALIDATOR_SURFACE_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=ROOT / TARGET_REL)
    parser.add_argument("--fixture", type=Path, default=ROOT / FIXTURE_REL)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    return run(args.target, args.fixture, strict=args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
