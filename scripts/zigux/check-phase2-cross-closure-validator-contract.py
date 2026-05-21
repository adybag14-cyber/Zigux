#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

VALIDATE_PHASE2_CLOSURE_REL = Path("scripts/zigux/validate-phase2-closure.py")
VALIDATE_PHASE2_REL = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")
TOOLCHAIN_POLICY_REL = Path("scripts/zigux/zig-toolchain-policy.json")
CROSS_FIXTURE_REL = Path("zigux/tests/fixtures/phase2_cross_targets.json")
CROSS_CHECKER_REL = Path("scripts/zigux/check-phase2-cross.py")
CROSS_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-cross-selftest-alignment.py")

REQUIRED_PATHS = (
    VALIDATE_PHASE2_CLOSURE_REL,
    VALIDATE_PHASE2_REL,
    PHASE2_CLOSURE_REL,
    WORKFLOW_REL,
    MAKEFILE_REL,
    TOOLCHAIN_POLICY_REL,
    CROSS_FIXTURE_REL,
    CROSS_CHECKER_REL,
    CROSS_ALIGNMENT_REL,
)

VALIDATOR_REQUIRED_MARKERS = (
    'CROSS_CHECKER_REL = Path("scripts/zigux/check-phase2-cross.py")',
    'CROSS_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-cross-selftest-alignment.py")',
    'CROSS_FIXTURE_REL = Path("zigux/tests/fixtures/phase2_cross_targets.json")',
    '"`scripts/zigux/check-phase2-cross.py`",',
    '"`scripts/zigux/check-phase2-cross-selftest-alignment.py`",',
    '"`zigux/tests/fixtures/phase2_cross_targets.json`",',
    '"`python3 scripts/zigux/check-phase2-cross.py --self-test`",',
    '"`python3 scripts/zigux/check-phase2-cross.py`",',
    '"`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",',
    '"`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",',
    '"`make -C zigux phase2-cross`",',
    '"run: python3 scripts/zigux/check-phase2-cross.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-cross.py",',
    '"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",',
)

CLOSURE_REQUIRED_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "`make -C zigux phase2-cross`",
    "`PHASE2_CURRENT_GAP_PACKET=`",
)

WORKFLOW_REQUIRED_LINES = {
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase2-cross.py": 1,
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "run: python3 scripts/zigux/validate-phase2-closure.py": 1,
}

MAKEFILE_REQUIRED_LINES = {
    "phase2-cross: phase2-toolchain": 1,
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test': 1,
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py': 1,
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test': 1,
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py': 1,
}

EXPECTED_ARCHIVE_SCOPE = ["x86_64-linux"]
EXPECTED_FIXTURE_ROUTE = "make -C zigux phase2-cross"
EXPECTED_CROSS_TARGETS = [
    {
        "target": "x86_64-linux",
        "review_status": "pinned bootstrap archive",
        "validation_mode": "archive_required",
        "route": EXPECTED_FIXTURE_ROUTE,
    },
    {
        "target": "aarch64-linux",
        "review_status": "route contract only",
        "validation_mode": "route_contract_only",
        "route": EXPECTED_FIXTURE_ROUTE,
    },
]

SELF_TEST_CASE_COUNT = 7


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_file():
        raise IsADirectoryError(path)
    return path.read_text(encoding="utf-8")


def load_json_object(path: Path) -> object:
    return json.loads(read_text(path))


def collect_exact_line_issues(text: str, expected_counts: dict[str, int], scope: str) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    for line, expected in expected_counts.items():
        count = sum(1 for actual in lines if actual == line)
        if count != expected:
            issues.append(f"{scope}:exact_count:{line}:count={count}:expected={expected}")
    return issues


def collect_required_marker_issues(text: str, markers: tuple[str, ...], scope: str) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        if marker not in text:
            issues.append(f"{scope}:missing_marker:{marker}")
    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    required_paths = [root / rel for rel in REQUIRED_PATHS]
    for path in required_paths:
        if not path.exists():
            issues.append(f"required_path:missing:{path.relative_to(root)}")
        elif not path.is_file():
            issues.append(f"required_path:not_file:{path.relative_to(root)}")
    if issues:
        return issues

    validator_text = read_text(root / VALIDATE_PHASE2_CLOSURE_REL)
    closure_text = read_text(root / PHASE2_CLOSURE_REL)
    workflow_text = read_text(root / WORKFLOW_REL)
    makefile_text = read_text(root / MAKEFILE_REL)
    policy = load_json_object(root / TOOLCHAIN_POLICY_REL)
    fixture = load_json_object(root / CROSS_FIXTURE_REL)

    issues.extend(
        collect_required_marker_issues(
            validator_text,
            VALIDATOR_REQUIRED_MARKERS,
            "closure_validator",
        )
    )
    issues.extend(
        collect_required_marker_issues(
            closure_text,
            CLOSURE_REQUIRED_MARKERS,
            "closure_note",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            workflow_text,
            WORKFLOW_REQUIRED_LINES,
            "workflow",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            makefile_text,
            MAKEFILE_REQUIRED_LINES,
            "makefile",
        )
    )

    if not isinstance(policy, dict):
        issues.append("toolchain_policy:root_not_object")
    else:
        upgrade_policy = policy.get("upgrade_policy")
        if not isinstance(upgrade_policy, dict):
            issues.append("toolchain_policy:missing_upgrade_policy")
        else:
            archive_scope = upgrade_policy.get("archive_target_scope")
            if archive_scope != EXPECTED_ARCHIVE_SCOPE:
                issues.append(
                    "toolchain_policy:archive_target_scope="
                    f"{archive_scope}:expected={EXPECTED_ARCHIVE_SCOPE}"
                )
            routes = upgrade_policy.get("required_make_routes")
            if routes != ["phase2-toolchain", "phase2-validate", "phase2-cross"]:
                issues.append(
                    "toolchain_policy:required_make_routes="
                    f"{routes}:expected=['phase2-toolchain', 'phase2-validate', 'phase2-cross']"
                )

    if not isinstance(fixture, dict):
        issues.append("cross_fixture:root_not_object")
    else:
        if fixture.get("route") != EXPECTED_FIXTURE_ROUTE:
            issues.append(
                "cross_fixture:route="
                f"{fixture.get('route')}:expected={EXPECTED_FIXTURE_ROUTE}"
            )
        if fixture.get("archive_target_scope") != EXPECTED_ARCHIVE_SCOPE:
            issues.append(
                "cross_fixture:archive_target_scope="
                f"{fixture.get('archive_target_scope')}:expected={EXPECTED_ARCHIVE_SCOPE}"
            )
        cross_targets = fixture.get("cross_targets")
        if cross_targets != EXPECTED_CROSS_TARGETS:
            issues.append(
                "cross_fixture:cross_targets="
                f"{cross_targets}:expected={EXPECTED_CROSS_TARGETS}"
            )

    return issues


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        VALIDATE_PHASE2_CLOSURE_REL,
        "\n".join(VALIDATOR_REQUIRED_MARKERS) + "\n",
    )
    write_text(root, VALIDATE_PHASE2_REL, "# phase2 validator stub\n")
    write_text(
        root,
        PHASE2_CLOSURE_REL,
        "\n".join(CLOSURE_REQUIRED_MARKERS) + "\n",
    )
    write_text(
        root,
        WORKFLOW_REL,
        "\n".join(WORKFLOW_REQUIRED_LINES.keys()) + "\n",
    )
    write_text(
        root,
        MAKEFILE_REL,
        "\n".join(MAKEFILE_REQUIRED_LINES.keys()) + "\n",
    )
    write_text(
        root,
        TOOLCHAIN_POLICY_REL,
        json.dumps(
            {
                "phase": "Phase 2",
                "upgrade_policy": {
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
        CROSS_FIXTURE_REL,
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": EXPECTED_FIXTURE_ROUTE,
                "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                "cross_targets": EXPECTED_CROSS_TARGETS,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root, CROSS_CHECKER_REL, "# direct cross checker stub\n")
    write_text(root, CROSS_ALIGNMENT_REL, "# cross alignment stub\n")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build_sample_root(root)
        cases_run = 0

        if collect_issues(root):
            raise SystemExit("phase2-cross-closure-validator-contract:self-test:sample_root")
        cases_run += 1

        validator_text = read_text(root / VALIDATE_PHASE2_CLOSURE_REL).replace(
            '"run: python3 scripts/zigux/check-phase2-cross.py",',
            "",
        )
        write_text(root, VALIDATE_PHASE2_CLOSURE_REL, validator_text)
        issues = collect_issues(root)
        expected = 'closure_validator:missing_marker:"run: python3 scripts/zigux/check-phase2-cross.py",'
        if expected not in issues:
            raise SystemExit("phase2-cross-closure-validator-contract:self-test:validator_marker")
        cases_run += 1

        build_sample_root(root)
        closure_text = read_text(root / PHASE2_CLOSURE_REL).replace(
            "`make -C zigux phase2-cross`",
            "",
        )
        write_text(root, PHASE2_CLOSURE_REL, closure_text)
        issues = collect_issues(root)
        if "closure_note:missing_marker:`make -C zigux phase2-cross`" not in issues:
            raise SystemExit("phase2-cross-closure-validator-contract:self-test:closure_marker")
        cases_run += 1

        build_sample_root(root)
        policy = load_json_object(root / TOOLCHAIN_POLICY_REL)
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]  # type: ignore[index]
        write_text(root, TOOLCHAIN_POLICY_REL, json.dumps(policy, indent=2) + "\n")
        issues = collect_issues(root)
        if not any(issue.startswith("toolchain_policy:required_make_routes=") for issue in issues):
            raise SystemExit("phase2-cross-closure-validator-contract:self-test:policy_routes")
        cases_run += 1

        build_sample_root(root)
        fixture = load_json_object(root / CROSS_FIXTURE_REL)
        fixture["cross_targets"][1]["target"] = "riscv64-linux"  # type: ignore[index]
        write_text(root, CROSS_FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")
        issues = collect_issues(root)
        if not any(issue.startswith("cross_fixture:cross_targets=") for issue in issues):
            raise SystemExit("phase2-cross-closure-validator-contract:self-test:fixture_targets")
        cases_run += 1

        build_sample_root(root)
        workflow_text = read_text(root / WORKFLOW_REL).replace(
            "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n",
            "",
        )
        write_text(root, WORKFLOW_REL, workflow_text)
        issues = collect_issues(root)
        expected = (
            "workflow:exact_count:run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py:"
            "count=0:expected=1"
        )
        if expected not in issues:
            raise SystemExit("phase2-cross-closure-validator-contract:self-test:workflow_line")
        cases_run += 1

        build_sample_root(root)
        (root / CROSS_FIXTURE_REL).unlink()
        (root / CROSS_FIXTURE_REL).mkdir(parents=True)
        issues = collect_issues(root)
        if f"required_path:not_file:{CROSS_FIXTURE_REL}" not in issues:
            raise SystemExit("phase2-cross-closure-validator-contract:self-test:fixture_directory")
        cases_run += 1

    if cases_run != SELF_TEST_CASE_COUNT:
        raise SystemExit(
            "phase2-cross-closure-validator-contract:self-test:case_count="
            f"{cases_run}:expected={SELF_TEST_CASE_COUNT}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0

    if args.self_test:
        run_self_test()
        print("PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT_SELF_TEST=pass")
        print(
            "PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT_SELF_TEST_CASE_COUNT="
            f"{SELF_TEST_CASE_COUNT}"
        )
        return 0

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT=pass")
    print(
        "PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT_REQUIRED_PATH_COUNT="
        f"{len(REQUIRED_PATHS)}"
    )
    print(
        "PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT_WORKFLOW_LINE_COUNT="
        f"{len(WORKFLOW_REQUIRED_LINES)}"
    )
    print(
        "PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT_CLOSURE_MARKER_COUNT="
        f"{len(CLOSURE_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT_VALIDATOR_MARKER_COUNT="
        f"{len(VALIDATOR_REQUIRED_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
