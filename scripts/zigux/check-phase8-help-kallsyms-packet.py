#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-help-kallsyms-packet.py"
DOCS_ROOT_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
SEQUENCING_PATH = "Documentation/zigux/phase8-tooling-lane-sequencing.md"

REQUIRED_FILES = (
    SCRIPT_PATH,
    DOCS_ROOT_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    SEQUENCING_PATH,
)

REQUIRED_MARKERS = {
    DOCS_ROOT_PATH: (
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`make -C zigux phase8`",
    ),
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the shared Phase 8 help-and-kallsyms packet",
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`tools/lib/symbol/kallsyms.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
    ),
    SCRIPTS_README_PATH: (
        "Phase 8 flow - the current shared Phase 8 review surface on `master` is",
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
    ),
    TESTS_README_PATH: (
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`zigux/tests/phase8_help.zig`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
    ),
    SEQUENCING_PATH: (
        "### 2. Symbol lane",
        "Use this lane for bounded `kallsyms` reminder, compile, or packet-truthfulness work only.",
        "the current Phase 8 test packet includes `zigux/tests/phase8_help_kallsyms_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig`",
        "shared Phase 8 reminder surfaces still group the symbol shard with the same parked build-and-validator packet",
        "Keep follow-up parked unless a concrete symbol-lane packet drift appears on current `master`.",
    ),
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            problems.append(f"missing-file:{rel_path}")
    if problems:
        return problems

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                problems.append(f"missing-marker:{rel_path}:{marker}")
    return problems


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    for rel_path in REQUIRED_FILES:
        if rel_path == SCRIPT_PATH:
            continue
        write_text(root, rel_path, "\n".join(REQUIRED_MARKERS[rel_path]) + "\n")


def assert_missing_case(root: Path, rel_path: str, marker: str) -> None:
    text = read_text(root, rel_path)
    if marker not in text:
        raise SystemExit(f"self-test-fixture-missing:{rel_path}:{marker}")
    (root / rel_path).write_text(text.replace(marker, "", 1), encoding="utf-8")
    result = run_validator(root)
    expected = f"missing-marker:{rel_path}:{marker}"
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{rel_path}:{marker}")
    if expected not in output:
        raise SystemExit(f"self-test-mismatch:{expected}:{output}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_help_kallsyms_packet_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        mutations = (
            (
                DOCS_ROOT_PATH,
                "`Documentation/zigux/phase8-kallsyms-slice.md`",
            ),
            (
                REVIEW_CHECKLIST_PATH,
                "if the change touches the shared Phase 8 help-and-kallsyms packet",
            ),
            (
                SCRIPTS_README_PATH,
                "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
            ),
            (
                TESTS_README_PATH,
                "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
            ),
            (
                SEQUENCING_PATH,
                "the current Phase 8 test packet includes `zigux/tests/phase8_help_kallsyms_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig`",
            ),
        )
        for rel_path, marker in mutations:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, rel_path, marker)
            cases += 1

        missing_file_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_file_root)
        (missing_file_root / SEQUENCING_PATH).unlink()
        missing_result = run_validator(missing_file_root)
        missing_output = missing_result.stdout.strip() or missing_result.stderr.strip() or "no_output"
        expected = f"missing-file:{SEQUENCING_PATH}"
        if missing_result.returncode == 0 or expected not in missing_output:
            raise SystemExit(f"self-test-missing-file-mismatch:{missing_output}")
        cases += 1

    print("PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST=pass")
    print(f"PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_HELP_KALLSYMS_PACKET=fail")
        print("PHASE8_HELP_KALLSYMS_PACKET_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_HELP_KALLSYMS_PACKET_PROBLEMS_END")
        return 1

    print("PHASE8_HELP_KALLSYMS_PACKET=pass")
    print(f"PHASE8_HELP_KALLSYMS_PACKET_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
