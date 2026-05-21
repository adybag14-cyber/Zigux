#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=compile_shard_matrix

Fail-closed checker for the bounded Phase 14 compile-shard matrix survey.

This guard cross-reads the machine-readable shared smoke manifest and the
human-readable compile-shard matrix survey so the roadmap-backed Phase 14
anchor coverage stays explicit without promoting the broader wrapper family
or any deep-core status change.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=compile_shard_matrix"
SURVEY_PATH = Path("Documentation/zigux/phase14-compile-shard-matrix-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
RELEASE_BOUNDARY_PATH = Path("Documentation/zigux/phase14-release-boundary-survey.md")

EXPECTED_COUNTS = {
    "total": 6,
    "focused_and_full_bundle": 1,
    "full_bundle_only": 5,
}

EXPECTED_ANCHOR_ROWS = (
    (
        "kernel/workqueue.c",
        "P14-L04",
        "phase14-workqueue-bridge-tests",
        "phase14-workqueue-reviewability-tests",
    ),
    (
        "kernel/trace/ring_buffer.c",
        "P14-L08",
        "phase14-ring-buffer-survey-tests",
    ),
    (
        "net/core/skbuff.c",
        "P14-L11",
        "phase14-skbuff-bridge-tests",
    ),
    (
        "kernel/rcu/tree.c",
        "P14-L16",
        "phase14-rcu-tree-survey-tests",
    ),
)

REQUIRED_SURVEY_MARKERS = (
    "# Phase 14 Compile Shard Matrix Survey",
    "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
    "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`",
    "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`",
    "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
    "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
    "- shared gate: `make -C zigux phase14-validate`",
    "- broader wrapper gaps: `phase14-smoke`, `phase14-test`, and `phase14` remain absent from the readable current `zigux/Makefile` body",
    "- machine-readable source: `zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "- shared survey shard: `phase14-end-to-end-smoke-tests` (`focused_and_full_bundle`)",
)

REQUIRED_RELEASE_BOUNDARY_MARKERS = (
    "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
    "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`",
    "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`",
    "publishes the exact six-row compile-shard matrix",
)


def require_markers(errors: list[str], rel: Path, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def load_manifest(root: Path) -> dict:
    return json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))


def find_anchor_lane(manifest: dict, anchor: str) -> str | None:
    for packet in manifest.get("anchor_packets", []):
        if packet.get("anchor") == anchor:
            return packet.get("lane_key")
    return None


def count_coverage(manifest: dict, coverage: str) -> int:
    return sum(1 for shard in manifest.get("compile_shards", []) if shard.get("coverage") == coverage)


def has_shard(manifest: dict, label: str) -> bool:
    return any(shard.get("label") == label for shard in manifest.get("compile_shards", []))


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in (SURVEY_PATH, MANIFEST_PATH, RELEASE_BOUNDARY_PATH):
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    survey_text = (root / SURVEY_PATH).read_text(encoding="utf-8")
    require_markers(errors, SURVEY_PATH, survey_text, REQUIRED_SURVEY_MARKERS)

    release_boundary_text = (root / RELEASE_BOUNDARY_PATH).read_text(encoding="utf-8")
    require_markers(errors, RELEASE_BOUNDARY_PATH, release_boundary_text, REQUIRED_RELEASE_BOUNDARY_MARKERS)

    manifest = load_manifest(root)
    compile_shards = manifest.get("compile_shards", [])
    if len(compile_shards) != EXPECTED_COUNTS["total"]:
        errors.append(
            f"manifest_value_mismatch:compile_shards.total:expected={EXPECTED_COUNTS['total']!r}:actual={len(compile_shards)!r}"
        )
    focused_count = count_coverage(manifest, "focused_and_full_bundle")
    if focused_count != EXPECTED_COUNTS["focused_and_full_bundle"]:
        errors.append(
            "manifest_value_mismatch:compile_shards.focused_and_full_bundle:"
            f"expected={EXPECTED_COUNTS['focused_and_full_bundle']!r}:actual={focused_count!r}"
        )
    full_bundle_only_count = count_coverage(manifest, "full_bundle_only")
    if full_bundle_only_count != EXPECTED_COUNTS["full_bundle_only"]:
        errors.append(
            "manifest_value_mismatch:compile_shards.full_bundle_only:"
            f"expected={EXPECTED_COUNTS['full_bundle_only']!r}:actual={full_bundle_only_count!r}"
        )

    smoke_commands = manifest.get("smoke_commands")
    if smoke_commands != ["make -C zigux phase14-validate"]:
        errors.append(
            f"manifest_value_mismatch:smoke_commands:expected={['make -C zigux phase14-validate']!r}:actual={smoke_commands!r}"
        )

    for anchor, lane_key, *labels in EXPECTED_ANCHOR_ROWS:
        actual_lane = find_anchor_lane(manifest, anchor)
        if actual_lane != lane_key:
            errors.append(
                f"manifest_value_mismatch:anchor_lane:{anchor}:expected={lane_key!r}:actual={actual_lane!r}"
            )
        survey_anchor_marker = f"- `{anchor}` -> lane `{lane_key}`"
        if survey_anchor_marker not in survey_text:
            errors.append(f"missing_marker:{SURVEY_PATH.as_posix()}:{survey_anchor_marker}")
        for label in labels:
            if not has_shard(manifest, label):
                errors.append(f"missing_manifest_shard:{label}")
            shard_marker = f"  - `{label}`"
            if shard_marker not in survey_text:
                errors.append(f"missing_marker:{SURVEY_PATH.as_posix()}:{shard_marker}")

    return errors


def fixture_manifest() -> str:
    payload = {
        "anchor_packets": [
            {"lane_key": "P14-L04", "anchor": "kernel/workqueue.c"},
            {"lane_key": "P14-L11", "anchor": "net/core/skbuff.c"},
            {"lane_key": "P14-L08", "anchor": "kernel/trace/ring_buffer.c"},
            {"lane_key": "P14-L16", "anchor": "kernel/rcu/tree.c"},
        ],
        "smoke_commands": ["make -C zigux phase14-validate"],
        "compile_shards": [
            {"label": "phase14-workqueue-bridge-tests", "coverage": "full_bundle_only"},
            {"label": "phase14-workqueue-reviewability-tests", "coverage": "full_bundle_only"},
            {"label": "phase14-skbuff-bridge-tests", "coverage": "full_bundle_only"},
            {"label": "phase14-ring-buffer-survey-tests", "coverage": "full_bundle_only"},
            {"label": "phase14-rcu-tree-survey-tests", "coverage": "full_bundle_only"},
            {"label": "phase14-end-to-end-smoke-tests", "coverage": "focused_and_full_bundle"},
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def fixture_survey() -> str:
    return """# Phase 14 Compile Shard Matrix Survey

- `PHASE14_COMPILE_SHARD_TOTAL=6`
- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`
- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`
- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`
- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`
- shared gate: `make -C zigux phase14-validate`
- broader wrapper gaps: `phase14-smoke`, `phase14-test`, and `phase14` remain absent from the readable current `zigux/Makefile` body
- machine-readable source: `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- shared survey shard: `phase14-end-to-end-smoke-tests` (`focused_and_full_bundle`)
- `kernel/workqueue.c` -> lane `P14-L04`
  - `phase14-workqueue-bridge-tests`
  - `phase14-workqueue-reviewability-tests`
- `kernel/trace/ring_buffer.c` -> lane `P14-L08`
  - `phase14-ring-buffer-survey-tests`
- `net/core/skbuff.c` -> lane `P14-L11`
  - `phase14-skbuff-bridge-tests`
- `kernel/rcu/tree.c` -> lane `P14-L16`
  - `phase14-rcu-tree-survey-tests`
"""


def fixture_release_boundary() -> str:
    return """# Phase 14 Release Boundary Survey

- `PHASE14_COMPILE_SHARD_TOTAL=6`
- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`
- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json` now returns through the current contents path and publishes the exact six-row compile-shard matrix with one `focused_and_full_bundle` shard and five `full_bundle_only` shards
"""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root / SURVEY_PATH, fixture_survey())
    write_text(root / MANIFEST_PATH, fixture_manifest())
    write_text(root / RELEASE_BOUNDARY_PATH, fixture_release_boundary())


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-compile-shard-matrix-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_COMPILE_SHARD_MATRIX_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        cases = 1

        write_fixture_tree(base)
        payload = json.loads((base / MANIFEST_PATH).read_text(encoding="utf-8"))
        payload["compile_shards"].pop()
        write_text(base / MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")
        if not any("compile_shards.total" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_SELF_TEST=fail")
            print("expected total-count drift failure")
            return 1
        cases += 1

        write_fixture_tree(base)
        payload = json.loads((base / MANIFEST_PATH).read_text(encoding="utf-8"))
        payload["anchor_packets"][0]["lane_key"] = "P14-L99"
        write_text(base / MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")
        if not any("anchor_lane:kernel/workqueue.c" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_SELF_TEST=fail")
            print("expected anchor-lane drift failure")
            return 1
        cases += 1

        write_fixture_tree(base)
        write_text(base / SURVEY_PATH, fixture_survey().replace("- `PHASE14_COMPILE_SHARD_TOTAL=6`\n", "", 1))
        if not any("PHASE14_COMPILE_SHARD_TOTAL=6" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_SELF_TEST=fail")
            print("expected survey-count marker failure")
            return 1
        cases += 1

        write_fixture_tree(base)
        write_text(
            base / RELEASE_BOUNDARY_PATH,
            fixture_release_boundary().replace("publishes the exact six-row compile-shard matrix", "drops the exact matrix wording", 1),
        )
        if not any("publishes the exact six-row compile-shard matrix" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_SELF_TEST=fail")
            print("expected release-boundary marker failure")
            return 1
        cases += 1

        print("PHASE14_COMPILE_SHARD_MATRIX_SELF_TEST=pass")
        print(f"PHASE14_COMPILE_SHARD_MATRIX_SELF_TEST_CASE_COUNT={cases}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_COMPILE_SHARD_MATRIX=fail")
        print("PHASE14_COMPILE_SHARD_MATRIX_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_COMPILE_SHARD_MATRIX_ISSUES_END")
        return 1

    print("PHASE14_COMPILE_SHARD_MATRIX=pass")
    print(f"PHASE14_COMPILE_SHARD_MATRIX_EXPECTED_TOTAL={EXPECTED_COUNTS['total']}")
    print(f"PHASE14_COMPILE_SHARD_MATRIX_EXPECTED_FOCUSED={EXPECTED_COUNTS['focused_and_full_bundle']}")
    print(f"PHASE14_COMPILE_SHARD_MATRIX_EXPECTED_FULL_BUNDLE_ONLY={EXPECTED_COUNTS['full_bundle_only']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())