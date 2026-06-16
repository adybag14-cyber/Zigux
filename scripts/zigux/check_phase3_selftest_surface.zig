const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_SELFTEST_SURFACE=pass";
pub const self_test_pass_marker = "PHASE3_SELFTEST_SURFACE_SELF_TEST=pass";

const README_MARKERS = [_][]const u8{
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-xarray-slot-slice.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "include/zigux/abi.h",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/helpers/bitmap_view.zig",
    "zigux/helpers/cpumask_view.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "scripts\\zigux/check_phase3_dev_t_starter_packet.zig",
    "scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig",
    "scripts\\zigux/check_phase3_xarray_slot.zig",
    "scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "scripts\\zigux/check_phase3_policy_dump.zig",
    "scripts\\zigux/check_phase3_catalog_selftest.zig",
    "scripts\\zigux/check_phase3_abi.zig",
    "scripts\\zigux/check_phase3_bitmap_cpumask.zig",
    "scripts/zigux/phase3_catalog.zig",
    "scripts\\zigux/validate_phase3.zig",
    "scripts\\zigux/validate_phase3_policy_unsafe_survey.zig",
    "scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "scripts\\zigux/validate_phase3_abi_header_family_survey.zig",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-export-uapi-layout-test",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "scripts\\zigux/validate_phase3_export_uapi_survey.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
};

const TESTS_README_MARKERS = [_][]const u8{
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "include/zigux/abi.h",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/abi.zig",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "scripts\\zigux/check_phase3_dev_t_starter_packet.zig",
    "scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "scripts\\zigux/validate_phase3_export_uapi_survey.zig",
    "scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "`zigux/tests/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the packet-local export/UAPI survey note, validator, focused export/UAPI layout replay, and direct C smoke companion family, so the tests-root reminder no longer carries a same-lane summary gap.",
    "keep the returned notifier-binding and focused export/UAPI layout replay pair explicit beside `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and `zigux/tests/phase3_export_uapi_layout_build.zig` as shipped tests-root evidence",
};

const REVIEW_CHECKLIST_MARKERS = [_][]const u8{
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "include/zigux/abi.h",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/abi.zig",
    "scripts\\zigux/check_phase3_dev_t_starter_packet.zig",
    "scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "scripts\\zigux/check_phase3_selftest_surface.zig",
    "scripts\\zigux/check_phase3_readme_tooling_inventory.zig",
    "scripts\\zigux/validate_phase3_validator_support_surface.zig",
    "scripts\\zigux/validate_phase3_export_uapi_survey.zig",
    "scripts\\zigux/validate_phase3_abi_header_family_survey.zig",
    "scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "scripts\\zigux/check_phase3_catalog_selftest.zig",
    "scripts/zigux/phase3_catalog.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "keep any broader shared replay or broader header-family completion claims framed as repo-reality gaps",
};

const VALIDATOR_SUPPORT_MARKERS = [_][]const u8{
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-xarray-slot-slice.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "scripts\\zigux/check_phase3_dev_t_starter_packet.zig",
    "scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig",
    "scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "zigux/bindings/version.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
    "scripts\\zigux/check_phase3_xarray_slot.zig",
    "zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "scripts\\zigux/validate_phase3_export_uapi_survey.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "scripts\\zigux/check_phase3_abi.zig",
    "scripts/zigux/phase3_catalog.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "scripts\\zigux/validate_phase3_abi_header_family_survey.zig",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "one focused helper-local `xarray_slot` classifier slice with both starter-packet and fixture-backed dump parity coverage",
    "It does not currently ship the broader shared Phase 3 replay packet itself, even though the shared `scripts\\zigux/validate_phase3.zig` validator entrypoint and `scripts\\zigux/check_phase3_abi.zig` shared ABI checker are directly readable on current `master`, current `master` also directly serves the bounded catalog helper at `scripts/zigux/phase3_catalog.zig` together with the shared ABI manifest at `zigux/tests/fixtures/phase3_abi_manifest.json`, and the aligned docs-root, review-checklist, tests-root, and scripts-root reminder surfaces now keep that broader shared-summary drift closed.",
    "Current `master` also directly serves the returned `Documentation/zigux/phase3-linux-zigux-header-governance.md` ownership note beside that adjacent export/UAPI layout replay pair, so the bounded Linux-facing relay is reviewable without turning this validator-support packet into the semantic owner of the separately landed header-family survey follow-through.",
    "Current `master` also directly serves the focused `Documentation/zigux/phase3-abi-h-boundary-next-step.md` note as the packet-local `include/zigux/abi.h` companion beside the dedicated `Documentation/zigux/phase3-abi-header-family-survey.md` plus `scripts\\zigux/validate_phase3_abi_header_family_survey.zig` follow-through and `Documentation/zigux/phase3-linux-zigux-header-governance.md`, but those returned same-family surfaces should not be used here to imply that the broader shared Phase 3 replay packet has returned.",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "scripts\\zigux/validate_phase3_validator_support_surface.zig",
    "Current `master` does still ship the separately readable shared validator entrypoint through `scripts\\zigux/validate_phase3.zig` together with the shared ABI checker through `scripts\\zigux/check_phase3_abi.zig`, and it also directly serves `scripts/zigux/phase3_catalog.zig` together with `zigux/tests/fixtures/phase3_abi_manifest.json`, but those shared validation, catalog, and manifest surfaces should not be used here to imply that the broader validator-support or shared replay packet has returned beyond that bounded survey-plus-next-step companion packet already enumerated here.",
    "`zigux/tests/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the packet-local export/UAPI survey note, validator, focused export/UAPI layout replay, and direct C smoke companion family, so keep any broader shared-summary follow-through parked unless a fresh reread reopens same-packet drift on current `master`.",
    "`Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root, review-checklist, tests-root, and scripts-root summaries, keeps the returned header-family survey follow-through explicit as a same-family companion, and records that no same-lane shared-summary drift remains on current `master`.",
    "broader export/UAPI survey, catalog, or shared Phase 3 replay packet",
    "make -C zigux phase3-low-level-wrappers-test",
};

const VALIDATOR_SUPPORT_EXACT_ONCE_MARKERS = [_][]const u8{
    "scripts\\zigux/validate_phase3_validator_support_surface.zig",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "scripts\\zigux/check_phase3_selftest_surface.zig",
    "zig run scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig --self-test",
    "scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig",
    "scripts\\zigux/check_phase3_readme_tooling_inventory.zig",
    "scripts\\zigux/check_phase3_shared_tests_routes.zig",
    "scripts\\zigux/validate_phase3_validator_support_surface.zig",
    "`scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig`",
    "scripts/zigux/validate_phase3_selftest.zig",
    "scripts/zigux/run_phase3_checks.zig",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "include/zigux/abi.h",
    "zigux/kernel/export_shim.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/bindings/abi.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zig run scripts\\zigux/check_phase3_readme_tooling_inventory.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig --self-test",
    "scripts\\zigux/check_phase3_catalog_selftest.zig",
    "scripts/zigux/phase3_catalog.zig",
    "scripts/zigux/check_phase3_wrapper_templates.zig",
    "scripts\\zigux/validate_phase3.zig",
    "scripts\\zigux/validate_phase3_abi_header_family_survey.zig",
    "still return missing on current `master`",
};

const SELFTEST_DRIVER_MARKERS = [_][]const u8{
    "Path(\"scripts\\zigux/check_phase3_dev_t_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_policy_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_policy_dump.zig\")",
    "Path(\"scripts\\zigux/validate_phase3.zig\")",
    "Path(\"scripts\\zigux/check_phase3_abi.zig\")",
    "Path(\"scripts\\zigux/check_phase3_abi_support_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig\")",
    "Path(\"scripts\\zigux/check_phase3_shared_tests_routes.zig\")",
    "Path(\"scripts\\zigux/check_phase3_readme_tooling_inventory.zig\")",
    "Path(\"scripts\\zigux/check_phase3_wrapper_templates.zig\")",
    "Path(\"scripts\\zigux/check_phase3_catalog_selftest.zig\")",
    "Path(\"scripts\\zigux/check_phase3_bitmap_cpumask.zig\")",
    "Path(\"scripts\\zigux/check_phase3_list_hlist_starter_packet.zig\")",
    "Path(\"scripts/zigux/run_phase3_checks.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_validator_support_surface.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_export_uapi_survey.zig\")",
    "Path(\"scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_abi_header_family_survey.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_policy_unsafe_survey.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_linux_zigux_header_governance.zig\")",
    "Path(\"scripts/zigux/check_phase3_wrapper_templates.zig\")",
    "Path(\"scripts\\zigux/check_phase3_selftest_surface.zig\")",
    "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=pass",
    "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST_CASE_COUNT=",
    "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass",
    "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST_CASE_COUNT=",
    "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass",
    "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT=",
    "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass",
    "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST_CASE_COUNT=",
    "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=pass",
    "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST_CASE_COUNT=",
    "PHASE3_WRAPPER_SELF_TEST=pass",
    "PHASE3_WRAPPER_SELF_TEST_CASE_COUNT=",
    "PHASE3_VALIDATE_SELFTEST=pass",
};

const SELFTEST_DRIVER_EXACT_ONCE_MARKERS = [_][]const u8{
    "Path(\"scripts/zigux/check_phase3_wrapper_templates.zig\")",
    "PHASE3_WRAPPER_SELF_TEST_CASE_COUNT=",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_readme_markers_path);
    const text_readme_markers = try guard.readUtf8File(io, allocator, text_readme_markers_path);
    defer allocator.free(text_readme_markers);
    for (README_MARKERS) |marker| try guard.requireMarker(text_readme_markers, marker);
    const text_tests_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_tests_readme_markers_path);
    const text_tests_readme_markers = try guard.readUtf8File(io, allocator, text_tests_readme_markers_path);
    defer allocator.free(text_tests_readme_markers);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text_tests_readme_markers, marker);
    const text_review_checklist_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_review_checklist_markers_path);
    const text_review_checklist_markers = try guard.readUtf8File(io, allocator, text_review_checklist_markers_path);
    defer allocator.free(text_review_checklist_markers);
    for (REVIEW_CHECKLIST_MARKERS) |marker| try guard.requireMarker(text_review_checklist_markers, marker);
    const text_validator_support_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_validator_support_markers_path);
    const text_validator_support_markers = try guard.readUtf8File(io, allocator, text_validator_support_markers_path);
    defer allocator.free(text_validator_support_markers);
    for (VALIDATOR_SUPPORT_MARKERS) |marker| try guard.requireMarker(text_validator_support_markers, marker);
    const text_validator_support_exact_once_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_validator_support_exact_once_markers_path);
    const text_validator_support_exact_once_markers = try guard.readUtf8File(io, allocator, text_validator_support_exact_once_markers_path);
    defer allocator.free(text_validator_support_exact_once_markers);
    for (VALIDATOR_SUPPORT_EXACT_ONCE_MARKERS) |marker| try guard.requireMarker(text_validator_support_exact_once_markers, marker);
    const text_scripts_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_scripts_readme_markers_path);
    const text_scripts_readme_markers = try guard.readUtf8File(io, allocator, text_scripts_readme_markers_path);
    defer allocator.free(text_scripts_readme_markers);
    for (SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text_scripts_readme_markers, marker);
    const text_selftest_driver_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_selftest_driver_markers_path);
    const text_selftest_driver_markers = try guard.readUtf8File(io, allocator, text_selftest_driver_markers_path);
    defer allocator.free(text_selftest_driver_markers);
    for (SELFTEST_DRIVER_MARKERS) |marker| try guard.requireMarker(text_selftest_driver_markers, marker);
    const text_selftest_driver_exact_once_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_selftest_driver_exact_once_markers_path);
    const text_selftest_driver_exact_once_markers = try guard.readUtf8File(io, allocator, text_selftest_driver_exact_once_markers_path);
    defer allocator.free(text_selftest_driver_exact_once_markers);
    for (SELFTEST_DRIVER_EXACT_ONCE_MARKERS) |marker| try guard.requireMarker(text_selftest_driver_exact_once_markers, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
