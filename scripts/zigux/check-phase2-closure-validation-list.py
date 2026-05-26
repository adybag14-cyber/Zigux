#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
SECTION_HEADER = "## Closure Validation"
SECTION_END = "\n## Next Step\n"
VALIDATOR_PREFIX = "PHASE2_CLOSURE_VALIDATORS="
SHARED_ROUTES_PREFIX = "PHASE2_SHARED_MAKE_ROUTES="

EXPECTED_VALIDATORS = (
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "python3 scripts/zigux/check-kconfig-bridge.py",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
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
EXPECTED_SHARED_ROUTES = (
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)

REQUIRED_SECTION_MARKERS = (
    "The current closure packet is intentionally narrow and replayable, and it now names the policy-only, archive-integrity, local-first archive, returned archive-verification and staged repo-local archive helper companions, returned installer and cross-route companions, current manifest guards, the helper-local kconfig allconfig guard, direct kconfig bridge checker plus direct `conf_bridge` and `confdata_bridge` Zig unit replays, bounded genksyms bridge checker, dedicated genksyms selftest-alignment checker, direct genksyms Zig unit replay, standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, returned dash-prefixed long-option-arguments-as-data and dash-prefixed short-option-arguments-as-data expected-output fixtures, the primary artifact helper plus artifact-support manifest guard, fixdep checker pair, required-make-route guard, docs-shared reminder, restored closure-side validator, and shipped wrapper routes that current `master` can actually replay:",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`",
    "`python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`zig test scripts/zigux/kconfig/confdata_bridge.zig`",
    "`python3 scripts/zigux/check-phase2-required-make-routes.py`",
    "`python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`zig test scripts/zigux/genksyms.zig`",
    "`python3 scripts/zigux/check-fixdep-diff.py`",
    "`python3 scripts/zigux/validate-phase2-closure.py --self-test`",
    "`make -C zigux phase2-genksyms`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def extract_section(text: str) -> str:
    start = SECTION_HEADER + "\n"
    if start not in text or SECTION_END not in text:
        raise SystemExit(f"required note section markers missing: {PHASE2_CLOSURE_REL}")
    after_start = text.split(start, 1)[1]
    return after_start.split(SECTION_END, 1)[0]


def extract_sentinel_payload(text: str, prefix: str) -> str | None:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        candidate = line
        if candidate.startswith("- "):
            candidate = candidate[2:].strip()
        if candidate.startswith("`") and candidate.endswith("`"):
            candidate = candidate[1:-1]
        if candidate.startswith(prefix):
            return candidate[len(prefix) :]
    return None


def collect_issues(root: Path) -> list[tuple[str, str]]:
    closure_text = read_text(root / PHASE2_CLOSURE_REL)
    section_text = extract_section(closure_text)
    issues: list[tuple[str, str]] = []

    validator_payload = extract_sentinel_payload(section_text, VALIDATOR_PREFIX)
    expected_validator_payload = ",".join(EXPECTED_VALIDATORS)
    if validator_payload is None:
        issues.append(("MISSING_VALIDATOR_SENTINEL", VALIDATOR_PREFIX))
    elif validator_payload != expected_validator_payload:
        issues.append(("MISMATCHED_VALIDATOR_SENTINEL", validator_payload))

    routes_payload = extract_sentinel_payload(section_text, SHARED_ROUTES_PREFIX)
    expected_routes_payload = ",".join(EXPECTED_SHARED_ROUTES)
    if routes_payload is None:
        issues.append(("MISSING_SHARED_ROUTE_SENTINEL", SHARED_ROUTES_PREFIX))
    elif routes_payload != expected_routes_payload:
        issues.append(("MISMATCHED_SHARED_ROUTE_SENTINEL", routes_payload))

    header_count = count_exact_lines(closure_text, SECTION_HEADER)
    if header_count != 1:
        issues.append(("EXACT_HEADER_COUNT", f"{header_count}::{SECTION_HEADER}"))

    validator_line = f"- `{VALIDATOR_PREFIX}{expected_validator_payload}`"
    validator_count = count_exact_lines(section_text, validator_line)
    if validator_count != 1:
        issues.append(("EXACT_VALIDATOR_SENTINEL_COUNT", f"{validator_count}::{validator_line}"))

    routes_line = f"- `{SHARED_ROUTES_PREFIX}{expected_routes_payload}`"
    routes_count = count_exact_lines(section_text, routes_line)
    if routes_count != 1:
        issues.append(("EXACT_SHARED_ROUTE_SENTINEL_COUNT", f"{routes_count}::{routes_line}"))

    for marker in REQUIRED_SECTION_MARKERS:
        if marker not in section_text:
            issues.append(("MISSING_SECTION_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CLOSURE_VALIDATION_LIST=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    validators_block = "\n".join(f"- `{validator}`" for validator in EXPECTED_VALIDATORS)
    markers_block = "\n".join(
        f"- {marker}" if marker.startswith("`") else marker for marker in REQUIRED_SECTION_MARKERS[1:]
    )
    text = (
        "# Phase 2 Closure\n\n"
        f"{SECTION_HEADER}\n\n"
        f"{REQUIRED_SECTION_MARKERS[0]}\n\n"
        f"{validators_block}\n"
        f"{markers_block}\n"
        f"- `{VALIDATOR_PREFIX}{','.join(EXPECTED_VALIDATORS)}`\n"
        f"- `{SHARED_ROUTES_PREFIX}{','.join(EXPECTED_SHARED_ROUTES)}`\n\n"
        f"{SECTION_END.strip()}\n\n"
        "- next step placeholder\n"
    )
    write_text(root / PHASE2_CLOSURE_REL, text)


def write_sample_root(root: Path) -> int:
    build_self_test_root(root)
    print(f"PHASE2_CLOSURE_VALIDATION_LIST_SAMPLE_ROOT={root}")
    return 0


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validation_list_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                VALIDATOR_PREFIX + ",".join(EXPECTED_VALIDATORS),
            ),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATOR_SENTINEL", VALIDATOR_PREFIX) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                SHARED_ROUTES_PREFIX + ",".join(EXPECTED_SHARED_ROUTES),
                SHARED_ROUTES_PREFIX + ",".join(EXPECTED_SHARED_ROUTES[:-1]),
            ),
            encoding="utf-8",
        )
        assert (
            "MISMATCHED_SHARED_ROUTE_SENTINEL",
            ",".join(EXPECTED_SHARED_ROUTES[:-1]),
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "`make -C zigux phase2-genksyms`",
                "`make -C zigux phase2-tools`",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_SECTION_MARKER",
            "`make -C zigux phase2-genksyms`",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                f"{SECTION_HEADER}\n", f"{SECTION_HEADER}\n{SECTION_HEADER}\n", 1
            ),
            encoding="utf-8",
        )
        assert ("EXACT_HEADER_COUNT", f"2::{SECTION_HEADER}") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        validator_line = f"- `{VALIDATOR_PREFIX}{','.join(EXPECTED_VALIDATORS)}`\n"
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                validator_line,
                validator_line + validator_line,
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "EXACT_VALIDATOR_SENTINEL_COUNT",
            f"2::- `{VALIDATOR_PREFIX}{','.join(EXPECTED_VALIDATORS)}`",
        ) in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_VALIDATION_LIST_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATION_LIST_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 closure note validation-list contract aligned."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit")
    args = parser.parse_args()

    if args.self-test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root.resolve())

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATION_LIST=pass")
    print(f"PHASE2_CLOSURE_VALIDATION_LIST_VALIDATOR_COUNT={len(EXPECTED_VALIDATORS)}")
    print(f"PHASE2_CLOSURE_VALIDATION_LIST_SHARED_ROUTE_COUNT={len(EXPECTED_SHARED_ROUTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
