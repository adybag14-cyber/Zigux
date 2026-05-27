#!/usr/bin/env python3
"""Validate the current Phase 3 policy-and-unsafe survey packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")
POLICY_SLICE_PATH = Path("Documentation/zigux/phase3-policy-slice.md")
LOW_LEVEL_SURVEY_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
LAYOUT_ASSERT_PATH = Path("zigux/helpers/layout_assert.zig")
PANIC_POLICY_PATH = Path("zigux/helpers/panic_policy.zig")
ALLOCATOR_POLICY_PATH = Path("zigux/helpers/allocator_policy.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
MMIO_PATH = Path("zigux/helpers/mmio.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")
MANIFEST_PATH = Path("zigux/tests/phase3_policy_starter_packet_manifest.json")
POLICY_UNSAFE_REPLAY_PATH = Path("zigux/tests/phase3_policy_unsafe.zig")
POLICY_UNSAFE_REPLAY_BUILD_PATH = Path("zigux/tests/phase3_policy_unsafe_build.zig")
POLICY_DUMP_PATH = Path("zigux/tests/phase3_policy_dump.zig")
POLICY_DUMP_BUILD_PATH = Path("zigux/tests/phase3_policy_dump_build.zig")
POLICY_DUMP_EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_policy_dump_expected.txt")

BLOB_FIELDS = {
    "PHASE3_LAYOUT_ASSERT_BLOB_SHA": LAYOUT_ASSERT_PATH,
    "PHASE3_PANIC_POLICY_BLOB_SHA": PANIC_POLICY_PATH,
    "PHASE3_ALLOCATOR_POLICY_BLOB_SHA": ALLOCATOR_POLICY_PATH,
    "PHASE3_UNSAFE_POLICY_BLOB_SHA": UNSAFE_POLICY_PATH,
    "PHASE3_MMIO_BLOB_SHA": MMIO_PATH,
    "PHASE3_UNSAFE_BLOB_SHA": NARROW_PATH,
    "PHASE3_POLICY_SLICE_DOC_BLOB_SHA": POLICY_SLICE_PATH,
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_DOC_BLOB_SHA": LOW_LEVEL_SURVEY_PATH,
}

REQUIRED_NOTE_MARKERS = (
    "PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig",
    "PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig",
    "PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig",
    "PHASE3_UNSAFE_POLICY_PATH=zigux/helpers/unsafe_policy.zig",
    "PHASE3_MMIO_PATH=zigux/helpers/mmio.zig",
    "PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig",
    "PHASE3_POLICY_STARTER_PACKET_MANIFEST_PATH=zigux/tests/phase3_policy_starter_packet_manifest.json",
    "PHASE3_POLICY_PACKET_GATE=python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    "PHASE3_POLICY_PACKET_TEST_GATE=zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "PHASE3_POLICY_PACKET_MAKE_GATE=make -C zigux phase3-policy-starter-packet-test",
    "PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py",
    "PHASE3_POLICY_DUMP_MAKE_GATE=make -C zigux phase3-policy-dump",
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "PHASE3_POLICY_UNSAFE_SURVEY_GATE=python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "PHASE3_POLICY_UNSAFE_REPLAY_PATH=zigux/tests/phase3_policy_unsafe.zig",
    "PHASE3_POLICY_UNSAFE_REPLAY_BUILD_PATH=zigux/tests/phase3_policy_unsafe_build.zig",
    "PHASE3_POLICY_UNSAFE_REPLAY_TEST_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    "PHASE3_BOUNDARY_GAP=no-further-policy-unsafe-gap-beyond-keeping-the-helper-local-packet-dedicated-replay-pair-and-the-directly-coupled-low-level-wrapper-packet-aligned",
    "PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-layout-assert-panic-policy-allocator-policy-unsafe-policy-mmio-or-narrow-helper-surfaces-the-dedicated-policy-unsafe-replay-pair-or-the-dedicated-policy-unsafe-survey-gate-drift-again",
    "The blob markers above are therefore the authoritative current boundary evidence for this directly coupled policy-and-unsafe packet.",
)

REQUIRED_FILE_MARKERS = {
    POLICY_SLICE_PATH: (
        "PHASE3_POLICY_SLICE_FILE_COUNT=current master now carries one bounded policy helper slice with shared ABI bindings, three helper-local decoders, one reusable layout guard, one cross-check narrow-surface decoder plus whole-policy and byte-level review entry points, one machine-readable manifest, one focused self-check replay route, one dedicated policy-unsafe replay route, one focused dump replay route, one dump expectation fixture, and one dedicated dump validator",
        "PHASE3_POLICY_NEXT_SAFE_STEP=keep policy helper coverage bounded to layout assertions, manifest-backed replay, dedicated policy-unsafe replay, focused dump replay, and narrow-surface cross-checks before widening into mmio, low-level wrapper, or shared runtime-shim families",
        "zigux/tests/phase3_policy_unsafe.zig",
        "zigux/tests/phase3_policy_unsafe_build.zig",
        "zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    ),
    MANIFEST_PATH: (
        '"zigux/tests/phase3_policy_unsafe.zig"',
        '"zigux/tests/phase3_policy_unsafe_build.zig"',
        '"zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig"',
        '"this packet proves bounded policy decoding, dedicated policy-unsafe replay, survey gating, and dump replay only, not permanent-boundary completion"',
        '"keep the policy helper family bounded to layout assertions, manifest-backed replay, dedicated policy-unsafe replay evidence, dedicated policy-unsafe survey gating, and narrow-surface cross-checks before widening into mmio, low-level wrapper, or shared runtime-shim families"',
    ),
    POLICY_UNSAFE_REPLAY_PATH: (
        'test "phase3 policy unsafe replay decodes shared policy records" {',
        'test "phase3 policy unsafe replay keeps helper and narrow gates aligned" {',
        'test "phase3 policy unsafe replay keeps require gates fail closed" {',
        'test "phase3 policy unsafe replay keeps policy consequences explicit" {',
    ),
    POLICY_UNSAFE_REPLAY_BUILD_PATH: (
        '.root_source_file = b.path("phase3_policy_unsafe.zig"),',
        'root_module.addImport("panic_policy", panic_policy);',
        'root_module.addImport("allocator_policy", allocator_policy);',
        'root_module.addImport("unsafe_policy", unsafe_policy);',
        'root_module.addImport("narrow", narrow);',
        '"phase3-policy-unsafe-test"',
        '"Run the focused Phase 3 policy and unsafe replay"',
    ),
    POLICY_DUMP_PATH: (
        'const RawBridgeReplay = struct {',
        'fn rawBridgeReplay(policy: abi.InteropPolicy) RawBridgeReplay {',
        'const bridge_replay = rawBridgeReplay(policy);',
        '"bridge_read_ok={any}|bridge_write_ok={any}|narrow={s}|narrow_boundary={s}|narrow_surface={s}\\n",',
    ),
    POLICY_DUMP_BUILD_PATH: (
        '.root_source_file = b.path("../unsafe/narrow.zig"),',
        '.root_source_file = b.path("phase3_policy_dump.zig"),',
        'root_module.addImport("unsafe_policy", unsafe_policy);',
        'root_module.addImport("narrow_surface", narrow_surface);',
        '.name = "phase3-policy-dump",',
    ),
    POLICY_DUMP_EXPECTED_PATH: (
        "safe-default|panic=abort|allocator=caller_provided|init_flow=caller_prepared|explicit_caller=true|owned_state=false|reset_on_init=false|unsafe=none|boundary=typed_safe|surface=safe_only|typed_only=true|global_fallback=false|warn_only=false|mmio=false|raw_bridge=false|audit=false|bridge_read_ok=false|bridge_write_ok=false|narrow=none|narrow_boundary=typed_safe|narrow_surface=safe_only",
        "raw-bridge-warn|panic=warn|allocator=arena|init_flow=helper_owned_with_reset|explicit_caller=false|owned_state=true|reset_on_init=true|unsafe=raw_pointer_bridge|boundary=raw_pointer_bridge|surface=raw_pointer_bridge_only|typed_only=false|global_fallback=true|warn_only=true|mmio=false|raw_bridge=true|audit=true|bridge_read_ok=true|bridge_write_ok=true|narrow=raw_pointer_bridge|narrow_boundary=raw_pointer_bridge|narrow_surface=raw_pointer_bridge_only",
    ),
}

SAMPLE_FILE_TEXT = {
    POLICY_SLICE_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_SLICE_PATH]) + "\n",
    LOW_LEVEL_SURVEY_PATH: "# sample low-level survey\n",
    LAYOUT_ASSERT_PATH: "pub fn assertInteropPolicyLayout() LayoutError!void {}\n",
    PANIC_POLICY_PATH: "pub const Escalation = enum { immediate_abort, kernel_bug, warning_only };\n",
    ALLOCATOR_POLICY_PATH: "pub const InitFlow = enum { caller_prepared, helper_owned, helper_owned_with_reset };\n",
    UNSAFE_POLICY_PATH: "pub const AccessBoundary = enum { typed_safe, volatile_mmio_window, raw_pointer_bridge };\n",
    MMIO_PATH: "pub fn readInteropPolicy(comptime T: type, policy: anytype, ptr: anytype) !T { _ = policy; _ = ptr; return undefined; }\n",
    NARROW_PATH: "pub const Surface = enum { safe_only, mmio_only, raw_pointer_bridge_only };\n",
    MANIFEST_PATH: "\n".join(REQUIRED_FILE_MARKERS[MANIFEST_PATH]) + "\n",
    POLICY_UNSAFE_REPLAY_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_UNSAFE_REPLAY_PATH]) + "\n",
    POLICY_UNSAFE_REPLAY_BUILD_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_UNSAFE_REPLAY_BUILD_PATH]) + "\n",
    POLICY_DUMP_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_DUMP_PATH]) + "\n",
    POLICY_DUMP_BUILD_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_DUMP_BUILD_PATH]) + "\n",
    POLICY_DUMP_EXPECTED_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_DUMP_EXPECTED_PATH]) + "\n",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git_blob_sha(text: str) -> str:
    payload = text.encode("utf-8")
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def render_note(sample_files: dict[Path, str]) -> str:
    lines = ["# sample survey", *[f"- `{marker}`" for marker in REQUIRED_NOTE_MARKERS]]
    for field, path in BLOB_FIELDS.items():
        lines.append(f"- `{field}={git_blob_sha(sample_files[path])}`")
    lines.append("")
    return "\n".join(lines)


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    try:
        note_text = _read(repo_root / NOTE_PATH)
    except FileNotFoundError:
        return [f"missing repo file: {NOTE_PATH.as_posix()}"]

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(f"missing {NOTE_PATH.as_posix()} marker: {marker}")

    for field, relative_path in BLOB_FIELDS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        expected_line = f"{field}={git_blob_sha(text)}"
        if expected_line not in note_text:
            issues.append(f"wrong {NOTE_PATH.as_posix()} blob marker: expected {expected_line}")

    for relative_path, markers in REQUIRED_FILE_MARKERS.items():
        try:
            text = _read(repo_root / relative_path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    return issues


def populate_sample_repo(root: Path) -> None:
    sample_files = dict(SAMPLE_FILE_TEXT)
    sample_files[NOTE_PATH] = render_note(sample_files)
    for relative_path, text in sample_files.items():
        _write(root / relative_path, text)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_survey_") as temp_dir:
        root = Path(temp_dir)
        populate_sample_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        cases = (
            (NOTE_PATH, REQUIRED_NOTE_MARKERS[13], f"missing {NOTE_PATH.as_posix()} marker: {REQUIRED_NOTE_MARKERS[13]}"),
            (NOTE_PATH, REQUIRED_NOTE_MARKERS[18], f"missing {NOTE_PATH.as_posix()} marker: {REQUIRED_NOTE_MARKERS[18]}"),
            (POLICY_SLICE_PATH, REQUIRED_FILE_MARKERS[POLICY_SLICE_PATH][3], f"missing {POLICY_SLICE_PATH.as_posix()} marker: {REQUIRED_FILE_MARKERS[POLICY_SLICE_PATH][3]}"),
            (MANIFEST_PATH, REQUIRED_FILE_MARKERS[MANIFEST_PATH][2], f"missing {MANIFEST_PATH.as_posix()} marker: {REQUIRED_FILE_MARKERS[MANIFEST_PATH][2]}"),
            (POLICY_UNSAFE_REPLAY_PATH, REQUIRED_FILE_MARKERS[POLICY_UNSAFE_REPLAY_PATH][3], f"missing {POLICY_UNSAFE_REPLAY_PATH.as_posix()} marker: {REQUIRED_FILE_MARKERS[POLICY_UNSAFE_REPLAY_PATH][3]}"),
            (POLICY_UNSAFE_REPLAY_BUILD_PATH, REQUIRED_FILE_MARKERS[POLICY_UNSAFE_REPLAY_BUILD_PATH][5], f"missing {POLICY_UNSAFE_REPLAY_BUILD_PATH.as_posix()} marker: {REQUIRED_FILE_MARKERS[POLICY_UNSAFE_REPLAY_BUILD_PATH][5]}"),
        )

        for relative_path, marker, expected in cases:
            populate_sample_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            if expected not in issues:
                print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=fail")
                print(f"expected issue not reported: {expected}")
                return 1

        populate_sample_repo(root)
        path = root / POLICY_SLICE_PATH
        path.write_text(_read(path) + "drift\n", encoding="utf-8")
        issues = validate_repo(root)
        if not any(issue.startswith(f"wrong {NOTE_PATH.as_posix()} blob marker: expected PHASE3_POLICY_SLICE_DOC_BLOB_SHA=") for issue in issues):
            print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=fail")
            print("expected policy-slice blob drift was not reported")
            return 1

    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass")
    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 3 policy-and-unsafe survey packet.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_POLICY_UNSAFE_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    print("PHASE3_POLICY_UNSAFE_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
