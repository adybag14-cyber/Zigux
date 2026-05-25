#!/usr/bin/env python3
"""Guard the dedicated Phase 2 genksyms survey reminder packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
GENKSYMS_SURVEY = Path("Documentation/zigux/phase2-genksyms-dual-implementation-survey.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")

REQUIRED_PATHS = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

PHASE2_CLOSURE_MARKERS = (
    "- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`",
    "- `scripts/zigux/check-genksyms-bridge.py`",
    "- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "- `scripts/zigux/genksyms.zig`",
    "- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "- `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "- `zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`",
    "- `make -C zigux phase2-genksyms`",
)

GENKSYMS_SURVEY_MARKERS = (
    "- The Phase 2 roadmap still keeps `scripts/genksyms/genksyms.c` inside the bounded toolchain and Kbuild enablement tranche, with `scripts/zigux/genksyms.zig` as the Zigux destination.",
    "- The live helper still carries embedded Zig unit tests for short and long option parsing, version or help side effects, getopt-style error rendering, empty inline `--reference=` and abbreviated `--dump-t=` argument preservation, passthrough handling, and the sixteen-reference-file cap, so helper-local replay evidence remains materialized.",
    "- Current shared Phase 2 reminder surfaces mostly keep the genksyms packet explicit: `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/tests/fixtures/phase2_tool_manifest.json` still name the dedicated survey note, selftest-alignment checker, fixture roster, standalone proof files, dedicated manifest, process-output packet, or `phase2-genksyms` replay route.",
    "- The narrower tests-root undercount is no longer current: live `zigux/tests/README.md` now explicitly names `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, the dedicated `manifest.json`, the returned dash-prefixed-long-option-arguments-as-data expected-output fixture, and the restored process-output fixture packet, while `scripts/zigux/check-phase2-tests-readme-alignment.py` now fail-closes on that fuller reminder packet together with the current shared docs-root and manifest-backed Phase 2 surfaces.",
    "- Current `master` now also carries `scripts/zigux/check-phase2-genksyms-survey-packet.py`, so this dedicated survey note has its own fail-closed guard against the returned closure-side, scripts-root, and tests-root packet without reopening those already-aligned reminder bodies.",
    "- Relative to the roadmap and ledger, the older inventory-shaped governance gap is no longer truthful on current `master`; the live work is now a bounded wrapper-first dual-implementation packet whose checker-owned manifest, process-output fixtures, standalone proofs, shared reminder surfaces, and dedicated survey guard are directly materialized.",
    "2. Reopen the same family only if `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md` drifts away from `scripts/zigux/check-phase2-genksyms-survey-packet.py`, and keep that repair checker-local or reminder-local instead of widening back into a broader docs rewrite.",
)

SCRIPTS_README_MARKERS = (
    "- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`",
    "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
)

TESTS_README_MARKERS = (
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`",
)

SAMPLE_PHASE2_CLOSURE = """# Phase 2 Closure

## Current Closure Packet

- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`
- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`
- `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`
- `zigux/tests/fixtures/genksyms_bridge/manifest.json`
- `zigux/tests/fixtures/genksyms_bridge/help_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`

## Closure Validation

- `make -C zigux phase2-genksyms`
"""

SAMPLE_GENKSYMS_SURVEY = """# Phase 2 genksyms dual-implementation survey

## Roadmap and ledger anchor

- The Phase 2 roadmap still keeps `scripts/genksyms/genksyms.c` inside the bounded toolchain and Kbuild enablement tranche, with `scripts/zigux/genksyms.zig` as the Zigux destination.

## Current repo evidence

- The live helper still carries embedded Zig unit tests for short and long option parsing, version or help side effects, getopt-style error rendering, empty inline `--reference=` and abbreviated `--dump-t=` argument preservation, passthrough handling, and the sixteen-reference-file cap, so helper-local replay evidence remains materialized.
- Current shared Phase 2 reminder surfaces mostly keep the genksyms packet explicit: `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/tests/fixtures/phase2_tool_manifest.json` still name the dedicated survey note, selftest-alignment checker, fixture roster, standalone proof files, dedicated manifest, process-output packet, or `phase2-genksyms` replay route.
- The narrower tests-root undercount is no longer current: live `zigux/tests/README.md` now explicitly names `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, the dedicated `manifest.json`, the returned dash-prefixed-long-option-arguments-as-data expected-output fixture, and the restored process-output fixture packet, while `scripts/zigux/check-phase2-tests-readme-alignment.py` now fail-closes on that fuller reminder packet together with the current shared docs-root and manifest-backed Phase 2 surfaces.
- Current `master` now also carries `scripts/zigux/check-phase2-genksyms-survey-packet.py`, so this dedicated survey note has its own fail-closed guard against the returned closure-side, scripts-root, and tests-root packet without reopening those already-aligned reminder bodies.

## Survey result

- Relative to the roadmap and ledger, the older inventory-shaped governance gap is no longer truthful on current `master`; the live work is now a bounded wrapper-first dual-implementation packet whose checker-owned manifest, process-output fixtures, standalone proofs, shared reminder surfaces, and dedicated survey guard are directly materialized.

## Next bounded same-family step

2. Reopen the same family only if `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md` drifts away from `scripts/zigux/check-phase2-genksyms-survey-packet.py`, and keep that repair checker-local or reminder-local instead of widening back into a broader docs rewrite.
"""

SAMPLE_SCRIPTS_README = """# scripts/zigux

## Phase 2

- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`
- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set
"""

SAMPLE_TESTS_README = """# zigux/tests

## Phase 2 review packet

current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder

- `zigux/tests/fixtures/genksyms_bridge/manifest.json`
- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`
"""


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"phase2 genksyms survey checker missing file: {path}") from exc
    except OSError as exc:
        raise SystemExit(f"phase2 genksyms survey checker unreadable file {path}: {exc}") from exc


def require_paths(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if not path.is_file():
            raise SystemExit(f"phase2 genksyms survey checker missing required path: {path}")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"phase2 genksyms survey checker missing {label} marker: {marker}")


def check_root(root: Path) -> None:
    require_paths(root)
    require_markers(read_text(root, PHASE2_CLOSURE), PHASE2_CLOSURE_MARKERS, "phase2-closure")
    require_markers(read_text(root, GENKSYMS_SURVEY), GENKSYMS_SURVEY_MARKERS, "genksyms survey")
    require_markers(read_text(root, SCRIPTS_README), SCRIPTS_README_MARKERS, "scripts README")
    require_markers(read_text(root, TESTS_README), TESTS_README_MARKERS, "tests README")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(root / PHASE2_CLOSURE, SAMPLE_PHASE2_CLOSURE)
    write_text(root / GENKSYMS_SURVEY, SAMPLE_GENKSYMS_SURVEY)
    write_text(root / SCRIPTS_README, SAMPLE_SCRIPTS_README)
    write_text(root / TESTS_README, SAMPLE_TESTS_README)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane25_phase2_genksyms_survey_") as tmp:
        sample_root = Path(tmp)
        write_sample_root(sample_root)
        check_root(sample_root)
        case_count += 1

        broken = sample_root / PHASE2_CLOSURE
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "phase2-closure marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing phase2-closure marker failure")
        write_sample_root(sample_root)

        broken = sample_root / GENKSYMS_SURVEY
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "genksyms survey marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing genksyms survey marker failure")
        write_sample_root(sample_root)

        broken = sample_root / SCRIPTS_README
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "scripts README marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing scripts README marker failure")
        write_sample_root(sample_root)

        broken = sample_root / TESTS_README
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "tests README marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing tests README marker failure")
        write_sample_root(sample_root)

        missing_required = sample_root / TESTS_README
        missing_required.unlink()
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "missing required path" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing required path failure")

    print("PHASE2_GENKSYMS_SURVEY_PACKET_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the dedicated Phase 2 genksyms survey reminder packet."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        write_sample_root(args.write_sample_root)
        return 0

    check_root(args.root.resolve())
    print("PHASE2_GENKSYMS_SURVEY_PACKET=pass")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_ROOT={args.root.resolve()}")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_PHASE2_CLOSURE_MARKER_COUNT={len(PHASE2_CLOSURE_MARKERS)}")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_SURVEY_MARKER_COUNT={len(GENKSYMS_SURVEY_MARKERS)}")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_GENKSYMS_SURVEY_PACKET_TESTS_README_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
