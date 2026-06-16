const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_CLOSURE_MATRIX=pass";
pub const self_test_pass_marker = "PHASE2_CLOSURE_MATRIX_SELF_TEST=pass";

const REQUIRED_CLOSURE_MARKERS = [_][]const u8{
    "`marker-a`",
    "`marker-b`",
};

const REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "run: alpha",
    "run: beta",
};

const REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "phase2-a:",
    "phase2-b:",
};

const EXPECTED_CONF_CASE_DETAILS = [_][]const u8{
    "{name:conf",
    "expected:conf.json}",
};

const EXPECTED_CONFDATA_CASE_DETAILS = [_][]const u8{
    "{name:confdata",
    "expected:confdata.json}",
};

const EXPECTED_GENKSYMS_CASES = [_][]const u8{
    "{name:genksyms",
    "expected_file:genksyms.json}",
};

const EXPECTED_MANIFEST_REVIEW_SURFACES = [_][]const u8{
    "review-a.md",
    "review-b.md",
};

const EXPECTED_MANIFEST_CLOSURE_NOTES = [_][]const u8{
    "closure-a.md",
    "closure-b.md",
};

const EXPECTED_MANIFEST_VALIDATORS = [_][]const u8{
    "validate-a.py",
    "validate-b.py",
};

const EXPECTED_MANIFEST_CHECKERS = [_][]const u8{
    "checker-a.py",
    "checker-b.py",
};

const EXPECTED_MANIFEST_BRIDGE_HELPERS = [_][]const u8{
    "bridge-a.zig",
    "bridge-b.zig",
};

const EXPECTED_MANIFEST_FIXTURE_ROSTER = [_][]const u8{
    "fixture-a.json",
    "fixture-b.json",
};

const EXPECTED_MANIFEST_POLICY = [_][]const u8{
    "policy-a.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_closure_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_closure_markers_path);
    const text_required_closure_markers = try guard.readUtf8File(io, allocator, text_required_closure_markers_path);
    defer allocator.free(text_required_closure_markers);
    for (REQUIRED_CLOSURE_MARKERS) |marker| try guard.requireMarker(text_required_closure_markers, marker);
    const text_required_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_workflow_lines_path);
    const text_required_workflow_lines = try guard.readUtf8File(io, allocator, text_required_workflow_lines_path);
    defer allocator.free(text_required_workflow_lines);
    for (REQUIRED_WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_required_workflow_lines, marker, 1);
    const text_required_makefile_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_makefile_lines_path);
    const text_required_makefile_lines = try guard.readUtf8File(io, allocator, text_required_makefile_lines_path);
    defer allocator.free(text_required_makefile_lines);
    for (REQUIRED_MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_required_makefile_lines, marker, 1);
    const text_expected_conf_case_details_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_conf_case_details_path);
    const text_expected_conf_case_details = try guard.readUtf8File(io, allocator, text_expected_conf_case_details_path);
    defer allocator.free(text_expected_conf_case_details);
    for (EXPECTED_CONF_CASE_DETAILS) |marker| try guard.requireMarker(text_expected_conf_case_details, marker);
    const text_expected_confdata_case_details_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_confdata_case_details_path);
    const text_expected_confdata_case_details = try guard.readUtf8File(io, allocator, text_expected_confdata_case_details_path);
    defer allocator.free(text_expected_confdata_case_details);
    for (EXPECTED_CONFDATA_CASE_DETAILS) |marker| try guard.requireMarker(text_expected_confdata_case_details, marker);
    const text_expected_genksyms_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_genksyms_cases_path);
    const text_expected_genksyms_cases = try guard.readUtf8File(io, allocator, text_expected_genksyms_cases_path);
    defer allocator.free(text_expected_genksyms_cases);
    for (EXPECTED_GENKSYMS_CASES) |marker| try guard.requireMarker(text_expected_genksyms_cases, marker);
    const text_expected_manifest_review_surfaces_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_manifest_review_surfaces_path);
    const text_expected_manifest_review_surfaces = try guard.readUtf8File(io, allocator, text_expected_manifest_review_surfaces_path);
    defer allocator.free(text_expected_manifest_review_surfaces);
    for (EXPECTED_MANIFEST_REVIEW_SURFACES) |marker| try guard.requireMarker(text_expected_manifest_review_surfaces, marker);
    const text_expected_manifest_closure_notes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_manifest_closure_notes_path);
    const text_expected_manifest_closure_notes = try guard.readUtf8File(io, allocator, text_expected_manifest_closure_notes_path);
    defer allocator.free(text_expected_manifest_closure_notes);
    for (EXPECTED_MANIFEST_CLOSURE_NOTES) |marker| try guard.requireMarker(text_expected_manifest_closure_notes, marker);
    const text_expected_manifest_validators_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_manifest_validators_path);
    const text_expected_manifest_validators = try guard.readUtf8File(io, allocator, text_expected_manifest_validators_path);
    defer allocator.free(text_expected_manifest_validators);
    for (EXPECTED_MANIFEST_VALIDATORS) |marker| try guard.requireMarker(text_expected_manifest_validators, marker);
    const text_expected_manifest_checkers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_manifest_checkers_path);
    const text_expected_manifest_checkers = try guard.readUtf8File(io, allocator, text_expected_manifest_checkers_path);
    defer allocator.free(text_expected_manifest_checkers);
    for (EXPECTED_MANIFEST_CHECKERS) |marker| try guard.requireMarker(text_expected_manifest_checkers, marker);
    const text_expected_manifest_bridge_helpers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_manifest_bridge_helpers_path);
    const text_expected_manifest_bridge_helpers = try guard.readUtf8File(io, allocator, text_expected_manifest_bridge_helpers_path);
    defer allocator.free(text_expected_manifest_bridge_helpers);
    for (EXPECTED_MANIFEST_BRIDGE_HELPERS) |marker| try guard.requireMarker(text_expected_manifest_bridge_helpers, marker);
    const text_expected_manifest_fixture_roster_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_manifest_fixture_roster_path);
    const text_expected_manifest_fixture_roster = try guard.readUtf8File(io, allocator, text_expected_manifest_fixture_roster_path);
    defer allocator.free(text_expected_manifest_fixture_roster);
    for (EXPECTED_MANIFEST_FIXTURE_ROSTER) |marker| try guard.requireMarker(text_expected_manifest_fixture_roster, marker);
    const text_expected_manifest_policy_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_manifest_policy_path);
    const text_expected_manifest_policy = try guard.readUtf8File(io, allocator, text_expected_manifest_policy_path);
    defer allocator.free(text_expected_manifest_policy);
    for (EXPECTED_MANIFEST_POLICY) |marker| try guard.requireMarker(text_expected_manifest_policy, marker);
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
