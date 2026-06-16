const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_RUNTIME_BITMAP_MODULE_SLICE_SELF_TEST=pass";

const MODULE_SLICE_REQUIRED_MARKERS = [_][]const u8{
    "`PHASE9_SLICE=runtime-bitmap-partial-slice`",
    "scope: partial runtime bitmap reminder packet, direct sample proof, direct loader proof, manifest-backed ownership packet, top-bit companion proof, bounded build-bundle vocabulary, and no broader shared runtime-loader claim",
    "`zigux/tests/runtime_bitmap_manifest.json`",
    "`zigux/tests/runtime_bitmap_module.zig`",
    "`zigux/tests/runtime_bitmap_diff.zig`",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "the bounded `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` routes inside `zigux/tests/phase9_build.zig`",
    "The current visible packet includes the direct bitmap sample, direct loader companion, focused top-bit companion, manifest-backed ownership packet, survey note, module-slice note, survey gate, and bounded build bundle.",
    "The shared `zigux/tests/phase9_build.zig` bundle reruns the direct sample, loader, survey gate, and top-bit companion;",
    "The module and diff legs are still absent on the trusted read path, and the older wider-family loader-gap survey and manifest vocabulary still does not return there either, so this slice must stay bitmap-local while keeping that narrower returned shared loader packet distinct from the still-missing wider-family loader backlog.",
    "the blocked follow-through remains `bitmap module-and-diff parity plus broader shared runtime-loader family completion`",
};

const SURVEY_REQUIRED_MARKERS = [_][]const u8{
    "the current runtime bitmap reminder packet is still `partial_packet_without_module_and_diff_follow_through`",
    "manifest-backed ownership packet",
    "keep `zigux/tests/runtime_bitmap_module.zig` and `zigux/tests/runtime_bitmap_diff.zig` framed as same-lane repo-reality gaps until the trusted current-tree read path returns them directly again",
};

const MANIFEST_REQUIRED_MARKERS = [_][]const u8{
    "\"lane_key\": \"P9-L08\"",
    "\"loader_reinit_and_re_selftest_guards\"",
    "\"loader_loaded_summary_stability\"",
    "\"shared_build_route_visibility\"",
};

const BUILD_REQUIRED_MARKERS = [_][]const u8{
    "\"phase9-runtime-bitmap-sample-tests\"",
    "\"phase9-runtime-bitmap-loader-tests\"",
    "\"phase9-runtime-bitmap-survey-tests\"",
    "\"phase9-runtime-bitmap-top-bit-tests\"",
    "\"phase9-runtime-bitmap-tests\"",
};

const BUILD_FORBIDDEN_MARKERS = [_][]const u8{
    "\"phase9-runtime-bitmap-module-tests\"",
    "\"phase9-runtime-bitmap-diff-tests\"",
};

const SAMPLES_README_REQUIRED_MARKERS = [_][]const u8{
    "Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.",
    "Keep `samples/zigux/runtime_bitmap_loader.zig` explicit as the returned loader-input companion proof for the same runtime bitmap starter.",
    "Keep `zigux/tests/runtime_bitmap_manifest.json` explicit as the manifest-backed ownership packet for the same runtime bitmap reminder family.",
};

const MODULE_SLICE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
};

const SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/runtime_bitmap_manifest.json",
};

const BUILD_PATH = [_][]const u8{
    "zigux/tests/phase9_build.zig",
};

const SAMPLES_README_PATH = [_][]const u8{
    "samples/zigux/README.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (MODULE_SLICE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SAMPLES_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_PATH) |marker| try guard.requireMarker(text, marker);
    for (SAMPLES_README_PATH) |marker| try guard.requireMarker(text, marker);
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
