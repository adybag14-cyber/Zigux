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
    "zig run scripts\\zigux/check_phase7_shared_surface.zig",
    "zig run scripts\\zigux/check_phase7_shared_surface.zig --self-test",
    "zig run scripts\\zigux/check_phase7_build_wiring.zig",
    "zig run scripts\\zigux/check_phase7_build_wiring.zig --self-test",
    "zig run scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "zig run scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig --self-test",
    "zig run scripts\\zigux/check_phase7_cmdline_packet.zig",
    "zig run scripts\\zigux/check_phase7_cmdline_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase7_argv_split_packet.zig",
    "zig run scripts\\zigux/check_phase7_argv_split_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "zig run scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase7_rbtree_parity.zig",
    "zig run scripts\\zigux/check_phase7_rbtree_parity.zig --self-test",
    "zig run scripts\\zigux/validate_phase7.zig",
    "zig run scripts\\zigux/validate_phase7.zig --self-test",
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
    "- `zig run scripts\\zigux/check_phase7_build_wiring.zig`",
    "- `zig run scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig`",
    "- `zig run scripts\\zigux/check_phase7_cmdline_packet.zig`",
    "- `zig run scripts\\zigux/check_phase7_argv_split_packet.zig`",
    "- `zig run scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig`",
    "- `zig run scripts\\zigux/check_phase7_rbtree_parity.zig`",
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
    "phase7 build-wiring evidence drift",
    "phase7 build marker missing: ../../lib/rbtree.zig",
    "phase7 build marker missing: phase7-rbtree-test",
    "CMDLINE_PACKET_CHECKER_PATH = Path(\"scripts\\zigux/check_phase7_cmdline_packet.zig\")",
    "ARGV_SPLIT_PACKET_CHECKER_PATH = Path(\"scripts\\zigux/check_phase7_argv_split_packet.zig\")",
    "STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH = Path(\"scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig\")",
    "RBTREE_PARITY_PACKET_CHECKER_PATH = Path(\"scripts\\zigux/check_phase7_rbtree_parity.zig\")",
    "run_checker(root, CMDLINE_PACKET_CHECKER_PATH)",
    "run_checker(root, ARGV_SPLIT_PACKET_CHECKER_PATH)",
    "run_checker(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH, \"--root\")",
    "run_checker(root, RBTREE_PARITY_PACKET_CHECKER_PATH)",
};

const MAKEFILE_REQUIRED_LINES = [_][]const u8{
    "phase7-validate:",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig --self-test",
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

const EXPECTED_HELPER_EVIDENCE = [_][]const u8{
    "{key:string_helpers",
    "zig_helper:lib/string_helpers.zig",
    "expected_markers:pub const STRING_UNITS_10pub const KasprintfStrarrayResultpub fn kstrdupQuotablepub fn kstrdupQuotableCmdline",
    "}",
    "{key:string_helpers_parse_int_array",
    "zig_helper:lib/string_helpers.zig",
    "expected_markers:pub const ParseIntArrayErrorpub fn parseIntArray",
    "}",
    "{key:cmdline",
    "zig_helper:lib/cmdline.zig",
    "expected_markers:pub fn parseOptionStrpub fn getOption",
    "}",
    "{key:argv_split",
    "zig_helper:lib/argv_split.zig",
    "expected_markers:pub const ArgvSplitResultpub fn argvSplit",
    "}",
    "{key:rbtree",
    "zig_helper:lib/rbtree.zig",
    "expected_markers:pub const Node = structpub const RootCached = structpub fn add(pub fn rb_find_add_cached(",
    "}",
};

const EXPECTED_BUILD_WIRING_EVIDENCE = [_][]const u8{
    "{path:zigux/tests/phase7_build.zig",
    "expected_markers:../../lib/string_helpers.zig../../lib/cmdline.zig../../lib/argv_split.zig../../lib/rbtree.zigphase7-string-helpers-testphase7-string-helpers-surveyphase7-string-helpers-sample-boundaryphase7-string-helpers-format-boundarystring_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step)string_helpers_format_boundary_step.dependOn(&run_string_helpers_format_boundary_tests.step)phase7-cmdline-testphase7-cmdline-surveycmdline_survey_step.dependOn(&run_cmdline_survey_tests.step)phase7-argv-split-testphase7-argv-split-surveyargv_split_survey_step.dependOn(&run_argv_split_survey_tests.step)phase7-rbtree-testphase7-rbtree-surveyconst test_step = b.step(\"test\", \"Run the Phase 7 runtime helper tests\");test_step.dependOn(&run_string_helpers_tests.step)test_step.dependOn(&run_string_helpers_survey_tests.step)test_step.dependOn(&run_string_helpers_sample_boundary_tests.step)test_step.dependOn(&run_string_helpers_format_boundary_tests.step)test_step.dependOn(&run_cmdline_tests.step)test_step.dependOn(&run_cmdline_survey_tests.step)test_step.dependOn(&run_argv_split_tests.step)test_step.dependOn(&run_argv_split_survey_tests.step)test_step.dependOn(&run_rbtree_tests.step)test_step.dependOn(&run_rbtree_survey_tests.step)",
    "}",
    "{path:zigux/Makefile",
    "expected_markers:phase7-validate:$(ZIG) run scripts/zigux/validate_phase7.zig --self-test$(ZIG) run scripts/zigux/validate_phase7.zig",
    "}",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_packet_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase7.zig");
    defer allocator.free(text_expected_packet_path);
    const text_expected_packet = try guard.readUtf8File(io, allocator, text_expected_packet_path);
    defer allocator.free(text_expected_packet);
    for (EXPECTED_PACKET) |marker| try guard.requireMarker(text_expected_packet, marker);
    const text_expected_scope_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase7.zig");
    defer allocator.free(text_expected_scope_path);
    const text_expected_scope = try guard.readUtf8File(io, allocator, text_expected_scope_path);
    defer allocator.free(text_expected_scope);
    for (EXPECTED_SCOPE) |marker| try guard.requireMarker(text_expected_scope, marker);
    const text_expected_replays_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase7.zig");
    defer allocator.free(text_expected_replays_path);
    const text_expected_replays = try guard.readUtf8File(io, allocator, text_expected_replays_path);
    defer allocator.free(text_expected_replays);
    for (EXPECTED_REPLAYS) |marker| try guard.requireMarker(text_expected_replays, marker);
    const text_expected_direct_companions_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase7.zig");
    defer allocator.free(text_expected_direct_companions_path);
    const text_expected_direct_companions = try guard.readUtf8File(io, allocator, text_expected_direct_companions_path);
    defer allocator.free(text_expected_direct_companions);
    for (EXPECTED_DIRECT_COMPANIONS) |marker| try guard.requireMarker(text_expected_direct_companions, marker);
    const text_expected_roadmap_anchors_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase7.zig");
    defer allocator.free(text_expected_roadmap_anchors_path);
    const text_expected_roadmap_anchors = try guard.readUtf8File(io, allocator, text_expected_roadmap_anchors_path);
    defer allocator.free(text_expected_roadmap_anchors);
    for (EXPECTED_ROADMAP_ANCHORS) |marker| try guard.requireMarker(text_expected_roadmap_anchors, marker);
    const text_expected_repo_gaps_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase7.zig");
    defer allocator.free(text_expected_repo_gaps_path);
    const text_expected_repo_gaps = try guard.readUtf8File(io, allocator, text_expected_repo_gaps_path);
    defer allocator.free(text_expected_repo_gaps);
    for (EXPECTED_REPO_GAPS) |marker| try guard.requireMarker(text_expected_repo_gaps, marker);
    const text_catalog_required_snippets_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase7.zig");
    defer allocator.free(text_catalog_required_snippets_path);
    const text_catalog_required_snippets = try guard.readUtf8File(io, allocator, text_catalog_required_snippets_path);
    defer allocator.free(text_catalog_required_snippets);
    for (CATALOG_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(text_catalog_required_snippets, marker);
    const text_validator_required_snippets_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase7.zig");
    defer allocator.free(text_validator_required_snippets_path);
    const text_validator_required_snippets = try guard.readUtf8File(io, allocator, text_validator_required_snippets_path);
    defer allocator.free(text_validator_required_snippets);
    for (VALIDATOR_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(text_validator_required_snippets, marker);
    const text_makefile_required_lines_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase7.zig");
    defer allocator.free(text_makefile_required_lines_path);
    const text_makefile_required_lines = try guard.readUtf8File(io, allocator, text_makefile_required_lines_path);
    defer allocator.free(text_makefile_required_lines);
    for (MAKEFILE_REQUIRED_LINES) |marker| try guard.requireExactLineCount(text_makefile_required_lines, marker, 1);
    const text_forbidden_makefile_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase7.zig");
    defer allocator.free(text_forbidden_makefile_markers_path);
    const text_forbidden_makefile_markers = try guard.readUtf8File(io, allocator, text_forbidden_makefile_markers_path);
    defer allocator.free(text_forbidden_makefile_markers);
    for (FORBIDDEN_MAKEFILE_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_makefile_markers, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_build_required_snippets_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase7.zig");
    defer allocator.free(text_build_required_snippets_path);
    const text_build_required_snippets = try guard.readUtf8File(io, allocator, text_build_required_snippets_path);
    defer allocator.free(text_build_required_snippets);
    for (BUILD_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(text_build_required_snippets, marker);
    const text_rbtree_required_snippets_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase7.zig");
    defer allocator.free(text_rbtree_required_snippets_path);
    const text_rbtree_required_snippets = try guard.readUtf8File(io, allocator, text_rbtree_required_snippets_path);
    defer allocator.free(text_rbtree_required_snippets);
    for (RBTREE_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(text_rbtree_required_snippets, marker);
    const text_expected_helper_evidence_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_helper_evidence_path);
    const text_expected_helper_evidence = try guard.readUtf8File(io, allocator, text_expected_helper_evidence_path);
    defer allocator.free(text_expected_helper_evidence);
    for (EXPECTED_HELPER_EVIDENCE) |marker| try guard.requireMarker(text_expected_helper_evidence, marker);
    const text_expected_build_wiring_evidence_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_build_wiring_evidence_path);
    const text_expected_build_wiring_evidence = try guard.readUtf8File(io, allocator, text_expected_build_wiring_evidence_path);
    defer allocator.free(text_expected_build_wiring_evidence);
    for (EXPECTED_BUILD_WIRING_EVIDENCE) |marker| try guard.requireMarker(text_expected_build_wiring_evidence, marker);
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
