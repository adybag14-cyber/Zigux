#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "scripts/zigux/validate-phase10-closure.py",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "zigux/Makefile",
    "zigux/tests/phase10_closure_manifest.json",
]

MAKE_MARKERS = [
    "PHONY += phase10-validate phase10-test phase10",
    "phase10-validate:",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "phase10: phase10-validate phase10-test",
]

CLOSURE_DOC_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/validate-phase10.py",
    "zigux/tests/phase10_closure_manifest.json",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "shared reminder-surface drift",
]

LANE_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/validate-phase10.py",
    "zigux/tests/phase10_closure_manifest.json",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

MANIFEST_MARKERS = [
    '"phase": "Phase 10"',
    '"tranche": "virtio-lab-bundle"',
    '"scripts/zigux/check-phase10-harness-coverage.py"',
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    checks = [
        ("make", "zigux/Makefile", MAKE_MARKERS),
        ("closure", "Documentation/zigux/phase10-closure-evidence.md", CLOSURE_DOC_MARKERS),
        ("lane", "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", LANE_MARKERS),
        ("manifest", "zigux/tests/phase10_closure_manifest.json", MANIFEST_MARKERS),
    ]
    for label, rel_path, markers in checks:
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing.append(f"{label}:{marker}")
    return missing


def run(cmd: list[str]) -> int:
    return subprocess.run(cmd, cwd=ROOT, check=False).returncode


def write_fixture(root: Path) -> None:
    files = {
        "scripts/zigux/validate-phase10-closure.py": "fixture\n",
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(CLOSURE_DOC_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": "\n".join(LANE_MARKERS) + "\n",
        "scripts/zigux/check-phase10-harness-coverage.py": "fixture\n",
        "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
        "zigux/tests/phase10_closure_manifest.json": "\n".join(MANIFEST_MARKERS) + "\n",
    }
    for rel_path, content in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files = collect_missing_files(root)
        missing_markers = collect_missing_markers(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-closure-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        makefile = root / "zigux/Makefile"
        makefile.write_text(makefile.read_text(encoding="utf-8").replace("phase10-validate:\n", "", 1), encoding="utf-8")
        if "make:phase10-validate:" not in collect_missing_markers(root):
            raise SystemExit("phase10-closure-self-test:missing_make_marker_not_detected")
        write_fixture(root)

        closure = root / "Documentation/zigux/phase10-closure-evidence.md"
        closure.write_text(closure.read_text(encoding="utf-8").replace("shared reminder-surface drift\n", "", 1), encoding="utf-8")
        if "closure:shared reminder-surface drift" not in collect_missing_markers(root):
            raise SystemExit("phase10-closure-self-test:missing_closure_marker_not_detected")
        write_fixture(root)

        lane = root / "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"
        lane.write_text(lane.read_text(encoding="utf-8").replace("make -C zigux phase10-validate\n", "", 1), encoding="utf-8")
        if "lane:make -C zigux phase10-validate" not in collect_missing_markers(root):
            raise SystemExit("phase10-closure-self-test:missing_lane_marker_not_detected")
        write_fixture(root)

        manifest = root / "zigux/tests/phase10_closure_manifest.json"
        manifest.write_text(manifest.read_text(encoding="utf-8").replace('"scripts/zigux/check-phase10-harness-coverage.py"\n', "", 1), encoding="utf-8")
        if 'manifest:"scripts/zigux/check-phase10-harness-coverage.py"' not in collect_missing_markers(root):
            raise SystemExit("phase10-closure-self-test:missing_manifest_marker_not_detected")

    print("PHASE10_CLOSURE_VALIDATION_SELF_TEST=pass")
    print("PHASE10_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 closure packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files = collect_missing_files(ROOT)
    if missing_files:
        print("PHASE10_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE10_CLOSURE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_CLOSURE_FILES_END")
        return 1

    missing_markers = collect_missing_markers(ROOT)
    if missing_markers:
        print("PHASE10_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE10_CLOSURE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_CLOSURE_MARKERS_END")
        return 1

    commands = [
        [sys.executable, str(ROOT / "scripts/zigux/check-phase10-harness-coverage.py"), "--self-test"],
        [sys.executable, str(ROOT / "scripts/zigux/check-phase10-harness-coverage.py")],
    ]
    for command in commands:
        if run(command) != 0:
            print("PHASE10_CLOSURE_VALIDATION=fail")
            print(f"PHASE10_CLOSURE_VALIDATION_FAILED_COMMAND={' '.join(command[1:])}")
            return 1

    print("PHASE10_CLOSURE_VALIDATION=pass")
    print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE10_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(MAKE_MARKERS) + len(CLOSURE_DOC_MARKERS) + len(LANE_MARKERS) + len(MANIFEST_MARKERS)}"
    )
    print("PHASE10_CLOSURE_COMMAND_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
