#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")
EXPECTED_LINES = (
    "# zigux-alpha",
    "`zigux-alpha` is the Zigux bootstrap workspace.",
    "Rules",
)


def check_identity_packet(root: Path) -> list[str]:
    lines = (root / README_PATH).read_text(encoding="utf-8").splitlines()

    try:
        heading_index = lines.index(EXPECTED_LINES[0])
    except ValueError:
        return [f"missing line: {EXPECTED_LINES[0]}"]

    try:
        summary_index = lines.index(EXPECTED_LINES[1])
    except ValueError:
        return [f"missing line: {EXPECTED_LINES[1]}"]

    try:
        rules_index = lines.index(EXPECTED_LINES[2])
    except ValueError:
        return [f"missing line: {EXPECTED_LINES[2]}"]

    if not (heading_index < summary_index < rules_index):
        return [
            "identity packet order mismatch",
            f"heading_index={heading_index}",
            f"summary_index={summary_index}",
            f"rules_index={rules_index}",
        ]

    return []


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# zigux-alpha

`zigux-alpha` is the Zigux bootstrap workspace.

It exists to hold:
- program-level planning

Rules
- Keep product planning and bootstrap artifacts here first.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_identity_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())

        errors = check_identity_packet(root)
        if errors:
            raise AssertionError(f"baseline identity fixture should pass: {errors}")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("# zigux-alpha\n", "", 1))
        errors = check_identity_packet(root)
        if errors != ["missing line: # zigux-alpha"]:
            raise AssertionError(f"unexpected heading error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "`zigux-alpha` is the Zigux bootstrap workspace.\n", "", 1
            ),
        )
        errors = check_identity_packet(root)
        if errors != ["missing line: `zigux-alpha` is the Zigux bootstrap workspace."]:
            raise AssertionError(f"unexpected summary error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Rules\n", "Guidelines\n", 1))
        errors = check_identity_packet(root)
        if errors != ["missing line: Rules"]:
            raise AssertionError(f"unexpected rules error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "`zigux-alpha` is the Zigux bootstrap workspace.\n\nIt exists to hold:\n- program-level planning\n\nRules\n",
                "It exists to hold:\n- program-level planning\n\nRules\n`zigux-alpha` is the Zigux bootstrap workspace.\n",
                1,
            ),
        )
        errors = check_identity_packet(root)
        if not errors or errors[0] != "identity packet order mismatch":
            raise AssertionError(f"unexpected order error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "`zigux-alpha` is the Zigux bootstrap workspace.\n\nIt exists to hold:\n- program-level planning\n\nRules\n",
                "Rules\n`zigux-alpha` is the Zigux bootstrap workspace.\n\nIt exists to hold:\n- program-level planning\n\n",
                1,
            ),
        )
        errors = check_identity_packet(root)
        if not errors or errors[0] != "identity packet order mismatch":
            raise AssertionError(f"unexpected late-rules error: {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_README_IDENTITY_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_README_IDENTITY_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 bootstrap README identity packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check_identity_packet(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Lane 01 bootstrap README identity check passed.")
    print(f"LANE01_BOOTSTRAP_README_IDENTITY_REQUIRED_LINE_COUNT={len(EXPECTED_LINES)}")
    print("LANE01_BOOTSTRAP_README_IDENTITY_SECTION_ORDER=Heading->Summary->Rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
