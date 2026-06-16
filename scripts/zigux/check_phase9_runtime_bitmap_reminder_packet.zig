const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "keep the partial runtime bitmap reminder packet distinct from that returned loader shard too:",
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`",
    "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`",
    "`zigux/tests/runtime_bitmap_manifest.json`",
    "`zigux/tests/runtime_bitmap_module.zig`",
    "`zigux/tests/runtime_bitmap_diff.zig`",
    "`samples/zigux/runtime_bitmap_top_bit_contract.zig`",
    "the partial separate runtime bitmap reminder packet stays explicit",
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`",
    "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`",
    "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
    "`zigux/tests/runtime_bitmap_manifest.json`",
    "`zigux/tests/runtime_bitmap_module.zig`",
    "`zigux/tests/runtime_bitmap_diff.zig`",
    "there is no standalone `samples/zigux/*bitmap*` reference sample",
    "keep the partial runtime bitmap reminder distinct too:",
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`",
    "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`",
    "`zigux/tests/runtime_bitmap_manifest.json`",
    "`zigux/tests/runtime_bitmap_module.zig`",
    "`zigux/tests/runtime_bitmap_diff.zig`",
    "`phase9-runtime-bitmap-test` plus `phase9-test` routes",
    "Fresh trusted mixed reread on 2026-05-23 also confirms a broader runtime bitmap sample-side packet on current `master`",
    "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
    "`zigux/tests/runtime_bitmap_manifest.json`",
    "`zigux/tests/runtime_bitmap_module.zig`",
    "`zigux/tests/runtime_bitmap_diff.zig`",
    "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage selftest, exit, mutation, and source-lifecycle guard companion proof for the same runtime bitmap starter.",
    "Keep `zigux/tests/runtime_bitmap_manifest.json` explicit as the manifest-backed ownership packet for the same runtime bitmap reminder family.",
    "the separate runtime bitmap reminder packet stays explicit",
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`",
    "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`",
    "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
    "`zigux/tests/runtime_bitmap_manifest.json`",
    "`zigux/tests/runtime_bitmap_module.zig`",
    "`zigux/tests/runtime_bitmap_diff.zig`",
    "Keep that broader bitmap-side visibility from being used to imply that the broader shared runtime-loader packet returned or that blocked publication boundaries are complete.",
    "`PHASE9_LANE_KEY=P9-L08`",
    "manifest-backed ownership packet",
    "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
    "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage sample-root guard companion",
    "current runtime bitmap reminder packet is still `partial_packet_with_diff_but_without_broader_runtime_loader_parity`",
    "the blocked deliverable remains `loadable Phase 9 runtime bitmap pilot module parity`",
    "`PHASE9_LANE_KEY=P9-L08`",
    "`zigux/tests/runtime_bitmap_manifest.json`",
    "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
    "The current visible packet includes the direct bitmap sample, direct cold-stage guard companion, direct loader companion, direct module proof, direct diff proof, focused top-bit companion, manifest-backed ownership packet, survey note, module-slice note, survey gate, and bounded build bundle.",
    "blocked follow-through remains `broader shared runtime-loader family completion plus loadable runtime bitmap module parity`",
    "\"lane_key\": \"P9-L08\"",
    "\"scope\": \"partial runtime bitmap reminder packet, direct sample proof, direct loader proof, direct module proof, direct diff proof, manifest-backed ownership packet, top-bit companion proof, and no broader shared runtime-loader parity claim\"",
    "\"cold_stage_guard_path\": \"samples/zigux/runtime_bitmap_cold_stage_guard.zig\"",
    "\"module_path\": \"zigux/tests/runtime_bitmap_module.zig\"",
    "\"diff_path\": \"zigux/tests/runtime_bitmap_diff.zig\"",
    "\"survey_note_path\": \"Documentation/zigux/phase9-runtime-bitmap-survey.md\"",
    "\"module_slice_note_path\": \"Documentation/zigux/phase9-runtime-bitmap-module-slice.md\"",
    "\"validation_entrypoint\": \"phase9-runtime-bitmap-tests\"",
    "\"Keep the cold-stage selftest, exit, mutation, and source-lifecycle guard companion explicit when the manifest summarizes the sample-root runtime bitmap packet.\"",
    "\"loadable runtime bitmap module parity\"",
    ".name = \"phase9-runtime-bitmap-sample-tests\"",
    ".name = \"phase9-runtime-bitmap-loader-tests\"",
    ".name = \"phase9-runtime-bitmap-survey-tests\"",
    ".name = \"phase9-runtime-bitmap-module-tests\"",
    ".name = \"phase9-runtime-bitmap-diff-tests\"",
    ".name = \"phase9-runtime-bitmap-top-bit-tests\"",
    "\"phase9-runtime-bitmap-tests\"",
};

const EXACT_ONCE_MARKERS = [_][]const u8{
    "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage selftest, exit, mutation, and source-lifecycle guard companion proof for the same runtime bitmap starter.",
    "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage sample-root guard companion; it is visible on the trusted path but still sits outside the shared `zigux/tests/phase9_build.zig` bundle.",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "proof that the broader shared runtime-loader packet returned",
    "full bitmap-family return",
    "fifth approved Phase 5 sample family",
};

const DOCS_README_PATH = [_][]const u8{
    "Documentation/zigux/README.md",
};

const REVIEW_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/review-checklist.md",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const SAMPLES_README_PATH = [_][]const u8{
    "samples/zigux/README.md",
};

const TESTS_README_PATH = [_][]const u8{
    "zigux/tests/README.md",
};

const SURVEY_NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
};

const MODULE_SLICE_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/runtime_bitmap_manifest.json",
};

const PHASE9_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase9_build.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXACT_ONCE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DOCS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (SAMPLES_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
    for (MODULE_SLICE_PATH) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (PHASE9_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
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
