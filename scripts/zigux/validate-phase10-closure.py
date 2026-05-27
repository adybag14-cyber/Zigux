#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

REQUIRED_FILES = [
    "scripts/zigux/check-phase10-bootstrap-route.py",
    "scripts/zigux/check-phase10-core-packet.py",
    "scripts/zigux/check-phase10-closure-manifest-counts.py",
    "scripts/zigux/validate-phase10-closure.py",
    "scripts/zigux/validate-phase10.py",
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "scripts/zigux/check-phase10-ring-packet.py",
    "scripts/zigux/check-phase10-input-packet.py",
    "scripts/zigux/check-phase10-mmio-packet.py",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "zigux/Makefile",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
]

MAKE_MARKERS = [
    "PHONY += phase10-validate phase10-test phase10",
]

DOCS_ROOT_MARKERS = [
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`scripts/zigux/check-phase10-harness-coverage.py`",
    "`scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`zigux/tests/phase10_build.zig`",
    "`drivers/virtio/virtio_input_probe_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_probe_preflight.zig`",
    "`make -C zigux phase10-validate`",
    "`make -C zigux phase10-test`",
    "`make -C zigux phase10`",
    "while risky transport stays parked behind the shared closure manifest and its lane-local follow-through notes.",
]

CLOSURE_DOC_MARKERS = [
    "scripts/zigux/check-phase10-bootstrap-route.py",
    "scripts/zigux/check-phase10-ring-packet.py",
    "scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "scripts/zigux/check-phase10-input-packet.py",
    "scripts/zigux/check-phase10-mmio-packet.py",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "scripts/zigux/check-phase10-closure-manifest-counts.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/tests/phase10_closure_manifest.json",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md",
    "fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`",
    "shared reminder-surface drift",
    "manifest-backed survey provenance for the core packet now stays explicit through `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`",
    "core survey lane `P10-L01` remains tied to surveyed commit `c11221dc7a68d7511ae1c69d64b3f08528287ed8`",
]

LANE_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/tests/phase10_closure_manifest.json",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

REVIEW_CHECKLIST_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "Documentation/zigux/phase10-closure-evidence.md",
    "zigux/tests/phase10_closure_manifest.json",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

LEDGER_MARKERS = [
    "PHASE10_LEDGER_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md",
    "PHASE10_LEDGER_MANIFEST=zigux/tests/phase10_closure_manifest.json",
    "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
    "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L10",
    "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L22",
    "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11",
    "PHASE10_LEDGER_SURVEY_CORE_COMMIT=c11221dc7a68d7511ae1c69d64b3f08528287ed8",
    "PHASE10_LEDGER_SURVEY_RING_COMMIT=0aa2db32bcb1c7065850ee3f66ec119b071fbf5c",
    "PHASE10_LEDGER_SURVEY_INPUT_COMMIT=ee789f026f11a0c5c70ded9a868979cdf4f55393",
    "PHASE10_LEDGER_SURVEY_MMIO_COMMIT=b53ec2bd507d0b3283486e76acc273b184ad5bf8",
]

MANIFEST_MARKERS = [
    '"phase": "Phase 10"',
    '"tranche": "virtio-lab-bundle"',
    "scripts/zigux/check-phase10-bootstrap-route.py",
    '"scripts/zigux/check-phase10-harness-coverage.py"',
]

COMMANDS = [
    ["scripts/zigux/check-phase10-bootstrap-route.py", "--self-test"],
    ["scripts/zigux/check-phase10-bootstrap-route.py"],
    ["scripts/zigux/check-phase10-core-packet.py", "--self-test"],
    ["scripts/zigux/check-phase10-core-packet.py"],
    ["scripts/zigux/check-phase10-shared-freeze-boundary.py", "--self-test"],
    ["scripts/zigux/check-phase10-shared-freeze-boundary.py"],
    ["scripts/zigux/check-phase10-ring-packet.py", "--self-test"],
    ["scripts/zigux/check-phase10-ring-packet.py"],
    ["scripts/zigux/check-phase10-input-packet.py", "--self-test"],
    ["scripts/zigux/check-phase10-input-packet.py"],
    ["scripts/zigux/check-phase10-mmio-packet.py", "--self-test"],
    ["scripts/zigux/check-phase10-mmio-packet.py"],
    ["scripts/zigux/check-phase10-harness-coverage.py", "--self-test"],
    ["scripts/zigux/check-phase10-harness-coverage.py"],
    ["scripts/zigux/check-phase10-tests-readme-core-surfaces.py", "--self-test"],
    ["scripts/zigux/check-phase10-tests-readme-core-surfaces.py"],
    ["scripts/zigux/check-phase10-closure-manifest-counts.py", "--self-test"],
    ["scripts/zigux/check-phase10-closure-manifest-counts.py"],
    ["scripts/zigux/validate-phase10.py", "--self-test"],
    ["scripts/zigux/validate-phase10.py"],
]

EXACT_CHECK_COUNT = 15


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    checks = [
        ("make", "zigux/Makefile", MAKE_MARKERS),
        ("docs-root", "Documentation/zigux/README.md", DOCS_ROOT_MARKERS),
        ("closure", "Documentation/zigux/phase10-closure-evidence.md", CLOSURE_DOC_MARKERS),
        ("lane", "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", LANE_MARKERS),
        ("review", "Documentation/zigux/review-checklist.md", REVIEW_CHECKLIST_MARKERS),
        ("ledger", "zigux-alpha/PHASE10_CLOSURE_LEDGER.md", LEDGER_MARKERS),
        ("manifest", "zigux/tests/phase10_closure_manifest.json", MANIFEST_MARKERS),
    ]
    for label, rel_path, markers in checks:
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing.append(f"{label}:{marker}")
    return missing


def run_command(root: Path, command: list[str]) -> int:
    return subprocess.run([sys.executable, str(root / command[0]), *command[1:]], cwd=root, check=False).returncode


def run_required_commands(root: Path) -> list[str]:
    failures: list[str] = []
    for command in COMMANDS:
        if run_command(root, command) != 0:
            failures.append(" ".join(command))
    return failures


def write_fixture(root: Path) -> None:
    stub = "#!/usr/bin/env python3\nimport sys\nraise SystemExit(0)\n"
    for rel_path in [
        "scripts/zigux/validate-phase10.py",
        "scripts/zigux/check-phase10-bootstrap-route.py",
        "scripts/zigux/check-phase10-core-packet.py",
        "scripts/zigux/check-phase10-shared-freeze-boundary.py",
        "scripts/zigux/check-phase10-ring-packet.py",
        "scripts/zigux/check-phase10-input-packet.py",
        "scripts/zigux/check-phase10-mmio-packet.py",
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        "scripts/zigux/check-phase10-closure-manifest-counts.py",
    ]:
        write_text(root / rel_path, stub)

    for rel_path, markers in {
        "Documentation/zigux/README.md": DOCS_ROOT_MARKERS,
        "Documentation/zigux/phase10-closure-evidence.md": CLOSURE_DOC_MARKERS,
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": LANE_MARKERS,
        "Documentation/zigux/review-checklist.md": REVIEW_CHECKLIST_MARKERS,
        "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": LEDGER_MARKERS,
        "zigux/Makefile": MAKE_MARKERS,
        "zigux/tests/phase10_closure_manifest.json": MANIFEST_MARKERS,
    }.items():
        write_text(root / rel_path, "\n".join(markers) + "\n")

    write_text(root / "scripts/zigux/validate-phase10-closure.py", "fixture\n")
    write_text(root / ".github/workflows/zigux-bootstrap.yml", "name: zigux-bootstrap\n")
    for rel_path in [
        "zigux/tests/phase10_virtio_core_manifest.json",
        "zigux/tests/phase10_virtio_ring_manifest.json",
        "zigux/tests/phase10_virtio_input_manifest.json",
        "zigux/tests/phase10_virtio_mmio_manifest.json",
    ]:
        write_text(root / rel_path, "{}\n")


def expect_contains(items: list[str], expected: str, label: str) -> None:
    if expected not in items:
        actual = ",".join(items) if items else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        if collect_missing_files(root) or collect_missing_markers(root) or run_required_commands(root):
            raise SystemExit("phase10-closure-self-test:baseline_failed")
        cases = 1

        docs_root = root / "Documentation/zigux/README.md"
        original_docs_root = docs_root.read_text(encoding="utf-8")
        docs_root.write_text(
            original_docs_root.replace(
                "while risky transport stays parked behind the shared closure manifest and its lane-local follow-through notes.",
                "while risky transport stays parked behind the shared closure packet.",
                1,
            ),
            encoding="utf-8",
        )
        expect_contains(
            collect_missing_markers(root),
            "docs-root:while risky transport stays parked behind the shared closure manifest and its lane-local follow-through notes.",
            "phase10-closure-self-test",
        )
        cases += 1
        docs_root.write_text(original_docs_root, encoding="utf-8")

        closure_doc = root / "Documentation/zigux/phase10-closure-evidence.md"
        original_doc = closure_doc.read_text(encoding="utf-8")
        closure_doc.write_text(original_doc.replace("shared reminder-surface drift", "shared note drift", 1), encoding="utf-8")
        expect_contains(collect_missing_markers(root), "closure:shared reminder-surface drift", "phase10-closure-self-test")
        cases += 1
        closure_doc.write_text(original_doc, encoding="utf-8")

        closure_doc.write_text(
            original_doc.replace(
                "scripts/zigux/check-phase10-closure-manifest-counts.py",
                "scripts/zigux/check-phase10-missing-checker.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_contains(
            collect_missing_markers(root),
            "closure:scripts/zigux/check-phase10-closure-manifest-counts.py",
            "phase10-closure-self-test",
        )
        cases += 1
        closure_doc.write_text(original_doc, encoding="utf-8")

        ledger = root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        original_ledger = ledger.read_text(encoding="utf-8")
        ledger.write_text(original_ledger.replace("PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11", "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L12", 1), encoding="utf-8")
        expect_contains(collect_missing_markers(root), "ledger:PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11", "phase10-closure-self-test")
        cases += 1
        ledger.write_text(original_ledger, encoding="utf-8")

        closure_doc.write_text(
            original_doc.replace(
                "core survey lane `P10-L01` remains tied to surveyed commit `c11221dc7a68d7511ae1c69d64b3f08528287ed8`",
                "core survey lane `P10-L02` remains tied to surveyed commit `c11221dc7a68d7511ae1c69d64b3f08528287ed8`",
                1,
            ),
            encoding="utf-8",
        )
        expect_contains(
            collect_missing_markers(root),
            "closure:core survey lane `P10-L01` remains tied to surveyed commit `c11221dc7a68d7511ae1c69d64b3f08528287ed8`",
            "phase10-closure-self-test",
        )
        cases += 1
        closure_doc.write_text(original_doc, encoding="utf-8")

        manifest = root / "zigux/tests/phase10_closure_manifest.json"
        original_manifest = manifest.read_text(encoding="utf-8")
        manifest.write_text(original_manifest.replace('"scripts/zigux/check-phase10-harness-coverage.py"', '"scripts/zigux/check-phase10-missing.py"', 1), encoding="utf-8")
        expect_contains(collect_missing_markers(root), 'manifest:"scripts/zigux/check-phase10-harness-coverage.py"', "phase10-closure-self-test")
        cases += 1
        manifest.write_text(original_manifest, encoding="utf-8")

        (root / "scripts/zigux/check-phase10-closure-manifest-counts.py").write_text(
            "#!/usr/bin/env python3\nimport sys\nraise SystemExit(0 if '--self-test' in sys.argv else 1)\n",
            encoding="utf-8",
        )
        failures = run_required_commands(root)
        if failures != ["scripts/zigux/check-phase10-closure-manifest-counts.py"]:
            actual = ",".join(failures) if failures else "none"
            raise SystemExit(f"phase10-closure-self-test:failed_counts_command_not_detected:{actual}")
        cases += 1
        write_fixture(root)

        (root / "scripts/zigux/check-phase10-ring-packet.py").write_text(
            "#!/usr/bin/env python3\nraise SystemExit(1)\n",
            encoding="utf-8",
        )
        failures = run_required_commands(root)
        expected = [
            "scripts/zigux/check-phase10-ring-packet.py --self-test",
            "scripts/zigux/check-phase10-ring-packet.py",
        ]
        if failures != expected:
            actual = ",".join(failures) if failures else "none"
            raise SystemExit(f"phase10-closure-self-test:failed_ring_command_not_detected:{actual}")
        cases += 1
        write_fixture(root)

        (root / "scripts/zigux/validate-phase10.py").write_text(
            "#!/usr/bin/env python3\nimport sys\nraise SystemExit(0 if '--self-test' in sys.argv else 1)\n",
            encoding="utf-8",
        )
        failures = run_required_commands(root)
        if failures != ["scripts/zigux/validate-phase10.py"]:
            actual = ",".join(failures) if failures else "none"
            raise SystemExit(f"phase10-closure-self-test:failed_live_validate_command_not_detected:{actual}")
        cases += 1
        write_fixture(root)

        (root / "Documentation/zigux/README.md").unlink()
        missing = collect_missing_files(root)
        expect_contains(missing, "Documentation/zigux/README.md", "phase10-closure-self-test")
        cases += 1
        write_fixture(root)

        (root / "zigux/tests/phase10_virtio_mmio_manifest.json").unlink()
        missing = collect_missing_files(root)
        expect_contains(missing, "zigux/tests/phase10_virtio_mmio_manifest.json", "phase10-closure-self-test")
        cases += 1

    print("PHASE10_CLOSURE_VALIDATION_SELF_TEST=pass")
    print(f"PHASE10_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={cases}")
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

    command_failures = run_required_commands(ROOT)
    if command_failures:
        print("PHASE10_CLOSURE_VALIDATION=fail")
        print("PHASE10_CLOSURE_REQUIRED_COMMAND_FAILURES_START")
        for item in command_failures:
            print(item)
        print("PHASE10_CLOSURE_REQUIRED_COMMAND_FAILURES_END")
        return 1

    print("PHASE10_CLOSURE_VALIDATION=pass")
    print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE10_CLOSURE_REQUIRED_MARKER_COUNT={len(MAKE_MARKERS) + len(DOCS_ROOT_MARKERS) + len(CLOSURE_DOC_MARKERS) + len(LANE_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(LEDGER_MARKERS) + len(MANIFEST_MARKERS)}")
    print(f"PHASE10_CLOSURE_EXACT_CHECK_COUNT={EXACT_CHECK_COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
