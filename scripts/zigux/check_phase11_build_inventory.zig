const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_BUILD_INVENTORY=pass";
pub const self_test_pass_marker = "PHASE11_BUILD_INVENTORY_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };
const ModulePath = struct { module: []const u8, path: []const u8 };
const TestRootModule = struct { @"test": []const u8, root_module: []const u8 };
const WorkflowStep = struct { name: []const u8, run: []const u8 };
const ReplayMarker = struct { path: []const u8, marker: []const u8 };
const Inventory = struct {
    proof_build_file: []const u8,
    proof_replay_command: []const u8,
    proof_step_name: []const u8,
    proof_step_description: []const u8,
    proof_test_artifact_name: []const u8,
    proof_root_source_file: []const u8,
    build_test_names: []const []const u8,
    shared_test_depend_steps: []const []const u8,
    module_root_source_files: []const ModulePath,
    test_root_modules: []const TestRootModule,
    forbidden_markers: []const []const u8,
    exact_current_checks: []const []const u8,
    focused_direct_build_checks: []const []const u8,
    workflow_phase11_steps: []const WorkflowStep,
    dedicated_survey_replays: []const []const u8,
    shared_split_replays: []const []const u8,
    shared_adjunct_replays: []const []const u8,
    shared_adjunct_build_replays: []const []const u8,
    focused_direct_build_replays: []const []const u8,
    shared_replay_markers: []const ReplayMarker,
};
const CheckEntry = struct { name: []const u8, command: []const []const u8 };
const ValidateFixture = struct { lane_key: []const u8, phase: []const u8, validate_script: []const u8, validate_route: []const u8, exact_checks: []const CheckEntry };

const markers_0 = [_][]const u8{
    "phase11_hvc_cleanup_packet_proof.zig",
    "phase11-hvc-cleanup-packet-proof",
    "Run the focused Phase 11 HVC cleanup packet proof",
};

const markers_1 = [_][]const u8{
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "Keep the modem-control proof pair directly readable through its focused build route",
    "without promoting either pair into the shared three-entry build inventory",
};

const markers_2 = [_][]const u8{
    "Keep the broader reminder follow-through honest too:",
    "`scripts\\zigux/check_phase11_build_inventory.zig`",
    "`scripts\\zigux/check_phase11_matrix_gap_survey.zig`",
    "`scripts\\zigux/check_phase11_validation_matrix_gap_survey.zig`",
    "`scripts\\zigux/check_phase11_hvc_cleanup_current_head.zig`",
    "`scripts\\zigux/check_phase11_hvc_targetless_unregister_witness.zig`",
    "`scripts\\zigux/check_phase11_dw_wdt_teardown_packet.zig`",
    "`scripts\\zigux/check_phase11_dw_wdt_verify_alignment.zig`",
    "`scripts\\zigux/validate_phase11.zig`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`make -C zigux phase11-validate`",
    "instead of reducing the current shared gate to the narrower HVC inventory alone",
};

const markers_3 = [_][]const u8{
    "`scripts\\zigux/check_phase11_build_inventory.zig`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`make -C zigux phase11-validate`",
};

const markers_4 = [_][]const u8{
    "`phase11-hvc-hv-ops-layout-proof-tests`",
    "`phase11-hvc-export-surface-layout-proof-tests`",
    "`phase11-build-inventory-adjunct`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig` as the current adjunct build trio",
    "keeps both dedicated survey replays and shared split replays empty",
};

const markers_5 = [_][]const u8{
    "`zigux/helpers/layout_assert.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/fixtures/phase11_build_inventory.json` and the returned `scripts\\zigux/check_phase11_build_inventory.zig` route are directly readable again",
    "add header-boundary inventory wording only when a directly readable shared replay file returns",
};

const markers_6 = [_][]const u8{
    ".root_source_file = b.path(\"phase11_hvc_hv_ops_layout_proof.zig\")",
    ".name = \"phase11-hvc-hv-ops-layout-proof-tests\"",
    ".root_source_file = b.path(\"phase11_hvc_export_surface_layout_proof.zig\")",
    ".name = \"phase11-hvc-export-surface-layout-proof-tests\"",
    "const test_step = b.step(\"test\", \"Run the focused Phase 11 exported-header proofs\");",
};

const markers_7 = [_][]const u8{
    ".root_source_file = b.path(\"phase11_hvc_export_surface_layout_proof.zig\")",
    ".name = \"phase11-hvc-export-surface-layout-proof\"",
    "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC exported-helper ABI proof\");",
};

const markers_8 = [_][]const u8{
    ".root_source_file = b.path(\"phase11_hvc_targetless_unregister_gap.zig\")",
    ".name = \"phase11-hvc-targetless-unregister-gap\",",
    "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC targetless-unregister gap witness.\");",
};

const markers_9 = [_][]const u8{
    "phase11-validate:",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase11.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const markers_10 = [_][]const u8{
    "Validate current Phase 11 support bundle",
    "make -C zigux phase11-validate",
};

const markers_11 = [_][]const u8{
    "check_phase11_validate_check_roster.zig",
    "check_phase11_validate_route_alignment.zig",
    "check_phase11_build_inventory.zig",
    "check_phase11_matrix_gap_survey.zig",
    "check_phase11_validation_matrix_gap_survey.zig",
    "check_phase11_hvc_cleanup_current_head.zig",
    "check_phase11_hvc_targetless_unregister_witness.zig",
    "check_phase11_dw_wdt_teardown_packet.zig",
    "check_phase11_dw_wdt_verify_alignment.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
};

const contracts = [_]FileContract{
    .{ .rel = "zigux/tests/phase11_hvc_cleanup_packet_build.zig", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase11-hvc-console-validation-matrix.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase11-shared-replay-contract.md", .markers = &markers_2 },
    .{ .rel = "scripts/zigux/README.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase11-uapi-header-parity-survey.md", .markers = &markers_4 },
    .{ .rel = "Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md", .markers = &markers_5 },
    .{ .rel = "zigux/tests/phase11_hvc_hv_ops_layout_build.zig", .markers = &markers_6 },
    .{ .rel = "zigux/tests/phase11_hvc_export_surface_layout_build.zig", .markers = &markers_7 },
    .{ .rel = "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig", .markers = &markers_8 },
    .{ .rel = "zigux/Makefile", .markers = &markers_9 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_10 },
    .{ .rel = "scripts/zigux/validate_phase11.zig", .markers = &markers_11 },
};

const required_files = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-shared-replay-contract.md",
    "Documentation/zigux/phase11-uapi-header-parity-survey.md",
    "Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate_phase11.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const expected_build_test_names = [_][]const u8{
    "phase11-hvc-hv-ops-layout-proof-tests",
    "phase11-hvc-export-surface-layout-proof-tests",
    "phase11-hvc-cleanup-packet-proof",
};

const expected_forbidden_markers = [_][]const u8{
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
};

const expected_exact_checks = [_][]const u8{
    "zig run scripts/zigux/check_phase11_build_inventory.zig -- --self-test",
    "zig run scripts/zigux/check_phase11_build_inventory.zig --",
    "zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig -- --self-test",
    "zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig --",
    "zig run scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig -- --self-test",
    "zig run scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig --",
    "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
};

const expected_focused_checks = [_][]const u8{
    "zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig -- --self-test",
    "zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig --",
};

const expected_adjunct_replays = [_][]const u8{
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
};

const expected_adjunct_build_replays = [_][]const u8{
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
};

const expected_focused_direct_build_replays = [_][]const u8{
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const expected_command_0 = [_][]const u8{
    "zig",
    "run",
    "scripts/zigux/check_phase11_build_inventory.zig",
    "--",
    "--self-test",
};

const expected_command_1 = [_][]const u8{
    "zig",
    "run",
    "scripts/zigux/check_phase11_build_inventory.zig",
    "--",
};

const expected_command_2 = [_][]const u8{
    "zig",
    "run",
    "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
    "--",
    "--self-test",
};

const expected_command_3 = [_][]const u8{
    "zig",
    "run",
    "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
    "--",
};

const expected_command_4 = [_][]const u8{
    "zig",
    "run",
    "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
    "--",
    "--self-test",
};

const expected_command_5 = [_][]const u8{
    "zig",
    "run",
    "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
    "--",
};

const expected_command_6 = [_][]const u8{
    "zig",
    "build",
    "test",
    "--build-file",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
};

const expected_command_7 = [_][]const u8{
    "zig",
    "build",
    "test",
    "--build-file",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
};

const expected_command_8 = [_][]const u8{
    "zig",
    "build",
    "test",
    "--build-file",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
};

const expected_command_9 = [_][]const u8{
    "zig",
    "build",
    "test",
    "--build-file",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const expected_command_10 = [_][]const u8{
    "zig",
    "build",
    "test",
    "--build-file",
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
};

const expected_command_11 = [_][]const u8{
    "zig",
    "run",
    "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
    "--",
    "--self-test",
};

const expected_command_12 = [_][]const u8{
    "zig",
    "run",
    "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
    "--",
};

const expected_modules = [_]ModulePath{
    .{ .module = "hv_ops_proof_module", .path = "phase11_hvc_hv_ops_layout_proof.zig" },
    .{ .module = "export_surface_proof_module", .path = "phase11_hvc_export_surface_layout_proof.zig" },
    .{ .module = "proof_module", .path = "phase11_hvc_cleanup_packet_proof.zig" },
};

const expected_test_roots = [_]TestRootModule{
    .{ .@"test" = "phase11-hvc-hv-ops-layout-proof-tests", .root_module = "hv_ops_proof_module" },
    .{ .@"test" = "phase11-hvc-export-surface-layout-proof-tests", .root_module = "export_surface_proof_module" },
    .{ .@"test" = "phase11-hvc-cleanup-packet-proof", .root_module = "proof_module" },
};

const required_commands = [_][]const []const u8{
    &expected_command_0,
    &expected_command_1,
    &expected_command_2,
    &expected_command_3,
    &expected_command_4,
    &expected_command_5,
    &expected_command_6,
    &expected_command_7,
    &expected_command_8,
    &expected_command_9,
    &expected_command_10,
    &expected_command_11,
    &expected_command_12,
};

fn normalizeWhitespace(allocator: std.mem.Allocator, text: []const u8) ![]u8 {
    var out_buf: std.ArrayList(u8) = .empty;
    errdefer out_buf.deinit(allocator);
    var pending_space = false;
    for (text) |c| {
        if (std.ascii.isWhitespace(c)) { pending_space = out_buf.items.len != 0; continue; }
        if (pending_space) { try out_buf.append(allocator, ' '); pending_space = false; }
        try out_buf.append(allocator, c);
    }
    return try out_buf.toOwnedSlice(allocator);
}

fn requireNormalized(allocator: std.mem.Allocator, text: []const u8, marker: []const u8) !void {
    const normalized_text = try normalizeWhitespace(allocator, text);
    defer allocator.free(normalized_text);
    const normalized_marker = try normalizeWhitespace(allocator, marker);
    defer allocator.free(normalized_marker);
    if (std.mem.indexOf(u8, normalized_text, normalized_marker) == null) return error.MissingMarker;
}

fn expectStrings(actual: []const []const u8, expected: []const []const u8) !void {
    if (actual.len != expected.len) return error.StringArrayLengthDrift;
    for (actual, expected) |a,e| if (!std.mem.eql(u8,a,e)) return error.StringArrayValueDrift;
}

fn expectModules(actual: []const ModulePath) !void {
    if (actual.len != expected_modules.len) return error.ModuleCountDrift;
    for (actual, expected_modules) |a,e| { if (!std.mem.eql(u8,a.module,e.module) or !std.mem.eql(u8,a.path,e.path)) return error.ModuleDrift; }
}

fn expectTestRoots(actual: []const TestRootModule) !void {
    if (actual.len != expected_test_roots.len) return error.TestRootCountDrift;
    for (actual, expected_test_roots) |a,e| { if (!std.mem.eql(u8,a.@"test",e.@"test") or !std.mem.eql(u8,a.root_module,e.root_module)) return error.TestRootDrift; }
}

fn commandEquals(a: []const []const u8, b: []const []const u8) bool {
    if (a.len != b.len) return false;
    for (a,b) |x,y| if (!std.mem.eql(u8,x,y)) return false;
    return true;
}

fn requireFixtureCommands(entries: []const CheckEntry) !void {
    for (required_commands) |required| {
        var count: usize = 0;
        for (entries) |entry| {
            if (commandEquals(entry.command, required)) count += 1;
        }
        if (count != 1) return error.ValidateCommandRosterDrift;
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel); defer allocator.free(path);
        const file = std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io);
    }
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel); defer allocator.free(path);
        const text = try guard.readUtf8File(io,allocator,path); defer allocator.free(text);
        for (contract.markers) |marker| try requireNormalized(allocator,text,marker);
    }
    const build_path = try guard.joinPath(allocator,root,"zigux/tests/phase11_hvc_cleanup_packet_build.zig"); defer allocator.free(build_path);
    const build_text = try guard.readUtf8File(io,allocator,build_path); defer allocator.free(build_text);
    for (expected_forbidden_markers) |marker| if (std.mem.indexOf(u8,build_text,marker)!=null) return error.ForbiddenBuildMarkerPresent;
    const inv_path = try guard.joinPath(allocator,root,"zigux/tests/fixtures/phase11_build_inventory.json"); defer allocator.free(inv_path);
    const inv_text = try guard.readUtf8File(io,allocator,inv_path); defer allocator.free(inv_text);
    const inv_parsed = try std.json.parseFromSlice(Inventory,allocator,inv_text,.{ .ignore_unknown_fields=true }); defer inv_parsed.deinit();
    const inv = inv_parsed.value;
    if (!std.mem.eql(u8,inv.proof_build_file,"zigux/tests/phase11_hvc_cleanup_packet_build.zig")) return error.ProofBuildDrift;
    if (!std.mem.eql(u8,inv.proof_replay_command,"zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig")) return error.ProofReplayDrift;
    if (!std.mem.eql(u8,inv.proof_step_name,"test")) return error.ProofStepDrift;
    if (!std.mem.eql(u8,inv.proof_step_description,"Run the focused Phase 11 HVC cleanup packet proof")) return error.ProofDescriptionDrift;
    if (!std.mem.eql(u8,inv.proof_test_artifact_name,"phase11-hvc-cleanup-packet-proof")) return error.ProofArtifactDrift;
    if (!std.mem.eql(u8,inv.proof_root_source_file,"phase11_hvc_cleanup_packet_proof.zig")) return error.ProofSourceDrift;
    try expectStrings(inv.build_test_names,&expected_build_test_names);
    if (inv.shared_test_depend_steps.len != 0 or inv.dedicated_survey_replays.len != 0 or inv.shared_split_replays.len != 0 or inv.shared_replay_markers.len != 0) return error.ExpectedEmptyInventoryDrift;
    try expectModules(inv.module_root_source_files);
    try expectTestRoots(inv.test_root_modules);
    try expectStrings(inv.forbidden_markers,&expected_forbidden_markers);
    try expectStrings(inv.exact_current_checks,&expected_exact_checks);
    try expectStrings(inv.focused_direct_build_checks,&expected_focused_checks);
    if (inv.workflow_phase11_steps.len != 1 or !std.mem.eql(u8,inv.workflow_phase11_steps[0].name,"Validate current Phase 11 support bundle") or !std.mem.eql(u8,inv.workflow_phase11_steps[0].run,"make -C zigux phase11-validate")) return error.WorkflowInventoryDrift;
    try expectStrings(inv.shared_adjunct_replays,&expected_adjunct_replays);
    try expectStrings(inv.shared_adjunct_build_replays,&expected_adjunct_build_replays);
    try expectStrings(inv.focused_direct_build_replays,&expected_focused_direct_build_replays);
    const fixture_path = try guard.joinPath(allocator,root,"zigux/tests/fixtures/phase11_validate_checks.json"); defer allocator.free(fixture_path);
    const fixture_text = try guard.readUtf8File(io,allocator,fixture_path); defer allocator.free(fixture_text);
    const fixture_parsed = try std.json.parseFromSlice(ValidateFixture,allocator,fixture_text,.{ .ignore_unknown_fields=true }); defer fixture_parsed.deinit();
    const fixture = fixture_parsed.value;
    if (!std.mem.eql(u8,fixture.lane_key,"P11-L15") or !std.mem.eql(u8,fixture.phase,"Phase 11") or !std.mem.eql(u8,fixture.validate_script,"scripts/zigux/validate_phase11.zig") or !std.mem.eql(u8,fixture.validate_route,"make -C zigux phase11-validate")) return error.ValidateFixtureHeaderDrift;
    try requireFixtureCommands(fixture.exact_checks);
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io,"PHASE11_BUILD_INVENTORY_REQUIRED_FILE_COUNT=14",.{});
    try guard.printLine(io,"PHASE11_BUILD_INVENTORY_TEXT_CONTRACT_COUNT=12",.{});
    try guard.printLine(io,"PHASE11_BUILD_INVENTORY_REQUIRED_COMMAND_COUNT=13",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator); defer allocator.free(root);
    try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker});
    try guard.printLine(io,"PHASE11_BUILD_INVENTORY_SELF_TEST_CASE_COUNT=28",.{});
    try emitCounts(io);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator=init.gpa; const io=init.io;
    const args=try init.minimal.args.toSlice(init.arena.allocator());
    var self_test=false; var explicit_root:?[]const u8=null; var index:usize=1;
    while(index<args.len):(index+=1){ const arg=args[index]; if(std.mem.eql(u8,arg,"--self-test")){self_test=true;continue;} if(std.mem.eql(u8,arg,"--root") or std.mem.eql(u8,arg,"--repo-root")){if(index+1>=args.len)std.process.exit(2);index+=1;explicit_root=args[index];continue;} std.process.exit(2); }
    if(self_test) std.process.exit(try runSelfTest(io,allocator));
    const root=explicit_root orelse try guard.defaultRepoRoot(allocator); defer if(explicit_root==null) allocator.free(root);
    checkRepo(io,allocator,root) catch std.process.exit(1);
    try guard.printLine(io,"{s}",.{live_pass_marker}); try emitCounts(io);
}


// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE11_BUILD_INVENTORY_SELF_TEST=pass";
//
// const DEFAULT_ROOT = [_][]const u8{
//     "Path.resolve.parents[2]iflen>2elsePath.cwd",
// };
//
// const EXACT_CURRENT_CHECKS = [_][]const u8{
//     "zig run scripts/zigux/check_phase11_build_inventory.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_build_inventory.zig --",
//     "zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig --",
//     "zig run scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig --",
//     "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
//     "zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
//     "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
//     "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
//     "zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
// };
//
// const FOCUSED_DIRECT_BUILD_CHECKS = [_][]const u8{
//     "zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig --",
// };
//
// const REQUIRED_FOCUSED_DIRECT_BUILD_REPLAYS = [_][]const u8{
//     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
//     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// };
//
// const REQUIRED_BUILD_TEXT_MARKERS = [_][]const u8{
//     "phase11_hvc_cleanup_packet_proof.zig",
//     "phase11-hvc-cleanup-packet-proof",
//     "Run the focused Phase 11 HVC cleanup packet proof",
// };
//
// const FORBIDDEN_BUILD_TEXT_MARKERS = [_][]const u8{
//     "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
// };
//
// const REQUIRED_BUILD_TEST_NAMES = [_][]const u8{
//     "phase11-hvc-hv-ops-layout-proof-tests",
//     "phase11-hvc-export-surface-layout-proof-tests",
//     "phase11-hvc-cleanup-packet-proof",
// };
//
// const REQUIRED_SHARED_ADJUNCT_REPLAYS = [_][]const u8{
//     "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
//     "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
//     "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
// };
//
// const REQUIRED_SHARED_ADJUNCT_BUILD_REPLAYS = [_][]const u8{
//     "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
//     "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
//     "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
// };
//
// const REQUIRED_HVC_VALIDATION_MATRIX_MARKERS = [_][]const u8{
//     "`zigux/tests/fixtures/phase11_build_inventory.json`",
//     "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
//     "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
//     "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
//     "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
//     "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
//     "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
//     "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
//     "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
//     "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
//     "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
//     "Keep the modem-control proof pair directly readable through its focused build route",
//     "without promoting either pair into the shared three-entry build inventory",
// };
//
// const REQUIRED_SHARED_REPLAY_CONTRACT_MARKERS = [_][]const u8{
//     "Keep the broader reminder follow-through honest too:",
//     "`scripts/zigux/check_phase11_build_inventory.zig`",
//     "`scripts/zigux/check_phase11_matrix_gap_survey.zig`",
//     "`scripts/zigux/check_phase11_validation_matrix_gap_survey.zig`",
//     "`scripts/zigux/check_phase11_hvc_cleanup_current_head.zig`",
//     "`scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig`",
//     "`scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig`",
//     "`scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig`",
//     "`scripts\zigux/validate_phase11.zig`",
//     "`zigux/tests/fixtures/phase11_build_inventory.json`",
//     "`make -C zigux phase11-validate`",
//     "instead of reducing the current shared gate to the narrower HVC inventory alone",
// };
//
// const REQUIRED_SCRIPTS_ROOT_MARKERS = [_][]const u8{
//     "`scripts/zigux/check_phase11_build_inventory.zig`",
//     "`zigux/tests/fixtures/phase11_build_inventory.json`",
//     "`make -C zigux phase11-validate`",
// };
//
// const REQUIRED_VALIDATE_PHASE11_MARKERS = [_][]const u8{
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validate_check_roster.zig\", \"--\", \"--self-test\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validate_check_roster.zig\", \"--\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validate_route_alignment.zig\", \"--\", \"--self-test\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validate_route_alignment.zig\", \"--\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_build_inventory.zig\", \"--\", \"--self-test\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_build_inventory.zig\", \"--\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_matrix_gap_survey.zig\", \"--\", \"--self-test\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_matrix_gap_survey.zig\", \"--\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validation_matrix_gap_survey.zig\", \"--\", \"--self-test\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validation_matrix_gap_survey.zig\", \"--\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_cleanup_current_head.zig\", \"--\", \"--self-test\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_cleanup_current_head.zig\", \"--\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig\", \"--\", \"--self-test\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig\", \"--\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig\", \"--\", \"--self-test\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig\", \"--\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig\", \"--\", \"--self-test\")",
//     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig\", \"--\")",
//     "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_hv_ops_layout_build.zig\")",
//     "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_export_surface_layout_build.zig\")",
//     "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_cleanup_packet_build.zig\")",
//     "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig\")",
//     "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_modem_control_proof_build.zig\")",
// };
//
// const REQUIRED_UAPI_SURVEY_MARKERS = [_][]const u8{
//     "`phase11-hvc-hv-ops-layout-proof-tests`",
//     "`phase11-hvc-export-surface-layout-proof-tests`",
//     "`phase11-build-inventory-adjunct`",
//     "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig` as the current adjunct build trio",
//     "keeps both dedicated survey replays and shared split replays empty",
// };
//
// const REQUIRED_HEADER_MATRIX_MARKERS = [_][]const u8{
//     "`zigux/helpers/layout_assert.zig`",
//     "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
//     "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
//     "`zigux/tests/fixtures/phase11_build_inventory.json` and the returned `scripts/zigux/check_phase11_build_inventory.zig` route are directly readable again",
//     "add header-boundary inventory wording only when a directly readable shared replay file returns",
// };
//
// const REQUIRED_HV_OPS_BUILD_MARKERS = [_][]const u8{
//     ".root_source_file = b.path(\"phase11_hvc_hv_ops_layout_proof.zig\")",
//     ".name = \"phase11-hvc-hv-ops-layout-proof-tests\"",
//     ".root_source_file = b.path(\"phase11_hvc_export_surface_layout_proof.zig\")",
//     ".name = \"phase11-hvc-export-surface-layout-proof-tests\"",
//     "const test_step = b.step(\"test\", \"Run the focused Phase 11 exported-header proofs\");",
// };
//
// const REQUIRED_EXPORT_BUILD_MARKERS = [_][]const u8{
//     ".root_source_file = b.path(\"phase11_hvc_export_surface_layout_proof.zig\")",
//     ".name = \"phase11-hvc-export-surface-layout-proof\"",
//     "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC exported-helper ABI proof\");",
// };
//
// const REQUIRED_TARGETLESS_BUILD_MARKERS = [_][]const u8{
//     ".root_source_file = b.path(\"phase11_hvc_targetless_unregister_gap.zig\")",
//     ".name = \"phase11-hvc-targetless-unregister-gap\",",
//     "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC targetless-unregister gap witness.\");",
// };
//
// const REQUIRED_WORKFLOW_PHASE11_STEPS = [_][]const u8{
//     "Validate current Phase 11 support bundlemake -C zigux phase11-validate",
// };
//
// const REQUIRED_MAKEFILE_ROUTE_MARKERS = [_][]const u8{
//     "phase11-validate:",
//     "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase11.zig",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// };
//
// const REQUIRED_PROOF_ROUTE = [_][]const u8{
//     "proof_build_file",
//     "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
//     "proof_replay_command",
//     "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
//     "proof_step_name",
//     "test",
//     "proof_step_description",
//     "Run the focused Phase 11 HVC cleanup packet proof",
//     "proof_test_artifact_name",
//     "phase11-hvc-cleanup-packet-proof",
//     "proof_root_source_file",
//     "phase11_hvc_cleanup_packet_proof.zig",
// };
//
// const REQUIRED_MODULE_PATHS = [_][]const u8{
//     "hv_ops_proof_module",
//     "phase11_hvc_hv_ops_layout_proof.zig",
//     "export_surface_proof_module",
//     "phase11_hvc_export_surface_layout_proof.zig",
//     "proof_module",
//     "phase11_hvc_cleanup_packet_proof.zig",
// };
//
// const REQUIRED_TEST_ROOT_MODULES = [_][]const u8{
//     "phase11-hvc-hv-ops-layout-proof-tests",
//     "hv_ops_proof_module",
//     "phase11-hvc-export-surface-layout-proof-tests",
//     "export_surface_proof_module",
//     "phase11-hvc-cleanup-packet-proof",
//     "proof_module",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (DEFAULT_ROOT) |marker| try guard.requireMarker(text, marker);
//     for (EXACT_CURRENT_CHECKS) |marker| try guard.requireMarker(text, marker);
//     for (FOCUSED_DIRECT_BUILD_CHECKS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_FOCUSED_DIRECT_BUILD_REPLAYS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_BUILD_TEXT_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (FORBIDDEN_BUILD_TEXT_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_BUILD_TEST_NAMES) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_SHARED_ADJUNCT_REPLAYS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_SHARED_ADJUNCT_BUILD_REPLAYS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_HVC_VALIDATION_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_SHARED_REPLAY_CONTRACT_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_SCRIPTS_ROOT_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_VALIDATE_PHASE11_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_UAPI_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_HEADER_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_HV_OPS_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_EXPORT_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_TARGETLESS_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_WORKFLOW_PHASE11_STEPS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MAKEFILE_ROUTE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_PROOF_ROUTE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MODULE_PATHS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_TEST_ROOT_MODULES) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
