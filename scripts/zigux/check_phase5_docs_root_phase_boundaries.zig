const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_DOCS_ROOT_PHASE_BOUNDARIES=pass";
pub const self_test_pass_marker = "PHASE5_DOCS_ROOT_PHASE_BOUNDARIES_SELF_TEST=pass";

const REQUIRED_TEXT = [_][]const u8{
    "keep the current four-anchor non-runtime sample packet explicit from the docs root instead of letting the shared contributor reminder drift away from the live sample-root, scripts-root, guide, sequencing, checklist, and tests-root packet.",
    "while `samples/zigux/trace_events_string_formatting_sample.zig` stays only the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.",
    "keep `scripts\\zigux/check_phase5_review_guide_surface.zig` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.",
    "keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.",
    "keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the current `kobject` anchor split explicit instead of falling back to older repo-reality-gap wording.",
    "keep the current `kobject` ownership-and-lifetime split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh reread restores direct authenticated proof for those two routes.",
};

const FORBIDDEN_TEXT = [_][]const u8{
    "treat `samples/zigux/runtime_*.zig` as extra Phase 5 proof",
    "returned full trace-events port or a fifth sample outside the bounded formatting companion",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_text_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_text_path);
    const text_required_text = try guard.readUtf8File(io, allocator, text_required_text_path);
    defer allocator.free(text_required_text);
    for (REQUIRED_TEXT) |marker| try guard.requireMarker(text_required_text, marker);
    const text_forbidden_text_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_forbidden_text_path);
    const text_forbidden_text = try guard.readUtf8File(io, allocator, text_forbidden_text_path);
    defer allocator.free(text_forbidden_text);
    for (FORBIDDEN_TEXT) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_text, marker) != null) return guard.GuardError.MissingMarker;
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
