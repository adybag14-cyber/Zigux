#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 base64 wrapper-gap packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


BASE64_SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
MAKEFILE_PATH = Path("zigux/Makefile")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")

REQUIRED_SLICE_SNIPPETS = [
    "- direct focused perf route: `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`",
    "- current wrapper nuance: the helper-owned perf gate is directly runnable through `zigux/tests/phase6_build.zig`, but the Linux-style `make -C zigux phase6-base64-perf` name still lives only in shared route inventory surfaces because current `zigux/Makefile` does not yet expose a committed target body",
    "The next honest same-lane reopen is therefore narrower and adjacent to the helper-owned perf gate: either restore a committed `phase6-base64-perf` target body in `zigux/Makefile` or update the remaining shared route-inventory surfaces so they stop presenting that Linux-style wrapper as runnable current-`master` evidence before it exists.",
]

REQUIRED_SURVEY_SNIPPETS = [
    "* shared replay note: the current Phase 6 route inventory still names `make -C zigux phase6`, `make -C zigux phase6-base64-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`, while current `zigux/Makefile` readback now also exposes committed target bodies for `phase6-bsearch-test`, `phase6-hexdump-test`, `phase6-hexdump-review`, and `phase6-hexdump-perf`; the aggregate `phase6`, `phase6-validate`, `phase6-perf`, and `phase6-base64-perf` names still remain inventory-only wrapper markers in the committed file text available to this survey, while `phase6-checksum-perf` now has a committed Linux-style target body",
    "* base64 shared posture: `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig` are directly readable on current `master`, and current `zigux/tests/phase6_build.zig` defines the dedicated `phase6-base64-perf` build step again; that slowdown gate is directly reviewable from the committed tree even though the broader `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` readbacks still expose the wrapper name only through shared route inventory surfaces",
    "* makefile route nuance: current `zigux/Makefile` readback does expose committed target bodies for `phase6-bsearch-test`, `phase6-hexdump-test`, `phase6-hexdump-review`, and `phase6-hexdump-perf`, so the inventory-only wrapper caveat now applies specifically to `phase6`, `phase6-validate`, `phase6-perf`, and `phase6-base64-perf` rather than to every Phase 6 route name in the file",
]

REQUIRED_MAKEFILE_SNIPPETS = [
    "PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6",
    "phase6-checksum-perf:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "phase6-hexdump-perf:",
]

REQUIRED_BUILD_SNIPPET = 'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");'
REQUIRED_BLOCKED_ROUTE = "make -C zigux phase6-base64-perf"
FORBIDDEN_MAKEFILE_TARGET = "phase6-base64-perf:"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected marker in {path}: {snippet}")


def validate_manifest(path: Path) -> None:
    manifest = read_json(path)
    if not isinstance(manifest, dict):
        raise ValidationError(f"expected object in {path}")

    note = manifest.get("shared_route_truthfulness_note")
    if not isinstance(note, str) or "phase6-base64-perf" not in note or "wrapper names without committed target bodies" not in note:
        raise ValidationError(f"unexpected shared_route_truthfulness_note in {path}")

    blocked = manifest.get("inventory_only_blocked_routes")
    if not isinstance(blocked, list) or REQUIRED_BLOCKED_ROUTE not in blocked:
        raise ValidationError(f"missing blocked base64 perf route in {path}")


def validate_repo(root: Path) -> None:
    require_snippets(root / BASE64_SLICE_PATH, REQUIRED_SLICE_SNIPPETS)
    require_snippets(root / SURVEY_PATH, REQUIRED_SURVEY_SNIPPETS)
    require_snippets(root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)

    build_text = read_text(root / BUILD_PATH)
    if REQUIRED_BUILD_SNIPPET not in build_text:
        raise ValidationError(f"missing expected marker in {BUILD_PATH}: {REQUIRED_BUILD_SNIPPET}")

    makefile_text = read_text(root / MAKEFILE_PATH)
    if FORBIDDEN_MAKEFILE_TARGET in makefile_text:
        raise ValidationError(f"unexpected committed base64 perf target body in {MAKEFILE_PATH}: {FORBIDDEN_MAKEFILE_TARGET}")

    validate_manifest(root / MANIFEST_PATH)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / BASE64_SLICE_PATH, "\n".join(REQUIRED_SLICE_SNIPPETS) + "\n")
    write(root / SURVEY_PATH, "\n".join(REQUIRED_SURVEY_SNIPPETS) + "\n")
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    write(root / BUILD_PATH, REQUIRED_BUILD_SNIPPET + "\n")
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "shared_route_truthfulness_note": "base64, bsearch, checksum, and hexdump now keep committed helper-local or direct review surfaces on current `master`, while the Linux-style `zigux/Makefile` inventory still advertises `phase6-base64-perf` and other wrapper names without committed target bodies.",
                "inventory_only_blocked_routes": [REQUIRED_BLOCKED_ROUTE],
            },
            indent=2,
        )
        + "\n",
    )


def assert_failure(root: Path, rel_path: Path, old: str, new: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    if old not in original:
        raise AssertionError(f"self-test marker not found in {rel_path}: {old}")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        validate_repo(root)
    except ValidationError as exc:
        if rel_path.as_posix() not in str(exc):
            raise AssertionError(f"unexpected failure for {rel_path}: {exc}") from exc
    else:
        raise AssertionError(f"expected failure for {rel_path}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate_repo(root)
        assert_failure(
            root,
            BASE64_SLICE_PATH,
            "phase6-base64-perf` name still lives only in shared route inventory surfaces",
            "phase6-base64-perf` name now reruns through a committed target body",
        )
        assert_failure(
            root,
            SURVEY_PATH,
            "phase6-base64-perf` names still remain inventory-only wrapper markers",
            "phase6-base64-perf` now reruns through a committed target body",
        )
        assert_failure(
            root,
            BUILD_PATH,
            'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");',
            'const base64_perf_step = b.step("phase6-base64-perf-missing", "Run Phase 6 base64 perf gate");',
        )
        assert_failure(
            root,
            MANIFEST_PATH,
            REQUIRED_BLOCKED_ROUTE,
            "make -C zigux phase6-checksum-perf",
        )
        assert_failure(
            root,
            MAKEFILE_PATH,
            "phase6-hexdump-perf:",
            "phase6-base64-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig\nphase6-hexdump-perf:",
        )
    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    validate_repo(Path(args.repo_root).resolve())
    print("Phase 6 base64 wrapper-gap markers look aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
