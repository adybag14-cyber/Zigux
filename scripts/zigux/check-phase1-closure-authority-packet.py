#!/usr/bin/env python3
"""Guard the current Phase 1 closure-authority packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_TEXT_FILES = {
    "Documentation/zigux/phase1-closure.md": [
        "- authority: current Linux C behavior remains the parity source",
        "- `PHASE1_HELPER_COUNT=13`",
        "- `PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py`",
        "- `scripts/zigux/check-phase1-installer-review-surfaces.py`",
        "- `scripts/zigux/check-phase1-installer-companion-checks.py`",
    ],
    "Documentation/zigux/README.md": [
        "- `scripts/zigux/check-phase1-installer-companion-checks.py` remains a focused companion check beside the counted docs-root packet instead of widening the exact marker line that `scripts/zigux/validate-phase1.py` enforces.",
        "- `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test` and `python3 scripts/zigux/check-phase1-installer-companion-checks.py` keep the docs-root companion note split explicit too: the self-test replays the bounded checker logic, while the live route guards the shipped Phase 1 reminder surfaces without widening the counted docs-root packet line that `scripts/zigux/validate-phase1.py` enforces.",
        "- `scripts/zigux/check-phase1-direct-owner-markers.py` also remains part of the live Phase 1 reminder packet beside `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` instead of leaving the helper-family owner map implicit from the lane note alone.",
        "- `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test` and `python3 scripts/zigux/check-phase1-direct-owner-markers.py` keep that owner-map replay explicit too: the self-test replays the bounded exact-count logic, while the live route guards the shipped Phase 1 direct-owner markers without widening the counted reminder packet.",
    ],
    "Documentation/zigux/review-checklist.md": [
        "* if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py`, `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`, `python3 scripts/zigux/check-phase1-installer-companion-checks.py`, `zigux/tests/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` still agree on the same closed helper tranche and validator-first replay path without widening Phase 1 beyond the bounded host-side helper packet?",
        "* if the change touches that same Phase 1 companion packet, does the checklist still say clearly that `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test` replays the bounded checker logic while `python3 scripts/zigux/check-phase1-installer-companion-checks.py` guards the shipped Phase 1 reminder surfaces without widening the counted docs-root packet line that `scripts/zigux/validate-phase1.py` enforces?",
    ],
    "scripts/zigux/README.md": [
        "- `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep that same closed host-side helper packet reviewable through the docs-root closure record, the shared owner-map note, the reviewer-facing checklist, the workflow-viability installer, the dedicated installer-review alignment checker, the dedicated installer-companion checker packet, the bootstrap workflow replay, and the Linux-style replay routes instead of leaving the Phase 1 closure stack visible only through direct script and Zig commands.",
        "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, and `zigux/tests/fixtures/phase1_helper_manifest.json` also keep the shared Phase 1 helper sequencing split explicit: `tools/lib/argv_split.zig`, `tools/lib/cmdline.zig`, `tools/lib/ctype.zig`, `tools/lib/hweight.zig`, `tools/lib/list_sort.zig`, `tools/lib/slab.zig`, `tools/lib/str_error_r.zig`, `tools/lib/vsprintf.zig`, and `tools/lib/zalloc.zig` stay parked on shared-replay packet drift only, while `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` keep the only direct helper-local follow-up anchors on current `master`, so shared reminder work should not batch those two sets back together.",
    ],
    "scripts/zigux/validate-phase1-closure.py": [
        '"scripts/zigux/check-phase1-direct-owner-markers.py",',
        '"scripts/zigux/check-phase1-installer-companion-checks.py",',
        '"scripts/zigux/check-phase1-installer-review-surfaces.py",',
        '"scripts/zigux/validate-phase1-closure.py",',
        '"run: python3 scripts/zigux/validate-phase1-closure.py",',
        '"run: python3 scripts/zigux/check-phase1-bench.py",',
        '"phase1-validate:",',
        '"phase1: phase1-validate phase1-test phase1-bench",',
    ],
    "zigux/Makefile": [
        "phase1-validate:",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py",
        "phase1: phase1-validate phase1-test phase1-bench",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "run: python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test",
        "run: python3 scripts/zigux/check-phase1-installer-review-surfaces.py",
        "run: python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test",
        "run: python3 scripts/zigux/check-phase1-installer-companion-checks.py",
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "run: python3 scripts/zigux/check-phase1-bench.py",
    ],
}

REQUIRED_JSON_FILES = {
    "zigux/tests/fixtures/phase1_helper_manifest.json": {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "lane_sequencing": {
            "direct_anchor_followup_helpers": [
                "tools/lib/bitmap.zig",
                "tools/lib/find_bit.zig",
                "tools/lib/rbtree.zig",
                "tools/lib/string.zig",
            ],
            "rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",
        },
    },
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_text_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path, markers in REQUIRED_TEXT_FILES.items():
        path = root / relative_path
        if not path.is_file():
            failures.append(f"missing_file:{relative_path}")
            continue
        text = read_text(root, relative_path)
        lines = [line.strip() for line in text.splitlines()]
        for marker in markers:
            count = sum(1 for line in lines if line == marker.strip())
            if count != 1:
                failures.append(f"{relative_path}:expected_once:actual_count={count}:{marker}")
    return failures


def collect_json_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path, expected in REQUIRED_JSON_FILES.items():
        path = root / relative_path
        if not path.is_file():
            failures.append(f"missing_file:{relative_path}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(
                f"{relative_path}:json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"
            )
            continue
        if payload.get("phase") != expected["phase"]:
            failures.append(f"{relative_path}:phase:{payload.get('phase')!r}")
        if payload.get("status") != expected["status"]:
            failures.append(f"{relative_path}:status:{payload.get('status')!r}")
        if payload.get("helper_count") != expected["helper_count"]:
            failures.append(f"{relative_path}:helper_count:{payload.get('helper_count')!r}")
        lane = payload.get("lane_sequencing")
        if not isinstance(lane, dict):
            failures.append(f"{relative_path}:lane_sequencing:missing")
            continue
        if lane.get("direct_anchor_followup_helpers") != expected["lane_sequencing"]["direct_anchor_followup_helpers"]:
            failures.append(f"{relative_path}:direct_anchor_followup_helpers:{lane.get('direct_anchor_followup_helpers')!r}")
        if lane.get("rule_summary") != expected["lane_sequencing"]["rule_summary"]:
            failures.append(f"{relative_path}:rule_summary:{lane.get('rule_summary')!r}")
    return failures


def collect_failures(root: Path) -> list[str]:
    return collect_text_failures(root) + collect_json_failures(root)


def build_sample_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_TEXT_FILES.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")
    for relative_path, expected in REQUIRED_JSON_FILES.items():
        write_text(root, relative_path, json.dumps(expected, indent=2) + "\n")


def remove_text_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    updated = text.replace(marker + "\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    path.write_text(updated, encoding="utf-8")


def corrupt_manifest(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["lane_sequencing"]["direct_anchor_followup_helpers"] = [
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
    ]
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("success", None)]
    for relative_path in REQUIRED_TEXT_FILES:
        cases.append(
            (
                f"missing_file:{relative_path}",
                lambda root, relative_path=relative_path: (root / relative_path).unlink(),
            )
        )
    for relative_path, markers in REQUIRED_TEXT_FILES.items():
        for marker in markers:
            cases.append(
                (
                    f"missing_marker:{relative_path}:{abs(hash(marker))}",
                    lambda root, relative_path=relative_path, marker=marker: remove_text_marker(
                        root, relative_path, marker
                    ),
                )
            )
    cases.append(("corrupt_manifest", corrupt_manifest))

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-authority-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_AUTHORITY_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_AUTHORITY_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_AUTHORITY_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    marker_count = sum(len(markers) for markers in REQUIRED_TEXT_FILES.values()) + 5
    file_count = len(REQUIRED_TEXT_FILES) + len(REQUIRED_JSON_FILES)
    print("PHASE1_CLOSURE_AUTHORITY_PACKET=pass")
    print(f"PHASE1_CLOSURE_AUTHORITY_PACKET_REQUIRED_FILE_COUNT={file_count}")
    print(f"PHASE1_CLOSURE_AUTHORITY_PACKET_REQUIRED_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
