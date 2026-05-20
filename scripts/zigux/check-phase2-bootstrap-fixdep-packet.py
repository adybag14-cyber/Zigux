#!/usr/bin/env python3
"""Guard the bootstrap workflow's fixdep packet on current master."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
INSTALL_ZIG_REL = Path("scripts/zigux/install-zig.py")
FIXDEP_GATE_REL = Path("scripts/zigux/check-phase2-fixdep-gate.py")
FIXDEP_DIFF_REL = Path("scripts/zigux/check-fixdep-diff.py")
FIXDEP_ZIG_REL = Path("scripts/zigux/fixdep.zig")
FIXDEP_CASES_REL = Path("zigux/tests/fixtures/fixdep/cases.json")

REQUIRED_FILES = (
    WORKFLOW_REL,
    INSTALL_ZIG_REL,
    FIXDEP_GATE_REL,
    FIXDEP_DIFF_REL,
    FIXDEP_ZIG_REL,
    FIXDEP_CASES_REL,
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py --self-test",
)

FIXDEP_GATE_MARKERS = (
    'print("PHASE2_FIXDEP_GATE=fail")',
    'print("PHASE2_FIXDEP_GATE=pass")',
    "run: zig test scripts/zigux/fixdep.zig",
    "phase2-fixdep:",
)

FIXDEP_DIFF_MARKERS = (
    'print("FIXDEP_DIFF=pass")',
    'print("FIXDEP_DETERMINISM=pass")',
    "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)",
)

FIXDEP_ZIG_MARKERS = (
    "const FixdepError = error{",
    'test "dep parsing returns NoTargets for comment-only depfiles" {',
    'test "dep parsing continues dependency lines across escaped newlines" {',
)

FIXDEP_CASE_NAMES = (
    "sample",
    "sample_multi_target",
    "sample_dependency_continuation",
    "sample_comment_only",
    "sample_output_write",
)

EXPECTED_SELF_TEST_CASE_COUNT = 1 + len(REQUIRED_FILES) + 6


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_required_files(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).is_file():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    return issues


def collect_workflow_issues(workflow_text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    indexes: list[int] = []

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
            continue
        indexes.append(workflow_text.splitlines().index(next(line for line in workflow_text.splitlines() if line.strip() == marker)))

    if len(indexes) == len(REQUIRED_WORKFLOW_LINES) and indexes != sorted(indexes):
        issues.append(("MISORDERED_WORKFLOW_PACKET", "bootstrap fixdep packet lines are out of order"))

    return issues


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_case_issues(cases_text: str) -> list[tuple[str, str]]:
    try:
        payload = json.loads(cases_text)
    except json.JSONDecodeError:
        return [("INVALID_FIXDEP_CASES_JSON", FIXDEP_CASES_REL.as_posix())]

    if not isinstance(payload, list):
        return [("INVALID_FIXDEP_CASES_JSON", FIXDEP_CASES_REL.as_posix())]

    names: list[str] = []
    for entry in payload:
        if not isinstance(entry, dict):
            return [("INVALID_FIXDEP_CASE_ENTRY", repr(entry))]
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            return [("INVALID_FIXDEP_CASE_NAME", repr(name))]
        names.append(name)

    issues: list[tuple[str, str]] = []
    for name in FIXDEP_CASE_NAMES:
        if name not in names:
            issues.append(("MISSING_FIXDEP_CASE_NAME", name))
    if len(names) != len(set(names)):
        issues.append(("DUPLICATE_FIXDEP_CASE_NAME", "cases.json contains duplicate case names"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues = collect_required_files(root)
    if issues:
        return issues

    workflow_text = read_text(resolve(root, WORKFLOW_REL))
    fixdep_gate_text = read_text(resolve(root, FIXDEP_GATE_REL))
    fixdep_diff_text = read_text(resolve(root, FIXDEP_DIFF_REL))
    fixdep_zig_text = read_text(resolve(root, FIXDEP_ZIG_REL))
    cases_text = read_text(resolve(root, FIXDEP_CASES_REL))

    issues.extend(collect_workflow_issues(workflow_text))
    issues.extend(
        collect_missing_markers(
            fixdep_gate_text,
            FIXDEP_GATE_MARKERS,
            "MISSING_FIXDEP_GATE_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            fixdep_diff_text,
            FIXDEP_DIFF_MARKERS,
            "MISSING_FIXDEP_DIFF_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            fixdep_zig_text,
            FIXDEP_ZIG_MARKERS,
            "MISSING_FIXDEP_ZIG_MARKER",
        )
    )
    issues.extend(collect_case_issues(cases_text))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_FIXDEP_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    workflow_lines = "\n".join(
        (
            "jobs:",
            "  bootstrap:",
            "    steps:",
            "      - name: Check current Lane 05 local archive README packet",
            "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
            "      - name: Self-test current Zig installer helper",
            "        run: python3 scripts/zigux/install-zig.py --self-test",
            "      - name: Self-test current Phase 2 fixdep gate checker",
            "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
            "      - name: Check current Phase 2 fixdep gate packet",
            "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
            "      - name: Self-test current fixdep parity checker",
            "        run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
            "      - name: Check current fixdep parity packet",
            "        run: python3 scripts/zigux/check-fixdep-diff.py",
            "      - name: Run current Phase 2 fixdep unit tests",
            "        run: zig test scripts/zigux/fixdep.zig",
            "      - name: Self-test current Lane 01 bootstrap charter checker",
            "        run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py --self-test",
            "",
        )
    )
    write_text(resolve(root, WORKFLOW_REL), workflow_lines)
    write_text(resolve(root, INSTALL_ZIG_REL), "def main() -> int:\n    return 0\n")
    write_text(
        resolve(root, FIXDEP_GATE_REL),
        "\n".join(
            (
                'print("PHASE2_FIXDEP_GATE=fail")',
                'print("PHASE2_FIXDEP_GATE=pass")',
                "run: zig test scripts/zigux/fixdep.zig",
                "phase2-fixdep:",
                "",
            )
        ),
    )
    write_text(
        resolve(root, FIXDEP_DIFF_REL),
        "\n".join(
            (
                'print("FIXDEP_DIFF=pass")',
                'print("FIXDEP_DETERMINISM=pass")',
                "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)",
                "",
            )
        ),
    )
    write_text(
        resolve(root, FIXDEP_ZIG_REL),
        "\n".join(
            (
                "const FixdepError = error{",
                "    NoTargets,",
                "};",
                'test "dep parsing returns NoTargets for comment-only depfiles" {',
                "}",
                'test "dep parsing continues dependency lines across escaped newlines" {',
                "}",
                "",
            )
        ),
    )
    write_text(
        resolve(root, FIXDEP_CASES_REL),
        json.dumps(
            [
                {"name": "sample"},
                {"name": "sample_multi_target"},
                {"name": "sample_dependency_continuation"},
                {"name": "sample_comment_only"},
                {"name": "sample_output_write"},
            ],
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane03_fixdep_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)

        issues = collect_issues(root)
        if issues:
            raise AssertionError(f"expected clean sample root, got {issues!r}")
        case_count += 1

        for rel in REQUIRED_FILES:
            broken_root = Path(tmp_dir) / f"missing_{rel.name.replace('.', '_')}"
            build_sample_root(broken_root)
            resolve(broken_root, rel).unlink()
            issue_codes = {code for code, _ in collect_issues(broken_root)}
            if "MISSING_REQUIRED_FILE" not in issue_codes:
                raise AssertionError(f"missing-file check failed for {rel}")
            case_count += 1

        sample_root = Path(tmp_dir) / "workflow_order"
        build_sample_root(sample_root)
        workflow_path = resolve(sample_root, WORKFLOW_REL)
        workflow_text = read_text(workflow_path)
        swapped = workflow_text.replace(
            "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test\n"
            "      - name: Check current Phase 2 fixdep gate packet\n"
            "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py\n",
            "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py\n"
            "      - name: Check current Phase 2 fixdep gate packet\n"
            "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test\n",
        )
        write_text(workflow_path, swapped)
        issue_codes = {code for code, _ in collect_issues(sample_root)}
        if "MISORDERED_WORKFLOW_PACKET" not in issue_codes:
            raise AssertionError("workflow order guard did not fail closed")
        case_count += 1

        duplicate_root = Path(tmp_dir) / "workflow_duplicate"
        build_sample_root(duplicate_root)
        workflow_path = resolve(duplicate_root, WORKFLOW_REL)
        workflow_text = read_text(workflow_path)
        duplicate_text = workflow_text.replace(
            "        run: python3 scripts/zigux/check-fixdep-diff.py --self-test\n",
            "        run: python3 scripts/zigux/check-fixdep-diff.py --self-test\n"
            "        run: python3 scripts/zigux/check-fixdep-diff.py --self-test\n",
            1,
        )
        write_text(workflow_path, duplicate_text)
        issue_codes = {code for code, _ in collect_issues(duplicate_root)}
        if "DUPLICATE_WORKFLOW_LINE" not in issue_codes:
            raise AssertionError("workflow duplicate guard did not fail closed")
        case_count += 1

        cases_root = Path(tmp_dir) / "cases_missing"
        build_sample_root(cases_root)
        write_text(
            resolve(cases_root, FIXDEP_CASES_REL),
            json.dumps([{"name": "sample"}], indent=2) + "\n",
        )
        issue_codes = {code for code, _ in collect_issues(cases_root)}
        if "MISSING_FIXDEP_CASE_NAME" not in issue_codes:
            raise AssertionError("case-name guard did not fail closed")
        case_count += 1

        gate_root = Path(tmp_dir) / "gate_marker_missing"
        build_sample_root(gate_root)
        gate_path = resolve(gate_root, FIXDEP_GATE_REL)
        gate_text = read_text(gate_path).replace('print("PHASE2_FIXDEP_GATE=pass")\n', "", 1)
        write_text(gate_path, gate_text)
        issue_codes = {code for code, _ in collect_issues(gate_root)}
        if "MISSING_FIXDEP_GATE_MARKER" not in issue_codes:
            raise AssertionError("fixdep-gate marker guard did not fail closed")
        case_count += 1

        diff_root = Path(tmp_dir) / "diff_marker_missing"
        build_sample_root(diff_root)
        diff_path = resolve(diff_root, FIXDEP_DIFF_REL)
        diff_text = read_text(diff_path).replace("EXPECTED_CASE_ORDER = list(EXPECTED_CASES)\n", "", 1)
        write_text(diff_path, diff_text)
        issue_codes = {code for code, _ in collect_issues(diff_root)}
        if "MISSING_FIXDEP_DIFF_MARKER" not in issue_codes:
            raise AssertionError("fixdep-diff marker guard did not fail closed")
        case_count += 1

        zig_root = Path(tmp_dir) / "zig_marker_missing"
        build_sample_root(zig_root)
        zig_path = resolve(zig_root, FIXDEP_ZIG_REL)
        zig_text = read_text(zig_path).replace(
            'test "dep parsing continues dependency lines across escaped newlines" {\n',
            "",
            1,
        )
        write_text(zig_path, zig_text)
        issue_codes = {code for code, _ in collect_issues(zig_root)}
        if "MISSING_FIXDEP_ZIG_MARKER" not in issue_codes:
            raise AssertionError("fixdep-zig marker guard did not fail closed")
        case_count += 1

    if case_count != EXPECTED_SELF_TEST_CASE_COUNT:
        raise AssertionError(
            f"self-test case count drifted: {case_count} != {EXPECTED_SELF_TEST_CASE_COUNT}"
        )

    print("PHASE2_BOOTSTRAP_FIXDEP_PACKET_SELF_TEST=pass")
    print(
        "PHASE2_BOOTSTRAP_FIXDEP_PACKET_SELF_TEST_CASE_COUNT="
        f"{EXPECTED_SELF_TEST_CASE_COUNT}"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--write-sample-root", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_FIXDEP_PACKET=pass")
    print(
        "PHASE2_BOOTSTRAP_FIXDEP_PACKET_WORKFLOW_STEP_COUNT="
        f"{len(REQUIRED_WORKFLOW_LINES) - 2}"
    )
    print(
        "PHASE2_BOOTSTRAP_FIXDEP_PACKET_REQUIRED_FILE_COUNT="
        f"{len(REQUIRED_FILES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
