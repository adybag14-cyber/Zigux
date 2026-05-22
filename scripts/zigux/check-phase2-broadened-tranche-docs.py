#!/usr/bin/env python3
"""Guard the broadened Phase 2 documentation reconciliation packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
ARTIFACT_DIFF = Path("Documentation/zigux/artifact-diff.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
BOOTSTRAP_LEDGER = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")

REQUIRED_PATHS = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/artifact-diff.md",
    "scripts/zigux/README.md",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
)

PHASE2_CLOSURE_MARKERS = (
    "This note keeps the current Phase 2 closure-side packet aligned",
    "- `Documentation/zigux/phase2-closure.md`",
    "- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`",
    "- `scripts/zigux/README.md`",
    "- `scripts/zigux/install-zig.py`",
    "- `scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "- `scripts/zigux/check-lane05-local-archive-readme.py`",
    "- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "- `scripts/zigux/validate-phase2.py`",
    "- `scripts/zigux/validate-phase2-closure.py`",
    "- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "- `third_party/README.md`",
    "- `zigux/Makefile`",
    "`make -C zigux phase2-genksyms`",
    "- `PHASE2_NEXT_SAFE_STEP=keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again",
)

ARTIFACT_DIFF_MARKERS = (
    "## Current Phase 2 use",
    "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep`, `genksyms`, and the kconfig bridge packet.",
    "## Current Phase 4 use",
    "ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL",
)

SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "- Phase 2 flow - the current scripts-root bridge packet stays reviewable",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "`scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep`",
)

LEDGER_MARKERS = (
    "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
    "- `Documentation/zigux/phase2-closure.md`",
    "- `Documentation/zigux/artifact-diff.md`",
    "- `scripts/zigux/README.md`",
    "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`",
)

SAMPLE_PHASE2_CLOSURE = """# Phase 2 Closure

This note keeps the current Phase 2 closure-side packet aligned to the directly readable toolchain, local-first archive, installer, cross-route, kconfig-bridge, genksyms bridge, fixdep, make-wrapper, manifest-guard, and validator surfaces on current `master`.

## Current Closure Packet

- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`
- `scripts/zigux/README.md`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-lane05-local-first-archive-workflow.py`
- `scripts/zigux/check-lane05-local-archive-readme.py`
- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`
- `third_party/README.md`
- `zigux/Makefile`

- `make -C zigux phase2-genksyms`
- `PHASE2_NEXT_SAFE_STEP=keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again`
"""

SAMPLE_ARTIFACT_DIFF = """# Zigux Artifact-Diff Notes

## Current Phase 2 use

Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep`, `genksyms`, and the kconfig bridge packet.

## Current Phase 4 use

The helper now compares `text`, `json`, and `bytes` artifacts, and publishes `ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR]`.
"""

SAMPLE_SCRIPTS_README = """# scripts/zigux

## Phase 2

- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet
- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, and `make -C zigux phase2` keep the shipped closure-side reminder packet explicit from the scripts root
- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording
- `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` keep the shipped artifact-support and fixdep packet explicit from the scripts root
"""

SAMPLE_LEDGER = """# Zigux Alpha Bootstrap Commit Ledger

25. `docs(zigux): reopen and close broadened Phase 2 tranche`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/artifact-diff.md`
- `scripts/zigux/README.md`
- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
"""


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"phase2 broadened tranche docs checker missing file: {path}") from exc
    except OSError as exc:
        raise SystemExit(f"phase2 broadened tranche docs checker unreadable file {path}: {exc}") from exc


def require_paths(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if not path.is_file():
            raise SystemExit(f"phase2 broadened tranche docs checker missing required path: {path}")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"phase2 broadened tranche docs checker missing {label} marker: {marker}")


def check_root(root: Path) -> None:
    require_paths(root)
    require_markers(read_text(root, PHASE2_CLOSURE), PHASE2_CLOSURE_MARKERS, "phase2-closure")
    require_markers(read_text(root, ARTIFACT_DIFF), ARTIFACT_DIFF_MARKERS, "artifact-diff")
    require_markers(read_text(root, SCRIPTS_README), SCRIPTS_README_MARKERS, "scripts README")
    require_markers(read_text(root, BOOTSTRAP_LEDGER), LEDGER_MARKERS, "bootstrap ledger")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(root / PHASE2_CLOSURE, SAMPLE_PHASE2_CLOSURE)
    write_text(root / ARTIFACT_DIFF, SAMPLE_ARTIFACT_DIFF)
    write_text(root / SCRIPTS_README, SAMPLE_SCRIPTS_README)
    write_text(root / BOOTSTRAP_LEDGER, SAMPLE_LEDGER)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane25_broadened_tranche_docs_") as tmp:
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

        broken = sample_root / ARTIFACT_DIFF
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "artifact-diff marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing artifact-diff marker failure")
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

        broken = sample_root / BOOTSTRAP_LEDGER
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "bootstrap ledger marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing bootstrap ledger marker failure")
        write_sample_root(sample_root)

        missing_required = sample_root / ARTIFACT_DIFF
        missing_required.unlink()
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "missing required path" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing required path failure")

    print("PHASE2_BROADENED_TRANCHE_DOCS_SELF_TEST=pass")
    print(f"PHASE2_BROADENED_TRANCHE_DOCS_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 25 broadened Phase 2 documentation packet."
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
    print("PHASE2_BROADENED_TRANCHE_DOCS=pass")
    print(f"PHASE2_BROADENED_TRANCHE_DOCS_ROOT={args.root.resolve()}")
    print(f"PHASE2_BROADENED_TRANCHE_DOCS_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_BROADENED_TRANCHE_DOCS_PHASE2_CLOSURE_MARKER_COUNT={len(PHASE2_CLOSURE_MARKERS)}")
    print(f"PHASE2_BROADENED_TRANCHE_DOCS_ARTIFACT_DIFF_MARKER_COUNT={len(ARTIFACT_DIFF_MARKERS)}")
    print(f"PHASE2_BROADENED_TRANCHE_DOCS_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_BROADENED_TRANCHE_DOCS_LEDGER_MARKER_COUNT={len(LEDGER_MARKERS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
