const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_CLOSURE_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass";

const required_paths = [_][]const u8{
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
    "Documentation/zigux/phase2-fixdep-dual-implementation-survey.md",
    "Documentation/zigux/phase2-kconfig-bridge-gap-survey.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/validate_phase2.zig",
    "scripts/zigux/check_phase2_tool_manifest.zig",
    "scripts/zigux/check_phase2_artifact_tools_manifest.zig",
    "scripts/zigux/check_phase2_bootstrap_workflow_routes.zig",
    "scripts/zigux/check_phase2_toolchain_pinning.zig",
    "scripts/zigux/check_phase2_toolchain_pin_scope.zig",
    "scripts/zigux/check_kconfig_bridge.zig",
    "scripts/zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
    "scripts/zigux/check_genksyms_bridge.zig",
    "scripts/zigux/check_phase2_genksyms_selftest_alignment.zig",
    "scripts/zigux/check_phase2_genksyms_dual_implementation_survey.zig",
    "scripts/zigux/check_phase2_cross.zig",
    "scripts/zigux/check_phase2_fixdep_gate.zig",
    "scripts/zigux/check_fixdep_diff.zig",
    "scripts/zigux/artifact_diff.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/fixdep.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/fixdep/cases.json",
};

const closure_markers = [_][]const u8{
    "PHASE2_STATUS=parked",
    "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest",
    "shared validator pair: `zig run validate_phase2.zig` and `zig run validate_phase2_closure.zig`",
    "scripts\\zigux/check_genksyms_bridge.zig",
    "scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig",
    "scripts\\zigux/check_phase2_genksyms_dual_implementation_survey.zig",
    "scripts\\zigux/check_phase2_tool_manifest.zig",
    "scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig",
    "scripts\\zigux/check_phase2_artifact_tools_manifest.zig",
    "scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
    "scripts\\zigux/check_phase2_cross.zig",
    "scripts\\zigux/check_phase2_fixdep_gate.zig",
    "scripts\\zigux/check_fixdep_diff.zig",
    "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2",
    "validate_phase2_closure.zig",
    "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md",
};

const workflow_markers = [_][]const u8{
    "run: zig run check_phase2_tool_manifest.zig --self-test",
    "run: zig run check_phase2_artifact_tools_manifest.zig --self-test",
    "run: zig run check_kconfig_bridge.zig --self-test",
    "run: zig run check_phase2_cross.zig --self-test",
    "run: zig run check_genksyms_bridge.zig --self-test",
    "run: zig run check_phase2_genksyms_selftest_alignment.zig --self-test",
    "run: zig run check_phase2_genksyms_dual_implementation_survey.zig --self-test",
    "run: zig run check_phase2_fixdep_gate.zig --self-test",
    "run: zig run check_fixdep_diff.zig --self-test",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
    "validate_phase2.zig",
    "run: zig run validate_phase2_closure.zig --self-test",
    "validate_phase2_closure.zig",
};

const makefile_markers = [_][]const u8{
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
    "check_phase2_tool_manifest.zig --self-test",
    "validate_phase2_closure.zig",
};

const manifest_markers = [_][]const u8{
    "\"phase\": \"Phase 2\"",
    "\"present_surfaces\"",
    "\"archive_support\"",
    "\"artifact_support\"",
    "\"bootstrap_helpers\"",
    "\"bridge_helpers\"",
    "\"checkers\"",
    "\"closure_notes\"",
    "\"cross_route_support\"",
    "\"fixdep_support\"",
    "\"fixture_roster\"",
    "\"make_wrappers\"",
    "\"policy\"",
    "validate_phase2.zig",
    "validate_phase2_closure.zig",
    "check_phase2_toolchain_pinning.zig",
    "check_phase2_toolchain_pin_scope.zig",
    "zig-x86_64-linux-0.17.0-dev.1415+64dfaa568.tar.xz",
};

const artifact_manifest_markers = [_][]const u8{
    "\"status\": \"active\"",
    "\"scope\": \"artifact-diff support for fixture-backed scripts/zigux validation\"",
    "\"scripts/zigux/artifact_diff.zig\"",
    "check_kconfig_bridge.zig",
    "check_fixdep_diff.zig",
};

const scripts_readme_markers = [_][]const u8{
    "Phase 2 flow",
    "`scripts\\zigux/check_phase2_toolchain_pinning.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`",
    "`scripts\\zigux/check_fixdep_diff.zig`",
    "`make -C zigux phase2-validate`",
};

const tests_readme_markers = [_][]const u8{
    "`scripts\\zigux/validate_phase2.zig`",
    "`scripts\\zigux/validate_phase2_closure.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pinning.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`scripts\\zigux/check_kconfig_bridge.zig`",
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`",
    "`scripts\\zigux/check_fixdep_diff.zig`",
    "`make -C zigux phase2-validate`",
};

const aggregate_validator_markers = [_][]const u8{
    "pub const live_pass_marker = \"PHASE2_VALIDATION=pass\";",
    "pub const self_test_pass_marker = \"PHASE2_VALIDATION_SELF_TEST=pass\";",
    "try validatePolicy(io, allocator, root);",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
};

fn readAndRequire(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
    rel: []const u8,
    markers: []const []const u8,
) !void {
    const path = try guard.joinPath(allocator, root, rel);
    defer allocator.free(path);
    const text = try guard.readUtf8File(io, allocator, path);
    defer allocator.free(text);
    for (markers) |marker| try guard.requireMarker(text, marker);
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_paths) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) return guard.GuardError.IOError;
    }

    try readAndRequire(io, allocator, root, "Documentation/zigux/phase2-closure.md", &closure_markers);
    try readAndRequire(io, allocator, root, ".github/workflows/zigux-bootstrap.yml", &workflow_markers);
    try readAndRequire(io, allocator, root, "zigux/Makefile", &makefile_markers);
    try readAndRequire(io, allocator, root, "zigux/tests/fixtures/phase2_tool_manifest.json", &manifest_markers);
    try readAndRequire(io, allocator, root, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json", &artifact_manifest_markers);
    try readAndRequire(io, allocator, root, "scripts/zigux/README.md", &scripts_readme_markers);
    try readAndRequire(io, allocator, root, "zigux/tests/README.md", &tests_readme_markers);
    try readAndRequire(io, allocator, root, "scripts/zigux/validate_phase2.zig", &aggregate_validator_markers);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !void {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

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
        std.process.exit(2);
    }

    if (self_test) {
        try runSelfTest(io, allocator);
        return;
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
