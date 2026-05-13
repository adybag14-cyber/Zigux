#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-fixdep-next-step-note.md",
    "scripts/basic/fixdep.c",
    "scripts/include/xalloc.h",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/validate-phase2.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/fixdep/cases.json",
]

TOOLCHAIN_NOTE_MARKERS = [
    "the broader fixdep, genksyms, artifact-tools, kconfig bridge, and manifest packet should stay documented through `Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and `zigux/Makefile` instead of presenting non-existent standalone checker scripts as live current-`master` evidence in this dedicated pin-scope note",
    "the closure note, tests root, and Makefile keep the committed `zigux/tests/fixtures/phase2_tool_manifest.json` plus `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` packet, the bounded fixdep replay, the committed genksyms and artifact-tools fixtures, and the direct kconfig and confdata Zig replays reviewable without restating missing standalone checker scripts in this dedicated pin-scope note",
    "the active Phase 2 closure note and tests root keep the shipped fixdep workflow gate plus the direct `zig test scripts/zigux/fixdep.zig` replay explicit beside the same bounded tools route",
]

CLOSURE_MARKERS = [
    "shared fixdep gate self-test: `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`",
    "shared fixdep gate: `python3 scripts/zigux/check-phase2-fixdep-gate.py`",
    "shared fixdep diff self-test: `python3 scripts/zigux/check-fixdep-diff.py --self-test`",
    "shared fixdep diff gate: `python3 scripts/zigux/check-fixdep-diff.py`",
    "zig test scripts/zigux/fixdep.zig",
]

PHASE2_FIXDEP_NEXT_STEP_MARKERS = [
    "`scripts/zigux/check-phase2-fixdep-gate.py` validates the live eleven-case packet, including `sample_comment_continuation`, `sample_output_write`, `sample_comment_only_stdout_full`, and `sample_missing_dep_stdout_full`.",
    "`zigux/tests/fixtures/fixdep/cases.json` names that same eleven-case packet and uses `stdout_mode: \"dev_full\"` on the three bounded `/dev/full` write-failure replays.",
    "The dedicated shared `fixdep` gate no longer trails the live docs-and-fixtures packet: `scripts/zigux/check-phase2-fixdep-gate.py`, `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase2-closure.md`, and `zigux/tests/fixtures/fixdep/cases.json` now agree on the same eleven-case packet.",
    "When a writable checkout with Zig is available, re-run `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig` so the dedicated gate and the direct replay stay aligned as one packet.",
]

ARTIFACT_DIFF_MARKERS = [
    "`zigux/tests/fixtures/fixdep/sample_expected.txt` is generated from the current in-tree C `scripts/basic/fixdep.c` behavior on a bounded committed sample.",
    "`zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt` anchors the escaped-whitespace dependency-token path so `fixdep.zig` must preserve escaped separators the same way as the C tool.",
    "`zigux/tests/fixtures/fixdep/sample_escaped_colon_expected.txt` anchors the escaped-colon dependency-token path so `fixdep.zig` must unescape `\\:` to the same on-disk dependency name that the C tool reads and emits.",
    "`zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt` widens that claim with a second committed depfile covering multi-target parsing, comments, duplicate deps, no-parse files, and escaped `#`.",
    "`zigux/tests/fixtures/fixdep/sample_concatenated_expected.txt` anchors the concatenated-target packet so `fixdep.zig` keeps the first source while still collecting later dependency tokens across the continued target entries.",
    "`zigux/tests/fixtures/fixdep/sample_comment_continuation_expected.txt` anchors escaped-newline rustc-style comments before the first target so `fixdep.zig` keeps skipping the continued comment until the next real newline.",
    "`zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt` plus `sample_comment_only_expected.stderr.txt` anchor the bounded comment-only depfile failure path while keeping the saved command line deterministic.",
    "`zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt` plus `sample_missing_dep_expected.stderr.txt` anchor the bounded missing-dependency open error and its exit-code contract while keeping stdout stable.",
    "`zigux/tests/fixtures/fixdep/sample_output_write_expected.txt` plus `sample_output_write_expected.stderr.txt` anchor the bounded stdout-write failure path for the main success packet and the replay variants that drive stdout into `/dev/full`.",
    "`zigux/tests/fixtures/fixdep/cases.json` keeps the current eleven-case fixdep packet reviewable by naming the committed stdout artifact for every shipped case and the expected stderr or exit-code contract whenever the case is not a plain success path, including the dedicated `sample_comment_continuation`, `sample_output_write`, `sample_comment_only_stdout_full`, and `sample_missing_dep_stdout_full` write-failure replays.",
    "`scripts/zigux/check-fixdep-diff.py` compares the committed fixdep samples against both the C tool and `scripts/zigux/fixdep.zig`.",
]

VALIDATE_PHASE2_MARKERS = [
    'FIXDEP_GATE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-fixdep-gate.py"',
    '(FIXDEP_GATE_CHECKER, "--self-test"),',
    "(FIXDEP_GATE_CHECKER,),",
]

MAKEFILE_MARKERS = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
]

WORKFLOW_MARKERS = [
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
]

TESTS_README_MARKERS = [
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "zig test scripts/zigux/fixdep.zig",
]

EXPECTED_CASE_NAMES = [
    "sample",
    "sample_multi_target",
    "sample_escaped_space",
    "sample_escaped_colon",
    "sample_concatenated",
    "sample_comment_continuation",
    "sample_comment_only",
    "sample_comment_only_stdout_full",
    "sample_missing_dep",
    "sample_missing_dep_stdout_full",
    "sample_output_write",
]

FILE_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": WORKFLOW_MARKERS,
    "Documentation/zigux/artifact-diff.md": ARTIFACT_DIFF_MARKERS,
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md": TOOLCHAIN_NOTE_MARKERS,
    "Documentation/zigux/phase2-closure.md": CLOSURE_MARKERS,
    "Documentation/zigux/phase2-fixdep-next-step-note.md": PHASE2_FIXDEP_NEXT_STEP_MARKERS,
    "scripts/zigux/validate-phase2.py": VALIDATE_PHASE2_MARKERS,
    "zigux/Makefile": MAKEFILE_MARKERS,
    "zigux/tests/README.md": TESTS_README_MARKERS,
}


def collect_missing_markers(text: str, markers: list[str], *, prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate_cases(root: Path) -> list[str]:
    issues: list[str] = []
    cases_path = root / "zigux/tests/fixtures/fixdep/cases.json"
    try:
        cases = json.loads(cases_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"zigux/tests/fixtures/fixdep/cases.json:json:{exc.msg}"]

    if not isinstance(cases, list):
        return ["zigux/tests/fixtures/fixdep/cases.json:type"]

    seen: list[str] = []
    for index, case in enumerate(cases):
        label = f"zigux/tests/fixtures/fixdep/cases.json:cases[{index}]"
        if not isinstance(case, dict):
            issues.append(f"{label}:type")
            continue

        for field in ("name", "depfile", "target", "cmdline", "expected"):
            value = case.get(field)
            if not isinstance(value, str) or not value:
                issues.append(f"{label}:{field}")

        name = case.get("name")
        if isinstance(name, str):
            seen.append(name)

        for field in ("depfile", "expected", "expected_stdout", "expected_stderr"):
            value = case.get(field)
            if value is None:
                continue
            if not isinstance(value, str) or not value:
                issues.append(f"{label}:{field}:type")
                continue
            if not (root / "zigux/tests/fixtures/fixdep" / value).is_file():
                issues.append(f"{label}:{field}:missing_fixture:{value}")

    if seen != EXPECTED_CASE_NAMES:
        issues.append(
            "zigux/tests/fixtures/fixdep/cases.json:case_names:"
            f"expected={EXPECTED_CASE_NAMES!r}:got={seen!r}"
        )

    return issues


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            issues.append(f"missing_file:{rel_path}")

    if issues:
        return issues

    for rel_path, markers in FILE_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        issues.extend(collect_missing_markers(text, markers, prefix=rel_path))

    issues.extend(validate_cases(root))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, "")

    for rel_path, markers in FILE_MARKERS.items():
        write_text(root / rel_path, "\n".join(markers) + "\n")

    fixture_root = root / "zigux/tests/fixtures/fixdep"
    for file_name in [
        "sample.d",
        "sample_expected.txt",
        "sample_escaped_space.d",
        "sample_escaped_space_expected.txt",
        "sample_escaped_colon.d",
        "sample_escaped_colon_expected.txt",
        "sample_multi_target.d",
        "sample_multi_target_expected.txt",
        "sample_concatenated.d",
        "sample_concatenated_expected.txt",
        "sample_comment_continuation.d",
        "sample_comment_continuation_expected.txt",
        "sample_comment_only.d",
        "sample_comment_only_expected.txt",
        "sample_comment_only_expected.stderr.txt",
        "sample_missing_dep.d",
        "sample_missing_dep_expected.txt",
        "sample_missing_dep_expected.stderr.txt",
        "sample_output_write_expected.txt",
        "sample_output_write_expected.stderr.txt",
    ]:
        write_text(fixture_root / file_name, "fixture\n")

    cases = [
        {
            "name": "sample",
            "depfile": "sample.d",
            "target": "sample.o",
            "cmdline": "clang -c sample.c -o sample.o",
            "expected": "sample_expected.txt",
            "expected_exit_code": 0,
        },
        {
            "name": "sample_multi_target",
            "depfile": "sample_multi_target.d",
            "target": "module/sample2.o",
            "cmdline": "clang -c sample2.c -o module/sample2.o",
            "expected": "sample_multi_target_expected.txt",
            "expected_exit_code": 0,
        },
        {
            "name": "sample_escaped_space",
            "depfile": "sample_escaped_space.d",
            "target": "sample_escaped_space.o",
            "cmdline": "clang -c sample.c -o sample_escaped_space.o",
            "expected": "sample_escaped_space_expected.txt",
            "expected_exit_code": 0,
        },
        {
            "name": "sample_escaped_colon",
            "depfile": "sample_escaped_colon.d",
            "target": "sample_escaped_colon.o",
            "cmdline": "clang -c sample_escaped_colon_source.c -o sample_escaped_colon.o",
            "expected": "sample_escaped_colon_expected.txt",
            "expected_exit_code": 0,
        },
        {
            "name": "sample_concatenated",
            "depfile": "sample_concatenated.d",
            "target": "sample_concatenated.o",
            "cmdline": "clang -c sample_concatenated_source.c -o sample_concatenated.o",
            "expected": "sample_concatenated_expected.txt",
            "expected_exit_code": 0,
        },
        {
            "name": "sample_comment_continuation",
            "depfile": "sample_comment_continuation.d",
            "target": "sample_comment_continuation.o",
            "cmdline": "clang -c sample_comment_continuation_source.c -o sample_comment_continuation.o",
            "expected": "sample_comment_continuation_expected.txt",
            "expected_exit_code": 0,
        },
        {
            "name": "sample_comment_only",
            "depfile": "sample_comment_only.d",
            "target": "sample_comment_only.o",
            "cmdline": "clang -c sample.c -o sample_comment_only.o",
            "expected": "sample_comment_only_expected.txt",
            "expected_stderr": "sample_comment_only_expected.stderr.txt",
            "expected_exit_code": 1,
        },
        {
            "name": "sample_comment_only_stdout_full",
            "depfile": "sample_comment_only.d",
            "target": "sample_comment_only_stdout_full.o",
            "cmdline": "clang -c sample.c -o sample_comment_only_stdout_full.o",
            "expected": "sample_output_write_expected.txt",
            "expected_stderr": "sample_comment_only_expected.stderr.txt",
            "expected_exit_code": 1,
            "stdout_mode": "dev_full",
        },
        {
            "name": "sample_missing_dep",
            "depfile": "sample_missing_dep.d",
            "target": "sample_missing_dep.o",
            "cmdline": "clang -c sample_missing_dep_source.c -o sample_missing_dep.o",
            "expected": "sample_missing_dep_expected.txt",
            "expected_stderr": "sample_missing_dep_expected.stderr.txt",
            "expected_exit_code": 2,
        },
        {
            "name": "sample_missing_dep_stdout_full",
            "depfile": "sample_missing_dep.d",
            "target": "sample_missing_dep_stdout_full.o",
            "cmdline": "clang -c sample_missing_dep_source.c -o sample_missing_dep_stdout_full.o",
            "expected": "sample_output_write_expected.txt",
            "expected_stderr": "sample_missing_dep_expected.stderr.txt",
            "expected_exit_code": 2,
            "stdout_mode": "dev_full",
        },
        {
            "name": "sample_output_write",
            "depfile": "sample.d",
            "target": "sample_output_write.o",
            "cmdline": "clang -c sample.c -o sample_output_write.o",
            "expected": "sample_output_write_expected.txt",
            "expected_stderr": "sample_output_write_expected.stderr.txt",
            "expected_exit_code": 1,
            "stdout_mode": "dev_full",
        },
    ]
    write_text(fixture_root / "cases.json", json.dumps(cases))


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_fixdep_gate_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert validate_root(root) == []
        case_count += 1

        build_self_test_root(root)
        path = root / "Documentation/zigux/artifact-diff.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(ARTIFACT_DIFF_MARKERS[8], "", 1),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert f"Documentation/zigux/artifact-diff.md:{ARTIFACT_DIFF_MARKERS[8]}" in issues
        case_count += 1

        build_self_test_root(root)
        path = root / "Documentation/zigux/phase2-closure.md"
        path.write_text(path.read_text(encoding="utf-8").replace(CLOSURE_MARKERS[0], "", 1), encoding="utf-8")
        issues = validate_root(root)
        assert f"Documentation/zigux/phase2-closure.md:{CLOSURE_MARKERS[0]}" in issues
        case_count += 1

        build_self_test_root(root)
        path = root / "Documentation/zigux/phase2-fixdep-next-step-note.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(PHASE2_FIXDEP_NEXT_STEP_MARKERS[2], "", 1),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert (
            f"Documentation/zigux/phase2-fixdep-next-step-note.md:{PHASE2_FIXDEP_NEXT_STEP_MARKERS[2]}"
            in issues
        )
        case_count += 1

        build_self_test_root(root)
        path = root / "zigux/Makefile"
        path.write_text(
            path.read_text(encoding="utf-8").replace(MAKEFILE_MARKERS[2], "", 1),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert f"zigux/Makefile:{MAKEFILE_MARKERS[2]}" in issues
        case_count += 1

        build_self_test_root(root)
        path = root / ".github/workflows/zigux-bootstrap.yml"
        path.write_text(
            path.read_text(encoding="utf-8").replace(WORKFLOW_MARKERS[4], "", 1),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert f".github/workflows/zigux-bootstrap.yml:{WORKFLOW_MARKERS[4]}" in issues
        case_count += 1

        build_self_test_root(root)
        (root / "scripts/zigux/check-fixdep-diff.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/check-fixdep-diff.py" in issues
        case_count += 1

        build_self_test_root(root)
        (root / "Documentation/zigux/phase2-fixdep-next-step-note.md").unlink()
        issues = validate_root(root)
        assert "missing_file:Documentation/zigux/phase2-fixdep-next-step-note.md" in issues
        case_count += 1

        build_self_test_root(root)
        write_text(root / "zigux/tests/fixtures/fixdep/cases.json", "[]")
        issues = validate_root(root)
        assert any(issue.startswith("zigux/tests/fixtures/fixdep/cases.json:case_names:") for issue in issues)
        case_count += 1

        build_self_test_root(root)
        cases = json.loads((root / "zigux/tests/fixtures/fixdep/cases.json").read_text(encoding="utf-8"))
        del cases[0]["expected"]
        write_text(root / "zigux/tests/fixtures/fixdep/cases.json", json.dumps(cases))
        issues = validate_root(root)
        assert "zigux/tests/fixtures/fixdep/cases.json:cases[0]:expected" in issues
        case_count += 1

    print("PHASE2_FIXDEP_GATE_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_GATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the shared Phase 2 fixdep governance and expected-output packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker coverage without needing a repo checkout.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(ROOT)
    if issues:
        print("PHASE2_FIXDEP_GATE=fail")
        print("PHASE2_FIXDEP_GATE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_FIXDEP_GATE_ISSUES_END")
        return 1

    marker_count = sum(len(markers) for markers in FILE_MARKERS.values())
    print("PHASE2_FIXDEP_GATE=pass")
    print(f"PHASE2_FIXDEP_GATE_MARKER_COUNT={marker_count}")
    print(f"PHASE2_FIXDEP_CASE_COUNT={len(EXPECTED_CASE_NAMES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
