#!/usr/bin/env python3
"""Check that the exact Phase 2 closure validator sentinel stays aligned."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

CLOSURE_NOTE_REL = Path("Documentation/zigux/phase2-closure.md")
SENTINEL_PREFIX = "PHASE2_CLOSURE_VALIDATORS="

EXPECTED_VALIDATORS = (
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "python3 scripts/zigux/check-kconfig-bridge.py",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "zig test scripts/zigux/kconfig/conf_bridge.zig",
    "zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "python3 scripts/zigux/check-phase2-required-make-routes.py",
    "python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "python3 scripts/zigux/check-phase2-tool-manifest.py",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "python3 scripts/zigux/check-genksyms-bridge.py",
    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "zig test scripts/zigux/genksyms.zig",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "python3 scripts/zigux/check-fixdep-diff.py",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py --self-test",
    "python3 scripts/zigux/validate-phase2-closure.py",
)

REQUIRED_FILES = (
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("scripts/zigux/check-lane05-local-first-archive-workflow.py"),
    Path("scripts/zigux/check-lane05-local-archive-readme.py"),
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/check-phase2-toolchain-pinning.py"),
    Path("scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    Path("scripts/zigux/check-phase2-kbuild-routes.py"),
    Path("scripts/zigux/check-kconfig-bridge.py"),
    Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-cross.py"),
    Path("scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-docs-shared-reminder.py"),
    Path("scripts/zigux/check-phase2-required-make-routes.py"),
    Path("scripts/zigux/check-phase2-tool-manifest.py"),
    Path("scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    Path("scripts/zigux/check-genksyms-bridge.py"),
    Path("scripts/zigux/check-phase2-genksyms-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-fixdep-gate.py"),
    Path("scripts/zigux/check-fixdep-diff.py"),
    Path("scripts/zigux/check-phase2-tests-readme-alignment.py"),
    Path("scripts/zigux/validate-phase2.py"),
    Path("scripts/zigux/validate-phase2-closure.py"),
    Path("scripts/zigux/kconfig/conf_bridge.zig"),
    Path("scripts/zigux/kconfig/confdata_bridge.zig"),
    Path("scripts/zigux/genksyms.zig"),
    Path("scripts/zigux/fixdep.zig"),
    CLOSURE_NOTE_REL,
)

REQUIRED_NOTE_MARKERS = (
    "`PHASE2_CURRENT_CLOSURE_PACKET=",
    "`PHASE2_SHARED_MAKE_ROUTES=",
    "`PHASE2_NEXT_SAFE_STEP=",
    "`python3 scripts/zigux/validate-phase2.py`",
    "`python3 scripts/zigux/validate-phase2-closure.py --self-test`",
    "`python3 scripts/zigux/validate-phase2-closure.py`",
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_closure_note_text(validators: tuple[str, ...] = EXPECTED_VALIDATORS) -> str:
    bullet_lines = "\n".join(f"- `{validator}`" for validator in validators)
    sentinel = ",".join(validators)
    return (
        "# Phase 2 Closure\n\n"
        "## Current Closure Packet\n\n"
        "- `PHASE2_CURRENT_CLOSURE_PACKET=placeholder`\n\n"
        "## Closure Validation\n\n"
        f"{bullet_lines}\n\n"
        f"- `{SENTINEL_PREFIX}{sentinel}`\n"
        "- `PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`\n"
        "- `PHASE2_NEXT_SAFE_STEP=keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again`\n"
    )


def parse_sentinel(text: str) -> list[str] | None:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if SENTINEL_PREFIX not in line:
            continue
        start = line.index(SENTINEL_PREFIX) + len(SENTINEL_PREFIX)
        remainder = line[start:]
        if remainder.endswith("`"):
            remainder = remainder[:-1]
        if remainder.endswith("`"):
            remainder = remainder[:-1]
        if remainder.startswith("`"):
            remainder = remainder[1:]
        return [entry for entry in remainder.split(",") if entry]
    return None


def collect_issues(root: Path) -> list[str]:
    closure_note_path = root / CLOSURE_NOTE_REL
    if not closure_note_path.is_file():
        return [f"missing_file:{CLOSURE_NOTE_REL.as_posix()}"]

    issues: list[str] = []
    text = closure_note_path.read_text(encoding="utf-8")
    actual = parse_sentinel(text)

    if actual is None:
        issues.append(f"missing_sentinel:{SENTINEL_PREFIX}")
    else:
        expected = list(EXPECTED_VALIDATORS)
        expected_set = set(expected)
        actual_set = set(actual)
        for entry in expected:
            if entry not in actual_set:
                issues.append(f"missing_validator:{entry}")
        for entry in actual:
            if entry not in expected_set:
                issues.append(f"unexpected_validator:{entry}")
        limit = min(len(expected), len(actual))
        for index in range(limit):
            if expected[index] != actual[index]:
                issues.append(
                    "validator_order_mismatch:"
                    f"index={index}:expected={expected[index]}:actual={actual[index]}"
                )
                break
        if len(actual) != len(expected):
            issues.append(
                "validator_count_mismatch:"
                f"expected={len(expected)}:actual={len(actual)}"
            )

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in text:
            issues.append(f"missing_note_marker:{marker}")

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            issues.append(f"missing_file:{rel_path.as_posix()}")

    return issues


def build_good_tree(root: Path, validators: tuple[str, ...] = EXPECTED_VALIDATORS) -> None:
    write_text(root / CLOSURE_NOTE_REL, build_closure_note_text(validators))
    for rel_path in REQUIRED_FILES:
        if rel_path == CLOSURE_NOTE_REL:
            continue
        write_text(root / rel_path, "placeholder\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_closure_validators_") as tmp_dir:
        root = Path(tmp_dir)

        build_good_tree(root)
        if collect_issues(root):
            raise SystemExit("phase2-closure-validators:self-test:good_tree")
        case_count += 1

        build_good_tree(root)
        write_text(root / CLOSURE_NOTE_REL, "# Phase 2 Closure\n")
        issues = collect_issues(root)
        if f"missing_sentinel:{SENTINEL_PREFIX}" not in issues:
            raise SystemExit("phase2-closure-validators:self-test:missing_sentinel")
        case_count += 1

        build_good_tree(root)
        validators = list(EXPECTED_VALIDATORS)
        validators.pop(7)
        write_text(root / CLOSURE_NOTE_REL, build_closure_note_text(tuple(validators)))
        issues = collect_issues(root)
        if "missing_validator:python3 scripts/zigux/install-zig.py --self-test" not in issues:
            raise SystemExit("phase2-closure-validators:self-test:missing_validator")
        case_count += 1

        build_good_tree(root)
        validators = list(EXPECTED_VALIDATORS)
        validators.insert(0, "python3 scripts/zigux/check-phase2-closure-validators.py --self-test")
        write_text(root / CLOSURE_NOTE_REL, build_closure_note_text(tuple(validators)))
        issues = collect_issues(root)
        if (
            "unexpected_validator:python3 scripts/zigux/check-phase2-closure-validators.py --self-test"
            not in issues
        ):
            raise SystemExit("phase2-closure-validators:self-test:unexpected_validator")
        case_count += 1

        build_good_tree(root)
        validators = list(EXPECTED_VALIDATORS)
        validators[0], validators[1] = validators[1], validators[0]
        write_text(root / CLOSURE_NOTE_REL, build_closure_note_text(tuple(validators)))
        issues = collect_issues(root)
        expected_issue = (
            "validator_order_mismatch:index=0:"
            "expected=python3 scripts/zigux/check-zig-toolchain.py --self-test:"
            "actual=python3 scripts/zigux/check-zig-toolchain.py --policy-only"
        )
        if expected_issue not in issues:
            raise SystemExit("phase2-closure-validators:self-test:order_mismatch")
        case_count += 1

        build_good_tree(root)
        note_path = root / CLOSURE_NOTE_REL
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                "`PHASE2_SHARED_MAKE_ROUTES=", "", 1
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if "missing_note_marker:`PHASE2_SHARED_MAKE_ROUTES=" not in issues:
            raise SystemExit("phase2-closure-validators:self-test:missing_note_marker")
        case_count += 1

        build_good_tree(root)
        (root / Path("scripts/zigux/check-phase2-required-make-routes.py")).unlink()
        issues = collect_issues(root)
        if "missing_file:scripts/zigux/check-phase2-required-make-routes.py" not in issues:
            raise SystemExit("phase2-closure-validators:self-test:missing_file")
        case_count += 1

    print("PHASE2_CLOSURE_VALIDATORS_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATORS_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> int:
    build_good_tree(root)
    print(f"PHASE2_CLOSURE_VALIDATORS_SAMPLE_ROOT={root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the exact Phase 2 closure validator sentinel stays aligned."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample tree for replay coverage",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_CLOSURE_VALIDATORS=fail")
        print("PHASE2_CLOSURE_VALIDATORS_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_CLOSURE_VALIDATORS_ISSUES_END")
        return 1

    print("PHASE2_CLOSURE_VALIDATORS=pass")
    print(f"PHASE2_CLOSURE_VALIDATORS_COMMAND_COUNT={len(EXPECTED_VALIDATORS)}")
    print(f"PHASE2_CLOSURE_VALIDATORS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_CLOSURE_VALIDATORS_NOTE_MARKER_COUNT={len(REQUIRED_NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
