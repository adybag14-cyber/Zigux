const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_KFIFO_SURVEY_SURFACE=pass";
pub const self_test_pass_marker = "PHASE5_KFIFO_SURVEY_SURFACE_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "This note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.",
    "- `PHASE5_LANE_KEY=P5-L01`",
    "- `samples/kfifo/bytestream-example.c` remains the Linux anchor for this slice.",
    "- `samples/zigux/bytestream_fifo.zig` is directly readable on current `master`.",
    "- the shipped sample-root companion `samples/zigux/bytestream_fifo_window_contract.zig` is directly readable on current `master`",
    "- the broader exact behavior packet is now directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo.zig`",
    "- the manifest-backed packet remains directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_manifest.json`.",
    "- the survey packet is now directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_survey.zig`",
    "- authenticated GitHub contents reads in this environment now recover `zigux/tests/phase5_build.zig` directly again",
    "- keep storage backing explicit as a fixed embedded ring through `StorageBacking.embedded_fixed_buffer`",
    "- keep remaining-capacity, rollover, occupancy, queue-shape, and two-window contract cues explicit through `runRemainingCapacityReplay()`, `occupancySummary()`, `visibleSpanSummary()`, `writableSpanSummary()`, `usesWrappedStorageWindow()`, and `samples/zigux/bytestream_fifo_window_contract.zig`",
    "- keep the direct `available()` helper explicit as the first remaining-capacity cue at cold, initialized, preview, wrapped, full, replay-complete, reset, and exited boundaries instead of leaving free-space review to derived queue-length math alone",
    "- keep bitmap helper or runtime bitmap claims out of this packet; current `master` still has no standalone `samples/zigux/*bitmap*` Phase 5 reference sample",
    "- `samples/zigux/bytestream_fifo.zig` currently carries four in-file self-checks",
    "- `samples/zigux/bytestream_fifo_window_contract.zig` currently carries two direct companion checks",
    "- `zigux/tests/phase5_bytestream_fifo.zig` currently carries five focused replay tests",
    "- `zigux/tests/phase5_bytestream_fifo_survey.zig` currently carries five survey-packet checks",
    "- `zigux/tests/phase5_build.zig` is directly readable through authenticated contents readback again and now reruns the sample-owned self-check route, the window-contract companion, the focused replay packet, and the survey gate together",
    "- `StorageBacking.embedded_fixed_buffer` is the only declared storage backing",
    "- does `BytestreamFifoSample.descriptor()` still name `samples/kfifo/bytestream-example.c`, keep `requires_runtime_substrate = false`, keep `provides_selfcheck = true`, and keep `StorageBacking.embedded_fixed_buffer` as the only storage backing so the packet stays in the non-runtime Phase 5 lane?",
    "- do `runAnchorReplay()`, `runPreviewBoundaryReplay()`, `runWrappedPreviewReplay()`, `runRemainingCapacityReplay()`, `runPartialEnqueueBoundaryReplay()`, `runReinitBoundaryReplay()`, and `samples/zigux/bytestream_fifo_window_contract.zig` still describe the same bounded packet across the sample root, focused replay file, manifest-backed contract, dedicated survey gate, and shared reminder surfaces?",
    "- do the direct validation routes stay explicit too: `zig test samples/zigux/bytestream_fifo.zig` should stay visible as the sample-owned self-check route, `zig test samples/zigux/bytestream_fifo_window_contract.zig` should stay visible as the queue-window companion route, `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig` should stay visible as the equivalent direct focused replay route, `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` should stay visible as the survey-packet guard, and the shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` line should stay visible as the current direct shared build route that reruns the sample-owned self-check route, the window-contract companion, the focused replay packet, and the survey guard together rather than being demoted back to companion-only wording?",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "current `master` still has no standalone `samples/zigux/*bitmap*` Phase 5 reference sample, so this bytestream packet must not be used to imply bitmap-side sample delivery or reopen the separate later-phase runtime bitmap family",
    "write a new sample",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kfifo-sample-survey.md");
    defer allocator.free(text_required_markers_path);
    const text_required_markers = try guard.readUtf8File(io, allocator, text_required_markers_path);
    defer allocator.free(text_required_markers);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text_required_markers, marker);
    const text_forbidden_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kfifo-sample-survey.md");
    defer allocator.free(text_forbidden_markers_path);
    const text_forbidden_markers = try guard.readUtf8File(io, allocator, text_forbidden_markers_path);
    defer allocator.free(text_forbidden_markers);
    for (FORBIDDEN_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_markers, marker) != null) return guard.GuardError.MissingMarker;
    }
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
