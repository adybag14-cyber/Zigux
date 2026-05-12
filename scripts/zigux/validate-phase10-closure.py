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
    "scripts/zigux/validate-phase10-closure.py",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "zigux/Makefile",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
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
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/tests/phase10_closure_manifest.json",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "shared reminder-surface drift",
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

MANIFEST_MARKERS = [
    '"phase": "Phase 10"',
    '"tranche": "virtio-lab-bundle"',
    '"scripts/zigux/check-phase10-harness-coverage.py"',
    '"source": "manifest_derived"',
    '"surveyed_commits": {',
    '"core": "31e9763eea7964dad7085d1a24bc098b4af49789"',
    '"ring": "bdfe88e865b94387b3c3bd41ca98054c452f78b9"',
    '"input": "7361ac51374149a96b7a7a2c6ea3c995d8cc1231"',
    '"mmio": "84f90e23ad1c28ae345905d5293a8c5395f37d43"',
    '"phase10-notification-data-summary-helper"',
    '"phase10-mmio-selected-queue-readiness-helper"',
    '"zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths"',
]

MMIO_SURVEY_MARKERS = [
    "phase10-mmio-selected-queue-readiness-helper",
    "phase10-mmio-lifecycle-and-irq-paths",
    "the live packet-local manifest `zigux/tests/phase10_virtio_mmio_manifest.json`",
    "the live dedicated MMIO freeze-boundary checker `scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
]

LEDGER_EXACT_ONCE_MARKERS = [
    "PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/validate-phase10.py",
    "PHASE10_LEDGER_EXACT_CHECK_2=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_EXACT_CHECK_3=make -C zigux phase10-validate",
    "PHASE10_LEDGER_EXACT_CHECK_4=python3 scripts/zigux/check-phase10-core-packet.py",
    "PHASE10_LEDGER_EXACT_CHECK_5=python3 scripts/zigux/check-phase10-ring-packet.py",
    "PHASE10_LEDGER_EXACT_CHECK_6=python3 scripts/zigux/check-phase10-input-packet.py",
    "PHASE10_LEDGER_EXACT_CHECK_7=python3 scripts/zigux/check-phase10-mmio-packet.py",
    "PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py",
    "PHASE10_LEDGER_EXACT_CHECK_9=python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test",
    "PHASE10_LEDGER_EXACT_CHECK_10=python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "PHASE10_LEDGER_EXACT_CHECK_11=python3 scripts/zigux/check-phase10-harness-coverage.py --self-test",
    "PHASE10_LEDGER_EXACT_CHECK_12=python3 scripts/zigux/check-phase10-harness-coverage.py",
    "PHASE10_LEDGER_EXACT_CHECK_13=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_LEDGER_EXACT_CHECK_14=make -C zigux phase10-test",
    "PHASE10_LEDGER_EXACT_CHECK_15=make -C zigux phase10",
]

LEDGER_EXACT_ONCE_ERROR = (
    "PHASE10_CLOSURE_VALIDATION_LEDGER_EXACT_CHECKS=fail\n"
    "PHASE10_CLOSURE_LEDGER_EXACT_ONCE_MISMATCH_START\n"
    "{details}\n"
    "PHASE10_CLOSURE_LEDGER_EXACT_ONCE_MISMATCH_END"
)

COMMANDS = [
    ["scripts/zigux/check-phase10-harness-coverage.py", "--self-test"],
    ["scripts/zigux/check-phase10-tests-readme-core-surfaces.py", "--self-test"],
    ["scripts/zigux/check-phase10-harness-coverage.py"],
    ["scripts/zigux/check-phase10-tests-readme-core-surfaces.py"],
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
        ("mmio-survey", "Documentation/zigux/phase10-virtio-mmio-survey.md", MMIO_SURVEY_MARKERS),
        ("review", "Documentation/zigux/review-checklist.md", REVIEW_CHECKLIST_MARKERS),
        ("manifest", "zigux/tests/phase10_closure_manifest.json", MANIFEST_MARKERS),
    ]
    for label, rel_path, markers in checks:
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing.append(f"{label}:{marker}")
    return missing


def collect_ledger_exact_once_mismatches(root: Path) -> list[str]:
    ledger_text = read_text(root, "zigux-alpha/PHASE10_CLOSURE_LEDGER.md")
    mismatches: list[str] = []
    for marker in LEDGER_EXACT_ONCE_MARKERS:
        count = ledger_text.count(marker)
        if count != 1:
            mismatches.append(f"{marker}:count={count}")
    return mismatches


def run_command(root: Path, cmd: list[str]) -> int:
    return subprocess.run([sys.executable, str(root / cmd[0]), *cmd[1:]], cwd=root, check=False).returncode


def run_required_commands(root: Path) -> list[str]:
    failed: list[str] = []
    for command in COMMANDS:
        if run_command(root, command) != 0:
            failed.append(" ".join(command))
    return failed


def write_fixture(root: Path) -> None:
    files = {
        "scripts/zigux/validate-phase10-closure.py": "fixture\n",
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(CLOSURE_DOC_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": "\n".join(LANE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-mmio-survey.md": "\n".join(MMIO_SURVEY_MARKERS) + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
        "scripts/zigux/check-phase10-harness-coverage.py": (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--self-test' in sys.argv[1:]:\n"
            "    print('PHASE10_HARNESS_COVERAGE_SELF_TEST=pass')\n"
            "    raise SystemExit(0)\n"
            "print('PHASE10_HARNESS_COVERAGE=pass')\n"
        ),
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py": (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--self-test' in sys.argv[1:]:\n"
            "    print('PHASE10_TESTS_README_CORE_SURFACES_CHECKER_SELF_TEST=pass')\n"
            "    raise SystemExit(0)\n"
            "print('PHASE10_TESTS_README_CORE_SURFACES_CHECK=pass')\n"
        ),
        "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
        "zigux/tests/phase10_closure_manifest.json": "\n".join(MANIFEST_MARKERS) + "\n",
        "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": "\n".join(LEDGER_EXACT_ONCE_MARKERS) + "\n",
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
        ledger_mismatches = collect_ledger_exact_once_mismatches(root)
        if missing_files or missing_markers or ledger_mismatches:
            raise SystemExit(
                "phase10-closure-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}:"
                f"ledger={','.join(ledger_mismatches) if ledger_mismatches else 'none'}"
            )
        failed_commands = run_required_commands(root)
        if failed_commands:
            raise SystemExit(
                "phase10-closure-self-test:baseline_command_failed:"
                f"commands={','.join(failed_commands)}"
            )

        makefile = root / "zigux/Makefile"
        makefile.write_text(makefile.read_text(encoding="utf-8").replace("phase10-validate:\n", "", 1), encoding="utf-8")
        if "make:phase10-validate:" not in collect_missing_markers(root):
            raise SystemExit("phase10-closure-self-test:missing_make_marker_not_detected")
        write_fixture(root)

        closure = root / "Documentation/zigux/phase10-closure-evidence.md"
        closure.write_text(
            closure.read_text(encoding="utf-8").replace("shared reminder-surface drift\n", "", 1),
            encoding="utf-8",
        )
        if "closure:shared reminder-surface drift" not in collect_missing_markers(root):
            raise SystemExit("phase10-closure-self-test:missing_closure_marker_not_detected")
        write_fixture(root)

        lane = root / "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"
        lane.write_text(
            lane.read_text(encoding="utf-8").replace("scripts/zigux/validate-phase10-closure.py\n", "", 1),
            encoding="utf-8",
        )
        if "lane:scripts/zigux/validate-phase10-closure.py" not in collect_missing_markers(root):
            raise SystemExit("phase10-closure-self-test:missing_lane_marker_not_detected")
        write_fixture(root)

        mmio_survey = root / "Documentation/zigux/phase10-virtio-mmio-survey.md"
        mmio_survey.write_text(
            mmio_survey.read_text(encoding="utf-8").replace("phase10-mmio-selected-queue-readiness-helper\n", "", 1),
            encoding="utf-8",
        )
        if "mmio-survey:phase10-mmio-selected-queue-readiness-helper" not in collect_missing_markers(root):
            raise SystemExit("phase10-closure-self-test:mmio_survey_marker_not_detected")
        write_fixture(root)

        mmio_survey.write_text(
            mmio_survey.read_text(encoding="utf-8").replace(
                "the live packet-local manifest `zigux/tests/phase10_virtio_mmio_manifest.json`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        if (
            "mmio-survey:the live packet-local manifest `zigux/tests/phase10_virtio_mmio_manifest.json`"
            not in collect_missing_markers(root)
        ):
            raise SystemExit("phase10-closure-self-test:mmio_survey_manifest_marker_not_detected")
        write_fixture(root)

        mmio_survey.write_text(
            mmio_survey.read_text(encoding="utf-8").replace(
                "the live dedicated MMIO freeze-boundary checker `scripts/zigux/check-phase10-mmio-freeze-boundary.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        if (
            "mmio-survey:the live dedicated MMIO freeze-boundary checker `scripts/zigux/check-phase10-mmio-freeze-boundary.py`"
            not in collect_missing_markers(root)
        ):
            raise SystemExit("phase10-closure-self-test:mmio_survey_freeze_boundary_marker_not_detected")
        write_fixture(root)

        review = root / "Documentation/zigux/review-checklist.md"
        review.write_text(
            review.read_text(encoding="utf-8").replace("zigux/tests/phase10_closure_manifest.json\n", "", 1),
            encoding="utf-8",
        )
        if "review:zigux/tests/phase10_closure_manifest.json" not in collect_missing_markers(root):
            raise SystemExit("phase10-closure-self-test:missing_review_marker_not_detected")
        write_fixture(root)

        manifest = root / "zigux/tests/phase10_closure_manifest.json"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace('"scripts/zigux/check-phase10-harness-coverage.py"\n', "", 1),
            encoding="utf-8",
        )
        if 'manifest:"scripts/zigux/check-phase10-harness-coverage.py"' not in collect_missing_markers(root):
            raise SystemExit("phase10-closure-self-test:missing_manifest_marker_not_detected")
        write_fixture(root)

        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                '"mmio": "84f90e23ad1c28ae345905d5293a8c5395f37d43"\n',
                '"mmio": "0000000000000000000000000000000000000000"\n',
                1,
            ),
            encoding="utf-8",
        )
        if 'manifest:"mmio": "84f90e23ad1c28ae345905d5293a8c5395f37d43"' not in collect_missing_markers(root):
            raise SystemExit("phase10-closure-self-test:missing_manifest_commit_marker_not_detected")
        write_fixture(root)

        ledger = root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        ledger.write_text(
            ledger.read_text(encoding="utf-8").replace(
                "PHASE10_LEDGER_EXACT_CHECK_4=python3 scripts/zigux/check-phase10-core-packet.py\n",
                "PHASE10_LEDGER_EXACT_CHECK_3=python3 scripts/zigux/check-phase10-core-packet.py\n",
                1,
            ),
            encoding="utf-8",
        )
        ledger_mismatches = collect_ledger_exact_once_mismatches(root)
        if "PHASE10_LEDGER_EXACT_CHECK_4=python3 scripts/zigux/check-phase10-core-packet.py:count=0" not in ledger_mismatches:
            raise SystemExit(
                "phase10-closure-self-test:missing_ledger_exact_once_mismatch_not_detected:"
                f"actual={','.join(ledger_mismatches) if ledger_mismatches else 'none'}"
            )
        write_fixture(root)

        checker = root / "scripts/zigux/check-phase10-harness-coverage.py"
        checker.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--self-test' in sys.argv[1:]:\n"
            "    print('PHASE10_HARNESS_COVERAGE_SELF_TEST=pass')\n"
            "    raise SystemExit(0)\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
        )
        failed_commands = run_required_commands(root)
        if failed_commands != ["scripts/zigux/check-phase10-harness-coverage.py"]:
            raise SystemExit(
                "phase10-closure-self-test:failed_command_not_detected:"
                f"actual={','.join(failed_commands) if failed_commands else 'none'}"
            )
        write_fixture(root)

        tests_readme_checker = root / "scripts/zigux/check-phase10-tests-readme-core-surfaces.py"
        tests_readme_checker.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--self-test' in sys.argv[1:]:\n"
            "    print('PHASE10_TESTS_README_CORE_SURFACES_CHECKER_SELF_TEST=pass')\n"
            "    raise SystemExit(0)\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
        )
        failed_commands = run_required_commands(root)
        if failed_commands != ["scripts/zigux/check-phase10-tests-readme-core-surfaces.py"]:
            raise SystemExit(
                "phase10-closure-self-test:tests_readme_checker_failure_not_detected:"
                f"actual={','.join(failed_commands) if failed_commands else 'none'}"
            )

    print("PHASE10_CLOSURE_VALIDATION_SELF_TEST=pass")
    print("PHASE10_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT=12")
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

    ledger_mismatches = collect_ledger_exact_once_mismatches(ROOT)
    if ledger_mismatches:
        print(LEDGER_EXACT_ONCE_ERROR.format(details="\n".join(ledger_mismatches)))
        return 1

    failed_commands = run_required_commands(ROOT)
    if failed_commands:
        print("PHASE10_CLOSURE_VALIDATION=fail")
        print("PHASE10_CLOSURE_VALIDATION_FAILED_COMMANDS_START")
        for command in failed_commands:
            print(command)
        print("PHASE10_CLOSURE_VALIDATION_FAILED_COMMANDS_END")
        return 1

    print("PHASE10_CLOSURE_VALIDATION=pass")
    print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE10_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(MAKE_MARKERS) + len(CLOSURE_DOC_MARKERS) + len(LANE_MARKERS) + len(MMIO_SURVEY_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(MANIFEST_MARKERS) + len(LEDGER_EXACT_ONCE_MARKERS)}"
    )
    print(f"PHASE10_CLOSURE_COMMAND_COUNT={len(COMMANDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
