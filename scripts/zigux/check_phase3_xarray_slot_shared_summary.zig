const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_XARRAY_SLOT_SHARED_SUMMARY=pass";
pub const self_test_pass_marker = "PHASE3_XARRAY_SLOT_SHARED_SUMMARY_SELF_TEST=pass";

const REQUIRED_MARKERS__Documentation_zigux_README_md = [_][]const u8{
    "Documentation/zigux/phase3-xarray-slot-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig",
    "scripts\\zigux/check_phase3_xarray_slot.zig",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "current `master` directly serves the focused `xarray_slot` packet through `zigux/helpers/xarray_slot_view.zig`, `zigux/tests/phase3_xarray_slot_starter_packet.zig`, `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`, `scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig`, `zigux/tests/phase3_xarray_slot_dump.zig`, `zigux/tests/phase3_xarray_slot_dump_build.zig`, `zigux/tests/fixtures/phase3_xarray_slot/expected.json`, and `scripts\\zigux/check_phase3_xarray_slot.zig`, so keep those helper-local slices explicit here instead of leaving them parked only inside packet-local validator wording.",
};

const REQUIRED_MARKERS__Documentation_zigux_review-checklist_md = [_][]const u8{
    "Documentation/zigux/phase3-xarray-slot-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "scripts\\zigux/validate_phase3_validator_support_surface.zig",
    "scripts\\zigux/check_phase3_selftest_surface.zig",
    "scripts\\zigux/check_phase3_readme_tooling_inventory.zig",
    "scripts\\zigux/validate_phase3_abi_header_family_survey.zig",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "if the change touches the shared Phase 3 ABI/runtime packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-xarray-slot-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts\\zigux/check_phase3_selftest_surface.zig`, `scripts\\zigux/check_phase3_readme_tooling_inventory.zig`, `scripts\\zigux/validate_phase3_validator_support_surface.zig`, `scripts\\zigux/validate_phase3_export_uapi_survey.zig`, `scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig`, `scripts\\zigux/check_phase3_abi.zig`, `scripts/zigux/phase3_catalog.zig`, `scripts\\zigux/check_phase3_catalog_selftest.zig`, `scripts/zigux/check_phase3_wrapper_templates.zig`, `zigux/tests/fixtures/phase3_abi_manifest.json`, and `zigux/tests/phase3_export_uapi_layout.zig` still agree on the current bounded starter, helper, policy, validator-support, export/UAPI, layout-replay, low-level-wrapper, catalog, manifest-backed inventory, linux-header-governance, returned header-family survey follow-through, and wrapper-retirement packet, keep `scripts\\zigux/validate_phase3_abi_header_family_survey.zig` and `Documentation/zigux/phase3-abi-header-family-survey.md` explicit as the current dedicated header-family survey companion beside `Documentation/zigux/phase3-linux-zigux-header-governance.md`, keep `Documentation/zigux/phase3-abi-h-boundary-next-step.md` explicit as the current focused abi.h next-step companion beside that dedicated survey and governance note, and keep any broader shared replay or broader header-family completion claims framed as repo-reality gaps until current `master` materializes them again?",
};

const REQUIRED_MARKERS__zigux_tests_README_md = [_][]const u8{
    "Documentation/zigux/phase3-xarray-slot-slice.md",
    "scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig",
    "scripts\\zigux/check_phase3_xarray_slot.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
    "keep the current docs-root Phase 3 reminder packet should stay parked on `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-xarray-slot-slice.md`",
};

const REQUIRED_MARKERS__scripts_zigux_README_md = [_][]const u8{
    "Documentation/zigux/phase3-xarray-slot-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig",
    "scripts\\zigux/check_phase3_xarray_slot.zig",
    "scripts\\zigux/check_phase3_selftest_surface.zig",
    "scripts/zigux/run_phase3_checks.zig",
    "scripts/zigux/validate_phase3_selftest.zig",
    "zigux/helpers/xarray_slot_view.zig",
    "Phase 3 flow - the current scripts-root ABI/runtime packet stays reviewable through the bounded `dev_t` starter packet, the focused helper-local `err_ptr` / `xarray` slice, the directly readable `xarray_slot` starter-and-checker packet, the focused policy slice with the returned notifier binding companion plus the dedicated policy-dump and policy-unsafe survey guards, the dedicated validator-support and selftest reminder guards, the adjacent low-level-wrapper packet, the packet-local export/UAPI survey note plus validator, the directly readable catalog helper, and the dedicated export/UAPI layout replay pair instead of rebuilding the broader export/UAPI, catalog-selftest, closure, or shared replay story from routes that current `master` still does not serve",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-xarray-slot-slice_md = [_][]const u8{
    "Documentation/zigux/phase3-validator-support-surface.md",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
    "scripts\\zigux/check_phase3_xarray_slot.zig",
    "The docs-root xarray-slot slice note is now landed, and `zigux/tests/fixtures/phase3_xarray_slot_manifest.json` keeps the remaining nearby repo-reality follow-up narrowed to `Documentation/zigux/phase3-validator-support-surface.md` and `scripts\\zigux/validate_phase3.zig`.",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-validator-support-surface_md = [_][]const u8{
    "Documentation/zigux/phase3-xarray-slot-slice.md",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
    "scripts\\zigux/check_phase3_xarray_slot.zig",
    "one focused helper-local `xarray_slot` classifier slice with both starter-packet and fixture-backed dump parity coverage",
    "Current `master` also keeps this note's dedicated packet-local validator explicit through `scripts\\zigux/validate_phase3_validator_support_surface.zig`, and that validator should stay aligned with this note rather than being left implicit behind the broader shared `scripts\\zigux/validate_phase3.zig` entrypoint.",
};

const SELF_TEST_CASES = [_][]const u8{
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__documentation_zigux_readme_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/README/md");
    defer allocator.free(text_required_markers__documentation_zigux_readme_md_path);
    const text_required_markers__documentation_zigux_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_readme_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_readme_md);
    for (REQUIRED_MARKERS__Documentation_zigux_README_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_readme_md, marker);
    const text_required_markers__documentation_zigux_review-checklist_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist/md");
    defer allocator.free(text_required_markers__documentation_zigux_review-checklist_md_path);
    const text_required_markers__documentation_zigux_review-checklist_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_review-checklist_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_review-checklist_md);
    for (REQUIRED_MARKERS__Documentation_zigux_review-checklist_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_review-checklist_md, marker);
    const text_required_markers__zigux_tests_readme_md_path = try guard.joinPath(allocator, root, "zigux/tests/README/md");
    defer allocator.free(text_required_markers__zigux_tests_readme_md_path);
    const text_required_markers__zigux_tests_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_readme_md_path);
    defer allocator.free(text_required_markers__zigux_tests_readme_md);
    for (REQUIRED_MARKERS__zigux_tests_README_md) |marker| try guard.requireMarker(text_required_markers__zigux_tests_readme_md, marker);
    const text_required_markers__scripts_zigux_readme_md_path = try guard.joinPath(allocator, root, "scripts/zigux/README/md");
    defer allocator.free(text_required_markers__scripts_zigux_readme_md_path);
    const text_required_markers__scripts_zigux_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_readme_md_path);
    defer allocator.free(text_required_markers__scripts_zigux_readme_md);
    for (REQUIRED_MARKERS__scripts_zigux_README_md) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_readme_md, marker);
    const text_required_markers__documentation_zigux_phase3-xarray-slot-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-xarray-slot-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-xarray-slot-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-xarray-slot-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-xarray-slot-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-xarray-slot-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-xarray-slot-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-xarray-slot-slice_md, marker);
    const text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-validator-support-surface/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path);
    const text_required_markers__documentation_zigux_phase3-validator-support-surface_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-validator-support-surface_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-validator-support-surface_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-validator-support-surface_md, marker);
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
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
