#!/usr/bin/env python3
"""Guard the current Phase 2 toolchain action-path reminder packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
BOOTSTRAP_NOTES = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = "Documentation/zigux/review-checklist.md"
SCRIPTS_README = "scripts/zigux/README.md"
TESTS_README = "zigux/tests/README.md"
THIRD_PARTY_README = "third_party/README.md"

ARCHIVE_NAME = "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
ARCHIVE_CHECK = (
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux"
)

WORKFLOW_SETUP_MARKERS = (
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'mirror_file=".zig-toolchain/community-mirrors.txt"',
    "if try_local_archive; then",
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
)

WORKFLOW_RUN_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: make -C zigux phase2-toolchain",
)

BOOTSTRAP_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
)

SCRIPTS_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/install-zig.py`",
)

TESTS_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
    "`make -C zigux phase2-toolchain`",
)

REVIEW_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`third_party/README.md`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    f"`{ARCHIVE_CHECK}`",
    "`make -C zigux phase2-toolchain`",
)

THIRD_PARTY_MARKERS = (
    f"`{ARCHIVE_NAME}`",
    f"`{ARCHIVE_CHECK}`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
)

EXPECTED_SELF_TEST_CASE_COUNT = 10


def resolve(root: Path, rel: str) -> Path:
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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_order_issues(text: str, markers: tuple[str, ...]) -> list[tuple[str, str]]:
    positions: list[int] = []
    for marker in markers:
        index = text.find(marker)
        if index == -1:
            return []
        positions.append(index)
    if positions != sorted(positions):
        return [("WORKFLOW_ACTION_PATH_ORDER_MISMATCH", "workflow Phase 2 toolchain action-path cluster is out of order")]
    return []


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    workflow = read_text(resolve(root, WORKFLOW))
    issues.extend(collect_missing_markers(workflow, WORKFLOW_SETUP_MARKERS, "MISSING_WORKFLOW_SETUP_MARKERS"))
    for marker in WORKFLOW_RUN_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_ACTION_PATH_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_ACTION_PATH_MARKERS", f"{marker}:count={count}"))
    issues.extend(collect_order_issues(workflow, WORKFLOW_RUN_LINES))

    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, BOOTSTRAP_NOTES)),
            BOOTSTRAP_MARKERS,
            "MISSING_BOOTSTRAP_NOTE_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, SCRIPTS_README)),
            SCRIPTS_MARKERS,
            "MISSING_SCRIPTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, TESTS_README)),
            TESTS_MARKERS,
            "MISSING_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, REVIEW_CHECKLIST)),
            REVIEW_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, THIRD_PARTY_README)),
            THIRD_PARTY_MARKERS,
            "MISSING_THIRD_PARTY_README_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("LANE18_PHASE2_TOOLCHAIN_ACTION_PATH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve(root, WORKFLOW), "\n".join((*WORKFLOW_SETUP_MARKERS, *WORKFLOW_RUN_LINES)) + "\n")
    write_text(resolve(root, BOOTSTRAP_NOTES), "\n".join(("# notes", *BOOTSTRAP_MARKERS)) + "\n")
    write_text(resolve(root, SCRIPTS_README), "\n".join(("# scripts", *SCRIPTS_MARKERS)) + "\n")
    write_text(resolve(root, TESTS_README), "\n".join(("# tests", *TESTS_MARKERS)) + "\n")
    write_text(resolve(root, REVIEW_CHECKLIST), "\n".join(("# checklist", *REVIEW_MARKERS)) + "\n")
    write_text(resolve(root, THIRD_PARTY_README), "\n".join(("# third_party", *THIRD_PARTY_MARKERS)) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane18_toolchain_action_path_") as tmp:
        root = Path(tmp)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        path = resolve(root, WORKFLOW)
        path.write_text(path.read_text(encoding="utf-8").replace(WORKFLOW_RUN_LINES[0], ""), encoding="utf-8")
        assert any(code == "MISSING_WORKFLOW_ACTION_PATH_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        path = resolve(root, WORKFLOW)
        path.write_text(path.read_text(encoding="utf-8").replace(WORKFLOW_RUN_LINES[1], WORKFLOW_RUN_LINES[0]), encoding="utf-8")
        assert any(code == "DUPLICATE_WORKFLOW_ACTION_PATH_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        path = resolve(root, WORKFLOW)
        workflow_lines = path.read_text(encoding="utf-8").splitlines()
        first = workflow_lines.index(WORKFLOW_RUN_LINES[2])
        second = workflow_lines.index(WORKFLOW_RUN_LINES[10])
        workflow_lines[first], workflow_lines[second] = workflow_lines[second], workflow_lines[first]
        path.write_text("\n".join(workflow_lines) + "\n", encoding="utf-8")
        assert any(code == "WORKFLOW_ACTION_PATH_ORDER_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        path = resolve(root, BOOTSTRAP_NOTES)
        path.write_text(path.read_text(encoding="utf-8").replace(BOOTSTRAP_MARKERS[-1], ""), encoding="utf-8")
        assert any(code == "MISSING_BOOTSTRAP_NOTE_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        path = resolve(root, SCRIPTS_README)
        path.write_text(path.read_text(encoding="utf-8").replace(SCRIPTS_MARKERS[0], ""), encoding="utf-8")
        assert any(code == "MISSING_SCRIPTS_README_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        path = resolve(root, TESTS_README)
        path.write_text(path.read_text(encoding="utf-8").replace(TESTS_MARKERS[4], ""), encoding="utf-8")
        assert any(code == "MISSING_TESTS_README_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        path = resolve(root, REVIEW_CHECKLIST)
        path.write_text(path.read_text(encoding="utf-8").replace(REVIEW_MARKERS[-1], ""), encoding="utf-8")
        assert any(code == "MISSING_REVIEW_CHECKLIST_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        path = resolve(root, THIRD_PARTY_README)
        path.write_text(path.read_text(encoding="utf-8").replace(THIRD_PARTY_MARKERS[1], ""), encoding="utf-8")
        assert any(code == "MISSING_THIRD_PARTY_README_MARKERS" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        path = resolve(root, WORKFLOW)
        path.write_text(path.read_text(encoding="utf-8").replace(WORKFLOW_SETUP_MARKERS[0], ""), encoding="utf-8")
        assert any(code == "MISSING_WORKFLOW_SETUP_MARKERS" for code, _ in collect_issues(root))
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("LANE18_PHASE2_TOOLCHAIN_ACTION_PATH_SELF_TEST=pass")
    print(f"LANE18_PHASE2_TOOLCHAIN_ACTION_PATH_SELF_TEST_CASE_COUNT={checks}")
    print(f"LANE18_PHASE2_TOOLCHAIN_ACTION_PATH_WORKFLOW_MARKER_COUNT={len(WORKFLOW_RUN_LINES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep the current Phase 2 toolchain action-path packet aligned.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("LANE18_PHASE2_TOOLCHAIN_ACTION_PATH=pass")
    print(f"LANE18_PHASE2_TOOLCHAIN_ACTION_PATH_WORKFLOW_MARKER_COUNT={len(WORKFLOW_RUN_LINES)}")
    print(f"LANE18_PHASE2_TOOLCHAIN_ACTION_PATH_REVIEW_MARKER_COUNT={len(REVIEW_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
