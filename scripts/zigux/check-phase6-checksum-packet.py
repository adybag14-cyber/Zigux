#!/usr/bin/env python3

"""Fail-closed Phase 6 checksum packet truthfulness checks."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


REQUIRED_PRESENT_FILE_PATHS = [
    "Documentation/zigux/phase6-checksum-slice.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
]

REQUIRED_ABSENT_FILE_PATHS = [
    "lib/checksum.zig",
    "zigux/tests/phase6_checksum.zig",
    "zigux/tests/phase6_checksum_c_parity.zig",
    "zigux/tests/phase6_checksum_perf.zig",
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
]

REQUIRED_SNIPPETS = {
    "Documentation/zigux/phase6-checksum-slice.md": [
        "`PHASE6_STATUS=blocked`",
        "current `master` lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "`zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`",
        "`tcpUdpV6Nofold`",
        "`replaceByDiff`",
        "documentary only until the checksum helper packet is restored or the shared packet routes are rewritten",
    ],
    "Documentation/zigux/phase6-helper-parity-catalog.md": [
        "`lib/checksum.c`",
        "helper expected by the shared packet: `lib/checksum.zig`",
        "current missing helper-local packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, and `zigux/tests/fixtures/phase6_checksum_c_harness.c`",
        "current review posture: blocked;",
    ],
    "Documentation/zigux/phase6-perf-gate-survey.md": [
        "current `master` lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "`64B` at `iterations = 200_000`",
        "`1501B` at `iterations = 12_000`",
        "no longer a fully truthful summary of shared perf posture on `master`",
    ],
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def validate(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for relative_path in REQUIRED_PRESENT_FILE_PATHS:
        if not (repo_root / relative_path).is_file():
            missing.append(f"missing required file: {relative_path}")
    for relative_path in REQUIRED_ABSENT_FILE_PATHS:
        if (repo_root / relative_path).exists():
            missing.append(f"unexpected present file: {relative_path}")
    for relative_path, snippets in REQUIRED_SNIPPETS.items():
        try:
            text = read_text(repo_root / relative_path)
        except ValidationError as exc:
            missing.append(str(exc))
            continue
        for snippet in snippets:
            if snippet not in text:
                missing.append(f"{relative_path}: {snippet}")
    return missing


def write_fixture(root: Path) -> None:
    for relative_path in REQUIRED_PRESENT_FILE_PATHS:
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("// fixture marker\n", encoding="utf-8")
    for relative_path, snippets in REQUIRED_SNIPPETS.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(snippets) + "\n", encoding="utf-8")


def expect_failure(repo_root: Path, needle: str) -> None:
    missing = validate(repo_root)
    if needle not in missing:
        raise ValidationError(f"expected self-test failure for {needle!r}, got {missing!r}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_fixture(root)

        missing = validate(root)
        if missing:
            raise ValidationError(f"self-test positive case failed: {missing!r}")

        slice_path = root / "Documentation/zigux/phase6-checksum-slice.md"
        slice_text = slice_path.read_text(encoding="utf-8")
        removed = "`PHASE6_STATUS=blocked`"
        slice_path.write_text(slice_text.replace(removed, "", 1), encoding="utf-8")
        expect_failure(root, f"Documentation/zigux/phase6-checksum-slice.md: {removed}")

        helper_path = root / "lib/checksum.zig"
        helper_path.parent.mkdir(parents=True, exist_ok=True)
        helper_path.write_text("// unexpectedly restored helper marker\n", encoding="utf-8")
        expect_failure(root, "unexpected present file: lib/checksum.zig")

        print("PHASE6_CHECKSUM_PACKET_SELF_TEST=pass")
        print(
            "PHASE6_CHECKSUM_PACKET_REQUIRED_FILE_COUNT=%d"
            % (len(REQUIRED_PRESENT_FILE_PATHS) + len(REQUIRED_ABSENT_FILE_PATHS) + len(REQUIRED_SNIPPETS))
        )
        print(
            "PHASE6_CHECKSUM_PACKET_REQUIRED_SNIPPET_COUNT=%d"
            % sum(len(snippets) for snippets in REQUIRED_SNIPPETS.values())
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker tests")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = validate(Path(args.repo_root).resolve())
    if missing:
        print("PHASE6_CHECKSUM_PACKET=fail")
        print("MISSING_PHASE6_CHECKSUM_PACKET_MARKERS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE6_CHECKSUM_PACKET_MARKERS_END")
        return 1

    print("PHASE6_CHECKSUM_PACKET=pass")
    print(
        "PHASE6_CHECKSUM_PACKET_REQUIRED_FILE_COUNT=%d"
        % (len(REQUIRED_PRESENT_FILE_PATHS) + len(REQUIRED_ABSENT_FILE_PATHS) + len(REQUIRED_SNIPPETS))
    )
    print(
        "PHASE6_CHECKSUM_PACKET_REQUIRED_SNIPPET_COUNT=%d"
        % sum(len(snippets) for snippets in REQUIRED_SNIPPETS.values())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
