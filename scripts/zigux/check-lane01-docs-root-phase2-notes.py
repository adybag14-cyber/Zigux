#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")

PHASE1_HEADING = "Phase 1 notes - "
PHASE2_HEADING = "Phase 2 notes - "
PHASE3_HEADING = "Phase 3 notes - "

REQUIRED_MARKERS = (
    "Phase 2 notes - `Documentation/zigux/phase2-closure.md` - `Documentation/zigux/phase2-toolchain-bootstrap-notes.md` - `Documentation/zigux/review-checklist.md` - `zigux/tests/README.md` - `zigux/tests/fixtures/phase2_tool_manifest.json` - `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` - `zigux/tests/fixtures/phase2_cross_targets.json` - `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` - `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` - `zigux/tests/fixtures/kconfig_bridge/cases.json` - `zigux/tests/fixtures/genksyms_bridge/cases.json` - `zigux/tests/fixtures/genksyms_bridge/help_expected.json` - `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json` - `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json` - `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json` - `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json` - `scripts/zigux/README.md` - `scripts/zigux/install-zig.py` - `scripts/zigux/check-zig-toolchain.py` - `scripts/zigux/check-phase2-kbuild-routes.py` - `scripts/zigux/check-phase2-kconfig-selftest-alignment.py` - `scripts/zigux/check-phase2-tests-readme-alignment.py` - `scripts/zigux/check-phase2-cross.py` - `scripts/zigux/check-phase2-cross-selftest-alignment.py` - `scripts/zigux/check-phase2-toolchain-pinning.py` - `scripts/zigux/check-phase2-toolchain-pin-scope.py` - `scripts/zigux/check-phase2-required-make-routes.py` - `scripts/zigux/check-phase2-docs-shared-reminder.py` - `scripts/zigux/check-phase2-tool-manifest.py` - `scripts/zigux/check-phase2-artifact-tools-manifest.py` - `scripts/zigux/check-genksyms-bridge.py` - `scripts/zigux/validate-phase2.py` - `scripts/zigux/validate-phase2-closure.py` - `scripts/zigux/kconfig/conf_bridge.zig` - `scripts/zigux/kconfig/confdata_bridge.zig` - `scripts/zigux/genksyms.zig` - `zigux/Makefile` keep the bounded Phase 2 docs-root packet explicit through the returned closure-side validator pair, the shipped installer and direct cross-route companions, the surviving toolchain, shared-reminder, and manifest guards, the selected kconfig bridge helpers, the bounded genksyms bridge helper packet, the current manifests, and the shipped make-wrapper routes instead of treating that now-rematerialized tranche as historical-only evidence.",
    "* the current docs-root Phase 2 reminder packet should stay parked on `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, and `zigux/Makefile`, with `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/phase2_cross_targets.json`, the current kconfig bridge manifests, and the current genksyms bridge fixture roster keeping the same packet aligned across docs-root, scripts-root, and tests-root surfaces.",
    "* `third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again, so keep the repo-local pinned archive contract, the `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay, the local-first `third_party`, mirror, then direct-download bootstrap order, and the two shipped Lane 05 reminder guards explicit from the docs root beside the returned toolchain packet.",
    "* `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
    "* `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.",
    "* `python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
)


def collect_errors(root: Path) -> list[str]:
    content = (root / DOCS_README_PATH).read_text(encoding="utf-8")

    errors: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in content:
            errors.append(f"missing:{marker}")

    phase1_index = content.find(PHASE1_HEADING)
    phase2_index = content.find(PHASE2_HEADING)
    phase3_index = content.find(PHASE3_HEADING)

    if phase1_index == -1:
        errors.append(f"missing:{PHASE1_HEADING}")
    if phase2_index == -1:
        errors.append(f"missing:{PHASE2_HEADING}")
    if phase3_index == -1:
        errors.append(f"missing:{PHASE3_HEADING}")

    if phase1_index != -1 and phase2_index != -1 and phase1_index >= phase2_index:
        errors.append("order:Phase 1 notes must appear before Phase 2 notes")
    if phase2_index != -1 and phase3_index != -1 and phase2_index >= phase3_index:
        errors.append("order:Phase 2 notes must appear before Phase 3 notes")

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_docs_readme() -> str:
    return f"""# Zigux Documentation
{PHASE1_HEADING}placeholder
{REQUIRED_MARKERS[0]}
{REQUIRED_MARKERS[1]}
{REQUIRED_MARKERS[2]}
{REQUIRED_MARKERS[3]}
{REQUIRED_MARKERS[4]}
{REQUIRED_MARKERS[5]}
{PHASE3_HEADING}placeholder
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase2_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DOCS_README_PATH, _sample_docs_readme())

        if collect_errors(root):
            raise AssertionError("baseline Phase 2 fixture should pass")
        case_count += 1

        for marker in REQUIRED_MARKERS:
            _write(root / DOCS_README_PATH, _sample_docs_readme().replace(marker + "\n", "", 1))
            errors = collect_errors(root)
            expected = [f"missing:{marker}"]
            if marker.startswith(PHASE2_HEADING):
                expected.append(f"missing:{PHASE2_HEADING}")
            if errors != expected:
                raise AssertionError(f"unexpected errors for marker removal: {errors}")
            case_count += 1

        reordered = (
            "# Zigux Documentation\n"
            f"{PHASE1_HEADING}placeholder\n"
            f"{PHASE3_HEADING}placeholder\n"
            + "\n".join(REQUIRED_MARKERS)
            + "\n"
        )
        _write(root / DOCS_README_PATH, reordered)
        errors = collect_errors(root)
        expected = ["order:Phase 2 notes must appear before Phase 3 notes"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for Phase 2/3 order case: {errors}")
        case_count += 1

        reordered = (
            "# Zigux Documentation\n"
            + REQUIRED_MARKERS[0]
            + "\n"
            f"{PHASE1_HEADING}placeholder\n"
            + "\n".join(REQUIRED_MARKERS[1:])
            + "\n"
            f"{PHASE3_HEADING}placeholder\n"
        )
        _write(root / DOCS_README_PATH, reordered)
        errors = collect_errors(root)
        expected = ["order:Phase 1 notes must appear before Phase 2 notes"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for Phase 1/2 order case: {errors}")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE2_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE2_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the current docs-root Phase 2 reminder packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Phase 2 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_errors(args.root)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1

    print("LANE01_DOCS_ROOT_PHASE2_NOTES=pass")
    print(f"LANE01_DOCS_ROOT_PHASE2_NOTES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("LANE01_DOCS_ROOT_PHASE2_NOTES_SECTION_ORDER=Phase1->Phase2->Phase3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
