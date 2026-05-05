#!/usr/bin/env python3
"""Fail-closed Phase 6 shared-surface checks for the leaf-helper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


REQUIRED_SNIPPETS = {
    "Documentation/zigux/README.md": [
        "- `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase6-validate`, `make -C zigux phase6`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf` now keep the current base64, bsearch, checksum, and hexdump helper bundle reviewable",
    ],
    "scripts/zigux/README.md": [
        "- the current shared Phase 6 review surface on `master` is the four slice notes (`Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, and `Documentation/zigux/phase6-hexdump-slice.md`) plus `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
        "- `make -C zigux phase6-validate` keeps the shared Phase 6 surface checker wired through the Zigux convenience target.",
        "- `zig build test --build-file zigux/tests/phase6_build.zig` is the bundled helper replay for the current `base64`, `bsearch`, `checksum`, and `hexdump` packet.",
        "- `make -C zigux phase6` keeps that same shared-surface check plus bundled helper replay wired through the Zigux convenience target.",
        "- there is no separate shared `validate-phase6.py`, external portability checker packet beyond `check-phase6-shared-surface.py`, or aggregated `phase6-perf` target on `master`; the shipped dedicated perf replays are `make -C zigux phase6-checksum-perf` and `make -C zigux phase6-hexdump-perf`, which keep the checksum slowdown ceiling and the formatter-sensitive hexdump fixture packet wired into Linux-style entrypoints without overstating perf coverage for the rest of the Phase 6 helper packet.",
    ],
    "Documentation/zigux/review-checklist.md": [
        "  * if the change touches the shared Phase 6 leaf-helper packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-hexdump-slice.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase6-validate`, `make -C zigux phase6`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf` still agree on the same bundled `base64`, `bsearch`, `checksum`, and `hexdump` helper packet without implying a removed shared `validate-phase6.py`, a broader external parity checker beyond `check-phase6-shared-surface.py`, or an aggregated `phase6-perf` route?",
    ],
    "zigux/tests/README.md": [
        "  * `zigux/tests/phase6_hexdump_perf.zig`",
        "  * keep the shared Phase 6 leaf-helper packet wired through `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, including `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, and `zigux/tests/phase6_hexdump.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase6-validate`, and `make -C zigux phase6`, so the landed `base64`, `bsearch`, `checksum`, and `hexdump` bundle stays reviewable through one bounded helper gate, and keep `zigux/tests/phase6_checksum_perf.zig` plus `make -C zigux phase6-checksum-perf` and `zigux/tests/phase6_hexdump_perf.zig` plus `make -C zigux phase6-hexdump-perf` explicit as the dedicated checksum and hexdump perf routes rather than implying a broader Phase 6 packet-wide perf target",
    ],
    "zigux/tests/phase6_build.zig": [
        'const test_step = b.step("test", "Run Phase 6 leaf helper tests");',
        '.name = "phase6-base64-tests"',
        '.name = "phase6-bsearch-tests"',
        '.name = "phase6-checksum-tests"',
        '.name = "phase6-hexdump-tests"',
    ],
    "zigux/Makefile": [
        "PHONY += phase6-validate phase6-test phase6-checksum-perf phase6-hexdump-perf phase6",
        "phase6-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py",
        "phase6-checksum-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6-hexdump-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6: phase6-validate phase6-test",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "- name: Self-test Phase 6 shared-surface checker\n        run: python3 scripts/zigux/check-phase6-shared-surface.py --self-test",
        "- name: Check Phase 6 shared surface\n        run: python3 scripts/zigux/check-phase6-shared-surface.py",
        "- name: Run Phase 6 leaf helper tests\n        run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
        "- name: Run Phase 6 checksum perf gate\n        run: zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "- name: Run Phase 6 hexdump perf gate\n        run: zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
    ],
}

REMOVED_PATHS = [
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/validate-phase6.py",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc


def run_checks(repo_root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(repo_root / rel_path)
        for snippet in snippets:
            if snippet not in content:
                raise ValidationError(
                    f"missing expected Phase 6 marker in {rel_path}: {snippet}"
                )

    for rel_path in REMOVED_PATHS:
        if (repo_root / rel_path).exists():
            raise ValidationError(
                f"removed Phase 6 shared-surface file unexpectedly present: {rel_path}"
            )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        for rel_path, snippets in REQUIRED_SNIPPETS.items():
            write(root / rel_path, "\n".join(snippets) + "\n")

        run_checks(root)

        removed_path = root / REMOVED_PATHS[0]
        write(removed_path, "stale\n")
        try:
            run_checks(root)
        except ValidationError as exc:
            if REMOVED_PATHS[0] not in str(exc):
                raise AssertionError(f"unexpected removed-path failure: {exc}") from exc
        else:
            raise AssertionError("expected removed-path failure")
        removed_path.unlink()

        scripts_readme = root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme.read_text(encoding="utf-8")
        scripts_readme.write_text(
            original_scripts_readme.replace(
                "phase6-checksum-perf",
                "phase6-checksum-bench",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "scripts/zigux/README.md" not in str(exc):
                raise AssertionError(f"unexpected scripts README failure: {exc}") from exc
        else:
            raise AssertionError("expected scripts README failure")
        scripts_readme.write_text(original_scripts_readme, encoding="utf-8")

        docs_readme = root / "Documentation/zigux/README.md"
        original_docs_readme = docs_readme.read_text(encoding="utf-8")
        docs_readme.write_text(
            original_docs_readme.replace(
                "phase6-hexdump-perf",
                "phase6-hexdump-bench",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "Documentation/zigux/README.md" not in str(exc):
                raise AssertionError(f"unexpected docs README failure: {exc}") from exc
        else:
            raise AssertionError("expected docs README failure")
        docs_readme.write_text(original_docs_readme, encoding="utf-8")

        workflow = root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow.read_text(encoding="utf-8")
        workflow.write_text(
            original_workflow.replace(
                "Run Phase 6 hexdump perf gate",
                "Run Phase 6 hexdump replay gate",
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if ".github/workflows/zigux-bootstrap.yml" not in str(exc):
                raise AssertionError(f"unexpected workflow failure: {exc}") from exc
        else:
            raise AssertionError("expected workflow failure")
        workflow.write_text(original_workflow, encoding="utf-8")

        makefile = root / "zigux/Makefile"
        original_makefile = makefile.read_text(encoding="utf-8")
        makefile.write_text(
            original_makefile.replace(
                "phase6-hexdump-perf",
                "phase6-hexdump-bench",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/Makefile" not in str(exc):
                raise AssertionError(f"unexpected Makefile failure: {exc}") from exc
        else:
            raise AssertionError("expected Makefile failure")
        makefile.write_text(original_makefile, encoding="utf-8")

        tests_readme = root / "zigux/tests/README.md"
        original_tests_readme = tests_readme.read_text(encoding="utf-8")
        tests_readme.write_text(
            original_tests_readme.replace(
                "phase6_hexdump_perf.zig",
                "phase6_hexdump_bench.zig",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/README.md" not in str(exc):
                raise AssertionError(f"unexpected tests README failure: {exc}") from exc
        else:
            raise AssertionError("expected tests README failure")
        tests_readme.write_text(original_tests_readme, encoding="utf-8")

        print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    run_checks(Path(args.repo_root).resolve())
    print("Phase 6 shared surface looks aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
