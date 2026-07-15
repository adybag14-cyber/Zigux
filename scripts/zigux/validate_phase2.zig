const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");
const policy = @import("toolchain_policy.zig");

pub const live_pass_marker = "PHASE2_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE2_VALIDATION_SELF_TEST=pass";

const expected_channel = "0.17.0-dev.1415+64dfaa568";
const expected_targets = [_][]const u8{
    "x86_64-linux",
    "x86_64-windows",
};
const expected_make_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

const required_paths = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/toolchain_policy.zig",
    "scripts/zigux/toolchain_resolver.zig",
    "scripts/zigux/check_zig_toolchain.zig",
    "scripts/zigux/install_zig.zig",
    "scripts/zigux/stage_pinned_zig_archive.zig",
    "scripts/zigux/check_phase2_toolchain_pinning.zig",
    "scripts/zigux/check_phase2_toolchain_pin_scope.zig",
    "scripts/zigux/check_phase2_kbuild_routes.zig",
    "scripts/zigux/check_phase2_tests_readme_alignment.zig",
    "scripts/zigux/check_phase2_cross.zig",
    "scripts/zigux/check_phase2_cross_selftest_alignment.zig",
    "scripts/zigux/check_phase2_required_make_routes.zig",
    "scripts/zigux/check_phase2_bootstrap_workflow_routes.zig",
    "scripts/zigux/check_phase2_docs_shared_reminder.zig",
    "scripts/zigux/check_phase2_tool_manifest.zig",
    "scripts/zigux/check_phase2_artifact_tools_manifest.zig",
    "scripts/zigux/check_kconfig_bridge.zig",
    "scripts/zigux/check_phase2_kconfig_selftest_alignment.zig",
    "scripts/zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/check_genksyms_bridge.zig",
    "scripts/zigux/check_phase2_genksyms_selftest_alignment.zig",
    "scripts/zigux/check_phase2_genksyms_dual_implementation_survey.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/check_phase2_fixdep_gate.zig",
    "scripts/zigux/check_fixdep_diff.zig",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/validate_phase2_closure.zig",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/fixdep/cases.json",
    "third_party/README.md",
};

const workflow_markers = [_][]const u8{
    "- name: Setup pinned Zig toolchain",
    "target = \"x86_64-linux\"",
    "canonical_tag = \"upstream-64dfaa568db0\"",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --self-test",
    "run: zig run check_phase2_toolchain_pinning.zig --self-test",
    "run: zig run check_phase2_toolchain_pin_scope.zig --self-test",
    "run: zig run check_kconfig_bridge.zig --self-test",
    "run: zig run check_genksyms_bridge.zig --self-test",
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
    "ZIG_PINNED_CHANNEL :=",
    "ZIG_PINNED_TARGET :=",
    "ZIG_PINNED_EXTRACT_ROOT :=",
    "ZIG_PINNED_TOOLCHAIN :=",
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
    "check_phase2_toolchain_pinning.zig --self-test",
    "check_phase2_toolchain_pin_scope.zig --self-test",
    "validate_phase2_closure.zig",
};

const bootstrap_note_markers = [_][]const u8{
    expected_channel,
    "`x86_64-linux` and `x86_64-windows`",
    "`scripts\\zigux/check_phase2_toolchain_pinning.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`scripts\\zigux/check_kconfig_bridge.zig`",
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`",
    "`scripts\\zigux/check_fixdep_diff.zig`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
};

const tool_manifest_markers = [_][]const u8{
    "\"phase\": \"Phase 2\"",
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
    "zig-x86_64-linux-0.17.0-dev.1415+64dfaa568.tar.xz",
    "check_phase2_toolchain_pinning.zig",
    "check_phase2_toolchain_pin_scope.zig",
    "validate_phase2.zig",
    "validate_phase2_closure.zig",
};

const artifact_manifest_markers = [_][]const u8{
    "\"phase\": \"Phase 2\"",
    "\"status\": \"active\"",
    "\"scripts/zigux/artifact_diff.zig\"",
    "check_kconfig_bridge.zig",
    "check_fixdep_diff.zig",
    "\"text\"",
    "\"json\"",
    "\"bytes\"",
};

const cross_manifest_markers = [_][]const u8{
    "\"phase\": \"Phase 2\"",
    "\"status\": \"active\"",
    "\"route\": \"make -C zigux phase2-cross\"",
    "\"target\": \"x86_64-linux\"",
    "\"validation_mode\": \"archive_required\"",
    "\"target\": \"aarch64-linux\"",
    "\"validation_mode\": \"route_contract_only\"",
};

const resolver_markers = [_][]const u8{
    "pub fn hostArchiveTarget() ?[]const u8",
    "\"x86_64-windows\"",
    "\"zig.exe\"",
    "\"bin/zig.exe\"",
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

fn validatePolicy(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const path = try guard.joinPath(allocator, root, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(path);
    const text = try guard.readUtf8File(io, allocator, path);
    defer allocator.free(text);

    var loaded = try policy.loadPolicyFromJson(allocator, text);
    defer policy.freePolicy(allocator, &loaded);

    if (!std.mem.eql(u8, loaded.phase, "Phase 2")) return guard.GuardError.ValidationFailed;
    if (!std.mem.eql(u8, loaded.channel, expected_channel)) return guard.GuardError.ValidationFailed;
    if (!std.mem.eql(u8, loaded.minimum_version, expected_channel)) return guard.GuardError.ValidationFailed;
    if (!loaded.upgrade_policy.channel_minimum_lockstep) return guard.GuardError.ValidationFailed;

    if (loaded.upgrade_policy.archive_target_scope.len != expected_targets.len) return guard.GuardError.ValidationFailed;
    for (expected_targets, 0..) |expected, index| {
        if (!std.mem.eql(u8, loaded.upgrade_policy.archive_target_scope[index], expected)) {
            return guard.GuardError.ValidationFailed;
        }
        const digest = loaded.archive_sha256.get(expected) orelse return guard.GuardError.ValidationFailed;
        if (!policy.isValidSha256Hex(digest)) return guard.GuardError.ValidationFailed;
    }

    if (loaded.upgrade_policy.required_make_routes.len != expected_make_routes.len) return guard.GuardError.ValidationFailed;
    for (expected_make_routes, 0..) |expected, index| {
        if (!std.mem.eql(u8, loaded.upgrade_policy.required_make_routes[index], expected)) {
            return guard.GuardError.ValidationFailed;
        }
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_paths) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) return guard.GuardError.IOError;
    }

    try validatePolicy(io, allocator, root);
    try readAndRequire(io, allocator, root, ".github/workflows/zigux-bootstrap.yml", &workflow_markers);
    try readAndRequire(io, allocator, root, "zigux/Makefile", &makefile_markers);
    try readAndRequire(io, allocator, root, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md", &bootstrap_note_markers);
    try readAndRequire(io, allocator, root, "zigux/tests/fixtures/phase2_tool_manifest.json", &tool_manifest_markers);
    try readAndRequire(io, allocator, root, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json", &artifact_manifest_markers);
    try readAndRequire(io, allocator, root, "zigux/tests/fixtures/phase2_cross_targets.json", &cross_manifest_markers);
    try readAndRequire(io, allocator, root, "scripts/zigux/toolchain_resolver.zig", &resolver_markers);
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
