#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
VALIDATE_PHASE2_CLOSURE = Path("scripts/zigux/validate-phase2-closure.py")
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

PAYLOAD = "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
ARCHIVE_README = "third_party/README.md"
TESTS_ROOT_SUMMARY_ROUTE_GAP = "scripts/zigux/check-phase2-tests-root-summary-route-gap.py"
CLOSURE_VALIDATOR_GAP = "scripts/zigux/check-phase2-closure-validator-gap.py"

REQUIRED_CLOSURE_MARKERS = (
    f"`PHASE2_CURRENT_GAP_PACKET={PAYLOAD}`",
    (
        "The current closure-side archive-contract packet now stays explicit through "
        "`scripts/zigux/check-phase2-archive-contract-packet.py`, "
        "`scripts/zigux/check-phase2-closure-archive-contract.py`, `third_party/README.md`, "
        "`zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, "
        "`scripts/zigux/check-phase2-tool-manifest.py`, and "
        "`scripts/zigux/check-phase2-tests-readme-alignment.py` while "
        f"`{PAYLOAD}` remains the lone current repo-reality gap on `master`."
    ),
)

REQUIRED_VALIDATE_MARKERS = (
    f'TESTS_ROOT_SUMMARY_ROUTE_GAP_REL = Path("{TESTS_ROOT_SUMMARY_ROUTE_GAP}")',
    f'CLOSURE_VALIDATOR_GAP_REL = Path("{CLOSURE_VALIDATOR_GAP}")',
    "EXPECTED_MANIFEST_GAPS = [ARCHIVE_PAYLOAD_REL.as_posix()]",
    "TESTS_ROOT_SUMMARY_ROUTE_GAP_REL,",
    "CLOSURE_VALIDATOR_GAP_REL,",
    '"archive_support": (',
    '"third_party/README.md",',
    "if manifest_gaps != EXPECTED_MANIFEST_GAPS:",
)

FORBIDDEN_VALIDATE_MARKERS = (
    "manifest_gaps != []",
    "manifest_gaps != list(EXPECTED_MANIFEST_GAPS)",
)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(root: Path, rel: Path) -> object:
    try:
        return json.loads(read_text(root, rel))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {root / rel}: {exc}") from exc


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    closure_text = read_text(root, PHASE2_CLOSURE)
    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    validate_text = read_text(root, VALIDATE_PHASE2_CLOSURE)
    for marker in REQUIRED_VALIDATE_MARKERS:
        if marker not in validate_text:
            issues.append(("MISSING_VALIDATE_MARKER", marker))
    for marker in FORBIDDEN_VALIDATE_MARKERS:
        if marker in validate_text:
            issues.append(("FORBIDDEN_VALIDATE_MARKER", marker))

    manifest = read_json(root, MANIFEST)
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    manifest_gaps = manifest.get("repo_reality_gaps")
    if manifest_gaps != [PAYLOAD]:
        issues.append(("UNEXPECTED_MANIFEST_GAPS", repr(manifest_gaps)))

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return issues

    archive_support = present_surfaces.get("archive_support")
    if archive_support != [ARCHIVE_README]:
        issues.append(("UNEXPECTED_ARCHIVE_SUPPORT", repr(archive_support)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_CLOSURE_VALIDATOR_GAP=fail")
    for code, value in issues:
        print(f"{code}:{value}")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        PHASE2_CLOSURE,
        "\n".join(
            (
                "# Phase 2 Closure",
                "",
                f"- `PHASE2_CURRENT_GAP_PACKET={PAYLOAD}`",
                "",
                (
                    "The current closure-side archive-contract packet now stays explicit through "
                    "`scripts/zigux/check-phase2-archive-contract-packet.py`, "
                    "`scripts/zigux/check-phase2-closure-archive-contract.py`, `third_party/README.md`, "
                    "`zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, "
                    "`scripts/zigux/check-phase2-tool-manifest.py`, and "
                    "`scripts/zigux/check-phase2-tests-readme-alignment.py` while "
                    f"`{PAYLOAD}` remains the lone current repo-reality gap on `master`."
                ),
                "",
            )
        )
        + "\n",
    )
    write_text(
        root,
        VALIDATE_PHASE2_CLOSURE,
        "\n".join(
            (
                "from pathlib import Path",
                f'TESTS_ROOT_SUMMARY_ROUTE_GAP_REL = Path("{TESTS_ROOT_SUMMARY_ROUTE_GAP}")',
                f'CLOSURE_VALIDATOR_GAP_REL = Path("{CLOSURE_VALIDATOR_GAP}")',
                f'ARCHIVE_PAYLOAD_REL = Path("{PAYLOAD}")',
                "EXPECTED_MANIFEST_GAPS = [ARCHIVE_PAYLOAD_REL.as_posix()]",
                "EXPECTED_MANIFEST_SURFACES = {",
                '    "archive_support": (',
                '        "third_party/README.md",',
                "    ),",
                "}",
                "REQUIRED_FILES = (",
                "    TESTS_ROOT_SUMMARY_ROUTE_GAP_REL,",
                "    CLOSURE_VALIDATOR_GAP_REL,",
                ")",
                'manifest_gaps = manifest.get("repo_reality_gaps")',
                "if manifest_gaps != EXPECTED_MANIFEST_GAPS:",
                '    issues.append(("UNEXPECTED_MANIFEST_GAPS", repr(manifest_gaps)))',
            )
        )
        + "\n",
    )
    write_text(
        root,
        MANIFEST,
        json.dumps(
            {
                "repo_reality_gaps": [PAYLOAD],
                "present_surfaces": {"archive_support": [ARCHIVE_README]},
            },
            indent=2,
        )
        + "\n",
    )


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="lane22_gap_checker_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root, PHASE2_CLOSURE, "# broken\n")
        assert any(code == "MISSING_CLOSURE_MARKER" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(root, VALIDATE_PHASE2_CLOSURE, "manifest_gaps != []\n")
        expect_issue(root, ("FORBIDDEN_VALIDATE_MARKER", "manifest_gaps != []"))
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            VALIDATE_PHASE2_CLOSURE,
            "\n".join(
                (
                    "from pathlib import Path",
                    f'TESTS_ROOT_SUMMARY_ROUTE_GAP_REL = Path("{TESTS_ROOT_SUMMARY_ROUTE_GAP}")',
                    f'CLOSURE_VALIDATOR_GAP_REL = Path("{CLOSURE_VALIDATOR_GAP}")',
                    f'ARCHIVE_PAYLOAD_REL = Path("{PAYLOAD}")',
                )
            )
            + "\n",
        )
        expect_issue(
            root,
            ("MISSING_VALIDATE_MARKER", "EXPECTED_MANIFEST_GAPS = [ARCHIVE_PAYLOAD_REL.as_posix()]"),
        )
        checks += 1

        build_self_test_root(root)
        manifest = json.loads(read_text(root, MANIFEST))
        manifest["repo_reality_gaps"] = []
        write_text(root, MANIFEST, json.dumps(manifest, indent=2) + "\n")
        expect_issue(root, ("UNEXPECTED_MANIFEST_GAPS", "[]"))
        checks += 1

        build_self_test_root(root)
        manifest = json.loads(read_text(root, MANIFEST))
        manifest["present_surfaces"]["archive_support"] = [ARCHIVE_README, PAYLOAD]
        write_text(root, MANIFEST, json.dumps(manifest, indent=2) + "\n")
        expect_issue(root, ("UNEXPECTED_ARCHIVE_SUPPORT", repr([ARCHIVE_README, PAYLOAD])))
        checks += 1

    print("PHASE2_CLOSURE_VALIDATOR_GAP_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_GAP_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the Phase 2 closure validator drifts away from the parked lone-archive-gap posture."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATOR_GAP=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_GAP_PAYLOAD={PAYLOAD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
