#!/usr/bin/env python3
"""Guard Phase 4 atomic64 wrapper rollback evidence.

This checker intentionally stays narrower than the shared Phase 4 gate-evidence
checker.  It verifies that the roadmap-targeted wrapper file remains present,
that the gate-evidence note pins its current Git blob, and that the wrapper still
contains the local source-inventory and shared gate-evidence guard tests that
make rollback reviewable.
"""

from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-gate-evidence.md")
ATOMIC64_DIFF = Path("zigux/tests/atomic64_diff.zig")

PIN_LABEL = "PHASE4_ATOMIC64_DIFF_BLOB_SHA"
REQUIRED_NOTE_MARKERS = (
    "# Phase 4 Gate Evidence",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true",
    "phase4-runtime-atomic64-diff-survey-tests",
    "make -C zigux phase4-runtime-atomic64-diff-survey",
)
REQUIRED_WRAPPER_MARKERS = (
    "test \"atomic64 diff wrapper keeps the shared gate-evidence packet explicit\" {",
    "test \"atomic64 diff wrapper keeps its own source inventory explicit\" {",
    "PHASE4_ATOMIC64_DIFF_BLOB_SHA={s}",
    "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA={s}",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def note_values(text: str, label: str) -> list[str]:
    needle = f"`{label}="
    values: list[str] = []
    cursor = 0
    while True:
        start = text.find(needle, cursor)
        if start == -1:
            return values
        value_start = start + len(needle)
        value_end = text.find("`", value_start)
        if value_end == -1:
            return values
        values.append(text[value_start:value_end])
        cursor = value_end + 1


def validate_root(root: Path) -> list[str]:
    failures: list[str] = []
    note_path = root / NOTE
    wrapper_path = root / ATOMIC64_DIFF

    if not note_path.is_file():
        failures.append(f"missing:{NOTE.as_posix()}")
    if not wrapper_path.is_file():
        failures.append(f"missing:{ATOMIC64_DIFF.as_posix()}")
    if failures:
        return failures

    note = read_text(note_path)
    wrapper = read_text(wrapper_path)

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"note:missing:{marker}")
    for marker in REQUIRED_WRAPPER_MARKERS:
        if marker not in wrapper:
            failures.append(f"wrapper:missing:{marker}")

    pins = note_values(note, PIN_LABEL)
    if len(pins) != 1:
        failures.append(f"note:{PIN_LABEL}:count={len(pins)}")
    else:
        expected = git_blob_sha(wrapper_path)
        if pins[0] != expected:
            failures.append(f"note:{PIN_LABEL}:expected={expected}:actual={pins[0]}")

    return failures


def build_fixture(root: Path) -> None:
    wrapper = "\n".join(REQUIRED_WRAPPER_MARKERS) + "\n"
    write_text(root / ATOMIC64_DIFF, wrapper)
    note = "\n".join((
        "# Phase 4 Gate Evidence",
        "",
        "## Status",
        f"  * `{PIN_LABEL}={git_blob_sha(root / ATOMIC64_DIFF)}`",
        "  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
        "",
        "## Exact Readback Evidence",
        "  * The runtime atomic64 handoff remains reviewable through `phase4-runtime-atomic64-diff-survey-tests` and `make -C zigux phase4-runtime-atomic64-diff-survey`.",
        "",
    ))
    write_text(root / NOTE, note)


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-atomic64-wrapper-evidence-") as tmp:
        root = Path(tmp)
        build_fixture(root)
        baseline = validate_root(root)
        if baseline:
            raise AssertionError(f"baseline failed: {baseline}")
        cases += 1

        build_fixture(root)
        (root / ATOMIC64_DIFF).unlink()
        failures = validate_root(root)
        if not any(failure == f"missing:{ATOMIC64_DIFF.as_posix()}" for failure in failures):
            raise AssertionError(f"missing wrapper not detected: {failures}")
        cases += 1

        build_fixture(root)
        write_text(root / NOTE, read_text(root / NOTE).replace(note_values(read_text(root / NOTE), PIN_LABEL)[0], "0" * 40, 1))
        failures = validate_root(root)
        if not any(failure.startswith(f"note:{PIN_LABEL}:expected=") for failure in failures):
            raise AssertionError(f"stale wrapper blob pin not detected: {failures}")
        cases += 1

        build_fixture(root)
        write_text(
            root / ATOMIC64_DIFF,
            read_text(root / ATOMIC64_DIFF).replace(REQUIRED_WRAPPER_MARKERS[0], "", 1),
        )
        failures = validate_root(root)
        if not any(failure.startswith("wrapper:missing:") for failure in failures):
            raise AssertionError(f"wrapper guard marker loss not detected: {failures}")
        cases += 1

    print(f"phase4 atomic64 wrapper evidence self-test: PASS ({cases} cases)")


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    failures = validate_root(Path(args.root).resolve())
    if failures:
        for failure in failures:
            print(f"phase4 atomic64 wrapper evidence check failed: {failure}")
        return 1
    print("phase4 atomic64 wrapper evidence check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
