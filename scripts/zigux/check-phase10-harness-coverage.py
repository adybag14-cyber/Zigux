#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

FILES = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
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
    "phase10_virtio_ring_reset_reuse.zig",
    "phase10_virtio_input_multitouch_preflight.zig",
    "phase10_virtio_mmio_queue_isolation.zig",
]

TESTS_README_MARKERS = [
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "scripts/zigux/check-phase10-closure-inventory.py",
    "scripts/zigux/check-phase10-core-packet.py",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "four lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
]

DOCS_README_MARKERS = [
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "focused ring drained-reset reuse replay",
    "focused harness replays",
    "queue-handling and ready-state gate",
]

CHECKLIST_MARKERS = [
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
]

BUILD_MARKERS = [
    "phase10-virtio-ring-reset-reuse-tests",
    "phase10-virtio-input-multitouch-preflight-tests",
    "phase10-virtio-mmio-queue-isolation-tests",
]

CLOSURE_NOTE_MARKERS = [
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "PHASE10_TEST_COUNT=11",
]

GUIDE_MARKERS = [
    "focused ring drained-reset reuse replay",
    "- `python3 scripts/zigux/check-phase10-harness-coverage.py --self-test`",
    "- `python3 scripts/zigux/check-phase10-harness-coverage.py`",
    "- `zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
    "- `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`",
    "- `zigux/tests/phase10_virtio_input_registration_blocker_build.zig`",
    "- `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`",
]

COMPANION_MARKERS = [
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "focused ring drained-reset reuse replay",
]

RING_RESET_REUSE_TEST_MARKERS = [
    'test "phase10 virtio ring drained reset clears the broken flag so the queue can be reused" {',
    'test "phase10 virtio ring drained reset restores callback bookkeeping to a clean reuse baseline" {',
    "brokenSummary(2)",
    "enableCallbackDelayed(3)",
]

INPUT_PREFLIGHT_TEST_MARKERS = [
    'test "phase10 virtio input queue and probe preflight carry multitouch slot intent through ready state" {',
    "queueCallbackPreflightSummary()",
    "probePreflightSummary()",
    "MultitouchSlotMinimumNegative",
]

BLOCKER_BUILD_MARKERS = [
    "phase10_virtio_input_registration_blocker.zig",
    "../../drivers/virtio/virtio_input_registration_blocker.zig",
    "phase10-virtio-input-registration-blocker-tests",
    "Run the focused Phase 10 virtio input registration blocker replay",
]

MMIO_QUEUE_ISOLATION_TEST_MARKERS = [
    'test "phase10 virtio mmio keeps queue state isolated across queue selection changes" {',
    'test "phase10 virtio mmio reset clears legacy and modern queue address plans after queue selection changes" {',
    "selectQueue(0)",
    "selectQueue(1)",
    "QueueReadyBlocksAddressRewrite",
    "const reset = window.reset();",
    "queueAddressSummary(.legacy)",
    "queueAddressSummary(.modern)",
    "QueueAddressRequiresConfiguredSize",
]

EXPECTED_FOCUSED_HARNESS_REPLAYS = {
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig": [
        "phase10 ring drained-reset reuse replay"
    ],
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig": [
        "phase10 input multitouch-ready preflight replay"
    ],
    "zigux/tests/phase10_virtio_input_registration_blocker_build.zig": [
        "phase10 input registration-blocker replay build"
    ],
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig": [
        "phase10 mmio multi-queue isolation replay",
        "phase10 mmio reset clears legacy and modern queue address plans after queue selection changes",
    ],
}

EXACT_ONCE = [
    ("scripts_readme", "scripts/zigux/README.md", "phase10_virtio_ring_reset_reuse.zig"),
    ("scripts_readme", "scripts/zigux/README.md", "phase10_virtio_input_multitouch_preflight.zig"),
    ("scripts_readme", "scripts/zigux/README.md", "phase10_virtio_mmio_queue_isolation.zig"),
    ("tests_readme", "zigux/tests/README.md", "zigux/tests/phase10_virtio_ring_reset_reuse.zig"),
    ("tests_readme", "zigux/tests/README.md", "zigux/tests/phase10_virtio_input_multitouch_preflight.zig"),
    ("tests_readme", "zigux/tests/README.md", "zigux/tests/phase10_virtio_input_registration_blocker_build.zig"),
    ("tests_readme", "zigux/tests/README.md", "zigux/tests/phase10_virtio_mmio_queue_isolation.zig"),
    ("docs_readme", "Documentation/zigux/README.md", "zigux/tests/phase10_virtio_ring_reset_reuse.zig"),
    ("docs_readme", "Documentation/zigux/README.md", "zigux/tests/phase10_virtio_input_multitouch_preflight.zig"),
    ("docs_readme", "Documentation/zigux/README.md", "zigux/tests/phase10_virtio_input_registration_blocker_build.zig"),
    ("docs_readme", "Documentation/zigux/README.md", "zigux/tests/phase10_virtio_mmio_queue_isolation.zig"),
    ("docs_readme", "Documentation/zigux/README.md", "focused ring drained-reset reuse replay"),
    ("docs_readme", "Documentation/zigux/README.md", "queue-handling and ready-state gate"),
    ("checklist", "Documentation/zigux/review-checklist.md", "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"),
    ("checklist", "Documentation/zigux/review-checklist.md", "scripts/zigux/check-phase10-harness-coverage.py"),
    ("checklist", "Documentation/zigux/review-checklist.md", "zigux/tests/phase10_virtio_ring_reset_reuse.zig"),
    ("checklist", "Documentation/zigux/review-checklist.md", "zigux/tests/phase10_virtio_input_multitouch_preflight.zig"),
    ("checklist", "Documentation/zigux/review-checklist.md", "zigux/tests/phase10_virtio_input_registration_blocker_build.zig"),
    ("checklist", "Documentation/zigux/review-checklist.md", "zigux/tests/phase10_virtio_mmio_queue_isolation.zig"),
    ("closure_note", "Documentation/zigux/phase10-closure-evidence.md", "zigux/tests/phase10_virtio_ring_reset_reuse.zig"),
    ("closure_note", "Documentation/zigux/phase10-closure-evidence.md", "zigux/tests/phase10_virtio_input_multitouch_preflight.zig"),
    ("closure_note", "Documentation/zigux/phase10-closure-evidence.md", "zigux/tests/phase10_virtio_input_registration_blocker_build.zig"),
    ("closure_note", "Documentation/zigux/phase10-closure-evidence.md", "zigux/tests/phase10_virtio_mmio_queue_isolation.zig"),
    ("closure_note", "Documentation/zigux/phase10-closure-evidence.md", "PHASE10_TEST_COUNT=11"),
    ("guide", "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md", "- `zigux/tests/phase10_virtio_ring_reset_reuse.zig`"),
    ("guide", "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md", "- `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`"),
    ("guide", "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md", "- `zigux/tests/phase10_virtio_input_registration_blocker_build.zig`"),
    ("guide", "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md", "- `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`"),
    ("companion", "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"),
    ("companion", "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", "zigux/tests/phase10_virtio_ring_reset_reuse.zig"),
    ("companion", "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", "zigux/tests/phase10_virtio_input_registration_blocker_build.zig"),
    ("companion", "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", "zigux/tests/phase10_virtio_ring_survey.zig"),
]

def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")

def load_json(root: Path, rel_path: str) -> dict[str, object]:
    return json.loads(read_text(root, rel_path))

def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")

def check_exact_count(missing: list[str], label: str, text: str, marker: str) -> None:
    actual = text.count(marker)
    if actual != 1:
        missing.append(f"{label}:count:{marker}={actual}")

def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []
    checks = [
        ("make", "zigux/Makefile", MAKE_MARKERS),
        ("workflow", ".github/workflows/zigux-bootstrap.yml", WORKFLOW_MARKERS),
        ("scripts_readme", "scripts/zigux/README.md", SCRIPTS_README_MARKERS),
        ("tests_readme", "zigux/tests/README.md", TESTS_README_MARKERS),
        ("docs_readme", "Documentation/zigux/README.md", DOCS_README_MARKERS),
        ("checklist", "Documentation/zigux/review-checklist.md", CHECKLIST_MARKERS),
        ("build", "zigux/tests/phase10_build.zig", BUILD_MARKERS),
        ("closure_note", "Documentation/zigux/phase10-closure-evidence.md", CLOSURE_NOTE_MARKERS),
        ("guide", "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md", GUIDE_MARKERS),
        ("companion", "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", COMPANION_MARKERS),
        ("ring_reset_reuse_test", "zigux/tests/phase10_virtio_ring_reset_reuse.zig", RING_RESET_REUSE_TEST_MARKERS),
        ("input_preflight_test", "zigux/tests/phase10_virtio_input_multitouch_preflight.zig", INPUT_PREFLIGHT_TEST_MARKERS),
        ("blocker_build", "zigux/tests/phase10_virtio_input_registration_blocker_build.zig", BLOCKER_BUILD_MARKERS),
        ("mmio_queue_isolation_test", "zigux/tests/phase10_virtio_mmio_queue_isolation.zig", MMIO_QUEUE_ISOLATION_TEST_MARKERS),
    ]
    for label, rel_path, markers in checks:
        check_markers(missing, label, read_text(root, rel_path), markers)

    for label, rel_path, marker in EXACT_ONCE:
        check_exact_count(missing, label, read_text(root, rel_path), marker)

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
                    "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
                    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
                    "scripts/zigux/check-phase10-harness-coverage.py",
                ]:
                    if path not in evidence:
                        missing.append(
                            "closure_manifest:roadmap_parity_scoreboard:"
                            f"lab_only_driver_validation:evidence:{path}"
                        )

    if closure_manifest.get("focused_harness_replays") != EXPECTED_FOCUSED_HARNESS_REPLAYS:
        missing.append("closure_manifest:focused_harness_replays")

    return [], missing

def write_fixture(root: Path) -> None:
    text_files = {
        "scripts/zigux/check-phase10-harness-coverage.py": "fixture\n",
        "scripts/zigux/README.md": "\n".join(SCRIPTS_README_MARKERS) + "\n",
        "zigux/tests/README.md": "\n".join(TESTS_README_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
        ".github/workflows/zigux-bootstrap.yml": "\n".join(WORKFLOW_MARKERS) + "\n",
        "Documentation/zigux/README.md": "\n".join(DOCS_README_MARKERS) + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(CHECKLIST_MARKERS) + "\n",
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(CLOSURE_NOTE_MARKERS) + "\n",
        "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md": "\n".join(GUIDE_MARKERS) + "\n",
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": "\n".join(COMPANION_MARKERS) + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_ring_reset_reuse.zig": "\n".join(RING_RESET_REUSE_TEST_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_input_multitouch_preflight.zig": "\n".join(INPUT_PREFLIGHT_TEST_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_input_registration_blocker_build.zig": "\n".join(BLOCKER_BUILD_MARKERS) + "\n",
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
                    "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
                    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
                    "scripts/zigux/check-phase10-harness-coverage.py",
                ]
            }
        },
        "focused_harness_replays": EXPECTED_FOCUSED_HARNESS_REPLAYS,
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

def expect_missing_file(label: str, root: Path, rel_path: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(
            f"phase10-harness-self-test:{label}:unexpected_missing_markers:{','.join(missing_markers)}"
        )
    if rel_path not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(
            f"phase10-harness-self-test:{label}:expected_missing_file:{rel_path}:actual:{actual}"
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

        build_path = root / "zigux/tests/phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace("phase10-virtio-ring-reset-reuse-tests", "phase10-ring-drift", 1),
            encoding="utf-8",
        )
        expect_missing_marker("build_ring_reset_reuse_marker", root, "build:phase10-virtio-ring-reset-reuse-tests")
        build_path.write_text(original_build, encoding="utf-8")

        scripts_readme_path = root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace("phase10_virtio_ring_reset_reuse.zig", "phase10_ring_drift.zig", 1),
            encoding="utf-8",
        )
        expect_missing_marker("scripts_readme_ring_entry", root, "scripts_readme:phase10_virtio_ring_reset_reuse.zig")
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        tests_readme_path = root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
                "zigux/tests/phase10_ring_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker("tests_readme_ring_entry", root, "tests_readme:zigux/tests/phase10_virtio_ring_reset_reuse.zig")
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
                "zigux/tests/phase10_input_blocker_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_blocker_build_entry",
            root,
            "tests_readme:zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
                "zigux-alpha/PHASE10_LEDGER_DRIFT.md",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_closure_ledger_entry",
            root,
            "tests_readme:zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        docs_readme_path = root / "Documentation/zigux/README.md"
        original_docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            original_docs_readme.replace("focused ring drained-reset reuse replay", "focused ring drift", 1),
            encoding="utf-8",
        )
        expect_missing_marker("docs_readme_ring_phrase", root, "docs_readme:focused ring drained-reset reuse replay")
        docs_readme_path.write_text(original_docs_readme, encoding="utf-8")

        checklist_path = root / "Documentation/zigux/review-checklist.md"
        original_checklist = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(
            original_checklist.replace(
                "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
                "zigux-alpha/PHASE10_LEDGER_DRIFT.md",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "checklist_closure_ledger_entry",
            root,
            "checklist:zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
        )
        checklist_path.write_text(original_checklist, encoding="utf-8")

        checklist_path.write_text(
            original_checklist.replace(
                "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
                "zigux/tests/phase10_ring_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "checklist_ring_entry",
            root,
            "checklist:zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        )
        checklist_path.write_text(original_checklist, encoding="utf-8")

        write_fixture(root)
        blocker_build_path = root / "zigux/tests/phase10_virtio_input_registration_blocker_build.zig"
        blocker_build_path.unlink()
        expect_missing_file(
            "blocker_build_file",
            root,
            "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
        )
        write_fixture(root)

        blocker_build_path = root / "zigux/tests/phase10_virtio_input_registration_blocker_build.zig"
        original_blocker_build = blocker_build_path.read_text(encoding="utf-8")
        blocker_build_path.write_text(
            original_blocker_build.replace(
                "phase10-virtio-input-registration-blocker-tests",
                "phase10-input-blocker-drift",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "blocker_build_marker",
            root,
            "blocker_build:phase10-virtio-input-registration-blocker-tests",
        )
        blocker_build_path.write_text(original_blocker_build, encoding="utf-8")

        closure_note_path = root / "Documentation/zigux/phase10-closure-evidence.md"
        original_closure_note = closure_note_path.read_text(encoding="utf-8")
        closure_note_path.write_text(
            original_closure_note.replace(
                "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
                "zigux/tests/phase10_ring_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker("closure_note_ring_entry", root, "closure_note:zigux/tests/phase10_virtio_ring_reset_reuse.zig")
        closure_note_path.write_text(original_closure_note, encoding="utf-8")

        ring_reset_reuse_path = root / "zigux/tests/phase10_virtio_ring_reset_reuse.zig"
        original_ring_reset_reuse = ring_reset_reuse_path.read_text(encoding="utf-8")
        ring_reset_reuse_path.write_text(
            original_ring_reset_reuse.replace(
                'test "phase10 virtio ring drained reset restores callback bookkeeping to a clean reuse baseline" {',
                'test "phase10 virtio ring drift" {',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ring_reset_reuse_second_test",
            root,
            'ring_reset_reuse_test:test "phase10 virtio ring drained reset restores callback bookkeeping to a clean reuse baseline" {',
        )
        ring_reset_reuse_path.write_text(original_ring_reset_reuse, encoding="utf-8")

        manifest_path = root / "zigux/tests/phase10_closure_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tests"] = [
            "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
            "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "closure_manifest_ring_test_inventory",
            root,
            "closure_manifest:tests:zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        evidence = manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
        manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            path for path in evidence if path != "zigux/tests/phase10_virtio_ring_reset_reuse.zig"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "closure_manifest_ring_evidence",
            root,
            "closure_manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence:zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            path
            for path in manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
            if path != "zigux/tests/phase10_virtio_input_registration_blocker_build.zig"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "closure_manifest_blocker_build_evidence",
            root,
            "closure_manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence:zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["focused_harness_replays"]["zigux/tests/phase10_virtio_mmio_queue_isolation.zig"] = [
            "phase10 mmio multi-queue isolation replay"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "focused_harness_replays_mmio_reset_guard",
            root,
            "closure_manifest:focused_harness_replays",
        )

    print("PHASE10_HARNESS_COVERAGE_SELF_TEST=pass")
    print("PHASE10_HARNESS_COVERAGE_SELF_TEST_CASE_COUNT=16")
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
    f"{len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(DOCS_README_MARKERS) + len(CHECKLIST_MARKERS) + len(BUILD_MARKERS) + len(CLOSURE_NOTE_MARKERS) + len(GUIDE_MARKERS) + len(COMPANION_MARKERS) + len(RING_RESET_REUSE_TEST_MARKERS) + len(INPUT_PREFLIGHT_TEST_MARKERS) + len(BLOCKER_BUILD_MARKERS) + len(MMIO_QUEUE_ISOLATION_TEST_MARKERS) + len(EXACT_ONCE)}"
)
