#!/usr/bin/env python3
"""Guard the shared Phase 2 fixdep reminder packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

DOCS_README = Path("Documentation/zigux/README.md")
PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
MAKEFILE = Path("zigux/Makefile")

REQUIRED_PATHS = (
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "zigux/tests/fixtures/fixdep/cases.json",
    "zigux/Makefile",
)

DOCS_README_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again",
    "keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces",
)

PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.",
)

PHASE2_CLOSURE_MARKERS = (
    "The current closure-side packet keeps the fixdep governance and parity checker pair explicit through `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep`",
    "- `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`",
    "- `python3 scripts/zigux/check-phase2-fixdep-gate.py`",
    "- `python3 scripts/zigux/check-fixdep-diff.py --self-test`",
    "- `python3 scripts/zigux/check-fixdep-diff.py`",
    "- `zig test scripts/zigux/fixdep.zig`",
)

REVIEW_CHECKLIST_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

TESTS_README_MARKERS = (
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`",
    "keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` keep the shipped artifact-support and fixdep packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
)

MAKEFILE_MARKERS = (
    ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
    "phase2-fixdep:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "$(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "$(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "$(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "$(ZIG) test scripts/zigux/fixdep.zig",
)

SAMPLE_DOCS_README = """# Zigux Documentation

* `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.
"""

SAMPLE_PHASE2_NOTES = """# Phase 2 Toolchain Bootstrap Notes

`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.
"""

SAMPLE_PHASE2_CLOSURE = """# Phase 2 Closure

The current closure-side packet keeps the fixdep governance and parity checker pair explicit through `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep`.

- `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`
- `python3 scripts/zigux/check-phase2-fixdep-gate.py`
- `python3 scripts/zigux/check-fixdep-diff.py --self-test`
- `python3 scripts/zigux/check-fixdep-diff.py`
- `zig test scripts/zigux/fixdep.zig`
"""

SAMPLE_REVIEW_CHECKLIST = """# Zigux Review Checklist

* if the change touches the shared Phase 2 toolchain packet, do `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` stay explicit as the current rematerialized Phase 2 fixdep packet?
"""

SAMPLE_TESTS_README = """# zigux/tests

current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder
"""

SAMPLE_SCRIPTS_README = """# scripts/zigux

`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` keep the shipped artifact-support and fixdep packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards
"""

SAMPLE_MAKEFILE = """.PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2

phase2-fixdep:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py
\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig

phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
"""


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"phase2 shared fixdep packet checker missing file: {path}") from exc
    except OSError as exc:
        raise SystemExit(
            f"phase2 shared fixdep packet checker unreadable file {path}: {exc}"
        ) from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(
                f"phase2 shared fixdep packet checker missing {label} marker: {marker}"
            )


def require_paths(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if not path.is_file():
            raise SystemExit(
                f"phase2 shared fixdep packet checker missing required path: {path}"
            )


def check_root(root: Path) -> None:
    require_paths(root)
    require_markers(read_text(root, DOCS_README), DOCS_README_MARKERS, "docs README")
    require_markers(read_text(root, PHASE2_NOTES), PHASE2_NOTES_MARKERS, "phase2 notes")
    require_markers(
        read_text(root, PHASE2_CLOSURE), PHASE2_CLOSURE_MARKERS, "phase2 closure"
    )
    require_markers(
        read_text(root, REVIEW_CHECKLIST),
        REVIEW_CHECKLIST_MARKERS,
        "review checklist",
    )
    require_markers(
        read_text(root, TESTS_README), TESTS_README_MARKERS, "tests README"
    )
    require_markers(
        read_text(root, SCRIPTS_README), SCRIPTS_README_MARKERS, "scripts README"
    )
    require_markers(read_text(root, MAKEFILE), MAKEFILE_MARKERS, "Makefile")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(root / DOCS_README, SAMPLE_DOCS_README)
    write_text(root / PHASE2_NOTES, SAMPLE_PHASE2_NOTES)
    write_text(root / PHASE2_CLOSURE, SAMPLE_PHASE2_CLOSURE)
    write_text(root / REVIEW_CHECKLIST, SAMPLE_REVIEW_CHECKLIST)
    write_text(root / TESTS_README, SAMPLE_TESTS_README)
    write_text(root / SCRIPTS_README, SAMPLE_SCRIPTS_README)
    write_text(root / MAKEFILE, SAMPLE_MAKEFILE)
    for rel in REQUIRED_PATHS[:-1]:
        write_text(root / rel, "# placeholder\n")
    write_text(root / "zigux/tests/fixtures/fixdep/cases.json", "{}\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane25_phase2_fixdep_packet_") as tmp:
        sample_root = Path(tmp)
        write_sample_root(sample_root)
        check_root(sample_root)
        case_count += 1

        broken = sample_root / DOCS_README
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "docs README marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected docs README marker failure")
        write_sample_root(sample_root)

        broken = sample_root / PHASE2_CLOSURE
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "phase2 closure marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected phase2 closure marker failure")
        write_sample_root(sample_root)

        broken = sample_root / SCRIPTS_README
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "scripts README marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected scripts README marker failure")
        write_sample_root(sample_root)

        broken = sample_root / MAKEFILE
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "Makefile marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected Makefile marker failure")
        write_sample_root(sample_root)

        missing_required = sample_root / "scripts/zigux/check-fixdep-diff.py"
        missing_required.unlink()
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "missing required path" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing required path failure")

    print("PHASE2_SHARED_FIXDEP_PACKET_SELF_TEST=pass")
    print(f"PHASE2_SHARED_FIXDEP_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the shared Phase 2 fixdep reminder packet."
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
    print("PHASE2_SHARED_FIXDEP_PACKET=pass")
    print(f"PHASE2_SHARED_FIXDEP_PACKET_ROOT={args.root.resolve()}")
    print(f"PHASE2_SHARED_FIXDEP_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(
        f"PHASE2_SHARED_FIXDEP_PACKET_DOCS_MARKER_COUNT={len(DOCS_README_MARKERS)}"
    )
    print(
        f"PHASE2_SHARED_FIXDEP_PACKET_NOTES_MARKER_COUNT={len(PHASE2_NOTES_MARKERS)}"
    )
    print(
        "PHASE2_SHARED_FIXDEP_PACKET_CLOSURE_MARKER_COUNT="
        f"{len(PHASE2_CLOSURE_MARKERS)}"
    )
    print(
        "PHASE2_SHARED_FIXDEP_PACKET_REVIEW_MARKER_COUNT="
        f"{len(REVIEW_CHECKLIST_MARKERS)}"
    )
    print(
        f"PHASE2_SHARED_FIXDEP_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}"
    )
    print(
        "PHASE2_SHARED_FIXDEP_PACKET_SCRIPTS_MARKER_COUNT="
        f"{len(SCRIPTS_README_MARKERS)}"
    )
    print(
        f"PHASE2_SHARED_FIXDEP_PACKET_MAKEFILE_MARKER_COUNT={len(MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
