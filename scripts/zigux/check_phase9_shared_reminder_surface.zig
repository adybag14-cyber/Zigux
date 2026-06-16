const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_SHARED_REMINDER_SURFACE_SELF_TEST=pass";

const REVIEW_CHECKLIST_MARKERS = [_][]const u8{
    "if the change touches the shared Phase 9 runtime-pilot packet",
    "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the older `samples/zigux/runtime_*_loader.zig` scaffolds",
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` while `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json` stay repo-reality gaps on the trusted contents path",
    "keep that partial bitmap packet framed as a separate bounded Phase 9 runtime reminder rather than proof that the broader shared runtime-loader packet returned",
    "`scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references and `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence",
};

const LANE_SEQUENCING_MARKERS = [_][]const u8{
    "Trusted mixed rereads on 2026-05-20 confirm three distinct current-master Phase 9 packets.",
    "direct shared-reminder proof is no longer split: `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` all keep the allocator/init-flow packet explicit again instead of leaving the scripts-root reminder behind",
    "`zigux/tests/phase9_build.zig` currently exposes `phase9-runtime-atomic64-diff`, `phase9-runtime-bitmap-tests`, `phase9-runtime-bitmap-top-bit-tests`, and `phase9-first-loadable-runtime-module-parity-survey-tests`",
    "public-tree fallback rereads still return the four loader scaffolds `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_trace_events_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig`",
    "current `master` therefore supports a partial runtime bitmap reminder packet plus the returned shared allocator/init-flow packet; the bitmap-side gaps should not be used to deny the allocator/init-flow packet that has already returned through the shared loader surfaces",
    "Treat stale shared-owner undercount or overclaim as the active blocker before reopening checker-local or runtime-behavior work.",
};

const SAMPLES_README_MARKERS = [_][]const u8{
    "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.",
    "direct authenticated contents reads now materialize `samples/zigux/runtime_bitmap.zig` and `samples/zigux/runtime_bitmap_top_bit_contract.zig`, while `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json` still remain absent on the same trusted path",
    "Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.",
};

const REVIEW_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/review-checklist.md",
};

const LANE_SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
};

const SAMPLES_README_PATH = [_][]const u8{
    "samples/zigux/README.md",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REVIEW_CHECKLIST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (LANE_SEQUENCING_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SAMPLES_README_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (LANE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (SAMPLES_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
