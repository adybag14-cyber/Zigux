const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_BUILD_WIRING=pass";
pub const self_test_pass_marker = "PHASE7_BUILD_WIRING_SELF_TEST=pass";

const EXPECTED_PACKET = [_][]const u8{
    "phase7-leaf-library-evidence",
};

const EXPECTED_SCOPE = [_][]const u8{
    "shared leaf-library evidence rows and validation foothold only",
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

const EXPECTED_DIRECT_COMPANIONS = [_][]const u8{
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

const EXPECTED_REPO_GAPS = [_][]const u8{
    "shared `scripts/zigux/README.md` and `zigux/tests/README.md` Phase 7 reminder text still omits the shipped `scripts\\zigux/check_phase7_cmdline_packet.zig` guard from the shared packet inventory",
};

const CATALOG_REQUIRED_SNIPPETS = [_][]const u8{
    "## Current direct-readback companions",
    "- `Documentation/zigux/review-checklist.md`",
    "- `scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig`",
    "- `scripts\\zigux/check_phase7_cmdline_packet.zig`",
    "- `scripts\\zigux/check_phase7_argv_split_packet.zig`",
    "- `scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig`",
    "- `scripts\\zigux/check_phase7_rbtree_parity.zig`",
    "- `zigux/tests/phase7_build.zig`",
    "- `lib/rbtree.zig`",
    "## Current replay inventory",
    "- `zig run scripts/zigux/check_phase7_build_wiring.zig`",
    "- `zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig`",
    "- `zig run scripts/zigux/check_phase7_cmdline_packet.zig`",
    "- `zig run scripts/zigux/check_phase7_argv_split_packet.zig`",
    "- `zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig`",
    "- `zig run scripts/zigux/check_phase7_rbtree_parity.zig`",
    "- `make -C zigux phase7-validate`",
    "## Current build-wiring evidence",
    "- `zigux/tests/phase7_build.zig` wires `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` into the shared Phase 7 build graph.",
    "- `zigux/tests/phase7_build.zig` still exposes the dedicated helper, survey, sample-boundary, and format-boundary routes through `phase7-string-helpers-test`, `phase7-string-helpers-survey`, `phase7-string-helpers-sample-boundary`, `phase7-string-helpers-format-boundary`, `phase7-cmdline-test`, `phase7-cmdline-survey`, `phase7-argv-split-test`, `phase7-argv-split-survey`, `phase7-rbtree-test`, and `phase7-rbtree-survey`.",
    "- `zigux/tests/phase7_build.zig` keeps the shared `test` build step aggregating every helper, survey, sample-boundary, and format-boundary replay through the current `test_step.dependOn(...)` handoff list.",
    "- `zigux/Makefile` keeps the narrow `phase7-validate` foothold explicit while broader wrapper routes remain outside this packet.",
    "## Current repo-reality gaps",
    "- shared `scripts/zigux/README.md` and `zigux/tests/README.md` Phase 7 reminder text still omits the shipped `scripts\\zigux/check_phase7_cmdline_packet.zig` guard from the shared packet inventory",
};

const VALIDATOR_REQUIRED_SNIPPETS = [_][]const u8{
    "pub const live_pass_marker = \"PHASE7_VALIDATE=pass\";",
    "pub const self_test_pass_marker = \"PHASE7_VALIDATE_SELF_TEST=pass\";",
    "const REQUIRED_MAKEFILE_LINES",
    "const BUILD_REQUIRED_SNIPPETS",
    "zigux/Makefile",
    "zigux/tests/phase7_build.zig",
    "for (REQUIRED_MAKEFILE_LINES)",
    "for (BUILD_REQUIRED_SNIPPETS)",
};

const MAKEFILE_REQUIRED_LINES = [_][]const u8{
    "phase7-validate:",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig -- --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig",
};

const FORBIDDEN_MAKEFILE_MARKERS = [_][]const u8{
    "phase7-test:",
    "phase7:",
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

const RBTREE_REQUIRED_SNIPPETS = [_][]const u8{
    "pub const Node = struct",
    "pub const RootCached = struct",
    "pub fn add(",
    "pub fn rb_find_add_cached(",
};

const STRING_HELPERS_REQUIRED_SNIPPETS = [_][]const u8{
    "pub const STRING_UNITS_10",
    "pub const KasprintfStrarrayResult",
    "pub fn kstrdupQuotable",
    "pub fn kstrdupQuotableCmdline",
    "pub const ParseIntArrayError",
    "pub fn parseIntArray",
};

const CMDLINE_REQUIRED_SNIPPETS = [_][]const u8{
    "pub fn parseOptionStr",
    "pub fn getOption",
};

const ARGV_SPLIT_REQUIRED_SNIPPETS = [_][]const u8{
    "pub const ArgvSplitResult",
    "pub fn argvSplit",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const catalog_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(catalog_path);
    const catalog = try guard.readUtf8File(io, allocator, catalog_path);
    defer allocator.free(catalog);
    for (EXPECTED_PACKET) |marker| try guard.requireMarker(catalog, marker);
    for (EXPECTED_SCOPE) |marker| try guard.requireMarker(catalog, marker);
    for (EXPECTED_REPLAYS) |marker| try guard.requireMarker(catalog, marker);
    for (EXPECTED_DIRECT_COMPANIONS) |marker| try guard.requireMarker(catalog, marker);
    for (EXPECTED_ROADMAP_ANCHORS) |marker| try guard.requireMarker(catalog, marker);
    for (EXPECTED_REPO_GAPS) |marker| try guard.requireMarker(catalog, marker);
    for (CATALOG_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(catalog, marker);

    const validator_path = try guard.joinPath(allocator, root, "scripts/zigux/validate_phase7.zig");
    defer allocator.free(validator_path);
    const validator = try guard.readUtf8File(io, allocator, validator_path);
    defer allocator.free(validator);
    for (VALIDATOR_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(validator, marker);

    const makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(makefile_path);
    const makefile = try guard.readUtf8File(io, allocator, makefile_path);
    defer allocator.free(makefile);
    for (MAKEFILE_REQUIRED_LINES) |marker| try guard.requireExactLineCount(makefile, marker, 1);
    for (FORBIDDEN_MAKEFILE_MARKERS) |marker| {
        if (std.mem.indexOf(u8, makefile, marker) != null) return guard.GuardError.MissingMarker;
    }

    const build_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_path);
    const build = try guard.readUtf8File(io, allocator, build_path);
    defer allocator.free(build);
    for (BUILD_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(build, marker);

    const string_helpers_path = try guard.joinPath(allocator, root, "lib/string_helpers.zig");
    defer allocator.free(string_helpers_path);
    const string_helpers = try guard.readUtf8File(io, allocator, string_helpers_path);
    defer allocator.free(string_helpers);
    for (STRING_HELPERS_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(string_helpers, marker);

    const cmdline_path = try guard.joinPath(allocator, root, "lib/cmdline.zig");
    defer allocator.free(cmdline_path);
    const cmdline = try guard.readUtf8File(io, allocator, cmdline_path);
    defer allocator.free(cmdline);
    for (CMDLINE_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(cmdline, marker);

    const argv_split_path = try guard.joinPath(allocator, root, "lib/argv_split.zig");
    defer allocator.free(argv_split_path);
    const argv_split = try guard.readUtf8File(io, allocator, argv_split_path);
    defer allocator.free(argv_split);
    for (ARGV_SPLIT_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(argv_split, marker);

    const rbtree_path = try guard.joinPath(allocator, root, "lib/rbtree.zig");
    defer allocator.free(rbtree_path);
    const rbtree = try guard.readUtf8File(io, allocator, rbtree_path);
    defer allocator.free(rbtree);
    for (RBTREE_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(rbtree, marker);
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
