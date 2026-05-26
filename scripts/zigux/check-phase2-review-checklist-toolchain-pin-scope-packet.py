#!/usr/bin/env python3
"""Guard the shared Phase 2 toolchain pin-scope packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
REVIEW_CHECKLIST = ROOT / "Documentation/zigux/review-checklist.md"
BOOTSTRAP_NOTES = ROOT / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
WORKFLOW = ROOT / ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux/Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts/zigux/zig-toolchain-policy.json"
TOOLCHAIN_CHECKER = ROOT / "scripts/zigux/check-zig-toolchain.py"

REVIEW_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "same pinned toolchain",
)

BOOTSTRAP_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "`third_party/README.md`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "pinned-channel",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-genksyms:",
    "phase2-fixdep:",
    "phase2-validate:",
    "phase2:",
)

CHECKER_MARKERS = (
    "def load_min_version(",
    "def load_pinned_channel(",
    "def resolve_zig_executable(",
    "def resolve_policy_archive(",
    "def validate_policy_archive(",
    'parser.add_argument("--allow-missing"',
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
    'parser.add_argument("--archive"',
    'parser.add_argument("--archive-target"',
    'parser.add_argument("--zig"',
)

EXPECTED_PHASE = "Phase 2"
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_ARCHIVE_TARGETS = ["x86_64-linux"]
EXPECTED_REQUIRED_ROUTES = [
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
]


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


def collect_occurrence_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_exact_line_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def validate_policy(payload: object) -> list[tuple[str, str]]:
    if not isinstance(payload, dict):
        return [("INVALID_POLICY", "expected-json-object")]

    issues: list[tuple[str, str]] = []
    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_POLICY_PHASE", repr(payload.get("phase"))))
    if payload.get("channel") != EXPECTED_CHANNEL:
        issues.append(("INVALID_POLICY_CHANNEL", repr(payload.get("channel"))))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + [("INVALID_POLICY_UPGRADE_POLICY", "missing-dict")]

    archive_targets = upgrade_policy.get("archive_target_scope")
    if archive_targets != EXPECTED_ARCHIVE_TARGETS:
        issues.append(("INVALID_POLICY_ARCHIVE_SCOPE", repr(archive_targets)))

    required_routes = upgrade_policy.get("required_make_routes")
    if required_routes != EXPECTED_REQUIRED_ROUTES:
        issues.append(("INVALID_POLICY_REQUIRED_ROUTES", repr(required_routes)))

    return issues


def validate(root: Path) -> list[tuple[str, str]]:
    review_text = read_text(root / REVIEW_CHECKLIST.relative_to(ROOT))
    bootstrap_text = read_text(root / BOOTSTRAP_NOTES.relative_to(ROOT))
    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))
    checker_text = read_text(root / TOOLCHAIN_CHECKER.relative_to(ROOT))
    policy_text = read_text(root / TOOLCHAIN_POLICY.relative_to(ROOT))

    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_occurrence_issues(
            review_text,
            REVIEW_MARKERS,
            "REVIEW_MARKER_MISSING",
            "REVIEW_MARKER_DUPLICATED",
        )
    )
    issues.extend(
        collect_occurrence_issues(
            bootstrap_text,
            BOOTSTRAP_MARKERS,
            "BOOTSTRAP_MARKER_MISSING",
            "BOOTSTRAP_MARKER_DUPLICATED",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            workflow_text,
            WORKFLOW_LINES,
            "WORKFLOW_LINE_MISSING",
            "WORKFLOW_LINE_DUPLICATED",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            makefile_text,
            MAKEFILE_LINES,
            "MAKEFILE_LINE_MISSING",
            "MAKEFILE_LINE_DUPLICATED",
        )
    )
    issues.extend(
        collect_occurrence_issues(
            checker_text,
            CHECKER_MARKERS,
            "TOOLCHAIN_CHECKER_MARKER_MISSING",
            "TOOLCHAIN_CHECKER_MARKER_DUPLICATED",
        )
    )
    issues.extend(validate_policy(json.loads(policy_text)))
    return issues


def sample_policy() -> str:
    return json.dumps(
        {
            "phase": EXPECTED_PHASE,
            "channel": EXPECTED_CHANNEL,
            "minimum_version": EXPECTED_CHANNEL,
            "upgrade_policy": {
                "archive_target_scope": EXPECTED_ARCHIVE_TARGETS,
                "required_make_routes": EXPECTED_REQUIRED_ROUTES,
            },
        },
        indent=2,
    ) + "\n"


def sample_checker() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "def load_min_version():",
            "    pass",
            "def load_pinned_channel():",
            "    pass",
            "def resolve_zig_executable():",
            "    pass",
            "def resolve_policy_archive():",
            "    pass",
            "def validate_policy_archive():",
            "    pass",
            "def build_parser(parser):",
            '    parser.add_argument("--allow-missing")',
            '    parser.add_argument("--policy-only")',
            '    parser.add_argument("--archive-only")',
            '    parser.add_argument("--archive")',
            '    parser.add_argument("--archive-target")',
            '    parser.add_argument("--zig")',
            "",
        ]
    )


def sample_markdown(title: str, markers: tuple[str, ...]) -> str:
    lines = [f"# {title}", ""]
    for marker in markers:
        lines.append(f"- {marker}")
    lines.append("")
    return "\n".join(lines)


def sample_lines(lines: tuple[str, ...]) -> str:
    return "\n".join(lines) + "\n"


def write_sample_root(root: Path) -> None:
    write_text(root / REVIEW_CHECKLIST.relative_to(ROOT), sample_markdown("Review Checklist", REVIEW_MARKERS))
    write_text(root / BOOTSTRAP_NOTES.relative_to(ROOT), sample_markdown("Bootstrap Notes", BOOTSTRAP_MARKERS))
    write_text(root / WORKFLOW.relative_to(ROOT), sample_lines(WORKFLOW_LINES))
    write_text(root / MAKEFILE.relative_to(ROOT), sample_lines(MAKEFILE_LINES))
    write_text(root / TOOLCHAIN_CHECKER.relative_to(ROOT), sample_checker())
    write_text(root / TOOLCHAIN_POLICY.relative_to(ROOT), sample_policy())


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane25_toolchain_pin_scope_") as tempdir:
        root = Path(tempdir)
        write_sample_root(root)

        pass_issues = validate(root)
        if pass_issues:
            raise SystemExit(f"sample root should pass, found: {pass_issues}")
        case_count += 1

        broken_review = read_text(root / REVIEW_CHECKLIST.relative_to(ROOT)).replace(REVIEW_MARKERS[0], "", 1)
        write_text(root / REVIEW_CHECKLIST.relative_to(ROOT), broken_review)
        fail_issues = validate(root)
        if not any(code == "REVIEW_MARKER_MISSING" and detail == REVIEW_MARKERS[0] for code, detail in fail_issues):
            raise SystemExit(f"expected missing review marker failure, found: {fail_issues}")
        case_count += 1

        write_sample_root(root)
        duplicated_workflow = read_text(root / WORKFLOW.relative_to(ROOT)) + WORKFLOW_LINES[0] + "\n"
        write_text(root / WORKFLOW.relative_to(ROOT), duplicated_workflow)
        fail_issues = validate(root)
        if not any(
            code == "WORKFLOW_LINE_DUPLICATED" and detail == f"{WORKFLOW_LINES[0]}:count=2"
            for code, detail in fail_issues
        ):
            raise SystemExit(f"expected duplicate workflow line failure, found: {fail_issues}")
        case_count += 1

        write_sample_root(root)
        broken_policy = json.loads(read_text(root / TOOLCHAIN_POLICY.relative_to(ROOT)))
        broken_policy["upgrade_policy"]["required_make_routes"] = EXPECTED_REQUIRED_ROUTES[:-1]
        write_text(root / TOOLCHAIN_POLICY.relative_to(ROOT), json.dumps(broken_policy, indent=2) + "\n")
        fail_issues = validate(root)
        if not any(code == "INVALID_POLICY_REQUIRED_ROUTES" for code, _detail in fail_issues):
            raise SystemExit(f"expected invalid policy required routes failure, found: {fail_issues}")
        case_count += 1

    print("PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repo root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", type=Path, help="write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    if args.write_sample_root:
        write_sample_root(args.write_sample_root)
        print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return

    issues = validate(args.root)
    if issues:
        for code, detail in issues:
            print(f"{code}={detail}")
        raise SystemExit(1)

    print("PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET=pass")
    print("PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_REQUIRED_PATH_COUNT=6")
    print(
        "PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_MARKER_COUNT="
        f"{len(REVIEW_MARKERS) + len(BOOTSTRAP_MARKERS) + len(WORKFLOW_LINES) + len(MAKEFILE_LINES) + len(CHECKER_MARKERS)}"
    )


if __name__ == "__main__":
    main()
