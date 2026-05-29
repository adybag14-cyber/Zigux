#!/usr/bin/env python3
"""Fail closed when the Phase 10 sample/runtime parity scoreboard loses gate evidence."""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
SCOREBOARD_PATH = "Documentation/zigux/phase10-sample-runtime-parity-scoreboard.md"
VALIDATOR_PATH = "scripts/zigux/validate-phase10.py"

SCOREBOARD_MARKERS = [
    "PHASE10_SCOREBOARD_STATUS=active_shared_packet",
    "PHASE10_SCOREBOARD_SCOPE=sample-runtime-parity-notes-only",
    "PHASE10_SCOREBOARD_ROADMAP_ANCHORS=virtqueue-wrappers,mmio-wrappers,lab-only-driver-validation",
    "PHASE10_SCOREBOARD_RISKY_TRANSPORT=blocked_on_risky_transport",
    "PHASE10_SCOREBOARD_SHARED_VALIDATOR=scripts/zigux/validate-phase10.py",
    "PHASE10_SCOREBOARD_SHARED_VALIDATOR_CHECK_COUNT=11",
    "PHASE10_SCOREBOARD_SELF_TEST_CASE_COUNT=35",
    "scripts/zigux/check-phase10-ring-manifest-destinations.py",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "Documentation/zigux/phase10-closure-evidence.md",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "python3 scripts/zigux/validate-phase10.py --self-test",
    "python3 scripts/zigux/check-phase10-ring-manifest-destinations.py --self-test",
    "python3 scripts/zigux/check-phase10-sample-runtime-scoreboard.py --self-test",
    "python3 scripts/zigux/check-phase10-sample-runtime-scoreboard.py",
    "without claiming transport-backed queue discovery, IRQ delivery, DMA behavior, probe/remove lifecycle behavior, or risky dual-implementation parity",
]

VALIDATOR_MARKERS = [
    "scripts/zigux/check-phase10-ring-manifest-destinations.py",
    '"phase10-ring-manifest-destinations"',
]


def read_text(root: Path, rel_path: str) -> str | None:
    path = root / rel_path
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def collect_drift(root: Path) -> list[str]:
    drift: list[str] = []
    scoreboard = read_text(root, SCOREBOARD_PATH)
    validator = read_text(root, VALIDATOR_PATH)
    if scoreboard is None:
        drift.append(f"missing:{SCOREBOARD_PATH}")
    else:
        for marker in SCOREBOARD_MARKERS:
            if marker not in scoreboard:
                drift.append(f"scoreboard:{marker}")
    if validator is None:
        drift.append(f"missing:{VALIDATOR_PATH}")
    else:
        for marker in VALIDATOR_MARKERS:
            if marker not in validator:
                drift.append(f"validator:{marker}")
    return drift


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture(root: Path) -> None:
    write_text(root / SCOREBOARD_PATH, "\n".join(SCOREBOARD_MARKERS) + "\n")
    write_text(root / VALIDATOR_PATH, "\n".join(VALIDATOR_MARKERS) + "\n")


def expect_contains(items: list[str], expected: str, label: str) -> None:
    if expected not in items:
        actual = ",".join(items) if items else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_sample_runtime_scoreboard_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        if collect_drift(root):
            raise SystemExit("phase10-sample-runtime-scoreboard-self-test:baseline_failed")
        cases = 1

        scoreboard_path = root / SCOREBOARD_PATH
        original_scoreboard = scoreboard_path.read_text(encoding="utf-8")
        scoreboard_path.write_text(
            original_scoreboard.replace("PHASE10_SCOREBOARD_SHARED_VALIDATOR_CHECK_COUNT=11", "PHASE10_SCOREBOARD_SHARED_VALIDATOR_CHECK_COUNT=10", 1),
            encoding="utf-8",
        )
        expect_contains(
            collect_drift(root),
            "scoreboard:PHASE10_SCOREBOARD_SHARED_VALIDATOR_CHECK_COUNT=11",
            "phase10-sample-runtime-scoreboard-self-test",
        )
        cases += 1
        scoreboard_path.write_text(original_scoreboard, encoding="utf-8")

        scoreboard_path.write_text(
            original_scoreboard.replace("zigux/tests/phase10_virtio_ring_manifest.json", "zigux/tests/phase10_virtio_ring_missing.json", 1),
            encoding="utf-8",
        )
        expect_contains(
            collect_drift(root),
            "scoreboard:zigux/tests/phase10_virtio_ring_manifest.json",
            "phase10-sample-runtime-scoreboard-self-test",
        )
        cases += 1
        scoreboard_path.write_text(original_scoreboard, encoding="utf-8")

        scoreboard_path.write_text(
            original_scoreboard.replace("python3 scripts/zigux/check-phase10-sample-runtime-scoreboard.py", "python3 scripts/zigux/check-phase10-scoreboard-missing.py", 1),
            encoding="utf-8",
        )
        expect_contains(
            collect_drift(root),
            "scoreboard:python3 scripts/zigux/check-phase10-sample-runtime-scoreboard.py --self-test",
            "phase10-sample-runtime-scoreboard-self-test",
        )
        cases += 1
        scoreboard_path.write_text(original_scoreboard, encoding="utf-8")

        validator_path = root / VALIDATOR_PATH
        original_validator = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(original_validator.replace('\"phase10-ring-manifest-destinations\"', '\"phase10-ring-packet\"', 1), encoding="utf-8")
        expect_contains(
            collect_drift(root),
            'validator:"phase10-ring-manifest-destinations"',
            "phase10-sample-runtime-scoreboard-self-test",
        )
        cases += 1
        validator_path.write_text(original_validator, encoding="utf-8")

        scoreboard_path.unlink()
        expect_contains(
            collect_drift(root),
            f"missing:{SCOREBOARD_PATH}",
            "phase10-sample-runtime-scoreboard-self-test",
        )
        cases += 1

    print("PHASE10_SAMPLE_RUNTIME_SCOREBOARD_SELF_TEST=pass")
    print(f"PHASE10_SAMPLE_RUNTIME_SCOREBOARD_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 10 sample/runtime parity scoreboard evidence.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    drift = collect_drift(args.repo_root)
    if drift:
        print("PHASE10_SAMPLE_RUNTIME_SCOREBOARD=fail")
        print("PHASE10_SAMPLE_RUNTIME_SCOREBOARD_DRIFT_START")
        for item in drift:
            print(item)
        print("PHASE10_SAMPLE_RUNTIME_SCOREBOARD_DRIFT_END")
        return 1

    print("PHASE10_SAMPLE_RUNTIME_SCOREBOARD=pass")
    print(f"PHASE10_SAMPLE_RUNTIME_SCOREBOARD_MARKER_COUNT={len(SCOREBOARD_MARKERS)}")
    print(f"PHASE10_SAMPLE_RUNTIME_SCOREBOARD_VALIDATOR_MARKER_COUNT={len(VALIDATOR_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
