#!/usr/bin/env python3
"""Guard the live Phase 2 closure validator packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")

REQUIRED_PATHS = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
)

PHASE2_CLOSURE_MARKERS = (
    "This note keeps the current Phase 2 closure-side packet aligned",
    "`python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`zig test scripts/zigux/genksyms.zig`",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py`",
    "`python3 scripts/zigux/check-fixdep-diff.py --self-test`",
    "`python3 scripts/zigux/check-fixdep-diff.py`",
    "`zig test scripts/zigux/fixdep.zig`",
    "`python3 scripts/zigux/validate-phase2.py`",
    "`python3 scripts/zigux/validate-phase2-closure.py --self-test`",
    "`python3 scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`PHASE2_CLOSURE_VALIDATORS=",
    "`PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`",
)

PHASE2_NOTES_MARKERS = (
    "`zig test scripts/zigux/genksyms.zig`",
    "`zig test scripts/zigux/fixdep.zig`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "the live bootstrap packet exercises",
)

SCRIPTS_README_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep`",
    "`scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.",
)

TESTS_README_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
)

MAKEFILE_LINES = (
    ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
    "phase2-genksyms:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

SAMPLE_PHASE2_CLOSURE = """# Phase 2 Closure

This note keeps the current Phase 2 closure-side packet aligned to the directly readable toolchain, local-first archive, installer, cross-route, kconfig-bridge, genksyms bridge, fixdep, make-wrapper, manifest-guard, and validator surfaces on current `master`.

## Closure Validation

- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `zig test scripts/zigux/genksyms.zig`
- `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`
- `python3 scripts/zigux/check-phase2-fixdep-gate.py`
- `python3 scripts/zigux/check-fixdep-diff.py --self-test`
- `python3 scripts/zigux/check-fixdep-diff.py`
- `zig test scripts/zigux/fixdep.zig`
- `python3 scripts/zigux/validate-phase2.py`
- `python3 scripts/zigux/validate-phase2-closure.py --self-test`
- `python3 scripts/zigux/validate-phase2-closure.py`

- `PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test,python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py,zig test scripts/zigux/genksyms.zig,python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py --self-test,python3 scripts/zigux/check-fixdep-diff.py,zig test scripts/zigux/fixdep.zig,python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py --self-test,python3 scripts/zigux/validate-phase2-closure.py`
- `PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`
- `make -C zigux phase2-genksyms`
- `make -C zigux phase2-fixdep`
- `make -C zigux phase2-validate`
"""

SAMPLE_PHASE2_NOTES = """# Phase 2 Toolchain Bootstrap Notes

## Current direct packet

- the live bootstrap packet exercises the pinned-channel, pinned-archive integrity, local-first archive workflow, third_party README contract, installer, toolchain-pinning, pin-scope, kbuild-route, tests-root reminder, direct cross-route, cross-selftest alignment, required-make-route, docs-shared-reminder, manifest, artifact-support, primary artifact-diff helper, dedicated genksyms selftest-alignment guard, genksyms bridge, kconfig bridge, fixdep governance and parity packet, and make-wrapper-backed `phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, and `phase2-validate` route replays instead of leaving the returned Phase 2 packet implicit beside the shipped CI path.
- `zig test scripts/zigux/genksyms.zig`
- `zig test scripts/zigux/fixdep.zig`
- `make -C zigux phase2-genksyms`
- `make -C zigux phase2-fixdep`
- `make -C zigux phase2-validate`
"""

SAMPLE_SCRIPTS_README = """# scripts/zigux

## Phase 2

- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set
- `scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` keep the shipped artifact-support and fixdep packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards
- `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.
"""

SAMPLE_TESTS_README = """# zigux/tests

## Phase 2 review packet

- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/check-phase2-fixdep-gate.py`
- `scripts/zigux/check-fixdep-diff.py`

Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.
"""

SAMPLE_WORKFLOW = "\n".join(WORKFLOW_LINES) + "\n"
SAMPLE_MAKEFILE = "\n".join(MAKEFILE_LINES) + "\n"


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"phase2 closure validator packet checker missing file: {path}") from exc
    except OSError as exc:
        raise SystemExit(f"phase2 closure validator packet checker unreadable file {path}: {exc}") from exc


def require_paths(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if not path.is_file():
            raise SystemExit(f"phase2 closure validator packet checker missing required path: {path}")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"phase2 closure validator packet checker missing {label} marker: {marker}")


def require_exact_lines(text: str, lines: tuple[str, ...], label: str) -> None:
    stripped = [line.strip() for line in text.splitlines()]
    for line in lines:
        count = sum(1 for candidate in stripped if candidate == line)
        if count == 0:
            raise SystemExit(f"phase2 closure validator packet checker missing {label} line: {line}")
        if count != 1:
            raise SystemExit(
                f"phase2 closure validator packet checker duplicate {label} line count={count}: {line}"
            )


def check_root(root: Path) -> None:
    require_paths(root)
    require_markers(read_text(root, PHASE2_CLOSURE), PHASE2_CLOSURE_MARKERS, "phase2-closure")
    require_markers(read_text(root, PHASE2_NOTES), PHASE2_NOTES_MARKERS, "phase2 notes")
    require_markers(read_text(root, SCRIPTS_README), SCRIPTS_README_MARKERS, "scripts README")
    require_markers(read_text(root, TESTS_README), TESTS_README_MARKERS, "tests README")
    require_exact_lines(read_text(root, WORKFLOW), WORKFLOW_LINES, "workflow")
    require_exact_lines(read_text(root, MAKEFILE), MAKEFILE_LINES, "Makefile")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(root / PHASE2_CLOSURE, SAMPLE_PHASE2_CLOSURE)
    write_text(root / PHASE2_NOTES, SAMPLE_PHASE2_NOTES)
    write_text(root / SCRIPTS_README, SAMPLE_SCRIPTS_README)
    write_text(root / TESTS_README, SAMPLE_TESTS_README)
    write_text(root / WORKFLOW, SAMPLE_WORKFLOW)
    write_text(root / MAKEFILE, SAMPLE_MAKEFILE)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane25_phase2_closure_validator_packet_") as tmp:
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

        broken = sample_root / PHASE2_NOTES
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "phase2 notes marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing phase2 notes marker failure")
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

        broken = sample_root / WORKFLOW
        broken.write_text("run: zig test scripts/zigux/genksyms.zig\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "workflow line" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing workflow line failure")
        write_sample_root(sample_root)

        broken = sample_root / MAKEFILE
        broken.write_text("phase2-genksyms:\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "Makefile line" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing Makefile line failure")
        write_sample_root(sample_root)

        missing_required = sample_root / PHASE2_NOTES
        missing_required.unlink()
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "missing required path" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing required path failure")

    print("PHASE2_CLOSURE_VALIDATOR_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the live Phase 2 closure validator packet."
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
    print("PHASE2_CLOSURE_VALIDATOR_PACKET=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_ROOT={args.root.resolve()}")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_PHASE2_CLOSURE_MARKER_COUNT={len(PHASE2_CLOSURE_MARKERS)}")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_PHASE2_NOTES_MARKER_COUNT={len(PHASE2_NOTES_MARKERS)}")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_TESTS_README_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
