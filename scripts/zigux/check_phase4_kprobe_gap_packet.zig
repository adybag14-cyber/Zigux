const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_KPROBE_GAP_PACKET=pass";
pub const self_test_pass_marker = "PHASE4_KPROBE_GAP_PACKET_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "PHASE4_KPROBE_STATUS=parked_gap_packet_landed",
    "PHASE4_KPROBE_LANE_KEY=P4-L19",
    "PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c",
    "PHASE4_KPROBE_CURRENT_LINUX_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig",
    "PHASE4_KPROBE_OWNER=Validation and Perf Team",
    "PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team",
    "Current `master` still does not ship `samples/zigux/kprobe_example.zig`.",
    "The same packet also keeps its reversible-delivery evidence string pinned in the paired manifest",
};

const MANIFEST_MARKERS = [_][]const u8{
    "\"lane_key\": \"P4-L19\"",
    "\"phase\": \"Phase 4\"",
    "\"owner\": \"Validation and Perf Team\"",
    "\"rollback_owner\": \"Validation and Perf Team\"",
    "\"anchor\": \"samples/kprobes/kprobe_example.c\"",
    "\"current_replay\": \"make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m\"",
    "\"isolated_survey_replay\": \"zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig\"",
    "\"shared_build_replay\": \"phase4-kprobe-example-survey-tests\"",
    "\"phase4_gate_evidence_present\": true",
    "\"local_lab_replay\"",
    "make -C zigux phase4-kprobe-example-survey",
};

const SURVEY_MARKERS = [_][]const u8{
    "test \"phase4 kprobe survey keeps the parked gap packet explicit\" {",
    "test \"phase4 kprobe survey keeps reversible-delivery evidence explicit\" {",
    "test \"phase4 kprobe survey keeps the bounded next step explicit\" {",
    "make -C zigux phase4-kprobe-example-survey",
    "zig test zigux/tests/phase4_kprobe_example_survey.zig",
    "Validation and Perf Team",
};

const FILES = [_][]const u8{
    "NOTE_REL",
    "MANIFEST_REL",
    "SURVEY_REL",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-kprobe-example-gap-survey.md");
    defer allocator.free(text_note_markers_path);
    const text_note_markers = try guard.readUtf8File(io, allocator, text_note_markers_path);
    defer allocator.free(text_note_markers);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text_note_markers, marker);
    const text_manifest_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-kprobe-example-gap-survey.md");
    defer allocator.free(text_manifest_markers_path);
    const text_manifest_markers = try guard.readUtf8File(io, allocator, text_manifest_markers_path);
    defer allocator.free(text_manifest_markers);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text_manifest_markers, marker);
    const text_survey_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-kprobe-example-gap-survey.md");
    defer allocator.free(text_survey_markers_path);
    const text_survey_markers = try guard.readUtf8File(io, allocator, text_survey_markers_path);
    defer allocator.free(text_survey_markers);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text_survey_markers, marker);
    const text_files_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_files_path);
    const text_files = try guard.readUtf8File(io, allocator, text_files_path);
    defer allocator.free(text_files);
    for (FILES) |marker| try guard.requireMarker(text_files, marker);
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
