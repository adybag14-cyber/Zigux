const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_VALIDATE=pass";
pub const self_test_pass_marker = "PHASE7_VALIDATE_SELF_TEST=pass";

const EXPECTED_PACKET = [_][]const u8{
    "phase7-leaf-library-evidence",
};

const EXPECTED_SCOPE = [_][]const u8{
    "shared leaf-library evidence rows and validation foothold only",
};

const EXPECTED_COMPANIONS = [_][]const u8{
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts\\zigux/check_phase7_shared_surface.zig",
    "scripts\\zigux/check_phase7_build_wiring.zig",
    "scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "scripts\\zigux/check_phase7_cmdline_packet.zig",
    "scripts\\zigux/check_phase7_argv_split_packet.zig",
    "scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "scripts\\zigux/check_phase7_rbtree_parity.zig",
    "scripts\\zigux/validate_phase7.zig",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase7_leaf_library_evidence_manifest.json",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
};

const EXPECTED_ROADMAP_ANCHORS = [_][]const u8{
    "lib/string_helpers.c",
    "lib/cmdline.c",
    "lib/argv_split.c",
    "lib/rbtree.c",
};

const EXPECTED_REPLAYS = [_][]const u8{
    "zig run scripts/zigux/check_phase7_shared_surface.zig",
    "zig run scripts/zigux/check_phase7_shared_surface.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_build_wiring.zig",
    "zig run scripts/zigux/check_phase7_build_wiring.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_cmdline_packet.zig",
    "zig run scripts/zigux/check_phase7_cmdline_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_argv_split_packet.zig",
    "zig run scripts/zigux/check_phase7_argv_split_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_rbtree_parity.zig",
    "zig run scripts/zigux/check_phase7_rbtree_parity.zig -- --self-test",
    "zig run scripts/zigux/validate_phase7.zig",
    "zig run scripts/zigux/validate_phase7.zig -- --self-test",
    "make -C zigux phase7-validate",
};

const EXPECTED_GAPS = [_][]const u8{
    "shared `scripts/zigux/README.md` and `zigux/tests/README.md` Phase 7 reminder text still omits the shipped `scripts\\zigux/check_phase7_cmdline_packet.zig` guard from the shared packet inventory",
};

const REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "phase7-validate:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig -- --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig",
};

const BUILD_WIRING_CHECKER_MARKERS = [_][]const u8{
    "const BUILD_REQUIRED_SNIPPETS",
    "zigux/tests/phase7_build.zig",
    "lib/rbtree.zig",
    "for (BUILD_REQUIRED_SNIPPETS)",
    "for (RBTREE_REQUIRED_SNIPPETS)",
};

const BUILD_REQUIRED_SNIPPETS = [_][]const u8{
    "../../lib/string_helpers.zig",
    "../../lib/cmdline.zig",
    "../../lib/argv_split.zig",
    "../../lib/rbtree.zig",
    "phase7-string-helpers-test",
    "phase7-string-helpers-survey",
    "phase7-string-helpers-sample-boundary",
    "phase7-string-helpers-format-boundary",
    "string_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step)",
    "string_helpers_format_boundary_step.dependOn(&run_string_helpers_format_boundary_tests.step)",
    "phase7-cmdline-test",
    "phase7-cmdline-survey",
    "cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step)",
    "phase7-argv-split-test",
    "phase7-argv-split-survey",
    "argv_split_survey_step.dependOn(&run_argv_split_survey_tests.step)",
    "phase7-rbtree-test",
    "phase7-rbtree-survey",
    "const test_step = b.step(\"test\", \"Run the Phase 7 runtime helper tests\");",
    "test_step.dependOn(&run_string_helpers_tests.step)",
    "test_step.dependOn(&run_string_helpers_survey_tests.step)",
    "test_step.dependOn(&run_string_helpers_sample_boundary_tests.step)",
    "test_step.dependOn(&run_string_helpers_format_boundary_tests.step)",
    "test_step.dependOn(&run_cmdline_tests.step)",
    "test_step.dependOn(&run_cmdline_survey_tests.step)",
    "test_step.dependOn(&run_argv_split_tests.step)",
    "test_step.dependOn(&run_argv_split_survey_tests.step)",
    "test_step.dependOn(&run_rbtree_tests.step)",
    "test_step.dependOn(&run_rbtree_survey_tests.step)",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_expected_packet_path);
    const text_expected_packet = try guard.readUtf8File(io, allocator, text_expected_packet_path);
    defer allocator.free(text_expected_packet);
    for (EXPECTED_PACKET) |marker| try guard.requireMarker(text_expected_packet, marker);
    const text_expected_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_expected_scope_path);
    const text_expected_scope = try guard.readUtf8File(io, allocator, text_expected_scope_path);
    defer allocator.free(text_expected_scope);
    for (EXPECTED_SCOPE) |marker| try guard.requireMarker(text_expected_scope, marker);
    const text_expected_companions_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_expected_companions_path);
    const text_expected_companions = try guard.readUtf8File(io, allocator, text_expected_companions_path);
    defer allocator.free(text_expected_companions);
    for (EXPECTED_COMPANIONS) |marker| try guard.requireMarker(text_expected_companions, marker);
    const text_expected_roadmap_anchors_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_expected_roadmap_anchors_path);
    const text_expected_roadmap_anchors = try guard.readUtf8File(io, allocator, text_expected_roadmap_anchors_path);
    defer allocator.free(text_expected_roadmap_anchors);
    for (EXPECTED_ROADMAP_ANCHORS) |marker| try guard.requireMarker(text_expected_roadmap_anchors, marker);
    const text_expected_replays_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_expected_replays_path);
    const text_expected_replays = try guard.readUtf8File(io, allocator, text_expected_replays_path);
    defer allocator.free(text_expected_replays);
    for (EXPECTED_REPLAYS) |marker| try guard.requireMarker(text_expected_replays, marker);
    const text_expected_gaps_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_expected_gaps_path);
    const text_expected_gaps = try guard.readUtf8File(io, allocator, text_expected_gaps_path);
    defer allocator.free(text_expected_gaps);
    for (EXPECTED_GAPS) |marker| try guard.requireMarker(text_expected_gaps, marker);
    const text_required_makefile_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_makefile_lines_path);
    const text_required_makefile_lines = try guard.readUtf8File(io, allocator, text_required_makefile_lines_path);
    defer allocator.free(text_required_makefile_lines);
    for (REQUIRED_MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_required_makefile_lines, marker, 1);
    const text_build_wiring_failure_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/check_phase7_build_wiring.zig");
    defer allocator.free(text_build_wiring_failure_markers_path);
    const text_build_wiring_failure_markers = try guard.readUtf8File(io, allocator, text_build_wiring_failure_markers_path);
    defer allocator.free(text_build_wiring_failure_markers);
    for (BUILD_WIRING_CHECKER_MARKERS) |marker| try guard.requireMarker(text_build_wiring_failure_markers, marker);
    const text_build_required_snippets_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_build.zig");
    defer allocator.free(text_build_required_snippets_path);
    const text_build_required_snippets = try guard.readUtf8File(io, allocator, text_build_required_snippets_path);
    defer allocator.free(text_build_required_snippets);
    for (BUILD_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(text_build_required_snippets, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);
    defer allocator.free(args);

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
        _ = try runSelfTest(io, allocator);
        return;
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
