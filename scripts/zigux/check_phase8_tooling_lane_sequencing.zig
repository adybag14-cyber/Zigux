const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_TOOLING_LANE_SEQUENCING=pass";
pub const self_test_pass_marker = "PHASE8_TOOLING_LANE_SEQUENCING_SELF_TEST=pass";

const SCRIPT_PATH = [_][]const u8{
    "scripts\\zigux/check_phase8_tooling_lane_sequencing.zig",
};

const SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const REQUIRED_MARKERS__Documentation_zigux_phase8-tooling-lane-sequencing_md = [_][]const u8{
    "current 2026-05-27 reread closes the earlier scripts-root perf-buffer-poll omission cue:",
    "`scripts/zigux/README.md` now explicitly carries `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, and `make -C zigux phase8-perf-buffer-poll-test` beside the shared validator-first packet, so shared-wording follow-through no longer needs a scripts-root perf-buffer reminder repair.",
    "current 2026-05-27 reread also closes the older scripts-root symbol undercount cue:",
    "`scripts/zigux/README.md` now keeps `Documentation/zigux/phase8-kallsyms-slice.md`, `tools/lib/symbol/kallsyms.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig` visible as broader public-tree-backed companions, so the shared wording lane no longer needs a scripts-root kallsyms reminder repair either.",
    "The smallest remaining shared-wording truthfulness task is therefore this sequencing note itself: it should stop pointing future runs at a scripts-root omission that current `master` no longer has.",
    "Keep the shared wording lane parked again after this note-local repair.",
    "If the lane reopens, start with a fresh reread of `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` together before widening to any validator, helper, or bridge-packet follow-through.",
};

const REQUIRED_MARKERS__scripts_zigux_README_md = [_][]const u8{
    "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`",
    "`zigux/tests/phase8_perf_buffer_poll.zig`",
    "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
    "`make -C zigux phase8-perf-buffer-poll-test`",
    "`Documentation/zigux/phase8-kallsyms-slice.md`",
    "`tools/lib/symbol/kallsyms.zig`",
    "`zigux/tests/phase8_kallsyms.zig`",
    "`zigux/tests/phase8_kallsyms_only_build.zig`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_script_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_tooling_lane_sequencing.zig");
    defer allocator.free(text_script_path_path);
    const text_script_path = try guard.readUtf8File(io, allocator, text_script_path_path);
    defer allocator.free(text_script_path);
    for (SCRIPT_PATH) |marker| try guard.requireMarker(text_script_path, marker);
    const text_sequencing_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_tooling_lane_sequencing.zig");
    defer allocator.free(text_sequencing_path_path);
    const text_sequencing_path = try guard.readUtf8File(io, allocator, text_sequencing_path_path);
    defer allocator.free(text_sequencing_path);
    for (SEQUENCING_PATH) |marker| try guard.requireMarker(text_sequencing_path, marker);
    const text_scripts_readme_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_tooling_lane_sequencing.zig");
    defer allocator.free(text_scripts_readme_path_path);
    const text_scripts_readme_path = try guard.readUtf8File(io, allocator, text_scripts_readme_path_path);
    defer allocator.free(text_scripts_readme_path);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text_scripts_readme_path, marker);
    const text_required_markers__documentation_zigux_phase8-tooling-lane-sequencing_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-tooling-lane-sequencing/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase8-tooling-lane-sequencing_md_path);
    const text_required_markers__documentation_zigux_phase8-tooling-lane-sequencing_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase8-tooling-lane-sequencing_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase8-tooling-lane-sequencing_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase8-tooling-lane-sequencing_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase8-tooling-lane-sequencing_md, marker);
    const text_required_markers__scripts_zigux_readme_md_path = try guard.joinPath(allocator, root, "scripts/zigux/README/md");
    defer allocator.free(text_required_markers__scripts_zigux_readme_md_path);
    const text_required_markers__scripts_zigux_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_readme_md_path);
    defer allocator.free(text_required_markers__scripts_zigux_readme_md);
    for (REQUIRED_MARKERS__scripts_zigux_README_md) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_readme_md, marker);
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
