const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_README_TOOLING_INVENTORY=pass";
pub const self_test_pass_marker = "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass";

const RUNNER_MARKER = [_][]const u8{
    "scripts/zigux/run_phase3_checks.zig",
};

const SHARED_TESTS_ROUTES_MARKER = [_][]const u8{
    "scripts\\zigux/check_phase3_shared_tests_routes.zig",
};

const ABI_MANIFEST_REPLAY_ROUTES_MARKER = [_][]const u8{
    "scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig",
};

const ABI_MANIFEST_REPLAY_ROUTES_SELFTEST_MARKER = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig --self-test",
};

const HEADER_MARKER = [_][]const u8{
    "include/linux/zigux.h",
};

const UAPI_MARKER = [_][]const u8{
    "zigux/uapi/dev_t.zig",
};

const NOTIFIER_BINDING_MARKER = [_][]const u8{
    "zigux/bindings/notifier_abi.zig",
};

const VALIDATOR_SUPPORT_NOTE_MARKER = [_][]const u8{
    "Documentation/zigux/phase3-validator-support-surface.md",
};

const SELFTEST_SURFACE_MARKER = [_][]const u8{
    "scripts\\zigux/check_phase3_selftest_surface.zig",
};

const XARRAY_SLOT_NOTE_MARKER = [_][]const u8{
    "Documentation/zigux/phase3-xarray-slot-slice.md",
};

const POLICY_UNSAFE_SURVEY_NOTE_MARKER = [_][]const u8{
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
};

const XARRAY_SLOT_CHECK_MARKER = [_][]const u8{
    "scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig",
};

const POLICY_DUMP_CHECK_MARKER = [_][]const u8{
    "scripts\\zigux/check_phase3_policy_dump.zig",
};

const POLICY_UNSAFE_SURVEY_VALIDATOR_MARKER = [_][]const u8{
    "scripts\\zigux/validate_phase3_policy_unsafe_survey.zig",
};

const MMIO_HELPER_MARKER = [_][]const u8{
    "zigux/helpers/mmio.zig",
};

const LOW_LEVEL_WRAPPER_SURVEY_VALIDATOR_MARKER = [_][]const u8{
    "scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
};

const LOW_LEVEL_WRAPPER_SURVEY_SELFTEST_MARKER = [_][]const u8{
    "zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig --self-test",
};

const LOW_LEVEL_WRAPPER_REPLAY_MARKER = [_][]const u8{
    "zigux/tests/phase3_low_level_wrappers.zig",
};

const LOW_LEVEL_WRAPPER_BUILD_MARKER = [_][]const u8{
    "zigux/tests/phase3_low_level_wrappers_build.zig",
};

const EXPORT_UAPI_LAYOUT_REPLAY_MARKER = [_][]const u8{
    "zigux/tests/phase3_export_uapi_layout.zig",
};

const EXPORT_UAPI_LAYOUT_BUILD_MARKER = [_][]const u8{
    "zigux/tests/phase3_export_uapi_layout_build.zig",
};

const EXPORT_UAPI_LAYOUT_BUILD_ROUTE_MARKER = [_][]const u8{
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
};

const EXPORT_UAPI_C_HEADER_SMOKE_CHECK_MARKER = [_][]const u8{
    "scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig",
};

const EXPORT_UAPI_C_HEADER_SMOKE_ROUTE_MARKER = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig",
};

const EXPORT_UAPI_C_HEADER_SMOKE_REPLAY_MARKER = [_][]const u8{
    "zigux/tests/phase3_export_uapi_c_header_smoke.c",
};

const WORKFLOW_MARKER = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const EXPORT_UAPI_SURVEY_NOTE_MARKER = [_][]const u8{
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
};

const EXPORT_UAPI_SURVEY_VALIDATOR_MARKER = [_][]const u8{
    "scripts\\zigux/validate_phase3_export_uapi_survey.zig",
};

const HEADER_GOVERNANCE_VALIDATOR_MARKER = [_][]const u8{
    "scripts\\zigux/validate_phase3_linux_zigux_header_governance.zig",
};

const HEADER_GOVERNANCE_VALIDATOR_SELFTEST_MARKER = [_][]const u8{
    "zig run scripts\\zigux/validate_phase3_linux_zigux_header_governance.zig --self-test",
};

const CATALOG_SELFTEST_GAP_MARKER = [_][]const u8{
    "scripts\\zigux/check_phase3_catalog_selftest.zig",
};

const CATALOG_TOOL_MARKER = [_][]const u8{
    "scripts/zigux/phase3_catalog.zig",
};

const WRAPPER_GENERATION_GAP_MARKER = [_][]const u8{
    "scripts/zigux/check_phase3_wrapper_templates.zig",
};

const WRAPPER_TEMPLATE_CHECK_MARKER = [_][]const u8{
    "scripts\\zigux/check_phase3_wrapper_templates.zig",
};

const WRAPPER_TEMPLATE_CHECK_SELFTEST_MARKER = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_wrapper_templates.zig --self-test",
};

const SHARED_VALIDATOR_MARKER = [_][]const u8{
    "scripts\\zigux/validate_phase3.zig",
};

const ABI_CHECK_MARKER = [_][]const u8{
    "scripts\\zigux/check_phase3_abi.zig",
};

const ABI_SUPPORT_PACKET_MARKER = [_][]const u8{
    "scripts\\zigux/check_phase3_abi_support_packet.zig",
};

const FIXTURE_MANIFEST_MARKER = [_][]const u8{
    "zigux/tests/fixtures/phase3_abi_manifest.json",
};

const XARRAY_SLOT_HELPER_MARKER = [_][]const u8{
    "zigux/helpers/xarray_slot_view.zig",
};

const XARRAY_SLOT_STARTER_MARKER = [_][]const u8{
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
};

const XARRAY_SLOT_STARTER_BUILD_MARKER = [_][]const u8{
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
};

const SHARED_TESTS_BUILD_MARKER = [_][]const u8{
    "zigux/tests/build.zig",
};

const XARRAY_SLOT_BUILD_ROUTE_MARKER = [_][]const u8{
    "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
};

const POLICY_DUMP_REPLAY_MARKER = [_][]const u8{
    "zigux/tests/phase3_policy_dump.zig",
};

const POLICY_DUMP_BUILD_MARKER = [_][]const u8{
    "zigux/tests/phase3_policy_dump_build.zig",
};

const POLICY_DUMP_BUILD_ROUTE_MARKER = [_][]const u8{
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
};

const HEADER_FAMILY_VALIDATOR_GAP_MARKER = [_][]const u8{
    "scripts\\zigux/validate_phase3_abi_header_family_survey.zig",
};

const HEADER_FAMILY_NOTE_GAP_MARKER = [_][]const u8{
    "Documentation/zigux/phase3-abi-header-family-survey.md",
};

const HEADER_FAMILY_NEXT_STEP_GAP_MARKER = [_][]const u8{
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
};

const HEADER_FAMILY_RETURNED_SURFACES_MARKER = [_][]const u8{
    "`scripts\\zigux/validate_phase3_abi_header_family_survey.zig` and `Documentation/zigux/phase3-abi-header-family-survey.md` are directly readable on current `master`, so keep the bounded header-family survey follow-through explicit beside the export/UAPI layout replay and shared ABI inventory instead of leaving those two surfaces in repo-reality-gap wording",
};

const HEADER_FAMILY_NEXT_STEP_REMINDER_MARKER = [_][]const u8{
    "`Documentation/zigux/phase3-abi-h-boundary-next-step.md` is directly readable on current `master`, so keep that focused abi.h next-step follow-through explicit beside the bounded header-family survey, the shared ABI inventory, and the export/UAPI layout replay instead of leaving it in repo-reality-gap wording",
};

const REQUIRED_MARKERS = [_][]const u8{
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "zig run scripts\\zigux/check_phase3_readme_tooling_inventory.zig --self-test",
    "zig run scripts\\zigux/check_phase3_readme_tooling_inventory.zig",
    "scripts\\zigux/check_phase3_selftest_surface.zig",
    "scripts\\zigux/check_phase3_shared_tests_routes.zig",
    "scripts\\zigux/validate_phase3_validator_support_surface.zig",
    "scripts\\zigux/validate_phase3_export_uapi_survey.zig",
    "scripts/zigux/validate_phase3_selftest.zig",
    "scripts/zigux/run_phase3_checks.zig",
    "scripts\\zigux/validate_phase3.zig",
    "scripts/zigux/phase3_catalog.zig",
    "scripts\\zigux/check_phase3_catalog_selftest.zig",
    "scripts\\zigux/check_phase3_dev_t_starter_packet.zig",
    "scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "include/zigux/abi.h",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/bindings/abi.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/uapi/version.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/build.zig",
    "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    ".github/workflows/zigux-bootstrap.yml",
};

const README_MARKER_CASES = [_][]const u8{
    "expected missing runner README marker was not reported",
    "expected missing shared-tests-routes README marker was not reported",
    "expected missing manifest-replay self-test README marker was not reported",
    "expected missing manifest-replay README marker was not reported",
    "expected missing header README marker was not reported",
    "expected missing UAPI README marker was not reported",
    "expected missing notifier-binding README marker was not reported",
    "expected missing validator-support note README marker was not reported",
    "expected missing selftest-surface README marker was not reported",
    "expected missing xarray-slot note README marker was not reported",
    "expected missing policy-unsafe survey note README marker was not reported",
    "expected missing xarray-slot checker README marker was not reported",
    "expected missing policy-dump checker README marker was not reported",
    "expected missing policy-unsafe validator README marker was not reported",
    "expected missing header-governance self-test README marker was not reported",
    "expected missing header-governance validator README marker was not reported",
    "expected missing export-uapi c-header smoke checker README marker was not reported",
    "expected missing export-uapi c-header smoke route README marker was not reported",
    "expected missing export-uapi c-header smoke replay README marker was not reported",
    "expected missing MMIO helper README marker was not reported",
    "expected missing low-level-wrapper survey validator README marker was not reported",
    "expected missing low-level-wrapper survey self-test README marker was not reported",
    "expected missing low-level-wrapper replay README marker was not reported",
    "expected missing low-level-wrapper build README marker was not reported",
    "expected missing export-uapi-layout replay README marker was not reported",
    "expected missing export-uapi-layout build README marker was not reported",
    "expected missing export-uapi-layout build-route README marker was not reported",
    "expected missing workflow README marker was not reported",
    "expected missing export-uapi survey note README marker was not reported",
    "expected missing export-uapi survey validator README marker was not reported",
    "expected missing catalog-selftest guard README marker was not reported",
    "expected missing catalog tool README marker was not reported",
    "expected missing wrapper-generation gap README marker was not reported",
    "expected missing wrapper-template self-test README marker was not reported",
    "expected missing wrapper-template checker README marker was not reported",
    "expected missing shared validator README marker was not reported",
    "expected missing shared ABI checker README marker was not reported",
    "expected missing shared ABI support-packet README marker was not reported",
    "expected missing fixture-manifest README marker was not reported",
    "expected missing xarray-slot helper README marker was not reported",
    "expected missing xarray-slot starter README marker was not reported",
    "expected missing xarray-slot starter build README marker was not reported",
    "expected missing shared tests build README marker was not reported",
    "expected missing xarray-slot build-route README marker was not reported",
    "expected missing policy-dump replay README marker was not reported",
    "expected missing policy-dump build README marker was not reported",
    "expected missing policy-dump build-route README marker was not reported",
    "expected missing header-family validator gap README marker was not reported",
    "expected missing header-family note gap README marker was not reported",
    "expected missing header-family next-step gap README marker was not reported",
    "expected missing header-family returned-surfaces README marker was not reported",
    "expected missing header-family next-step reminder README marker was not reported",
};

const FILE_CASES = [_][]const u8{
    "expected missing runner file was not reported",
    "expected missing shared-tests-routes file was not reported",
    "expected missing manifest-replay-routes file was not reported",
    "expected missing binding file was not reported",
    "expected missing notifier-binding file was not reported",
    "expected missing narrow-unsafe file was not reported",
    "expected missing UAPI file was not reported",
    "expected missing catalog tool file was not reported",
    "expected missing catalog-selftest guard file was not reported",
    "expected missing generated-wrapper file was not reported",
    "expected missing wrapper-template checker file was not reported",
    "expected missing fixture manifest file was not reported",
    "expected missing header-family validator file was not reported",
    "expected missing header-family survey note was not reported",
    "expected missing header-family next-step note was not reported",
    "expected missing header-governance validator file was not reported",
    "expected missing low-level-wrapper survey validator file was not reported",
    "expected missing low-level-wrapper replay file was not reported",
    "expected missing low-level-wrapper build file was not reported",
    "expected missing export-uapi-layout replay file was not reported",
    "expected missing export-uapi-layout build file was not reported",
    "expected missing export-uapi c-header smoke checker file was not reported",
    "expected missing export-uapi c-header smoke replay file was not reported",
    "expected missing workflow file was not reported",
    "expected missing export-uapi survey note file was not reported",
    "expected missing export-uapi survey validator file was not reported",
    "expected missing starter build file was not reported",
    "expected missing policy-dump replay file was not reported",
    "expected missing policy-dump build file was not reported",
    "expected missing xarray-slot helper file was not reported",
    "expected missing xarray-slot starter file was not reported",
    "expected missing xarray-slot starter build file was not reported",
    "expected missing xarray-slot checker file was not reported",
    "expected missing shared tests build file was not reported",
    "expected missing shared ABI replay file was not reported",
    "expected missing shared ABI dump replay file was not reported",
    "expected missing shared validator file was not reported",
    "expected missing shared ABI checker file was not reported",
    "expected missing shared ABI support-packet file was not reported",
    "Documentation/zigux/phase3-policy-slice.mdexpected missing policy-slice file was not reported",
    "expected missing xarray-slot note file was not reported",
    "expected missing policy-unsafe survey note was not reported",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.mdexpected missing low-level-wrapper survey note was not reported",
    "include/zigux/abi.hexpected missing ABI header file was not reported",
    "expected missing policy-dump checker file was not reported",
    "expected missing policy-unsafe survey validator file was not reported",
    "zigux/helpers/unsafe_policy.zigexpected missing unsafe-policy helper file was not reported",
    "zigux/helpers/atomic.zigexpected missing atomic helper file was not reported",
    "zigux/helpers/barrier.zigexpected missing barrier helper file was not reported",
    "zigux/helpers/mmio.zigexpected missing MMIO helper file was not reported",
    "zigux/kernel/export_shim.zigexpected missing export-shim file was not reported",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_runner_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_runner_marker_path);
    const text_runner_marker = try guard.readUtf8File(io, allocator, text_runner_marker_path);
    defer allocator.free(text_runner_marker);
    for (RUNNER_MARKER) |marker| try guard.requireMarker(text_runner_marker, marker);
    const text_shared_tests_routes_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_shared_tests_routes_marker_path);
    const text_shared_tests_routes_marker = try guard.readUtf8File(io, allocator, text_shared_tests_routes_marker_path);
    defer allocator.free(text_shared_tests_routes_marker);
    for (SHARED_TESTS_ROUTES_MARKER) |marker| try guard.requireMarker(text_shared_tests_routes_marker, marker);
    const text_abi_manifest_replay_routes_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_abi_manifest_replay_routes_marker_path);
    const text_abi_manifest_replay_routes_marker = try guard.readUtf8File(io, allocator, text_abi_manifest_replay_routes_marker_path);
    defer allocator.free(text_abi_manifest_replay_routes_marker);
    for (ABI_MANIFEST_REPLAY_ROUTES_MARKER) |marker| try guard.requireMarker(text_abi_manifest_replay_routes_marker, marker);
    const text_abi_manifest_replay_routes_selftest_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_abi_manifest_replay_routes_selftest_marker_path);
    const text_abi_manifest_replay_routes_selftest_marker = try guard.readUtf8File(io, allocator, text_abi_manifest_replay_routes_selftest_marker_path);
    defer allocator.free(text_abi_manifest_replay_routes_selftest_marker);
    for (ABI_MANIFEST_REPLAY_ROUTES_SELFTEST_MARKER) |marker| try guard.requireMarker(text_abi_manifest_replay_routes_selftest_marker, marker);
    const text_header_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_header_marker_path);
    const text_header_marker = try guard.readUtf8File(io, allocator, text_header_marker_path);
    defer allocator.free(text_header_marker);
    for (HEADER_MARKER) |marker| try guard.requireMarker(text_header_marker, marker);
    const text_uapi_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_uapi_marker_path);
    const text_uapi_marker = try guard.readUtf8File(io, allocator, text_uapi_marker_path);
    defer allocator.free(text_uapi_marker);
    for (UAPI_MARKER) |marker| try guard.requireMarker(text_uapi_marker, marker);
    const text_notifier_binding_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_notifier_binding_marker_path);
    const text_notifier_binding_marker = try guard.readUtf8File(io, allocator, text_notifier_binding_marker_path);
    defer allocator.free(text_notifier_binding_marker);
    for (NOTIFIER_BINDING_MARKER) |marker| try guard.requireMarker(text_notifier_binding_marker, marker);
    const text_validator_support_note_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_validator_support_note_marker_path);
    const text_validator_support_note_marker = try guard.readUtf8File(io, allocator, text_validator_support_note_marker_path);
    defer allocator.free(text_validator_support_note_marker);
    for (VALIDATOR_SUPPORT_NOTE_MARKER) |marker| try guard.requireMarker(text_validator_support_note_marker, marker);
    const text_selftest_surface_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_selftest_surface_marker_path);
    const text_selftest_surface_marker = try guard.readUtf8File(io, allocator, text_selftest_surface_marker_path);
    defer allocator.free(text_selftest_surface_marker);
    for (SELFTEST_SURFACE_MARKER) |marker| try guard.requireMarker(text_selftest_surface_marker, marker);
    const text_xarray_slot_note_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_xarray_slot_note_marker_path);
    const text_xarray_slot_note_marker = try guard.readUtf8File(io, allocator, text_xarray_slot_note_marker_path);
    defer allocator.free(text_xarray_slot_note_marker);
    for (XARRAY_SLOT_NOTE_MARKER) |marker| try guard.requireMarker(text_xarray_slot_note_marker, marker);
    const text_policy_unsafe_survey_note_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_policy_unsafe_survey_note_marker_path);
    const text_policy_unsafe_survey_note_marker = try guard.readUtf8File(io, allocator, text_policy_unsafe_survey_note_marker_path);
    defer allocator.free(text_policy_unsafe_survey_note_marker);
    for (POLICY_UNSAFE_SURVEY_NOTE_MARKER) |marker| try guard.requireMarker(text_policy_unsafe_survey_note_marker, marker);
    const text_xarray_slot_check_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_xarray_slot_check_marker_path);
    const text_xarray_slot_check_marker = try guard.readUtf8File(io, allocator, text_xarray_slot_check_marker_path);
    defer allocator.free(text_xarray_slot_check_marker);
    for (XARRAY_SLOT_CHECK_MARKER) |marker| try guard.requireMarker(text_xarray_slot_check_marker, marker);
    const text_policy_dump_check_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_policy_dump_check_marker_path);
    const text_policy_dump_check_marker = try guard.readUtf8File(io, allocator, text_policy_dump_check_marker_path);
    defer allocator.free(text_policy_dump_check_marker);
    for (POLICY_DUMP_CHECK_MARKER) |marker| try guard.requireMarker(text_policy_dump_check_marker, marker);
    const text_policy_unsafe_survey_validator_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_policy_unsafe_survey_validator_marker_path);
    const text_policy_unsafe_survey_validator_marker = try guard.readUtf8File(io, allocator, text_policy_unsafe_survey_validator_marker_path);
    defer allocator.free(text_policy_unsafe_survey_validator_marker);
    for (POLICY_UNSAFE_SURVEY_VALIDATOR_MARKER) |marker| try guard.requireMarker(text_policy_unsafe_survey_validator_marker, marker);
    const text_mmio_helper_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_mmio_helper_marker_path);
    const text_mmio_helper_marker = try guard.readUtf8File(io, allocator, text_mmio_helper_marker_path);
    defer allocator.free(text_mmio_helper_marker);
    for (MMIO_HELPER_MARKER) |marker| try guard.requireMarker(text_mmio_helper_marker, marker);
    const text_low_level_wrapper_survey_validator_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_low_level_wrapper_survey_validator_marker_path);
    const text_low_level_wrapper_survey_validator_marker = try guard.readUtf8File(io, allocator, text_low_level_wrapper_survey_validator_marker_path);
    defer allocator.free(text_low_level_wrapper_survey_validator_marker);
    for (LOW_LEVEL_WRAPPER_SURVEY_VALIDATOR_MARKER) |marker| try guard.requireMarker(text_low_level_wrapper_survey_validator_marker, marker);
    const text_low_level_wrapper_survey_selftest_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_low_level_wrapper_survey_selftest_marker_path);
    const text_low_level_wrapper_survey_selftest_marker = try guard.readUtf8File(io, allocator, text_low_level_wrapper_survey_selftest_marker_path);
    defer allocator.free(text_low_level_wrapper_survey_selftest_marker);
    for (LOW_LEVEL_WRAPPER_SURVEY_SELFTEST_MARKER) |marker| try guard.requireMarker(text_low_level_wrapper_survey_selftest_marker, marker);
    const text_low_level_wrapper_replay_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_low_level_wrapper_replay_marker_path);
    const text_low_level_wrapper_replay_marker = try guard.readUtf8File(io, allocator, text_low_level_wrapper_replay_marker_path);
    defer allocator.free(text_low_level_wrapper_replay_marker);
    for (LOW_LEVEL_WRAPPER_REPLAY_MARKER) |marker| try guard.requireMarker(text_low_level_wrapper_replay_marker, marker);
    const text_low_level_wrapper_build_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_low_level_wrapper_build_marker_path);
    const text_low_level_wrapper_build_marker = try guard.readUtf8File(io, allocator, text_low_level_wrapper_build_marker_path);
    defer allocator.free(text_low_level_wrapper_build_marker);
    for (LOW_LEVEL_WRAPPER_BUILD_MARKER) |marker| try guard.requireMarker(text_low_level_wrapper_build_marker, marker);
    const text_export_uapi_layout_replay_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_export_uapi_layout_replay_marker_path);
    const text_export_uapi_layout_replay_marker = try guard.readUtf8File(io, allocator, text_export_uapi_layout_replay_marker_path);
    defer allocator.free(text_export_uapi_layout_replay_marker);
    for (EXPORT_UAPI_LAYOUT_REPLAY_MARKER) |marker| try guard.requireMarker(text_export_uapi_layout_replay_marker, marker);
    const text_export_uapi_layout_build_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_export_uapi_layout_build_marker_path);
    const text_export_uapi_layout_build_marker = try guard.readUtf8File(io, allocator, text_export_uapi_layout_build_marker_path);
    defer allocator.free(text_export_uapi_layout_build_marker);
    for (EXPORT_UAPI_LAYOUT_BUILD_MARKER) |marker| try guard.requireMarker(text_export_uapi_layout_build_marker, marker);
    const text_export_uapi_layout_build_route_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_export_uapi_layout_build_route_marker_path);
    const text_export_uapi_layout_build_route_marker = try guard.readUtf8File(io, allocator, text_export_uapi_layout_build_route_marker_path);
    defer allocator.free(text_export_uapi_layout_build_route_marker);
    for (EXPORT_UAPI_LAYOUT_BUILD_ROUTE_MARKER) |marker| try guard.requireMarker(text_export_uapi_layout_build_route_marker, marker);
    const text_export_uapi_c_header_smoke_check_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_export_uapi_c_header_smoke_check_marker_path);
    const text_export_uapi_c_header_smoke_check_marker = try guard.readUtf8File(io, allocator, text_export_uapi_c_header_smoke_check_marker_path);
    defer allocator.free(text_export_uapi_c_header_smoke_check_marker);
    for (EXPORT_UAPI_C_HEADER_SMOKE_CHECK_MARKER) |marker| try guard.requireMarker(text_export_uapi_c_header_smoke_check_marker, marker);
    const text_export_uapi_c_header_smoke_route_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_export_uapi_c_header_smoke_route_marker_path);
    const text_export_uapi_c_header_smoke_route_marker = try guard.readUtf8File(io, allocator, text_export_uapi_c_header_smoke_route_marker_path);
    defer allocator.free(text_export_uapi_c_header_smoke_route_marker);
    for (EXPORT_UAPI_C_HEADER_SMOKE_ROUTE_MARKER) |marker| try guard.requireMarker(text_export_uapi_c_header_smoke_route_marker, marker);
    const text_export_uapi_c_header_smoke_replay_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_export_uapi_c_header_smoke_replay_marker_path);
    const text_export_uapi_c_header_smoke_replay_marker = try guard.readUtf8File(io, allocator, text_export_uapi_c_header_smoke_replay_marker_path);
    defer allocator.free(text_export_uapi_c_header_smoke_replay_marker);
    for (EXPORT_UAPI_C_HEADER_SMOKE_REPLAY_MARKER) |marker| try guard.requireMarker(text_export_uapi_c_header_smoke_replay_marker, marker);
    const text_workflow_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_workflow_marker_path);
    const text_workflow_marker = try guard.readUtf8File(io, allocator, text_workflow_marker_path);
    defer allocator.free(text_workflow_marker);
    for (WORKFLOW_MARKER) |marker| try guard.requireMarker(text_workflow_marker, marker);
    const text_export_uapi_survey_note_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_export_uapi_survey_note_marker_path);
    const text_export_uapi_survey_note_marker = try guard.readUtf8File(io, allocator, text_export_uapi_survey_note_marker_path);
    defer allocator.free(text_export_uapi_survey_note_marker);
    for (EXPORT_UAPI_SURVEY_NOTE_MARKER) |marker| try guard.requireMarker(text_export_uapi_survey_note_marker, marker);
    const text_export_uapi_survey_validator_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_export_uapi_survey_validator_marker_path);
    const text_export_uapi_survey_validator_marker = try guard.readUtf8File(io, allocator, text_export_uapi_survey_validator_marker_path);
    defer allocator.free(text_export_uapi_survey_validator_marker);
    for (EXPORT_UAPI_SURVEY_VALIDATOR_MARKER) |marker| try guard.requireMarker(text_export_uapi_survey_validator_marker, marker);
    const text_header_governance_validator_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_header_governance_validator_marker_path);
    const text_header_governance_validator_marker = try guard.readUtf8File(io, allocator, text_header_governance_validator_marker_path);
    defer allocator.free(text_header_governance_validator_marker);
    for (HEADER_GOVERNANCE_VALIDATOR_MARKER) |marker| try guard.requireMarker(text_header_governance_validator_marker, marker);
    const text_header_governance_validator_selftest_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_header_governance_validator_selftest_marker_path);
    const text_header_governance_validator_selftest_marker = try guard.readUtf8File(io, allocator, text_header_governance_validator_selftest_marker_path);
    defer allocator.free(text_header_governance_validator_selftest_marker);
    for (HEADER_GOVERNANCE_VALIDATOR_SELFTEST_MARKER) |marker| try guard.requireMarker(text_header_governance_validator_selftest_marker, marker);
    const text_catalog_selftest_gap_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_catalog_selftest_gap_marker_path);
    const text_catalog_selftest_gap_marker = try guard.readUtf8File(io, allocator, text_catalog_selftest_gap_marker_path);
    defer allocator.free(text_catalog_selftest_gap_marker);
    for (CATALOG_SELFTEST_GAP_MARKER) |marker| try guard.requireMarker(text_catalog_selftest_gap_marker, marker);
    const text_catalog_tool_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_catalog_tool_marker_path);
    const text_catalog_tool_marker = try guard.readUtf8File(io, allocator, text_catalog_tool_marker_path);
    defer allocator.free(text_catalog_tool_marker);
    for (CATALOG_TOOL_MARKER) |marker| try guard.requireMarker(text_catalog_tool_marker, marker);
    const text_wrapper_generation_gap_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_wrapper_generation_gap_marker_path);
    const text_wrapper_generation_gap_marker = try guard.readUtf8File(io, allocator, text_wrapper_generation_gap_marker_path);
    defer allocator.free(text_wrapper_generation_gap_marker);
    for (WRAPPER_GENERATION_GAP_MARKER) |marker| try guard.requireMarker(text_wrapper_generation_gap_marker, marker);
    const text_wrapper_template_check_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_wrapper_template_check_marker_path);
    const text_wrapper_template_check_marker = try guard.readUtf8File(io, allocator, text_wrapper_template_check_marker_path);
    defer allocator.free(text_wrapper_template_check_marker);
    for (WRAPPER_TEMPLATE_CHECK_MARKER) |marker| try guard.requireMarker(text_wrapper_template_check_marker, marker);
    const text_wrapper_template_check_selftest_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_wrapper_template_check_selftest_marker_path);
    const text_wrapper_template_check_selftest_marker = try guard.readUtf8File(io, allocator, text_wrapper_template_check_selftest_marker_path);
    defer allocator.free(text_wrapper_template_check_selftest_marker);
    for (WRAPPER_TEMPLATE_CHECK_SELFTEST_MARKER) |marker| try guard.requireMarker(text_wrapper_template_check_selftest_marker, marker);
    const text_shared_validator_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_shared_validator_marker_path);
    const text_shared_validator_marker = try guard.readUtf8File(io, allocator, text_shared_validator_marker_path);
    defer allocator.free(text_shared_validator_marker);
    for (SHARED_VALIDATOR_MARKER) |marker| try guard.requireMarker(text_shared_validator_marker, marker);
    const text_abi_check_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_abi_check_marker_path);
    const text_abi_check_marker = try guard.readUtf8File(io, allocator, text_abi_check_marker_path);
    defer allocator.free(text_abi_check_marker);
    for (ABI_CHECK_MARKER) |marker| try guard.requireMarker(text_abi_check_marker, marker);
    const text_abi_support_packet_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_abi_support_packet_marker_path);
    const text_abi_support_packet_marker = try guard.readUtf8File(io, allocator, text_abi_support_packet_marker_path);
    defer allocator.free(text_abi_support_packet_marker);
    for (ABI_SUPPORT_PACKET_MARKER) |marker| try guard.requireMarker(text_abi_support_packet_marker, marker);
    const text_fixture_manifest_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_fixture_manifest_marker_path);
    const text_fixture_manifest_marker = try guard.readUtf8File(io, allocator, text_fixture_manifest_marker_path);
    defer allocator.free(text_fixture_manifest_marker);
    for (FIXTURE_MANIFEST_MARKER) |marker| try guard.requireMarker(text_fixture_manifest_marker, marker);
    const text_xarray_slot_helper_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_xarray_slot_helper_marker_path);
    const text_xarray_slot_helper_marker = try guard.readUtf8File(io, allocator, text_xarray_slot_helper_marker_path);
    defer allocator.free(text_xarray_slot_helper_marker);
    for (XARRAY_SLOT_HELPER_MARKER) |marker| try guard.requireMarker(text_xarray_slot_helper_marker, marker);
    const text_xarray_slot_starter_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_xarray_slot_starter_marker_path);
    const text_xarray_slot_starter_marker = try guard.readUtf8File(io, allocator, text_xarray_slot_starter_marker_path);
    defer allocator.free(text_xarray_slot_starter_marker);
    for (XARRAY_SLOT_STARTER_MARKER) |marker| try guard.requireMarker(text_xarray_slot_starter_marker, marker);
    const text_xarray_slot_starter_build_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_xarray_slot_starter_build_marker_path);
    const text_xarray_slot_starter_build_marker = try guard.readUtf8File(io, allocator, text_xarray_slot_starter_build_marker_path);
    defer allocator.free(text_xarray_slot_starter_build_marker);
    for (XARRAY_SLOT_STARTER_BUILD_MARKER) |marker| try guard.requireMarker(text_xarray_slot_starter_build_marker, marker);
    const text_shared_tests_build_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_shared_tests_build_marker_path);
    const text_shared_tests_build_marker = try guard.readUtf8File(io, allocator, text_shared_tests_build_marker_path);
    defer allocator.free(text_shared_tests_build_marker);
    for (SHARED_TESTS_BUILD_MARKER) |marker| try guard.requireMarker(text_shared_tests_build_marker, marker);
    const text_xarray_slot_build_route_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_xarray_slot_build_route_marker_path);
    const text_xarray_slot_build_route_marker = try guard.readUtf8File(io, allocator, text_xarray_slot_build_route_marker_path);
    defer allocator.free(text_xarray_slot_build_route_marker);
    for (XARRAY_SLOT_BUILD_ROUTE_MARKER) |marker| try guard.requireMarker(text_xarray_slot_build_route_marker, marker);
    const text_policy_dump_replay_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_policy_dump_replay_marker_path);
    const text_policy_dump_replay_marker = try guard.readUtf8File(io, allocator, text_policy_dump_replay_marker_path);
    defer allocator.free(text_policy_dump_replay_marker);
    for (POLICY_DUMP_REPLAY_MARKER) |marker| try guard.requireMarker(text_policy_dump_replay_marker, marker);
    const text_policy_dump_build_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_policy_dump_build_marker_path);
    const text_policy_dump_build_marker = try guard.readUtf8File(io, allocator, text_policy_dump_build_marker_path);
    defer allocator.free(text_policy_dump_build_marker);
    for (POLICY_DUMP_BUILD_MARKER) |marker| try guard.requireMarker(text_policy_dump_build_marker, marker);
    const text_policy_dump_build_route_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_policy_dump_build_route_marker_path);
    const text_policy_dump_build_route_marker = try guard.readUtf8File(io, allocator, text_policy_dump_build_route_marker_path);
    defer allocator.free(text_policy_dump_build_route_marker);
    for (POLICY_DUMP_BUILD_ROUTE_MARKER) |marker| try guard.requireMarker(text_policy_dump_build_route_marker, marker);
    const text_header_family_validator_gap_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_header_family_validator_gap_marker_path);
    const text_header_family_validator_gap_marker = try guard.readUtf8File(io, allocator, text_header_family_validator_gap_marker_path);
    defer allocator.free(text_header_family_validator_gap_marker);
    for (HEADER_FAMILY_VALIDATOR_GAP_MARKER) |marker| try guard.requireMarker(text_header_family_validator_gap_marker, marker);
    const text_header_family_note_gap_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_header_family_note_gap_marker_path);
    const text_header_family_note_gap_marker = try guard.readUtf8File(io, allocator, text_header_family_note_gap_marker_path);
    defer allocator.free(text_header_family_note_gap_marker);
    for (HEADER_FAMILY_NOTE_GAP_MARKER) |marker| try guard.requireMarker(text_header_family_note_gap_marker, marker);
    const text_header_family_next_step_gap_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_header_family_next_step_gap_marker_path);
    const text_header_family_next_step_gap_marker = try guard.readUtf8File(io, allocator, text_header_family_next_step_gap_marker_path);
    defer allocator.free(text_header_family_next_step_gap_marker);
    for (HEADER_FAMILY_NEXT_STEP_GAP_MARKER) |marker| try guard.requireMarker(text_header_family_next_step_gap_marker, marker);
    const text_header_family_returned_surfaces_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_header_family_returned_surfaces_marker_path);
    const text_header_family_returned_surfaces_marker = try guard.readUtf8File(io, allocator, text_header_family_returned_surfaces_marker_path);
    defer allocator.free(text_header_family_returned_surfaces_marker);
    for (HEADER_FAMILY_RETURNED_SURFACES_MARKER) |marker| try guard.requireMarker(text_header_family_returned_surfaces_marker, marker);
    const text_header_family_next_step_reminder_marker_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_header_family_next_step_reminder_marker_path);
    const text_header_family_next_step_reminder_marker = try guard.readUtf8File(io, allocator, text_header_family_next_step_reminder_marker_path);
    defer allocator.free(text_header_family_next_step_reminder_marker);
    for (HEADER_FAMILY_NEXT_STEP_REMINDER_MARKER) |marker| try guard.requireMarker(text_header_family_next_step_reminder_marker, marker);
    const text_required_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_markers_path);
    const text_required_markers = try guard.readUtf8File(io, allocator, text_required_markers_path);
    defer allocator.free(text_required_markers);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text_required_markers, marker);
    const text_readme_marker_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_readme_marker_cases_path);
    const text_readme_marker_cases = try guard.readUtf8File(io, allocator, text_readme_marker_cases_path);
    defer allocator.free(text_readme_marker_cases);
    for (README_MARKER_CASES) |marker| try guard.requireMarker(text_readme_marker_cases, marker);
    const text_file_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_file_cases_path);
    const text_file_cases = try guard.readUtf8File(io, allocator, text_file_cases_path);
    defer allocator.free(text_file_cases);
    for (FILE_CASES) |marker| try guard.requireMarker(text_file_cases, marker);
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
