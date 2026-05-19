#!/usr/bin/env python3
"""Fail-close the current Phase 3 low-level wrapper survey packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
ABI_SLICE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
CHECKER_PATH = Path("scripts/zigux/check-phase3-abi.py")
ATOMIC_PATH = Path("zigux/helpers/atomic.zig")
BARRIER_PATH = Path("zigux/helpers/barrier.zig")
MMIO_PATH = Path("zigux/helpers/mmio.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")
WRAPPER_REPLAY_PATH = Path("zigux/tests/phase3_low_level_wrappers.zig")
WRAPPER_BUILD_PATH = Path("zigux/tests/phase3_low_level_wrappers_build.zig")
SHARED_TESTS_README_PATH = Path("zigux/tests/README.md")
SHARED_TESTS_BUILD_PATH = Path("zigux/tests/build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
WRAPPER_BUILD_COMMAND = "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"

REQUIRED_MARKERS = {
    NOTE_PATH: (
        "PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, and current master now directly exposes one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, one shared narrow-unsafe decoder, this dedicated survey note, a dedicated survey validator, one focused low-level-wrapper replay shard, and one dedicated shared build companion",
        "PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; adjacent shared Phase 3 validator, shared ABI checker, shared ABI catalog helper, export/UAPI survey-validator, and catalog-selftest guard surfaces now read separately on current master, while the low-level-wrapper packet stays bounded to its own helper-local evidence",
        "PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through bounded to shared validation truthfulness around the directly coupled unsafe-policy companion, the dedicated build companion, the direct zig build phase3-low-level-wrappers-test replay route, and the shared tests-root reminder while the adjacent catalog-selftest guard stays outside this wrapper packet",
        "`zigux/helpers/atomic.zig`",
        "`zigux/helpers/barrier.zig`",
        "`zigux/helpers/mmio.zig`",
        "`zigux/helpers/unsafe_policy.zig`",
        "`zigux/unsafe/narrow.zig`",
        "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
        "`zigux/tests/phase3_low_level_wrappers.zig`",
        "`zigux/tests/phase3_low_level_wrappers_build.zig`",
        "`zigux/Makefile`",
        "`zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`",
        "`make -C zigux phase3-low-level-wrappers-test`",
        "The shared tests-root reminder in `zigux/tests/README.md` now keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig` explicit beside the starter, helper, policy, and layout-replay packet, so the low-level-wrapper survey no longer treats shared tests-root coverage as a separate missing follow-through.",
        "Current `master` also keeps `zigux/Makefile` and `make -C zigux phase3-low-level-wrappers-test` explicit beside the dedicated shared build companion, so the low-level-wrapper packet now has both the direct Zig replay command and the returned shared Makefile replay gate without widening into broader Phase 3 completion claims.",
        "That directly coupled build companion and the live `zigux/helpers/mmio.zig` helper both depend on `zigux/helpers/unsafe_policy.zig`, so the packet reminder needs to keep that helper-local unsafe-policy surface explicit instead of undercounting it as if the MMIO wrapper stood alone.",
        "Reviewers should treat the low-level wrapper family as materially landed as a bounded packet on current `master`: one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, the shared narrow-unsafe decoder, the dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, one returned shared Makefile replay gate, and one direct replay command are directly readable, while the separately readable Phase 3 catalog-selftest guard stays adjacent cross-packet support rather than extra low-level-wrapper proof.",
        "Current `master` now separately exposes the adjacent shared Phase 3 validator entrypoint through `scripts/zigux/validate-phase3.py`, the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, the shared ABI catalog helper through `scripts/zigux/phase3_catalog.py`, the export/UAPI boundary survey note through `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, the packet-local export/UAPI survey validator through `scripts/zigux/validate-phase3-export-uapi-survey.py`, the focused export/UAPI layout replay through `zigux/tests/phase3_export_uapi_layout.zig` plus `zigux/tests/phase3_export_uapi_layout_build.zig`, and the adjacent catalog-selftest guard through `scripts/zigux/check-phase3-catalog-selftest.py`, and those separate surfaces should stay framed as cross-packet support rather than as landed same-lane proof.",
    ),
    ABI_SLICE_PATH: (
        "one adjacent low-level-wrapper reminder surface built around the surviving atomic helper shard, one directly readable barrier helper companion, one directly readable MMIO helper companion, one directly readable helper-local unsafe-policy companion, the shared unsafe-scope decoder, the dedicated survey validator, one focused low-level-wrapper replay shard, and one dedicated shared build companion",
        "one adjacent low-level-wrapper reminder surface built around zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig, while the still-missing broader header-family survey follow-through remains the separate wider gap",
        "and it separately reaches one adjacent low-level-wrapper reminder surface through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; representative broader Phase 3 paths still remain absent, including scripts/zigux/validate-phase3-abi-header-family-survey.py and Documentation/zigux/phase3-abi-header-family-survey.md",
        "Current `master` still presents the honest same-lane outcome as a bounded starter-packet set plus a bounded shared ABI binding surface, one focused export-or-UAPI layout replay, and one bounded low-level-wrapper reminder surface, not as full Phase 3 completion.",
        "That reminder surface keeps one directly readable MMIO helper companion, the directly coupled helper-local `zigux/helpers/unsafe_policy.zig` companion, the manifest-backed shared ABI inventory companion, the shared validator entrypoint, the shared ABI checker, the Phase 3 catalog helper, the returned catalog-selftest guard, the export/UAPI survey validator, the returned linux-header governance companion, the dedicated survey validator, the focused replay shard, and the dedicated shared build companion explicit without implying that the broader header-family survey follow-through already ships.",
        "`zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`",
    ),
    CHECKER_PATH: (
        '"""Fail-close the current bounded Phase 3 shared ABI packet."""',
        'ABI_SLICE_NOTE = Path("Documentation/zigux/phase3-abi-slice.md")',
        'BINDING_ABI = Path("zigux/bindings/abi.zig")',
        'EXPORT_SHIM = Path("zigux/kernel/export_shim.zig")',
        'print("PHASE3_ABI_CHECK=pass")',
    ),
    ATOMIC_PATH: (
        "pub fn compareExchangeFailureOrderAllowed(success: Ordering, failure: Ordering) bool {",
    ),
    BARRIER_PATH: (
        "pub fn compiler() void {",
        "pub fn acquire() void {",
        "pub fn release() void {",
        "pub fn full() void {",
        "pub fn acquireRelease() void {",
        "pub fn fullFence() void {",
    ),
    MMIO_PATH: (
        "pub fn read(comptime T: type, ptr: *const volatile T) T {",
        "pub fn write(comptime T: type, ptr: *volatile T, value: T) void {",
        "pub fn exchange(comptime T: type, ptr: *volatile T, value: T) T {",
        "pub fn writeMasked(comptime T: type, ptr: *volatile T, clear_mask: T, set_mask: T) T {",
        "pub fn exchangeInteropPolicyBytes(",
        "pub fn writeMaskedInteropPolicyBytes(",
    ),
    UNSAFE_POLICY_PATH: (
        "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {",
        "pub fn permitsVolatileMmio(mode: abi.UnsafeScope) bool {",
        "pub fn permitsRawPointerBridge(mode: abi.UnsafeScope) bool {",
    ),
    NARROW_PATH: (
        "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {",
    ),
    WRAPPER_REPLAY_PATH: (
        'test "phase3 low-level wrappers keep atomic ordering, barriers, and MMIO handoffs aligned" {',
        'test "phase3 low-level wrappers keep masked MMIO updates explicit after compare-exchange setup" {',
        'test "phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff" {',
        'test "phase3 low-level wrappers keep MMIO byte-policy shorthand aligned with reserved-byte gates" {',
        'test "phase3 low-level wrappers keep atomic load-store exchange and MMIO echo explicit" {',
        'test "phase3 low-level wrappers keep exchange-style MMIO policy handoffs explicit" {',
    ),
    WRAPPER_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/atomic.zig"),',
        '.root_source_file = b.path("../helpers/barrier.zig"),',
        '.root_source_file = b.path("../helpers/mmio.zig"),',
        'root_module.addImport("atomic", atomic);',
        'root_module.addImport("barrier", barrier);',
        'mmio.addImport("abi_bindings", abi_bindings);',
        'mmio.addImport("unsafe_policy", unsafe_policy);',
        '"phase3-low-level-wrappers-test"',
    ),
    SHARED_TESTS_README_PATH: (
        "## Phase 3 shared substrate packet",
        "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
        "`scripts/zigux/validate-phase3-export-uapi-survey.py`",
        "`Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`",
        "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
        "`zigux/tests/phase3_low_level_wrappers.zig`",
        "`zigux/tests/phase3_low_level_wrappers_build.zig`",
        "`zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`",
        "`zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig`",
        "`zig build phase3-test --build-file zigux/tests/build.zig`",
    ),
    SHARED_TESTS_BUILD_PATH: (
        "fn addPhase3LowLevelWrappers(",
        '.root_source_file = b.path("../helpers/atomic.zig"),',
        '.root_source_file = b.path("../helpers/barrier.zig"),',
        '.root_source_file = b.path("../helpers/mmio.zig"),',
        '"phase3-low-level-wrappers"',
        '"phase3-test"',
        "phase3_low_level_wrapper_step.dependOn(&phase3_low_level_wrappers.step);",
        "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
    ),
    MAKEFILE_PATH: (
        "phase3-low-level-wrappers-test:",
        "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    WORKFLOW_PATH: (
        'name: Self-test current Phase 3 low-level wrapper survey validator',
        'run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test',
        'name: Check current Phase 3 low-level wrapper survey packet',
        'name: Run current Phase 3 low-level wrapper replay',
        'run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig',
    ),
}

SELF_TEST_CASES = (
    (
        NOTE_PATH,
        "PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, and current master now directly exposes one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, one shared narrow-unsafe decoder, this dedicated survey note, a dedicated survey validator, one focused low-level-wrapper replay shard, and one dedicated shared build companion",
    ),
    (
        NOTE_PATH,
        "PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; adjacent shared Phase 3 validator, shared ABI checker, shared ABI catalog helper, export/UAPI survey-validator, and catalog-selftest guard surfaces now read separately on current master, while the low-level-wrapper packet stays bounded to its own helper-local evidence",
    ),
    (
        NOTE_PATH,
        "PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through bounded to shared validation truthfulness around the directly coupled unsafe-policy companion, the dedicated build companion, the direct zig build phase3-low-level-wrappers-test replay route, and the shared tests-root reminder while the adjacent catalog-selftest guard stays outside this wrapper packet",
    ),
    (
        NOTE_PATH,
        "The shared tests-root reminder in `zigux/tests/README.md` now keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig` explicit beside the starter, helper, policy, and layout-replay packet, so the low-level-wrapper survey no longer treats shared tests-root coverage as a separate missing follow-through.",
    ),
    (
        NOTE_PATH,
        "Current `master` also keeps `zigux/Makefile` and `make -C zigux phase3-low-level-wrappers-test` explicit beside the dedicated shared build companion, so the low-level-wrapper packet now has both the direct Zig replay command and the returned shared Makefile replay gate without widening into broader Phase 3 completion claims.",
    ),
    (
        NOTE_PATH,
        "That directly coupled build companion and the live `zigux/helpers/mmio.zig` helper both depend on `zigux/helpers/unsafe_policy.zig`, so the packet reminder needs to keep that helper-local unsafe-policy surface explicit instead of undercounting it as if the MMIO wrapper stood alone.",
    ),
    (
        NOTE_PATH,
        "Current `master` now separately exposes the adjacent shared Phase 3 validator entrypoint through `scripts/zigux/validate-phase3.py`, the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, the shared ABI catalog helper through `scripts/zigux/phase3_catalog.py`, the export/UAPI boundary survey note through `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, the packet-local export/UAPI survey validator through `scripts/zigux/validate-phase3-export-uapi-survey.py`, the focused export/UAPI layout replay through `zigux/tests/phase3_export_uapi_layout.zig` plus `zigux/tests/phase3_export_uapi_layout_build.zig`, and the adjacent catalog-selftest guard through `scripts/zigux/check-phase3-catalog-selftest.py`, and those separate surfaces should stay framed as cross-packet support rather than as landed same-lane proof.",
    ),
    (
        ABI_SLICE_PATH,
        "That reminder surface keeps one directly readable MMIO helper companion, the directly coupled helper-local `zigux/helpers/unsafe_policy.zig` companion, the manifest-backed shared ABI inventory companion, the shared validator entrypoint, the shared ABI checker, the Phase 3 catalog helper, the returned catalog-selftest guard, the export/UAPI survey validator, the returned linux-header governance companion, the dedicated survey validator, the focused replay shard, and the dedicated shared build companion explicit without implying that the broader header-family survey follow-through already ships.",
    ),
    (
        CHECKER_PATH,
        'print("PHASE3_ABI_CHECK=pass")',
    ),
    (ATOMIC_PATH, "pub fn compareExchangeFailureOrderAllowed(success: Ordering, failure: Ordering) bool {"),
    (BARRIER_PATH, "pub fn compiler() void {"),
    (BARRIER_PATH, "pub fn acquire() void {"),
    (BARRIER_PATH, "pub fn full() void {"),
    (BARRIER_PATH, "pub fn fullFence() void {"),
    (MMIO_PATH, "pub fn read(comptime T: type, ptr: *const volatile T) T {"),
    (MMIO_PATH, "pub fn write(comptime T: type, ptr: *volatile T, value: T) void {"),
    (MMIO_PATH, "pub fn exchange(comptime T: type, ptr: *volatile T, value: T) T {"),
    (MMIO_PATH, "pub fn writeMasked(comptime T: type, ptr: *volatile T, clear_mask: T, set_mask: T) T {"),
    (MMIO_PATH, "pub fn exchangeInteropPolicyBytes("),
    (MMIO_PATH, "pub fn writeMaskedInteropPolicyBytes("),
    (UNSAFE_POLICY_PATH, "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {"),
    (UNSAFE_POLICY_PATH, "pub fn permitsVolatileMmio(mode: abi.UnsafeScope) bool {"),
    (NARROW_PATH, "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {"),
    (WRAPPER_REPLAY_PATH, 'test "phase3 low-level wrappers keep atomic ordering, barriers, and MMIO handoffs aligned" {'),
    (WRAPPER_REPLAY_PATH, 'test "phase3 low-level wrappers keep masked MMIO updates explicit after compare-exchange setup" {'),
    (WRAPPER_REPLAY_PATH, 'test "phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff" {'),
    (WRAPPER_REPLAY_PATH, 'test "phase3 low-level wrappers keep MMIO byte-policy shorthand aligned with reserved-byte gates" {'),
    (WRAPPER_REPLAY_PATH, 'test "phase3 low-level wrappers keep atomic load-store exchange and MMIO echo explicit" {'),
    (WRAPPER_REPLAY_PATH, 'test "phase3 low-level wrappers keep exchange-style MMIO policy handoffs explicit" {'),
    (WRAPPER_BUILD_PATH, '.root_source_file = b.path("../helpers/atomic.zig"),'),
    (WRAPPER_BUILD_PATH, '.root_source_file = b.path("../helpers/barrier.zig"),'),
    (WRAPPER_BUILD_PATH, '.root_source_file = b.path("../helpers/mmio.zig"),'),
    (WRAPPER_BUILD_PATH, 'root_module.addImport("atomic", atomic);'),
    (WRAPPER_BUILD_PATH, 'root_module.addImport("barrier", barrier);'),
    (WRAPPER_BUILD_PATH, 'mmio.addImport("abi_bindings", abi_bindings);'),
    (WRAPPER_BUILD_PATH, 'mmio.addImport("unsafe_policy", unsafe_policy);'),
    (WRAPPER_BUILD_PATH, '"phase3-low-level-wrappers-test"'),
    (SHARED_TESTS_README_PATH, "## Phase 3 shared substrate packet"),
    (SHARED_TESTS_README_PATH, "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`"),
    (SHARED_TESTS_README_PATH, "`scripts/zigux/validate-phase3-export-uapi-survey.py`"),
    (SHARED_TESTS_README_PATH, "`Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`"),
    (SHARED_TESTS_README_PATH, "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`"),
    (SHARED_TESTS_README_PATH, "`zigux/tests/phase3_low_level_wrappers.zig`"),
    (SHARED_TESTS_README_PATH, "`zigux/tests/phase3_low_level_wrappers_build.zig`"),
    (SHARED_TESTS_README_PATH, "`zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`"),
    (SHARED_TESTS_README_PATH, "`zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig`"),
    (SHARED_TESTS_README_PATH, "`zig build phase3-test --build-file zigux/tests/build.zig`"),
    (SHARED_TESTS_BUILD_PATH, "fn addPhase3LowLevelWrappers("),
    (SHARED_TESTS_BUILD_PATH, '"phase3-low-level-wrappers"'),
    (SHARED_TESTS_BUILD_PATH, '"phase3-test"'),
    (SHARED_TESTS_BUILD_PATH, "phase3_low_level_wrapper_step.dependOn(&phase3_low_level_wrappers.step);"),
    (SHARED_TESTS_BUILD_PATH, "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);"),
    (MAKEFILE_PATH, "phase3-low-level-wrappers-test:"),
    (MAKEFILE_PATH, "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"),
    (WORKFLOW_PATH, 'name: Self-test current Phase 3 low-level wrapper survey validator'),
    (WORKFLOW_PATH, 'run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test'),
    (WORKFLOW_PATH, 'name: Check current Phase 3 low-level wrapper survey packet'),
    (WORKFLOW_PATH, 'name: Run current Phase 3 low-level wrapper replay'),
    (WORKFLOW_PATH, 'run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig'),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\\n".join(markers) + "\\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_wrapper_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("\\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 low-level wrapper survey packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 low-level wrapper survey packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
