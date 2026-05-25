#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESTS_README = Path("zigux/tests/README.md")

PHASE13_HEADING = "## Phase 13 shared-helper packet"
PHASE13_SECTION_END = "Tests-root reviewer prompt:"

REQUIRED_SHIPPED_MARKERS = (
    "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "`Documentation/zigux/phase13-shared-summary-guard-gap.md`",
    "`Documentation/zigux/phase13-notifier-summary-gap.md`",
    "`scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "`scripts/zigux/check-phase13-tests-readme-alignment.py`",
    "`scripts/zigux/validate-phase13-release.py`",
    "`Documentation/zigux/phase13-landlock-ruleset-survey.md`",
    "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
    "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-slice.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-survey.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`",
    "`scripts/zigux/check-phase13-landlock-syscalls-packet.py`",
    "`security/landlock/ruleset.zig`",
    "`security/landlock/syscalls.zig`",
    "`zigux/tests/phase13_landlock_ruleset.zig`",
    "`zigux/tests/phase13_landlock_ruleset_manifest.json`",
)

REQUIRED_GAP_MARKERS = (
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`Documentation/zigux/phase13-landlock-ruleset-slice.md`",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "`zigux/helpers/notifier_chain_view.zig`",
    "`include/zigux/notifier_abi.h`",
)

REQUIRED_TEXT = (
    "Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality gaps rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
    "Current `master` also materializes the helper-owned Landlock survey-and-checker packet through `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-landlock-syscalls-packet.py`, `security/landlock/ruleset.zig`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, and `zigux/tests/phase13_landlock_ruleset_manifest.json`, so contributor workflow wording should keep those shipped helper anchors explicit while `Documentation/zigux/phase13-landlock-ruleset-ownership.md` and `Documentation/zigux/phase13-landlock-ruleset-slice.md` stay framed as repo-reality gaps and the direct syscall replay companions stay separate repo-reality gaps.",
    "Current `master` still does not materialize `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/helpers/notifier_chain_view.zig`, or `include/zigux/notifier_abi.h`, so keep those Landlock ruleset-note, direct Landlock syscall replay, and adjacent notifier helper or header surfaces framed as repo-reality gaps rather than shipped tests-root evidence.",
    "- Does the bounded Phase 13 reminder keep the stable contributor-facing handle, the shipped helper-local `libfs`, `devres`, and Landlock anchors, the shared-summary guard, the shared release-discipline validator, the adjacent notifier checker-backed evidence, the returned-but-still-non-owner `zigux/Makefile` file, and the still-missing Phase 13 build-route, deeper devres replay, Landlock ruleset ownership and slice notes, Landlock syscall replay, adjacent notifier helper and header, and notifier-priority surfaces aligned without promoting repo-reality gaps back into shipped tests-root proof?",
)

FORBIDDEN_SHIPPED_LINES = (
    "- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "- `Documentation/zigux/phase13-landlock-ruleset-slice.md`",
    "- `zigux/tests/phase13_landlock_syscalls.zig`",
    "- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "- `zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "- `zigux/helpers/notifier_chain_view.zig`",
    "- `include/zigux/notifier_abi.h`",
    "- `make -C zigux phase13-validate`",
    "- `make -C zigux phase13`",
)

FORBIDDEN_TEXT = (
    "Current `master` also materializes the helper-owned Landlock ownership and syscall-governance notes",
    "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`",
    "Keep `make -C zigux phase13-validate` as the stable contributor-facing handle",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def extract_phase13_section(text: str) -> str:
    heading_index = text.find(PHASE13_HEADING)
    if heading_index == -1:
        raise SystemExit(f"missing heading: {PHASE13_HEADING}")
    end_index = text.find(PHASE13_SECTION_END, heading_index)
    if end_index == -1:
        raise SystemExit(f"missing section terminator: {PHASE13_SECTION_END}")
    return text[heading_index:end_index]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    text = read_text(root / TESTS_README)
    shipped_section = extract_phase13_section(text)
    issues: list[tuple[str, str]] = []
    for marker in REQUIRED_SHIPPED_MARKERS:
        if marker not in text:
            issues.append(("MISSING_MARKER", marker))
    for marker in REQUIRED_GAP_MARKERS:
        if marker not in text:
            issues.append(("MISSING_GAP_MARKER", marker))
    for fragment in REQUIRED_TEXT:
        if fragment not in text:
            issues.append(("MISSING_TEXT", fragment))
    for line in FORBIDDEN_SHIPPED_LINES:
        if line in shipped_section:
            issues.append(("FORBIDDEN_SHIPPED_MARKER", line))
    for fragment in FORBIDDEN_TEXT:
        if fragment in text:
            issues.append(("FORBIDDEN_TEXT", fragment))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE13_TESTS_README_ALIGNMENT=fail")
    print("PHASE13_TESTS_README_ALIGNMENT_ISSUES_START")
    for code, value in issues:
        print(f"{code}:{value}")
    print("PHASE13_TESTS_README_ALIGNMENT_ISSUES_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    lines = [
        "# zigux/tests",
        "",
        PHASE13_HEADING,
        "",
        "Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
        "",
        "Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:",
    ]
    lines.extend(f"- {marker}" for marker in REQUIRED_SHIPPED_MARKERS)
    lines.extend(
        [
            "",
            REQUIRED_TEXT[1],
            "",
            REQUIRED_TEXT[0],
            "",
            REQUIRED_TEXT[2],
            "",
            "Keep `zigux/helpers/notifier_chain_view.zig` and `include/zigux/notifier_abi.h` framed as adjacent repo-reality gaps rather than shipped shared surfaces.",
            "",
            PHASE13_SECTION_END,
            "",
            REQUIRED_TEXT[3],
            "",
        ]
    )
    write_text(root / TESTS_README, "\n".join(lines))


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 7
    with tempfile.TemporaryDirectory(prefix="zigux_p13_tests_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        path = root / TESTS_README

        path.write_text(replace_once(path.read_text(encoding="utf-8"), REQUIRED_SHIPPED_MARKERS[1]), encoding="utf-8")
        assert ("MISSING_MARKER", REQUIRED_SHIPPED_MARKERS[1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), REQUIRED_TEXT[1]), encoding="utf-8")
        assert ("MISSING_TEXT", REQUIRED_TEXT[1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path.write_text(path.read_text(encoding="utf-8").replace(
            "Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:\n",
            "Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:\n- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`\n",
            1,
        ), encoding="utf-8")
        assert ("FORBIDDEN_SHIPPED_MARKER", "- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path.write_text(path.read_text(encoding="utf-8") + "\nCurrent `master` still exposes `make -C zigux phase13` through `zigux/Makefile`\n", encoding="utf-8")
        assert ("FORBIDDEN_TEXT", "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), REQUIRED_TEXT[3]), encoding="utf-8")
        assert ("MISSING_TEXT", REQUIRED_TEXT[3]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (root / TESTS_README).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing tests readme did not abort")

    assert checks_run == expected_case_count
    print("PHASE13_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE13_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current Phase 13 tests-root reminder packet aligned with shared-helper repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)
    print("PHASE13_TESTS_README_ALIGNMENT=pass")
    print(f"PHASE13_TESTS_README_ALIGNMENT_MARKER_COUNT={len(REQUIRED_SHIPPED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())