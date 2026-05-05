#!/usr/bin/env python3
"""Fail-closed Phase 6 shared-surface checks for the simplified helper bundle."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


REQUIRED_SNIPPETS = {
    "Documentation/zigux/README.md": [
        "- `Documentation/zigux/phase6-base64-slice.md`",
        "- `Documentation/zigux/phase6-bsearch-slice.md`",
        "- `Documentation/zigux/phase6-checksum-slice.md`",
        "- `Documentation/zigux/phase6-hexdump-slice.md`",
        "- `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, and `make -C zigux phase6` now gate the current base64, bsearch, checksum, and hexdump helper bundle together",
    ],
    "Documentation/zigux/phase6-base64-slice.md": [
        "- `zigux/tests/fixtures/phase6_base64_vectors.zig`",
        "- shared kernel-derived encode, decode, variant, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig`",
        "- a separate external C-vs-Zig parity packet on `master`",
    ],
    "scripts/zigux/README.md": [
        "- the current shared Phase 6 review surface on `master` is the four slice notes (`Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, and `Documentation/zigux/phase6-hexdump-slice.md`) plus `Documentation/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase6_build.zig`, and `zigux/Makefile`.",
        "- `zig build test --build-file zigux/tests/phase6_build.zig` is the bundled helper replay for the current `base64`, `bsearch`, `checksum`, and `hexdump` packet.",
        "- `make -C zigux phase6` keeps that same bundled helper replay wired through the Zigux convenience target.",
        "- there is no separate shared `validate-phase6.py`, external portability checker packet, or `phase6-perf` make target on `master`; if those gates land later, document them here only after the files and targets ship.",
    ],
    "zigux/tests/README.md": [
        "- keep the shared Phase 6 leaf-helper packet wired through `zigux/tests/phase6_build.zig`, including `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, and `zigux/tests/phase6_hexdump.zig`, so the landed `base64`, `bsearch`, `checksum`, and `hexdump` bundle stays reviewable through one bounded helper gate",
    ],
    "Documentation/zigux/review-checklist.md": [
        "- if the change touches the shared Phase 6 leaf-helper packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-hexdump-slice.md`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/Makefile`, and `make -C zigux phase6` still agree on the same bundled `base64`, `bsearch`, `checksum`, and `hexdump` helper packet without implying a removed shared `validate-phase6.py`, external parity checker, or `phase6-perf` route?",
    ],
    "zigux/tests/phase6_build.zig": [
        'const test_step = b.step("test", "Run Phase 6 leaf helper tests");',
        '.name = "phase6-base64-tests"',
        '.name = "phase6-bsearch-tests"',
        '.name = "phase6-checksum-tests"',
        '.name = "phase6-hexdump-tests"',
    ],
    "zigux/tests/phase6_base64.zig": [
        'const fixtures = @import("fixtures/phase6_base64_vectors.zig");',
        "for (fixtures.standard_cases) |case| {",
        "for (fixtures.variant_cases) |case| {",
        "for (fixtures.standard_decode_cases) |case| {",
        "for (fixtures.invalid_decode_cases) |case| {",
        "for (fixtures.variant_decode_cases) |case| {",
    ],
    "zigux/tests/fixtures/phase6_base64_vectors.zig": [
        "pub const standard_cases = [_]EncodeCase{",
        "pub const variant_cases = [_]VariantCase{",
        "pub const standard_decode_cases = [_]DecodeCase{",
        "pub const invalid_decode_cases = [_]InvalidDecodeCase{",
        "pub const variant_decode_cases = [_]DecodeCase{",
    ],
    "zigux/Makefile": [
        "PHONY += phase6-validate phase6-test phase6",
        "phase6-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py",
        "phase6: phase6-validate phase6-test",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "- name: Self-test Phase 6 shared-surface checker\n        run: python3 scripts/zigux/check-phase6-shared-surface.py --self-test",
        "- name: Check Phase 6 shared surface\n        run: python3 scripts/zigux/check-phase6-shared-surface.py",
        "- name: Run Phase 6 leaf helper tests\n        run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
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
                raise ValidationError(f"missing expected Phase 6 marker in {rel_path}: {snippet}")

    for rel_path in REMOVED_PATHS:
        if (repo_root / rel_path).exists():
            raise ValidationError(f"removed Phase 6 shared-surface file unexpectedly present: {rel_path}")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        for rel_path, snippets in REQUIRED_SNIPPETS.items():
            write(root / rel_path, "\n".join(snippets) + "\n")

        run_checks(root)

        write(root / REMOVED_PATHS[0], "stale\n")
        try:
            run_checks(root)
        except ValidationError as exc:
            if REMOVED_PATHS[0] not in str(exc):
                raise AssertionError(f"unexpected removed-path failure: {exc}") from exc
        else:
            raise AssertionError("expected removed-path failure")
        (root / REMOVED_PATHS[0]).unlink()

        scripts_readme = root / "scripts/zigux/README.md"
        original = scripts_readme.read_text(encoding="utf-8")
        scripts_readme.write_text(original.replace("there is no separate shared `validate-phase6.py`", "there is still a shared `validate-phase6.py`"), encoding="utf-8")
        try:
            run_checks(root)
        except ValidationError as exc:
            if "scripts/zigux/README.md" not in str(exc):
                raise AssertionError(f"unexpected scripts README failure: {exc}") from exc
        else:
            raise AssertionError("expected scripts README failure")
        scripts_readme.write_text(original, encoding="utf-8")

        makefile = root / "zigux/Makefile"
        original_makefile = makefile.read_text(encoding="utf-8")
        makefile.write_text(original_makefile.replace("phase6: phase6-validate phase6-test", "phase6: phase6-test"), encoding="utf-8")
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/Makefile" not in str(exc):
                raise AssertionError(f"unexpected Makefile failure: {exc}") from exc
        else:
            raise AssertionError("expected Makefile failure")
        makefile.write_text(original_makefile, encoding="utf-8")

        base64_slice = root / "Documentation/zigux/phase6-base64-slice.md"
        original_base64_slice = base64_slice.read_text(encoding="utf-8")
        base64_slice.write_text(
            original_base64_slice.replace(
                "- shared kernel-derived encode, decode, variant, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig`",
                "- shared base64 notes only",
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "Documentation/zigux/phase6-base64-slice.md" not in str(exc):
                raise AssertionError(f"unexpected base64 slice failure: {exc}") from exc
        else:
            raise AssertionError("expected base64 slice failure")
        base64_slice.write_text(original_base64_slice, encoding="utf-8")

        base64_test = root / "zigux/tests/phase6_base64.zig"
        original_base64_test = base64_test.read_text(encoding="utf-8")
        base64_test.write_text(
            original_base64_test.replace(
                "for (fixtures.invalid_decode_cases) |case| {",
                "for (inline_invalid_decode_cases) |case| {",
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_base64.zig" not in str(exc):
                raise AssertionError(f"unexpected base64 test failure: {exc}") from exc
        else:
            raise AssertionError("expected base64 test failure")

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
