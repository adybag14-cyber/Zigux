const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_SURVEYED_HEAD_TRUTHFULNESS=pass";
pub const self_test_pass_marker = "PHASE6_SURVEYED_HEAD_TRUTHFULNESS_SELF_TEST=pass";

const EXPECTED_OLD_HEAD = [_][]const u8{
    "current-master-readback-2026-05-22",
};

const EXPECTED_NEW_PERF_DATE = [_][]const u8{
    "2026-05-27",
};

const REQUIRED_NOTE_SNIPPETS = [_][]const u8{
    "`Documentation/zigux/phase6-helper-evidence-catalog.md` still advertises `surveyed head: current-master-readback-2026-05-22`",
    "`Documentation/zigux/phase6-helper-parity-catalog.md` still advertises `surveyed head: current-master-readback-2026-05-22`",
    "`zigux/tests/phase6_helper_evidence_manifest.json` still pins `surveyed_head` to `current-master-readback-2026-05-22`",
    "`zigux/tests/phase6_helper_parity_manifest.json` still pins `surveyed_head` to `current-master-readback-2026-05-22`",
    "`Documentation/zigux/phase6-perf-gate-survey.md` now says the shared perf packet was re-read from current `master` on `2026-05-27`",
    "Do not retag only one or two of those files. The honest fix is a one-pass refresh of the whole shared packet.",
};

const REQUIRED_EVIDENCE_CATALOG_SNIPPET = [_][]const u8{
    "- surveyed head: `current-master-readback-2026-05-22`",
};

const REQUIRED_PARITY_CATALOG_SNIPPET = [_][]const u8{
    "- surveyed head: `current-master-readback-2026-05-22`",
};

const REQUIRED_PERF_SURVEY_SNIPPET = [_][]const u8{
    "the exact posture below was re-read from current `master` on `2026-05-27`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_old_head_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-surveyed-head-truthfulness-gap.md");
    defer allocator.free(text_expected_old_head_path);
    const text_expected_old_head = try guard.readUtf8File(io, allocator, text_expected_old_head_path);
    defer allocator.free(text_expected_old_head);
    for (EXPECTED_OLD_HEAD) |marker| try guard.requireMarker(text_expected_old_head, marker);
    const text_expected_new_perf_date_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-surveyed-head-truthfulness-gap.md");
    defer allocator.free(text_expected_new_perf_date_path);
    const text_expected_new_perf_date = try guard.readUtf8File(io, allocator, text_expected_new_perf_date_path);
    defer allocator.free(text_expected_new_perf_date);
    for (EXPECTED_NEW_PERF_DATE) |marker| try guard.requireMarker(text_expected_new_perf_date, marker);
    const text_required_note_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-surveyed-head-truthfulness-gap.md");
    defer allocator.free(text_required_note_snippets_path);
    const text_required_note_snippets = try guard.readUtf8File(io, allocator, text_required_note_snippets_path);
    defer allocator.free(text_required_note_snippets);
    for (REQUIRED_NOTE_SNIPPETS) |marker| try guard.requireMarker(text_required_note_snippets, marker);
    const text_required_evidence_catalog_snippet_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-surveyed-head-truthfulness-gap.md");
    defer allocator.free(text_required_evidence_catalog_snippet_path);
    const text_required_evidence_catalog_snippet = try guard.readUtf8File(io, allocator, text_required_evidence_catalog_snippet_path);
    defer allocator.free(text_required_evidence_catalog_snippet);
    for (REQUIRED_EVIDENCE_CATALOG_SNIPPET) |marker| try guard.requireMarker(text_required_evidence_catalog_snippet, marker);
    const text_required_parity_catalog_snippet_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-surveyed-head-truthfulness-gap.md");
    defer allocator.free(text_required_parity_catalog_snippet_path);
    const text_required_parity_catalog_snippet = try guard.readUtf8File(io, allocator, text_required_parity_catalog_snippet_path);
    defer allocator.free(text_required_parity_catalog_snippet);
    for (REQUIRED_PARITY_CATALOG_SNIPPET) |marker| try guard.requireMarker(text_required_parity_catalog_snippet, marker);
    const text_required_perf_survey_snippet_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-surveyed-head-truthfulness-gap.md");
    defer allocator.free(text_required_perf_survey_snippet_path);
    const text_required_perf_survey_snippet = try guard.readUtf8File(io, allocator, text_required_perf_survey_snippet_path);
    defer allocator.free(text_required_perf_survey_snippet);
    for (REQUIRED_PERF_SURVEY_SNIPPET) |marker| try guard.requireMarker(text_required_perf_survey_snippet, marker);
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
