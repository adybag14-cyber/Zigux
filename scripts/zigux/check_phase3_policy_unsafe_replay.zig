const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_POLICY_UNSAFE_REPLAY=pass";
pub const self_test_pass_marker = "PHASE3_POLICY_UNSAFE_REPLAY_SELF_TEST=pass";

const REQUIRED_MARKERS__Documentation_zigux_phase3-policy-unsafe-boundary-survey_md = [_][]const u8{
    "PHASE3_POLICY_UNSAFE_REPLAY_GATE=zig run scripts\\zigux/check_phase3_policy_unsafe_replay.zig",
    "scripts\\zigux/check_phase3_policy_unsafe_replay.zig",
    "packet-local replay checker",
};

const REQUIRED_MARKERS__zigux_tests_phase3_policy_unsafe_zig = [_][]const u8{
    "test \"phase3 policy unsafe replay decodes shared policy records\" {",
    "test \"phase3 policy unsafe replay keeps ABI recognition aligned with helper decoders\" {",
    "test \"phase3 policy unsafe replay keeps require gates fail closed\" {",
    "test \"phase3 policy unsafe replay keeps policy consequences explicit\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_policy_unsafe_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../bindings/abi.zig\"),",
    ".root_source_file = b.path(\"../helpers/panic_policy.zig\"),",
    ".root_source_file = b.path(\"../helpers/allocator_policy.zig\"),",
    ".root_source_file = b.path(\"../helpers/unsafe_policy.zig\"),",
    ".root_source_file = b.path(\"../unsafe/narrow.zig\"),",
    ".root_source_file = b.path(\"phase3_policy_unsafe.zig\"),",
    "root_module.addImport(\"panic_policy\", panic_policy);",
    "root_module.addImport(\"allocator_policy\", allocator_policy);",
    "root_module.addImport(\"unsafe_policy\", unsafe_policy);",
    "root_module.addImport(\"narrow\", narrow);",
    "\"phase3-policy-unsafe-test\"",
    "\"Run the focused Phase 3 policy and unsafe replay\"",
};

const REQUIRED_MARKERS__zigux_Makefile = [_][]const u8{
    "phase3-policy-unsafe-test:",
    "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
};

const REQUIRED_MARKERS__zigux_tests_phase3_policy_starter_packet_manifest_json = [_][]const u8{
    "\"zigux/tests/phase3_policy_unsafe.zig\"",
    "\"zigux/tests/phase3_policy_unsafe_build.zig\"",
    "\"scripts\\zigux/check_phase3_policy_unsafe_replay.zig\"",
    "\"zig run scripts\\zigux/check_phase3_policy_unsafe_replay.zig -- --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_policy_unsafe_replay.zig\"",
    "\"zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig\"",
    "\"make -C zigux phase3-policy-unsafe-test\"",
};

const REQUIRED_MARKERS__zigux_bindings_abi_zig = [_][]const u8{
    "pub fn interopPolicyIsRecognized(policy: InteropPolicy) bool {",
    "pub fn unsafeScopeFromInteropPolicy(policy: InteropPolicy) ?UnsafeScope {",
};

const REQUIRED_MARKERS__zigux_helpers_panic_policy_zig = [_][]const u8{
    "pub fn causesImmediateHaltInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn actionForInteropPolicy(policy: abi.InteropPolicy) ?Action {",
};

const REQUIRED_MARKERS__zigux_helpers_allocator_policy_zig = [_][]const u8{
    "pub fn requireInitFlowInteropPolicy(policy: abi.InteropPolicy, expected: InitFlow) InitFlowError!void {",
    "pub fn requiresResetOnInitInteropPolicy(policy: abi.InteropPolicy) bool {",
};

const REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig = [_][]const u8{
    "pub fn requiresDedicatedAuditInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
};

const REQUIRED_MARKERS__zigux_unsafe_narrow_zig = [_][]const u8{
    "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn surfaceFromInteropPolicy(policy: abi.InteropPolicy) ?Surface {",
};

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_policy_unsafe_replay.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_policy_unsafe_replay.zig",
    "zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    "make -C zigux phase3-policy-unsafe-test",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__documentation_zigux_phase3-policy-unsafe-boundary-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-policy-unsafe-boundary-survey_md_path);
    const text_required_markers__documentation_zigux_phase3-policy-unsafe-boundary-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-policy-unsafe-boundary-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-policy-unsafe-boundary-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-policy-unsafe-boundary-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-policy-unsafe-boundary-survey_md, marker);
    const text_required_markers__zigux_tests_phase3_policy_unsafe_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/policy/unsafe/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_unsafe_zig_path);
    const text_required_markers__zigux_tests_phase3_policy_unsafe_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_policy_unsafe_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_unsafe_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_policy_unsafe_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_policy_unsafe_zig, marker);
    const text_required_markers__zigux_tests_phase3_policy_unsafe_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/policy/unsafe/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_unsafe_build_zig_path);
    const text_required_markers__zigux_tests_phase3_policy_unsafe_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_policy_unsafe_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_unsafe_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_policy_unsafe_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_policy_unsafe_build_zig, marker);
    const text_required_markers__zigux_makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_markers__zigux_makefile_path);
    const text_required_markers__zigux_makefile = try guard.readUtf8File(io, allocator, text_required_markers__zigux_makefile_path);
    defer allocator.free(text_required_markers__zigux_makefile);
    for (REQUIRED_MARKERS__zigux_Makefile) |marker| try guard.requireMarker(text_required_markers__zigux_makefile, marker);
    const text_required_markers__zigux_tests_phase3_policy_starter_packet_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/policy/starter/packet/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_starter_packet_manifest_json_path);
    const text_required_markers__zigux_tests_phase3_policy_starter_packet_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_policy_starter_packet_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_starter_packet_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase3_policy_starter_packet_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_policy_starter_packet_manifest_json, marker);
    const text_required_markers__zigux_bindings_abi_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/abi/zig");
    defer allocator.free(text_required_markers__zigux_bindings_abi_zig_path);
    const text_required_markers__zigux_bindings_abi_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_abi_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_abi_zig);
    for (REQUIRED_MARKERS__zigux_bindings_abi_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_abi_zig, marker);
    const text_required_markers__zigux_helpers_panic_policy_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/panic/policy/zig");
    defer allocator.free(text_required_markers__zigux_helpers_panic_policy_zig_path);
    const text_required_markers__zigux_helpers_panic_policy_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_panic_policy_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_panic_policy_zig);
    for (REQUIRED_MARKERS__zigux_helpers_panic_policy_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_panic_policy_zig, marker);
    const text_required_markers__zigux_helpers_allocator_policy_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/allocator/policy/zig");
    defer allocator.free(text_required_markers__zigux_helpers_allocator_policy_zig_path);
    const text_required_markers__zigux_helpers_allocator_policy_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_allocator_policy_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_allocator_policy_zig);
    for (REQUIRED_MARKERS__zigux_helpers_allocator_policy_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_allocator_policy_zig, marker);
    const text_required_markers__zigux_helpers_unsafe_policy_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/unsafe/policy/zig");
    defer allocator.free(text_required_markers__zigux_helpers_unsafe_policy_zig_path);
    const text_required_markers__zigux_helpers_unsafe_policy_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_unsafe_policy_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_unsafe_policy_zig);
    for (REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_unsafe_policy_zig, marker);
    const text_required_markers__zigux_unsafe_narrow_zig_path = try guard.joinPath(allocator, root, "zigux/unsafe/narrow/zig");
    defer allocator.free(text_required_markers__zigux_unsafe_narrow_zig_path);
    const text_required_markers__zigux_unsafe_narrow_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_unsafe_narrow_zig_path);
    defer allocator.free(text_required_markers__zigux_unsafe_narrow_zig);
    for (REQUIRED_MARKERS__zigux_unsafe_narrow_zig) |marker| try guard.requireMarker(text_required_markers__zigux_unsafe_narrow_zig, marker);
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_required_replay_routes_path);
    const text_required_replay_routes = try guard.readUtf8File(io, allocator, text_required_replay_routes_path);
    defer allocator.free(text_required_replay_routes);
    for (REQUIRED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_replay_routes, marker);
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
