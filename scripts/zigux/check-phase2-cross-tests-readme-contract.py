#!/usr/bin/env python3
"""Guard the tests-readme side of the live Phase 2 cross packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_ARCHIVE_SCOPE = ["x86_64-linux"]
EXPECTED_TARGETS = [
    ("x86_64-linux", "archive_required"),
    ("aarch64-linux", "route_contract_only"),
]

TESTS_README_DIRECT_PACKET_SENTENCE = (
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, "
    "`python3 scripts/zigux/install-zig.py --self-test`, "
    "`scripts/zigux/check-phase2-cross.py`, "
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`, and "
    "`zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, "
    "direct cross-route, and cross-target fixture packet explicit here instead of leaving "
    "it in the historical-gap bucket"
)
BOOTSTRAP_NOTES_CROSS_SENTENCE = (
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct "
    "cross-route packet explicit through the pinned `x86_64-linux` `archive_required` "
    "lane plus the `aarch64-linux` `route_contract_only` lane, so toolchain follow-through "
    "should treat the returned cross packet as present evidence instead of a repo-reality gap."
)
SCRIPTS_README_DIRECT_PACKET_SENTENCE = (
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, "
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`, "
    "`python3 scripts/zigux/check-phase2-cross.py`, and "
    "`zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current "
    "`master`, so keep those installer and direct cross-route surfaces explicit beside "
    "the shipped toolchain and kbuild reminder packet instead of leaving them in "
    "repo-reality-gap wording"
)

TESTS_README_MARKERS = [
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "make -C zigux phase2-cross",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    TESTS_README_DIRECT_PACKET_SENTENCE,
]
BOOTSTRAP_NOTES_MARKERS = [
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "make -C zigux phase2-cross",
    BOOTSTRAP_NOTES_CROSS_SENTENCE,
]
SCRIPTS_README_MARKERS = [
    "scripts/zigux/install-zig.py",
    "python3 scripts/zigux/install-zig.py --self-test",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    SCRIPTS_README_DIRECT_PACKET_SENTENCE,
]

FORBIDDEN_STALE_MARKERS = [
    "three-target compile matrix",
    "riscv64-linux-musl",
    "riscv64-linux",
]

EXPECTED_SELF_TEST_CASE_COUNT = 9


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def count_literal(text: str, marker: str) -> int:
    return text.count(marker)


def validate_markers(text: str, *, label: str, markers: list[str]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        if marker not in text:
            issues.append(("MISSING_MARKER", f"{label}:{marker}"))
    return issues


def validate_forbidden(text: str, *, label: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in FORBIDDEN_STALE_MARKERS:
        if marker in text:
            issues.append(("FORBIDDEN_STALE_MARKER", f"{label}:{marker}"))
    return issues


def validate_makefile(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    exact_lines = [
        "phase2-cross:",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
        "phase2: phase2-validate",
    ]
    for marker in exact_lines:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))
    return issues


def validate_fixture(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", "root")]

    if payload.get("phase") != "Phase 2":
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if payload.get("status") != "active":
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if payload.get("route") != EXPECTED_ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if payload.get("archive_target_scope") != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list):
        return issues + [("INVALID_FIXTURE_FIELD", "cross_targets")]

    if len(cross_targets) != len(EXPECTED_TARGETS):
        issues.append(("INVALID_CROSS_TARGET_COUNT", str(len(cross_targets))))
        return issues

    seen_targets: list[tuple[str, str]] = []
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", repr(entry)))
            continue
        target = entry.get("target")
        mode = entry.get("validation_mode")
        route = entry.get("route")
        review_status = entry.get("review_status")
        if not isinstance(target, str) or not target:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        if not isinstance(review_status, str) or not review_status.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
        if route != EXPECTED_ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        seen_targets.append((target, mode))

    if seen_targets != EXPECTED_TARGETS:
        issues.append(("INVALID_CROSS_TARGET_PACKET", repr(seen_targets)))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    bootstrap_notes_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    fixture = read_json(resolve_path(root, FIXTURE))

    issues.extend(validate_markers(tests_readme_text, label="tests_readme", markers=TESTS_README_MARKERS))
    issues.extend(validate_markers(bootstrap_notes_text, label="bootstrap_notes", markers=BOOTSTRAP_NOTES_MARKERS))
    issues.extend(validate_markers(scripts_readme_text, label="scripts_readme", markers=SCRIPTS_README_MARKERS))

    issues.extend(validate_forbidden(tests_readme_text, label="tests_readme"))
    issues.extend(validate_forbidden(bootstrap_notes_text, label="bootstrap_notes"))
    issues.extend(validate_forbidden(scripts_readme_text, label="scripts_readme"))

    if count_literal(tests_readme_text, TESTS_README_DIRECT_PACKET_SENTENCE) != 1:
        issues.append(
            (
                "INVALID_TESTS_README_DIRECT_PACKET_SENTENCE_COUNT",
                str(count_literal(tests_readme_text, TESTS_README_DIRECT_PACKET_SENTENCE)),
            )
        )
    if count_literal(bootstrap_notes_text, BOOTSTRAP_NOTES_CROSS_SENTENCE) != 1:
        issues.append(
            (
                "INVALID_BOOTSTRAP_NOTES_CROSS_SENTENCE_COUNT",
                str(count_literal(bootstrap_notes_text, BOOTSTRAP_NOTES_CROSS_SENTENCE)),
            )
        )
    if count_literal(scripts_readme_text, SCRIPTS_README_DIRECT_PACKET_SENTENCE) != 1:
        issues.append(
            (
                "INVALID_SCRIPTS_README_DIRECT_PACKET_SENTENCE_COUNT",
                str(count_literal(scripts_readme_text, SCRIPTS_README_DIRECT_PACKET_SENTENCE)),
            )
        )

    issues.extend(validate_makefile(makefile_text))
    issues.extend(validate_fixture(fixture))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_TESTS_README_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, TESTS_README),
        "\n".join(TESTS_README_MARKERS + [""]) + "\n",
    )
    write_text(
        resolve_path(root, BOOTSTRAP_NOTES),
        "\n".join(BOOTSTRAP_NOTES_MARKERS + [""]) + "\n",
    )
    write_text(
        resolve_path(root, SCRIPTS_README),
        "\n".join(SCRIPTS_README_MARKERS + [""]) + "\n",
    )
    write_text(
        resolve_path(root, MAKEFILE),
        "\n".join(
            [
                "phase2-cross:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
                "",
                "phase2: phase2-validate",
                "",
            ]
        ),
    )
    write_text(
        resolve_path(root, FIXTURE),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": EXPECTED_ROUTE,
                "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                "cross_targets": [
                    {
                        "target": "x86_64-linux",
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": EXPECTED_ROUTE,
                    },
                    {
                        "target": "aarch64-linux",
                        "review_status": "route contract only",
                        "validation_mode": "route_contract_only",
                        "route": EXPECTED_ROUTE,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise AssertionError(f"marker not found: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_testsreadme_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        tests_path = resolve_path(root, TESTS_README)
        build_self_test_root(root)
        tests_path.write_text(
            replace_once(tests_path.read_text(encoding="utf-8"), "make -C zigux phase2-cross", "make -C zigux phase2"),
            encoding="utf-8",
        )
        assert ("MISSING_MARKER", "tests_readme:make -C zigux phase2-cross") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        tests_path.write_text(tests_path.read_text(encoding="utf-8") + "riscv64-linux\n", encoding="utf-8")
        assert ("FORBIDDEN_STALE_MARKER", "tests_readme:riscv64-linux") in collect_issues(root)
        checks_run += 1

        scripts_path = resolve_path(root, SCRIPTS_README)
        build_self_test_root(root)
        scripts_path.write_text(
            scripts_path.read_text(encoding="utf-8") + SCRIPTS_README_DIRECT_PACKET_SENTENCE + "\n",
            encoding="utf-8",
        )
        assert ("INVALID_SCRIPTS_README_DIRECT_PACKET_SENTENCE_COUNT", "2") in collect_issues(root)
        checks_run += 1

        makefile_path = resolve_path(root, MAKEFILE)
        build_self_test_root(root)
        makefile_path.write_text(
            replace_once(
                makefile_path.read_text(encoding="utf-8"),
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-target-replay.py",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_MAKEFILE_LINE",
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
        ) in collect_issues(root)
        checks_run += 1

        fixture_path = resolve_path(root, FIXTURE)
        build_self_test_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"].append(
            {
                "target": "riscv64-linux",
                "review_status": "historical only",
                "validation_mode": "route_contract_only",
                "route": EXPECTED_ROUTE,
            }
        )
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_COUNT", "3") in collect_issues(root)
        checks_run += 1

        bootstrap_path = resolve_path(root, BOOTSTRAP_NOTES)
        build_self_test_root(root)
        bootstrap_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing bootstrap notes did not abort")
        checks_run += 1

        build_self_test_root(root)
        fixture_path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
        else:
            raise AssertionError("invalid fixture json did not abort")
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_TESTS_README_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TESTS_README_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the tests-readme side of the Phase 2 cross packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    fixture = read_json(resolve_path(args.root.resolve(), FIXTURE))
    assert isinstance(fixture, dict)
    cross_targets = fixture.get("cross_targets")
    assert isinstance(cross_targets, list)
    print("PHASE2_CROSS_TESTS_README_CONTRACT=pass")
    print(f"PHASE2_CROSS_TESTS_README_CONTRACT_TARGET_COUNT={len(cross_targets)}")
    print(
        "PHASE2_CROSS_TESTS_README_CONTRACT_REQUIRED_PATH_COUNT=5"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
