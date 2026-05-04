#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

FILES = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
]

MAKE_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py --self-test",
    "scripts/zigux/check-phase10-harness-coverage.py",
]

WORKFLOW_MARKERS = [
    "Self-test Phase 10 harness coverage checker",
    "python3 scripts/zigux/check-phase10-harness-coverage.py --self-test",
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
]

SCRIPTS_README_MARKERS = [
    "check-phase10-harness-coverage.py",
    "phase10_virtio_input_multitouch_preflight.zig",
    "phase10_virtio_mmio_queue_isolation.zig",
]

SCRIPTS_README_EXACT_ONCE_MARKERS = [
    "check-phase10-harness-coverage.py",
    "phase10_virtio_input_multitouch_preflight.zig",
    "phase10_virtio_mmio_queue_isolation.zig",
]

TESTS_README_MARKERS = [
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "scripts/zigux/check-phase10-closure-inventory.py",
    "scripts/zigux/check-phase10-core-packet.py",
    "four lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
]

TESTS_README_EXACT_ONCE_MARKERS = [
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "scripts/zigux/check-phase10-closure-inventory.py",
    "scripts/zigux/check-phase10-core-packet.py",
]

DOCS_README_MARKERS = [
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "focused harness replays",
    "queue-handling and ready-state gate",
]

DOCS_README_EXACT_ONCE_MARKERS = [
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "queue-handling and ready-state gate",
]

BUILD_MARKERS = [
    "phase10-virtio-input-multitouch-preflight-tests",
    "phase10-virtio-mmio-queue-isolation-tests",
]

CLOSURE_NOTE_MARKERS = [
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "PHASE10_TEST_COUNT=11",
]

CLOSURE_NOTE_EXACT_ONCE_MARKERS = [
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "PHASE10_TEST_COUNT=11",
]

GUIDE_MARKERS = [
    "focused ring drained-reset reuse replay",
]

GUIDE_EXACT_ONCE_MARKERS = [
    "- `python3 scripts/zigux/check-phase10-harness-coverage.py --self-test`",
    "- `python3 scripts/zigux/check-phase10-harness-coverage.py`",
    "- `zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "- `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`",
    "- `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`",
]

COMPANION_MARKERS = [
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "focused ring drained-reset reuse replay",
]

COMPANION_EXACT_ONCE_MARKERS = [
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
]

INPUT_PREFLIGHT_TEST_MARKERS = [
    'test "phase10 virtio input queue and probe preflight carry multitouch slot intent through ready state" {',
    "queueCallbackPreflightSummary()",
    "probePreflightSummary()",
    "MultitouchSlotMinimumNegative",
]

MMIO_QUEUE_ISOLATION_TEST_MARKERS = [
    'test "phase10 virtio mmio keeps queue state isolated across queue selection changes" {',
    "selectQueue(0)",
    "selectQueue(1)",
    "QueueReadyBlocksAddressRewrite",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> dict[str, object]:
    return json.loads(read_text(root, rel_path))


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def check_exact_count(
    missing: list[str], label: str, text: str, marker: str, expected: int = 1
) -> None:
    actual = text.count(marker)
    if actual != expected:
        missing.append(f"{label}:count:{marker}={actual}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []
    for name, rel_path, markers in [
        ("make", "zigux/Makefile", MAKE_MARKERS),
        ("workflow", ".github/workflows/zigux-bootstrap.yml", WORKFLOW_MARKERS),
        ("scripts_readme", "scripts/zigux/README.md", SCRIPTS_README_MARKERS),
        ("tests_readme", "zigux/tests/README.md", TESTS_README_MARKERS),
        ("docs_readme", "Documentation/zigux/README.md", DOCS_README_MARKERS),
        ("build", "zigux/tests/phase10_build.zig", BUILD_MARKERS),
        ("closure_note", "Documentation/zigux/phase10-closure-evidence.md", CLOSURE_NOTE_MARKERS),
        (
            "guide",
            "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
            GUIDE_MARKERS,
        ),
        (
            "companion",
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            COMPANION_MARKERS,
        ),
        (
            "input_preflight_test",
            "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
            INPUT_PREFLIGHT_TEST_MARKERS,
        ),
        (
            "mmio_queue_isolation_test",
            "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
            MMIO_QUEUE_ISOLATION_TEST_MARKERS,
        ),
    ]:
        check_markers(missing, name, read_text(root, rel_path), markers)

    for name, rel_path, markers in [
        ("scripts_readme", "scripts/zigux/README.md", SCRIPTS_README_EXACT_ONCE_MARKERS),
        ("tests_readme", "zigux/tests/README.md", TESTS_README_EXACT_ONCE_MARKERS),
        ("docs_readme", "Documentation/zigux/README.md", DOCS_README_EXACT_ONCE_MARKERS),
        (
            "closure_note",
            "Documentation/zigux/phase10-closure-evidence.md",
            CLOSURE_NOTE_EXACT_ONCE_MARKERS,
        ),
        (
            "guide",
            "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
            GUIDE_EXACT_ONCE_MARKERS,
        ),
        (
            "companion",
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            COMPANION_EXACT_ONCE_MARKERS,
        ),
    ]:
        text = read_text(root, rel_path)
        for marker in markers:
            check_exact_count(missing, name, text, marker)

    closure_manifest = load_json(root, "zigux/tests/phase10_closure_manifest.json")
    if closure_manifest.get("test_count") != 11:
        missing.append("closure_manifest:test_count=11")

    tests = closure_manifest.get("tests")
    if not isinstance(tests, list):
        missing.append("closure_manifest:tests")
    else:
        for path in [
            "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
            "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
            "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
        ]:
            if path not in tests:
                missing.append(f"closure_manifest:tests:{path}")

    scoreboard = closure_manifest.get("roadmap_parity_scoreboard")
    if not isinstance(scoreboard, dict):
        missing.append("closure_manifest:roadmap_parity_scoreboard")
    else:
        lab_validation = scoreboard.get("lab_only_driver_validation")
        if not isinstance(lab_validation, dict):
            missing.append("closure_manifest:roadmap_parity_scoreboard:lab_only_driver_validation")
        else:
            evidence = lab_validation.get("evidence")
            if not isinstance(evidence, list):
                missing.append("closure_manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence")
            else:
                for path in [
                    "zigux/tests/phase10_build.zig",
                    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
                    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
                    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
                    "scripts/zigux/check-phase10-harness-coverage.py",
                ]:
                    if path not in evidence:
                        missing.append(
                            "closure_manifest:roadmap_parity_scoreboard:"
                            f"lab_only_driver_validation:evidence:{path}"
                        )

    return [], missing


def write_fixture(root: Path) -> None:
    text_files = {
        "scripts/zigux/check-phase10-harness-coverage.py": "fixture\n",
        "scripts/zigux/README.md": "\n".join(SCRIPTS_README_MARKERS) + "\n",
        "zigux/tests/README.md": "\n".join(TESTS_README_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
        ".github/workflows/zigux-bootstrap.yml": "\n".join(WORKFLOW_MARKERS) + "\n",
        "Documentation/zigux/README.md": "\n".join(DOCS_README_MARKERS) + "\n",
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(CLOSURE_NOTE_MARKERS) + "\n",
        "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md": "\n".join(GUIDE_MARKERS + GUIDE_EXACT_ONCE_MARKERS) + "\n",
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": "\n".join(COMPANION_MARKERS) + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_input_multitouch_preflight.zig": "\n".join(INPUT_PREFLIGHT_TEST_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_mmio_queue_isolation.zig": "\n".join(MMIO_QUEUE_ISOLATION_TEST_MARKERS) + "\n",
        "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": "fixture\n",
    }
    manifest = {
        "test_count": 11,
        "tests": [
            "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
            "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
            "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
        ],
        "roadmap_parity_scoreboard": {
            "lab_only_driver_validation": {
                "evidence": [
                    "zigux/tests/phase10_build.zig",
                    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
                    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
                    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
                    "scripts/zigux/check-phase10-harness-coverage.py",
                ]
            }
        },
    }

    for rel_path in FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path == "zigux/tests/phase10_closure_manifest.json":
            path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        else:
            path.write_text(text_files[rel_path], encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase10-harness-self-test:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase10-harness-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def expect_missing_file(label: str, root: Path, expected_file: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(
            f"phase10-harness-self-test:{label}:unexpected_missing_markers:{','.join(missing_markers)}"
        )
    if expected_file not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(
            f"phase10-harness-self-test:{label}:expected_missing_file:{expected_file}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_harness_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-harness-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        makefile_path = root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "scripts/zigux/check-phase10-harness-coverage.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_harness_self_test_hook",
            root,
            "make:scripts/zigux/check-phase10-harness-coverage.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "Self-test Phase 10 harness coverage checker\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_harness_self_test_step",
            root,
            "workflow:Self-test Phase 10 harness coverage checker",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        docs_readme_path = root / "Documentation/zigux/README.md"
        original_docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            original_docs_readme.replace(
                "python3 scripts/zigux/check-phase10-harness-coverage.py",
                "python3 scripts/zigux/check-phase10-harness-coverage-drift.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "docs_readme_harness_gate",
            root,
            "docs_readme:python3 scripts/zigux/check-phase10-harness-coverage.py",
        )
        docs_readme_path.write_text(original_docs_readme, encoding="utf-8")

        docs_readme_path.write_text(
            original_docs_readme.replace(
                "focused harness replays",
                "focused replay drift",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "docs_readme_harness_phrase",
            root,
            "docs_readme:focused harness replays",
        )
        docs_readme_path.write_text(original_docs_readme, encoding="utf-8")

        docs_readme_path.write_text(
            original_docs_readme + "\npython3 scripts/zigux/check-phase10-harness-coverage.py\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "docs_readme_harness_gate_duplicate",
            root,
            "docs_readme:count:python3 scripts/zigux/check-phase10-harness-coverage.py=2",
        )
        docs_readme_path.write_text(original_docs_readme, encoding="utf-8")

        docs_readme_path.write_text(
            original_docs_readme + "\nqueue-handling and ready-state gate\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "docs_readme_ready_state_phrase_duplicate",
            root,
            "docs_readme:count:queue-handling and ready-state gate=2",
        )
        docs_readme_path.write_text(original_docs_readme, encoding="utf-8")

        guide_path = root / "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md"
        original_guide = guide_path.read_text(encoding="utf-8")
        guide_path.write_text(
            original_guide.replace(
                "- `zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
                "- `zigux/tests/phase10_virtio_ring_reset_reuse_drift.zig`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "guide_ring_reset_reuse_entry",
            root,
            "guide:count:- `zigux/tests/phase10_virtio_ring_reset_reuse.zig`=0",
        )
        guide_path.write_text(original_guide, encoding="utf-8")

        guide_path.write_text(
            original_guide.replace(
                "focused ring drained-reset reuse replay",
                "focused ring replay drift",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "guide_ring_reset_reuse_phrase",
            root,
            "guide:focused ring drained-reset reuse replay",
        )
        guide_path.write_text(original_guide, encoding="utf-8")

        guide_path.write_text(
            original_guide + "\n- `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "guide_mmio_queue_isolation_duplicate",
            root,
            "guide:count:- `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`=2",
        )
        guide_path.write_text(original_guide, encoding="utf-8")

        guide_path.write_text(
            original_guide + "\n- `python3 scripts/zigux/check-phase10-harness-coverage.py`\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "guide_harness_gate_duplicate",
            root,
            "guide:count:- `python3 scripts/zigux/check-phase10-harness-coverage.py`=2",
        )
        guide_path.write_text(original_guide, encoding="utf-8")

        build_path = root / "zigux/tests/phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace(
                "phase10-virtio-mmio-queue-isolation-tests",
                "phase10-virtio-mmio-queue-isolation-drift",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "build_queue_isolation_marker",
            root,
            "build:phase10-virtio-mmio-queue-isolation-tests",
        )
        build_path.write_text(original_build, encoding="utf-8")

        scripts_readme_path = root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "phase10_virtio_mmio_queue_isolation.zig",
                "phase10_virtio_mmio_queue_isolation_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_queue_isolation_entry",
            root,
            "scripts_readme:phase10_virtio_mmio_queue_isolation.zig",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme + "\ncheck-phase10-harness-coverage.py\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_harness_checker_duplicate",
            root,
            "scripts_readme:count:check-phase10-harness-coverage.py=2",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme + "\nphase10_virtio_input_multitouch_preflight.zig\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_multitouch_duplicate",
            root,
            "scripts_readme:count:phase10_virtio_input_multitouch_preflight.zig=2",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        tests_readme_path = root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
                "zigux/tests/phase10_virtio_input_multitouch_preflight_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_multitouch_entry",
            root,
            "tests_readme:zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "four lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
                "three lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_manifest_summary",
            root,
            "tests_readme:four lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "scripts/zigux/check-phase10-closure-inventory.py",
                "scripts/zigux/check-phase10-closure-inventory-drift.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_closure_inventory_entry",
            root,
            "tests_readme:scripts/zigux/check-phase10-closure-inventory.py",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme + "\nscripts/zigux/check-phase10-core-packet.py\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_core_packet_duplicate",
            root,
            "tests_readme:count:scripts/zigux/check-phase10-core-packet.py=2",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme + "\nzigux/tests/phase10_virtio_input_multitouch_preflight.zig\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_multitouch_duplicate",
            root,
            "tests_readme:count:zigux/tests/phase10_virtio_input_multitouch_preflight.zig=2",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        closure_note_path = root / "Documentation/zigux/phase10-closure-evidence.md"
        original_closure_note = closure_note_path.read_text(encoding="utf-8")
        closure_note_path.write_text(
            original_closure_note.replace(
                "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
                "zigux/tests/phase10_virtio_mmio_queue_isolation_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_note_queue_isolation_entry",
            root,
            "closure_note:zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
        )
        closure_note_path.write_text(original_closure_note, encoding="utf-8")

        closure_note_path.write_text(
            original_closure_note + "\nPHASE10_TEST_COUNT=11\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_note_test_count_duplicate",
            root,
            "closure_note:count:PHASE10_TEST_COUNT=11=2",
        )
        closure_note_path.write_text(original_closure_note, encoding="utf-8")

        closure_note_path.write_text(
            original_closure_note + "\nzigux/tests/phase10_virtio_mmio_queue_isolation.zig\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_note_queue_isolation_duplicate",
            root,
            "closure_note:count:zigux/tests/phase10_virtio_mmio_queue_isolation.zig=2",
        )
        closure_note_path.write_text(original_closure_note, encoding="utf-8")

        companion_path = root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
        original_companion = companion_path.read_text(encoding="utf-8")
        companion_path.write_text(
            original_companion.replace(
                "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
                "zigux-alpha/PHASE10_CLOSURE_LEDGER_DRIFT.md",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "companion_closure_ledger_entry",
            root,
            "companion:zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
        )
        companion_path.write_text(original_companion, encoding="utf-8")

        companion_path.write_text(
            original_companion.replace(
                "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
                "zigux/tests/phase10_virtio_ring_reset_reuse_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "companion_ring_reset_reuse_entry",
            root,
            "companion:zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        )
        companion_path.write_text(original_companion, encoding="utf-8")

        companion_path.write_text(
            original_companion + "\nzigux-alpha/PHASE10_CLOSURE_LEDGER.md\n",
            encoding="utf-8")
        expect_missing_marker(
            "companion_closure_ledger_duplicate",
            root,
            "companion:count:zigux-alpha/PHASE10_CLOSURE_LEDGER.md=2",
        )
        companion_path.write_text(original_companion, encoding="utf-8")

        companion_path.write_text(
            original_companion + "\nzigux/tests/phase10_virtio_ring_survey.zig\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "companion_ring_survey_duplicate",
            root,
            "companion:count:zigux/tests/phase10_virtio_ring_survey.zig=2",
        )
        companion_path.write_text(original_companion, encoding="utf-8")

        manifest_path = root / "zigux/tests/phase10_closure_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["test_count"] = 10
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "closure_manifest_test_count",
            root,
            "closure_manifest:test_count=11",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tests"] = [
            "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
            "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "closure_manifest_tests_inventory",
            root,
            "closure_manifest:tests:zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tests"] = [
            "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
            "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "closure_manifest_ring_reset_reuse_test_inventory",
            root,
            "closure_manifest:tests:zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        evidence = manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
        manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            path for path in evidence if path != "scripts/zigux/check-phase10-harness-coverage.py"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "closure_manifest_harness_evidence",
            root,
            "closure_manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence:scripts/zigux/check-phase10-harness-coverage.py",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        evidence = manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
        manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            path for path in evidence if path != "zigux/tests/phase10_build.zig"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "closure_manifest_phase10_build_evidence",
            root,
            "closure_manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence:zigux/tests/phase10_build.zig",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        evidence = manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
        manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            path
            for path in evidence
            if path != "zigux/tests/phase10_virtio_ring_reset_reuse.zig"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "closure_manifest_ring_reset_reuse_evidence",
            root,
            "closure_manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence:zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        )
        write_fixture(root)

        input_preflight_path = root / "zigux/tests/phase10_virtio_input_multitouch_preflight.zig"
        original_input_preflight = input_preflight_path.read_text(encoding="utf-8")
        input_preflight_path.unlink()
        expect_missing_file(
            "input_preflight_file",
            root,
            "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
        )
        input_preflight_path.write_text(original_input_preflight, encoding="utf-8")

        input_preflight_path.write_text(
            original_input_preflight.replace(
                "probePreflightSummary()",
                "probePreflightSummaryDrift()",
                1,
            ),
            encoding="utf-8")
        expect_missing_marker(
            "input_preflight_probe_summary_marker",
            root,
            "input_preflight_test:probePreflightSummary()",
        )
        input_preflight_path.write_text(original_input_preflight, encoding="utf-8")

        queue_isolation_path = root / "zigux/tests/phase10_virtio_mmio_queue_isolation.zig"
        original_queue_isolation = queue_isolation_path.read_text(encoding="utf-8")
        queue_isolation_path.unlink()
        expect_missing_file(
            "queue_isolation_file",
            root,
            "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
        )
        queue_isolation_path.write_text(original_queue_isolation, encoding="utf-8")

        queue_isolation_path.write_text(
            original_queue_isolation.replace(
                "QueueReadyBlocksAddressRewrite",
                "QueueReadyBlocksRewriteDrift",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "queue_isolation_test_guard",
            root,
            "mmio_queue_isolation_test:QueueReadyBlocksAddressRewrite",
        )
        queue_isolation_path.write_text(original_queue_isolation, encoding="utf-8")

        ledger_path = root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        ledger_path.unlink()
        expect_missing_file(
            "closure_ledger_file",
            root,
            "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
        )

    print("PHASE10_HARNESS_COVERAGE_SELF_TEST=pass")
    print("PHASE10_HARNESS_COVERAGE_SELF_TEST_CASE_COUNT=38")
    return 0


if "--self-test" in sys.argv[1:]:
    sys.exit(run_self_test())

missing_files, missing_markers = validate(ROOT)
if missing_files:
    print("PHASE10_HARNESS_COVERAGE=fail")
    print("MISSING_PHASE10_HARNESS_FILES_START")
    for item in missing_files:
        print(item)
    print("MISSING_PHASE10_HARNESS_FILES_END")
    sys.exit(1)
if missing_markers:
    print("PHASE10_HARNESS_COVERAGE=fail")
    print("MISSING_PHASE10_HARNESS_MARKERS_START")
    for item in missing_markers:
        print(item)
    print("MISSING_PHASE10_HARNESS_MARKERS_END")
    sys.exit(1)

print("PHASE10_HARNESS_COVERAGE=pass")
print(f"PHASE10_HARNESS_REQUIRED_FILE_COUNT={len(FILES)}")
print(
    "PHASE10_HARNESS_REQUIRED_MARKER_COUNT="
    f"{len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(SCRIPTS_README_MARKERS) + len(SCRIPTS_README_EXACT_ONCE_MARKERS) + len(TESTS_README_MARKERS) + len(TESTS_README_EXACT_ONCE_MARKERS) + len(DOCS_README_MARKERS) + len(DOCS_README_EXACT_ONCE_MARKERS) + len(BUILD_MARKERS) + len(CLOSURE_NOTE_MARKERS) + len(CLOSURE_NOTE_EXACT_ONCE_MARKERS) + len(GUIDE_MARKERS) + len(GUIDE_EXACT_ONCE_MARKERS) + len(COMPANION_MARKERS) + len(COMPANION_EXACT_ONCE_MARKERS) + len(INPUT_PREFLIGHT_TEST_MARKERS) + len(MMIO_QUEUE_ISOLATION_TEST_MARKERS)}"
)
