#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

LANE_NOTE = "Documentation/zigux/phase2-toolchain-lane-sequencing.md"
BOOTSTRAP_NOTE = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
DIRECT_CHECKER = "scripts/zigux/check-phase2-cross.py"
ALIGNMENT_CHECKER = "scripts/zigux/check-phase2-cross-selftest-alignment.py"
VALIDATOR = "scripts/zigux/validate-phase2.py"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
FIXTURE = "zigux/tests/fixtures/phase2_cross_targets.json"
MAKEFILE = "zigux/Makefile"

REQUIRED_PATHS = (
    LANE_NOTE,
    BOOTSTRAP_NOTE,
    DIRECT_CHECKER,
    ALIGNMENT_CHECKER,
    VALIDATOR,
    POLICY,
    FIXTURE,
    MAKEFILE,
)

EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_ARCHIVE_SCOPE = ["x86_64-linux"]
EXPECTED_CROSS_TARGETS = [
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
]

REQUIRED_LANE_NOTE_MARKERS = (
    "shared sequencing lane `P2-Y10`",
    "shared backlog truthfulness lane `P2-Y12`",
    "Makefile toolchain lane `P2-X09`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-cross`",
    "Reopen `P2-Y10` only for shared route-inventory, reminder-surface, tool-manifest, cross-target, or validator alignment drift",
    "Reopen `P2-Y12` only when current `master` evidence shows a shared backlog or review surface pointing at the wrong next step",
)

REQUIRED_BOOTSTRAP_NOTE_MARKERS = (
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "`x86_64-linux` `archive_required` lane",
    "`aarch64-linux` `route_contract_only` lane",
    "`make -C zigux phase2-cross`",
)

REQUIRED_VALIDATOR_MARKERS = (
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "zigux/Makefile",
)

REQUIRED_MAKEFILE_LINES = (
    ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2: phase2-validate",
)


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_paths(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_PATHS if not (root / rel).exists()]


def count_substring(text: str, marker: str) -> int:
    return text.count(marker)


def parse_json_object(root: Path, rel: str) -> dict[str, object]:
    payload = json.loads(read_text(root, rel))
    if not isinstance(payload, dict):
        raise ValueError(f"{rel} must decode to a JSON object")
    return payload


def collect_marker_issues(
    issues: list[tuple[str, str]],
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> None:
    for marker in markers:
        count = count_substring(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))


def collect_fixture_issues(root: Path, issues: list[tuple[str, str]]) -> None:
    payload = parse_json_object(root, FIXTURE)

    if payload.get("phase") != "Phase 2":
        issues.append(("FIXTURE_FIELD_MISMATCH", f"phase:{payload.get('phase')!r}"))
    if payload.get("status") != "active":
        issues.append(("FIXTURE_FIELD_MISMATCH", f"status:{payload.get('status')!r}"))
    if payload.get("route") != EXPECTED_ROUTE:
        issues.append(("FIXTURE_FIELD_MISMATCH", f"route:{payload.get('route')!r}"))
    if payload.get("archive_target_scope") != EXPECTED_ARCHIVE_SCOPE:
        issues.append(
            (
                "FIXTURE_FIELD_MISMATCH",
                f"archive_target_scope:{payload.get('archive_target_scope')!r}",
            )
        )
    if payload.get("cross_targets") != EXPECTED_CROSS_TARGETS:
        issues.append(("FIXTURE_FIELD_MISMATCH", f"cross_targets:{payload.get('cross_targets')!r}"))


def collect_policy_issues(root: Path, issues: list[tuple[str, str]]) -> None:
    payload = parse_json_object(root, POLICY)
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("POLICY_FIELD_MISMATCH", f"upgrade_policy:{upgrade_policy!r}"))
        return

    if upgrade_policy.get("archive_target_scope") != EXPECTED_ARCHIVE_SCOPE:
        issues.append(
            (
                "POLICY_FIELD_MISMATCH",
                f"archive_target_scope:{upgrade_policy.get('archive_target_scope')!r}",
            )
        )

    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or "phase2-cross" not in routes:
        issues.append(("POLICY_FIELD_MISMATCH", f"required_make_routes:{routes!r}"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in require_paths(root):
        issues.append(("MISSING_REQUIRED_PATH", rel))

    if issues:
        return issues

    lane_note = read_text(root, LANE_NOTE)
    bootstrap_note = read_text(root, BOOTSTRAP_NOTE)
    validator = read_text(root, VALIDATOR)
    makefile = read_text(root, MAKEFILE)

    collect_marker_issues(
        issues,
        lane_note,
        REQUIRED_LANE_NOTE_MARKERS,
        "MISSING_LANE_NOTE_MARKER",
        "DUPLICATE_LANE_NOTE_MARKER",
    )
    collect_marker_issues(
        issues,
        bootstrap_note,
        REQUIRED_BOOTSTRAP_NOTE_MARKERS,
        "MISSING_BOOTSTRAP_NOTE_MARKER",
        "DUPLICATE_BOOTSTRAP_NOTE_MARKER",
    )
    collect_marker_issues(
        issues,
        validator,
        REQUIRED_VALIDATOR_MARKERS,
        "MISSING_VALIDATOR_MARKER",
        "DUPLICATE_VALIDATOR_MARKER",
    )
    collect_marker_issues(
        issues,
        makefile,
        REQUIRED_MAKEFILE_LINES,
        "MISSING_MAKEFILE_LINE",
        "DUPLICATE_MAKEFILE_LINE",
    )

    collect_fixture_issues(root, issues)
    collect_policy_issues(root, issues)
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_LANE_SEQUENCING_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        LANE_NOTE,
        """# Phase 2 Toolchain Lane Sequencing

shared sequencing lane `P2-Y10`
shared backlog truthfulness lane `P2-Y12`
Makefile toolchain lane `P2-X09`
`zigux/tests/fixtures/phase2_cross_targets.json`
`scripts/zigux/check-phase2-cross.py`
`scripts/zigux/check-phase2-cross-selftest-alignment.py`
`scripts/zigux/validate-phase2.py`
`zigux/Makefile`
`make -C zigux phase2-cross`
Reopen `P2-Y10` only for shared route-inventory, reminder-surface, tool-manifest, cross-target, or validator alignment drift
Reopen `P2-Y12` only when current `master` evidence shows a shared backlog or review surface pointing at the wrong next step
""",
    )
    write_text(
        root,
        BOOTSTRAP_NOTE,
        """# Phase 2 Toolchain Bootstrap Notes

`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit
`x86_64-linux` `archive_required` lane
`aarch64-linux` `route_contract_only` lane
`make -C zigux phase2-cross`
""",
    )
    write_text(root, DIRECT_CHECKER, "print('direct checker stub')\n")
    write_text(root, ALIGNMENT_CHECKER, "print('alignment checker stub')\n")
    write_text(
        root,
        VALIDATOR,
        """# validator stub
zigux/tests/fixtures/phase2_cross_targets.json
scripts/zigux/check-phase2-cross.py
scripts/zigux/check-phase2-cross-selftest-alignment.py
zigux/Makefile
""",
    )
    write_text(
        root,
        POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                    "required_make_routes": [
                        "phase2-toolchain",
                        "phase2-validate",
                        "phase2-cross",
                    ],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        FIXTURE,
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": EXPECTED_ROUTE,
                "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                "cross_targets": EXPECTED_CROSS_TARGETS,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        """.PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2

phase2-cross:
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py

phase2: phase2-validate
""",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_cross_lane_seq_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert require_paths(root) == []
        assert collect_issues(root) == []
        case_count += 1

        build_sample_root(root)
        (root / FIXTURE).write_text(
            json.dumps(
                {
                    "phase": "Phase 2",
                    "status": "active",
                    "route": EXPECTED_ROUTE,
                    "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                    "cross_targets": EXPECTED_CROSS_TARGETS[:1],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("FIXTURE_FIELD_MISMATCH", f"cross_targets:{EXPECTED_CROSS_TARGETS[:1]!r}") in issues
        case_count += 1

        build_sample_root(root)
        write_text(
            root,
            POLICY,
            json.dumps(
                {
                    "upgrade_policy": {
                        "archive_target_scope": ["aarch64-linux"],
                        "required_make_routes": ["phase2-toolchain"],
                    }
                },
                indent=2,
            )
            + "\n",
        )
        issues = collect_issues(root)
        assert (
            "POLICY_FIELD_MISMATCH",
            "archive_target_scope:['aarch64-linux']",
        ) in issues
        assert (
            "POLICY_FIELD_MISMATCH",
            "required_make_routes:['phase2-toolchain']",
        ) in issues
        case_count += 1

        build_sample_root(root)
        write_text(root, LANE_NOTE, "# broken\n")
        issues = collect_issues(root)
        assert ("MISSING_LANE_NOTE_MARKER", "shared sequencing lane `P2-Y10`") in issues
        case_count += 1

    print("PHASE2_CROSS_LANE_SEQUENCING_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_LANE_SEQUENCING_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the Lane 21 Phase 2 sequencing note drifts away from the live cross-route packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a passing sample repository root for focused contract replays.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_CROSS_LANE_SEQUENCING_CONTRACT_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    fixture = parse_json_object(args.root, FIXTURE)
    cross_targets = fixture["cross_targets"]
    print("PHASE2_CROSS_LANE_SEQUENCING_CONTRACT=pass")
    print(f"PHASE2_CROSS_LANE_SEQUENCING_CONTRACT_TARGET_COUNT={len(cross_targets)}")
    print(
        "PHASE2_CROSS_LANE_SEQUENCING_CONTRACT_TARGETS="
        + ",".join(target["target"] for target in cross_targets)
    )
    print(
        "PHASE2_CROSS_LANE_SEQUENCING_CONTRACT_ARCHIVE_SCOPE="
        + ",".join(EXPECTED_ARCHIVE_SCOPE)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
