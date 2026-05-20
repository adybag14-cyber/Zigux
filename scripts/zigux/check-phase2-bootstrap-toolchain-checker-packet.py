#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
TOOLCHAIN_CHECKER = Path("scripts/zigux/check-zig-toolchain.py")
POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
NEXT_STEP = "Self-test current Lane 05 local-first archive checker"

REQUIRED_STEPS = [
    ("Compile current scripts", 'run: |'),
    ("Self-test current Zig toolchain checker", "run: python3 scripts/zigux/check-zig-toolchain.py --self-test"),
    ("Check current Zig toolchain policy packet", "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only"),
    (
        "Check current pinned Zig archive packet",
        "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    ),
    (NEXT_STEP, "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test"),
]

REQUIRED_CHECKER_MARKERS = [
    'parser.add_argument("--policy-only", action="store_true"',
    'parser.add_argument("--archive-only", action="store_true"',
    'parser.add_argument("--allow-missing", action="store_true"',
    'parser.add_argument("--archive", help="Explicit Zig archive path for archive-integrity validation.")',
    'parser.add_argument("--archive-target", help="Archive target key from scripts/zigux/zig-toolchain-policy.json.")',
    'parser.add_argument("--self-test", action="store_true"',
    'print("ZIG_TOOLCHAIN_POLICY_STATUS=present")',
    'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")',
]


def normalized_lines(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines()]


def count_line(lines: list[str], needle: str) -> int:
    return sum(1 for line in lines if line.strip() == needle)


def find_line(lines: list[str], needle: str) -> int:
    for index, line in enumerate(lines):
        if line.strip() == needle:
            return index
    return -1


def require_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path in [WORKFLOW, TOOLCHAIN_CHECKER, POLICY]:
        if not (root / rel_path).is_file():
            missing.append(str(rel_path))
    return missing


def validate_workflow(text: str) -> list[str]:
    issues: list[str] = []
    lines = normalized_lines(text)

    step_positions: list[int] = []
    for step_name, run_line in REQUIRED_STEPS:
        step_line = f"- name: {step_name}"
        step_count = count_line(lines, step_line)
        if step_count != 1:
            issues.append(f"workflow:step_count:{step_name}:{step_count}")
        run_count = count_line(lines, run_line)
        if run_count != 1:
            issues.append(f"workflow:run_count:{step_name}:{run_count}")
        step_positions.append(find_line(lines, step_line))

    if all(position != -1 for position in step_positions):
        if step_positions != sorted(step_positions):
            issues.append("workflow:toolchain_packet_order:out_of_order")
    else:
        issues.append("workflow:toolchain_packet_order:missing_boundary")

    return issues


def validate_checker(text: str) -> list[str]:
    issues: list[str] = []
    for marker in REQUIRED_CHECKER_MARKERS:
        if marker not in text:
            issues.append(f"checker:missing_marker:{marker}")
    return issues


def validate_policy(text: str) -> list[str]:
    issues: list[str] = []
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"policy:json_error:{exc.msg}"]

    if payload.get("channel") != payload.get("minimum_version"):
        issues.append("policy:channel_minimum_version:not_lockstep")

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append("policy:archive_sha256:not_object")
    elif sorted(archive_sha256.keys()) != ["x86_64-linux"]:
        issues.append("policy:archive_targets:unexpected")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append("policy:upgrade_policy:not_object")
    else:
        if upgrade_policy.get("archive_target_scope") != ["x86_64-linux"]:
            issues.append("policy:archive_target_scope:unexpected")
        if upgrade_policy.get("required_make_routes") != ["phase2-toolchain", "phase2-validate"]:
            issues.append("policy:required_make_routes:unexpected")

    return issues


def validate_root(root: Path) -> list[str]:
    issues = [f"missing:{path}" for path in require_files(root)]
    if issues:
        return issues

    workflow_text = (root / WORKFLOW).read_text(encoding="utf-8")
    checker_text = (root / TOOLCHAIN_CHECKER).read_text(encoding="utf-8")
    policy_text = (root / POLICY).read_text(encoding="utf-8")

    issues.extend(validate_workflow(workflow_text))
    issues.extend(validate_checker(checker_text))
    issues.extend(validate_policy(policy_text))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    workflow_text = """name: zigux-bootstrap

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Compile current scripts
        run: |
          set -euxo pipefail
          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
          if [ \"${#scripts[@]}\" -eq 0 ]; then
            echo 'no Python scripts found under scripts/zigux' >&2
            exit 1
          fi
          python3 -m py_compile \"${scripts[@]}\"

      - name: Self-test current Zig toolchain checker
        run: python3 scripts/zigux/check-zig-toolchain.py --self-test

      - name: Check current Zig toolchain policy packet
        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only

      - name: Check current pinned Zig archive packet
        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing

      - name: Self-test current Lane 05 local-first archive checker
        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test
"""
    checker_text = """#!/usr/bin/env python3
import argparse

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy-only", action="store_true", help="policy only")
    parser.add_argument("--archive-only", action="store_true", help="archive only")
    parser.add_argument("--allow-missing", action="store_true", help="allow missing")
    parser.add_argument("--archive", help="Explicit Zig archive path for archive-integrity validation.")
    parser.add_argument("--archive-target", help="Archive target key from scripts/zigux/zig-toolchain-policy.json.")
    parser.add_argument("--self-test", action="store_true", help="self-test")
    print("ZIG_TOOLCHAIN_POLICY_STATUS=present")
    print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
"""
    policy_text = """{
  "phase": "Phase 2",
  "channel": "0.17.0-dev.87+9b177a7d2",
  "minimum_version": "0.17.0-dev.87+9b177a7d2",
  "archive_sha256": {
    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
  },
  "upgrade_policy": {
    "channel_minimum_lockstep": true,
    "archive_target_scope": [
      "x86_64-linux"
    ],
    "required_make_routes": [
      "phase2-toolchain",
      "phase2-validate"
    ]
  }
}
"""
    write_text(root / WORKFLOW, workflow_text)
    write_text(root / TOOLCHAIN_CHECKER, checker_text)
    write_text(root / POLICY, policy_text)


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase2_bootstrap_toolchain_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert validate_root(root) == []
        case_count += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\n",
                "",
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert "workflow:run_count:Check current Zig toolchain policy packet:0" in issues
        case_count += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\n",
                "run: python3 scripts/zigux/check-zig-toolchain.py --allow-missing --archive-only\n",
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert "workflow:run_count:Check current pinned Zig archive packet:0" in issues
        case_count += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "      - name: Check current pinned Zig archive packet\n"
                "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\n\n"
                "      - name: Self-test current Lane 05 local-first archive checker\n",
                "      - name: Self-test current Lane 05 local-first archive checker\n"
                "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test\n\n"
                "      - name: Check current pinned Zig archive packet\n"
                "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\n\n",
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert "workflow:toolchain_packet_order:out_of_order" in issues
        case_count += 1

        build_sample_root(root)
        checker_path = root / TOOLCHAIN_CHECKER
        checker_path.write_text(
            checker_path.read_text(encoding="utf-8").replace(
                'parser.add_argument(\"--archive-only\", action=\"store_true\", help=\"archive only\")\n',
                "",
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert any(issue.startswith("checker:missing_marker:parser.add_argument(\"--archive-only\"") for issue in issues)
        case_count += 1

        build_sample_root(root)
        checker_path = root / TOOLCHAIN_CHECKER
        checker_path.write_text(
            checker_path.read_text(encoding="utf-8").replace(
                'parser.add_argument(\"--allow-missing\", action=\"store_true\", help=\"allow missing\")\n',
                "",
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert any(issue.startswith("checker:missing_marker:parser.add_argument(\"--allow-missing\"") for issue in issues)
        case_count += 1

        build_sample_root(root)
        policy_path = root / POLICY
        policy_text = json.loads(policy_path.read_text(encoding="utf-8"))
        policy_text["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        policy_path.write_text(json.dumps(policy_text, indent=2) + "\n", encoding="utf-8")
        issues = validate_root(root)
        assert "policy:required_make_routes:unexpected" in issues
        case_count += 1

        build_sample_root(root)
        (root / POLICY).unlink()
        issues = validate_root(root)
        assert "missing:scripts/zigux/zig-toolchain-policy.json" in issues
        case_count += 1

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Lane 03 bootstrap workflow toolchain-checker packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the current checkout root.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for replay coverage.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = validate_root(args.root)
    if issues:
        print("PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET=fail")
        for issue in issues:
            print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_ISSUE={issue}")
        return 1

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_REQUIRED_STEP_COUNT={len(REQUIRED_STEPS)}")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_REQUIRED_CHECKER_MARKER_COUNT={len(REQUIRED_CHECKER_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
