const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_TESTS_README_ALIGNMENT=pass";
pub const self_test_pass_marker = "PHASE3_TESTS_README_ALIGNMENT_SELF_TEST=pass";

const README_MARKERS = [_][]const u8{
    "Keep the focused helper and starter packet explicit through `zigux/helpers/err_ptr.zig`, `zigux/helpers/xa_value.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/tests/phase3_dev_t_starter_packet.zig`, `zigux/tests/phase3_dev_t_starter_packet_build.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`, `zigux/tests/phase3_xarray_slot_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet_build.zig`, and `zigux/tests/phase3_policy_starter_packet_manifest.json`.",
    "keep the returned notifier-binding and focused export/UAPI layout replay pair explicit here instead of leaving `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and `zigux/tests/phase3_export_uapi_layout_build.zig` framed as broader repo-reality gaps",
    "Keep the current same-lane helper follow-through explicit too: `Documentation/zigux/phase3-bitmap-cpumask-slice.md`, `zigux/helpers/bitmap_view.zig`, `zigux/helpers/cpumask_view.zig`, `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`, `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`, `Documentation/zigux/phase3-list-hlist-slice.md`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/tests/phase3_list_hlist_starter_packet.zig`, and `zigux/tests/phase3_list_hlist_starter_packet_build.zig`.",
    "Keep the direct rerun surface explicit through `zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`, `zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig`, `make -C zigux phase3-export-uapi-layout-test`, and `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`.",
    "Keep the broader validator, manifest, and replay-family boundary truthful: keep `scripts\\zigux/validate_phase3.zig`, `zigux/tests/fixtures/phase3_abi_manifest.json`, `zigux/tests/phase3_export_uapi_c_header_smoke.c`, and `zig run scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig` reviewable as same-lane companions instead of presenting the broader validator, export/UAPI layout, low-level-wrapper, catalog, IDR, or IDA packet as shipped tests-root evidence.",
    "Tests-root reviewer prompt:",
    "- Does the bounded Phase 3 reminder keep the direct helper, starter, policy, low-level-wrapper, bitmap/cpumask, list/hlist, and export/UAPI layout packet aligned without widening into the broader shared validator, catalog, or replay family?",
};

const GAP_MARKERS = [_][]const u8{
    "PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the dedicated ABI header-family survey follow-through, the focused abi.h next-step note, the shared ABI catalog helper plus manifest-backed inventory companion, the bounded bitmap/cpumask and list/hlist helper slices, the shared tests-root export/UAPI layout route, the named Linux-side boundary-header helper family plus validation relay, and the direct C smoke proof; the docs-root reminder, shared review checklist, tests-root reminder, and scripts-root reminder are now aligned on those already-returned helper-local slices, and no same-lane shared-summary drift remains on current master",
    "PHASE3_SHARED_REMINDER_NEXT_STEP=keep this note parked unless a fresh current-master reread shows a smaller one-file shared-summary drift around the returned export/UAPI, bitmap/cpumask, list/hlist, shared tests-root layout, named boundary-header helper, or direct C smoke packet",
    "- `zigux/tests/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the packet-local export/UAPI survey note, validator, focused export/UAPI layout replay, and direct C smoke companion family, so the tests-root reminder no longer carries a same-lane summary gap.",
    "The earlier shared-reminder drift is now closed for the packet-local export/UAPI survey, the dedicated header-family and abi.h follow-through, the manifest-backed catalog packet, the landed helper-local interop slices themselves, and the shared docs-root, review-checklist, tests-root, and scripts-root reminder surfaces. No smaller same-lane shared-summary drift is visible on current `master` right now.",
    "Current `master` already keeps the returned bitmap/cpumask packet explicit through `Documentation/zigux/phase3-bitmap-cpumask-slice.md`, `zigux/helpers/bitmap_view.zig`, `zigux/helpers/cpumask_view.zig`, `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`, and `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`, and it already keeps the returned list/hlist packet explicit through `Documentation/zigux/phase3-list-hlist-slice.md`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/tests/phase3_list_hlist_starter_packet.zig`, and `zigux/tests/phase3_list_hlist_starter_packet_build.zig`. `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` now all reflect those returned helper-local slices directly, so the next same-lane follow-through should stay parked until future boundary evidence actually lands.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_readme_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_readme_markers_path);
    const text_readme_markers = try guard.readUtf8File(io, allocator, text_readme_markers_path);
    defer allocator.free(text_readme_markers);
    for (README_MARKERS) |marker| try guard.requireMarker(text_readme_markers, marker);
    const text_gap_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_gap_markers_path);
    const text_gap_markers = try guard.readUtf8File(io, allocator, text_gap_markers_path);
    defer allocator.free(text_gap_markers);
    for (GAP_MARKERS) |marker| try guard.requireMarker(text_gap_markers, marker);
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
