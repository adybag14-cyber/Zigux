#!/usr/bin/env python3
"""Validate the current Phase 6 Linux-style Make route posture."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_PRESENT_TARGETS = {
    "phase6-bsearch-test": (
        "$(ZIG) build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
    ),
    "phase6-hexdump-test": (
        "$(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
    ),
    "phase6-hexdump-review": (
        "$(PYTHON) scripts/zigux/check-phase6-hexdump-packet.py",
        "$(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
        "$(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    ),
    "phase6-hexdump-perf": (
        "$(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    ),
    "phase6-checksum-perf": (
        "$(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    ),
}

EXPECTED_ABSENT_TARGETS = (
    "phase6-validate",
    "phase6-test",
    "phase6-base64-c-parity",
    "phase6-checksum-c-parity",
    "phase6-base64-perf",
    "phase6-perf",
    "phase6",
)

EXPECTED_PHONY_MARKER = (
    "PHONY += phase6-validate phase6-test phase6-bsearch-test "
    "phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test "
    "phase6-hexdump-review phase6-base64-perf phase6-checksum-perf "
    "phase6-hexdump-perf phase6-perf phase6"
)


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc


def parse_target_bodies(text: str) -> dict[str, list[str]]:
    targets: dict[str, list[str]] = {}
    current_target: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue

        if not raw_line.startswith(("\t", " ")):
            if ":" in line and not line.startswith("#"):
                candidate = line.split(":", 1)[0].strip()
                if candidate and " " not in candidate and "=" not in candidate and "$(" not in candidate:
                    current_target = candidate
                    targets.setdefault(current_target, [])
                    continue
            current_target = None
            continue

        if current_target is None:
            continue

        if raw_line.startswith("\t"):
            targets[current_target].append(line.strip())

    return targets


def run_checks(repo_root: Path) -> None:
    makefile_text = read_text(repo_root / MAKEFILE_PATH)
    if EXPECTED_PHONY_MARKER not in makefile_text:
        raise ValidationError(f"missing Phase 6 phony marker in {MAKEFILE_PATH}")

    target_bodies = parse_target_bodies(makefile_text)

    for target, expected_commands in EXPECTED_PRESENT_TARGETS.items():
        body = target_bodies.get(target)
        if not body:
            raise ValidationError(f"missing Phase 6 target body: {target}")
        for command in expected_commands:
            if not any(command in line for line in body):
                raise ValidationError(
                    f"missing Phase 6 command in {MAKEFILE_PATH}: {target} -> {command}"
                )

    for target in EXPECTED_ABSENT_TARGETS:
        body = target_bodies.get(target, [])
        if body:
            raise ValidationError(
                f"unexpected Phase 6 target body present in {MAKEFILE_PATH}: {target}"
            )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    makefile = "\n".join(
        [
            EXPECTED_PHONY_MARKER,
            "",
            "phase6-bsearch-test:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
            "",
            "phase6-hexdump-test:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
            "",
            "phase6-hexdump-review:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-hexdump-packet.py",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
            "",
            "phase6-hexdump-perf:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
            "",
            "phase6-checksum-perf:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
            "",
        ]
    )
    write(root / MAKEFILE_PATH, makefile + "\n")


def assert_failure(root: Path, old: str, new: str) -> None:
    path = root / MAKEFILE_PATH
    original = path.read_text(encoding="utf-8")
    if old not in original:
        raise AssertionError(f"self-test marker not found: {old}")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        run_checks(root)
    except ValidationError:
        pass
    else:
        raise AssertionError(f"expected validation failure for replacement: {old}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        run_checks(root)

        assert_failure(
            root,
            "phase6-checksum-perf:",
            "phase6-checksum-perf-missing:",
        )
        assert_failure(
            root,
            "$(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
            "$(ZIG) build phase6-checksum-perf-missing --build-file zigux/tests/phase6_build.zig",
        )
        assert_failure(
            root,
            "phase6-hexdump-review:",
            "phase6-hexdump-review-missing:",
        )
        assert_failure(
            root,
            "phase6-hexdump-perf:",
            "phase6-hexdump-perf-missing:",
        )
        assert_failure(
            root,
            "phase6-bsearch-test:",
            "phase6-bsearch-test-missing:",
        )

        path = root / MAKEFILE_PATH
        original = path.read_text(encoding="utf-8")
        path.write_text(
            original + "\nphase6-base64-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig\n",
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "unexpected Phase 6 target body present" not in str(exc):
                raise AssertionError(f"unexpected failure: {exc}") from exc
        else:
            raise AssertionError("expected unexpected-target-body failure")

    print("PHASE6_MAKE_ROUTE_TRUTHFULNESS_SELF_TEST=pass")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    run_checks(Path(args.repo_root).resolve())
    print("Phase 6 Make route posture matches the committed shared packet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
