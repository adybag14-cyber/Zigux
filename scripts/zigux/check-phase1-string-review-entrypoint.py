#!/usr/bin/env python3
"""Run the Phase 1 string review checker with stable repo-root detection."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def checker_path(root: Path) -> Path:
    return root / CHECKER_REL


def run_checker(root: Path, passthrough: list[str]) -> subprocess.CompletedProcess[str]:
    checker = checker_path(root)
    return subprocess.run(
        [sys.executable, str(checker), "--root", str(root), *passthrough],
        capture_output=True,
        text=True,
        check=False,
    )


def write_file(root: Path, relative: Path, text: str) -> None:
    destination = root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_stub_checker(root: Path) -> None:
    write_file(
        root,
        CHECKER_REL,
        """#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--root")
parser.add_argument("--self-test", action="store_true")
args = parser.parse_args()

if args.self_test:
    print("STUB_STRING_REVIEW_SELF_TEST=pass")
    raise SystemExit(0)

expected = Path(__file__).resolve().parents[2]
actual = Path(args.root).resolve() if args.root else None
if actual != expected:
    print(f"stub-root-mismatch:expected={expected}:actual={actual}")
    raise SystemExit(1)

print("phase1-string-review-packet:ok")
""",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_entrypoint_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        wrapper_rel = Path("scripts/zigux/check-phase1-string-review-entrypoint.py")
        write_file(tmp_root, wrapper_rel, HERE.read_text(encoding="utf-8"))
        build_stub_checker(tmp_root)

        wrapper = tmp_root / wrapper_rel

        default_run = subprocess.run(
            [sys.executable, str(wrapper)],
            capture_output=True,
            text=True,
            check=False,
        )
        if default_run.returncode != 0:
            raise SystemExit(
                "phase1-string-review-entrypoint:self-test:default-root\n"
                + default_run.stdout
                + default_run.stderr
            )
        if "phase1-string-review-packet:ok" not in default_run.stdout:
            raise SystemExit("phase1-string-review-entrypoint:self-test:default-root-output")
        case_count += 1

        explicit_run = subprocess.run(
            [sys.executable, str(wrapper), "--root", str(tmp_root)],
            capture_output=True,
            text=True,
            check=False,
        )
        if explicit_run.returncode != 0:
            raise SystemExit(
                "phase1-string-review-entrypoint:self-test:explicit-root\n"
                + explicit_run.stdout
                + explicit_run.stderr
            )
        if "phase1-string-review-packet:ok" not in explicit_run.stdout:
            raise SystemExit("phase1-string-review-entrypoint:self-test:explicit-root-output")
        case_count += 1

        checker_self_test = run_checker(tmp_root, ["--self-test"])
        if checker_self_test.returncode != 0:
            raise SystemExit(
                "phase1-string-review-entrypoint:self-test:passthrough-self-test\n"
                + checker_self_test.stdout
                + checker_self_test.stderr
            )
        if "STUB_STRING_REVIEW_SELF_TEST=pass" not in checker_self_test.stdout:
            raise SystemExit("phase1-string-review-entrypoint:self-test:passthrough-self-test-output")
        case_count += 1

    print("PHASE1_STRING_REVIEW_ENTRYPOINT_SELF_TEST=pass")
    print(f"PHASE1_STRING_REVIEW_ENTRYPOINT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for invocation")
    parser.add_argument("--self-test", action="store_true", help="forward --self-test to the underlying checker")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = repo_root(args.root)
    checker = checker_path(root)
    if not checker.exists():
        print(f"missing_checker:{checker.as_posix()}")
        return 1

    result = run_checker(root, [])
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
