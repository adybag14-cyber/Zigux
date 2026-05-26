#!/usr/bin/env python3
"""Guard the current Phase 2 review-checklist packet.

This checker keeps the shared reviewer-facing Phase 2 toolchain packet explicit
without reopening the checklist file itself. It intentionally validates only the
current Phase 2 checklist bullet and its adjacent anchors.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
CURRENT_ANCHOR = "* if the change touches the shared Phase 2 toolchain packet,"
PREVIOUS_ANCHOR = "* if the change touches the shared Phase 2 toolchain pin-scope packet,"
NEXT_ANCHOR = "* if the change touches the shared Phase 3 ABI/runtime packet,"

REQUIRED_MARKERS = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/review-checklist.md",
    "third_party/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/fixdep.zig",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2",
    "scripts/zigux/install-zig.py",
    "python3 scripts/zigux/install-zig.py --self-test",
    "scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
]


def build_sample_review_checklist() -> str:
    marker_lines = ", ".join(f"`{marker}`" for marker in REQUIRED_MARKERS[:28])
    replay_lines = ", ".join(f"`{marker}`" for marker in REQUIRED_MARKERS[28:])
    return (
        "# Zigux Review Checklist\n\n"
        "## Validation\n\n"
        f"  * if the change touches the shared Phase 2 kconfig bridge packet, do `{PREVIOUS_ANCHOR[:-1]}`\n"
        f"  * if the change touches the shared Phase 2 toolchain pin-scope packet, do `{PREVIOUS_ANCHOR[:-1]}`\n"
        f"  * if the change touches the shared Phase 2 toolchain packet, do {marker_lines} still agree on the "
        "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, "
        "kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, "
        f"genksyms-bridge, and required-make-route packet, while {replay_lines} stay explicit as the current "
        "rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, "
        "direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet?\n"
        f"  * if the change touches the shared Phase 3 ABI/runtime packet, do `{NEXT_ANCHOR[:-1]}`\n"
    )


def write_sample_root(root: Path) -> None:
    checklist_path = root / REVIEW_CHECKLIST_REL
    checklist_path.parent.mkdir(parents=True, exist_ok=True)
    checklist_path.write_text(build_sample_review_checklist(), encoding="utf-8")


def extract_phase2_packet(text: str) -> str:
    previous_index = text.find(PREVIOUS_ANCHOR)
    current_index = text.find(CURRENT_ANCHOR)
    next_index = text.find(NEXT_ANCHOR)
    if previous_index == -1:
        raise ValueError(f"missing previous anchor: {PREVIOUS_ANCHOR}")
    if current_index == -1:
        raise ValueError(f"missing current anchor: {CURRENT_ANCHOR}")
    if next_index == -1:
        raise ValueError(f"missing next anchor: {NEXT_ANCHOR}")
    if not previous_index < current_index < next_index:
        raise ValueError("phase2 checklist anchors are out of order")
    return text[current_index:next_index]


def validate_root(root: Path) -> tuple[int, int]:
    checklist_path = root / REVIEW_CHECKLIST_REL
    if not checklist_path.is_file():
        raise ValueError(f"missing file: {REVIEW_CHECKLIST_REL}")
    text = checklist_path.read_text(encoding="utf-8")
    packet = extract_phase2_packet(text)
    missing_markers = [marker for marker in REQUIRED_MARKERS if marker not in packet]
    if missing_markers:
        preview = ", ".join(missing_markers[:5])
        raise ValueError(f"phase2 review-checklist packet is missing markers: {preview}")
    return len(REQUIRED_MARKERS), packet.count("`")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2-review-checklist-selftest-") as tmpdir:
        root = Path(tmpdir)
        write_sample_root(root)
        required_count, quote_count = validate_root(root)
        assert required_count == len(REQUIRED_MARKERS)
        assert quote_count > len(REQUIRED_MARKERS)
        case_count += 1

        checklist_path = root / REVIEW_CHECKLIST_REL
        original = checklist_path.read_text(encoding="utf-8")

        checklist_path.write_text(original.replace(CURRENT_ANCHOR, "* if the change touches the shared Phase 2 packet,"), encoding="utf-8")
        try:
            validate_root(root)
        except ValueError as exc:
            assert "missing current anchor" in str(exc)
            case_count += 1
        else:
            raise AssertionError("missing current anchor should fail")

        checklist_path.write_text(original.replace(REQUIRED_MARKERS[16], "scripts/zigux/check-phase2-artifacts.py"), encoding="utf-8")
        try:
            validate_root(root)
        except ValueError as exc:
            assert REQUIRED_MARKERS[16] in str(exc)
            case_count += 1
        else:
            raise AssertionError("missing artifact-tools manifest marker should fail")

        checklist_path.write_text(original.replace(REQUIRED_MARKERS[-1], "python3 scripts/zigux/check-phase2-cross.py --policy-only"), encoding="utf-8")
        try:
            validate_root(root)
        except ValueError as exc:
            assert REQUIRED_MARKERS[-1] in str(exc)
            case_count += 1
        else:
            raise AssertionError("missing cross replay marker should fail")

        reordered = original.replace(
            f"  * if the change touches the shared Phase 2 toolchain packet,",
            "PHASE2_TEMP_SENTINEL",
            1,
        ).replace(
            f"  * if the change touches the shared Phase 3 ABI/runtime packet,",
            f"  * if the change touches the shared Phase 2 toolchain packet,",
            1,
        ).replace(
            "PHASE2_TEMP_SENTINEL",
            f"  * if the change touches the shared Phase 3 ABI/runtime packet,",
            1,
        )
        checklist_path.write_text(reordered, encoding="utf-8")
        try:
            validate_root(root)
        except ValueError as exc:
            assert "out of order" in str(exc)
            case_count += 1
        else:
            raise AssertionError("out-of-order anchors should fail")

        shutil.rmtree(root / "Documentation")
        try:
            validate_root(root)
        except ValueError as exc:
            assert str(REVIEW_CHECKLIST_REL) in str(exc)
            case_count += 1
        else:
            raise AssertionError("missing file should fail")

    print("PHASE2_REVIEW_CHECKLIST_PACKET=self-test-pass")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_SELF_TEST_CASES={case_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE2_REVIEW_CHECKLIST_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0
    try:
        required_count, quote_count = validate_root(args.root)
    except ValueError as exc:
        print(f"PHASE2_REVIEW_CHECKLIST_PACKET=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE2_REVIEW_CHECKLIST_PACKET=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_REQUIRED_MARKER_COUNT={required_count}")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_BACKTICK_COUNT={quote_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
