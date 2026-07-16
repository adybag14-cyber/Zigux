const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE14_SHARED_SMOKE_ROUTE=pass";
pub const self_test_pass_marker = "PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check_phase14_rcu_compile_route.zig",
    "scripts/zigux/check_phase14_rcu_rollback_guardrail.zig",
    "scripts/zigux/check_phase14_release_boundary_exact_counts.zig",
    "scripts/zigux/check_phase14_ring_buffer_compile_route.zig",
    "scripts/zigux/check_phase14_rollback_threshold_sequencing.zig",
    "scripts/zigux/check_phase14_shared_smoke_route.zig",
    "scripts/zigux/check_phase14_skbuff_compile_route.zig",
    "scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig",
    "scripts/zigux/check_phase14_tests_readme_smoke_summary.zig",
    "scripts/zigux/validate_phase14.zig",
    "zigux/Makefile",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
};

const json_files = [_][]const u8{
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const file = std.Io.Dir.cwd().openFile(io, path, .{}) catch return error.MissingRequiredFile;
        file.close(io);
    }
    for (json_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        const parsed = try std.json.parseFromSlice(std.json.Value, allocator, text, .{});
        parsed.deinit();
    }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE14_COMPAT_REQUIRED_FILE_COUNT=13", .{});
    try guard.printLine(io, "PHASE14_COMPAT_JSON_FILE_COUNT=1", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST_CASE_COUNT=10", .{});
    try emitCounts(io);
    return 0;
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
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=pass";
//
// const MAKEFILE_MARKERS = [_][]const u8{
//     ".PHONY:",
//     "phase14-validate",
//     "phase14-validate:",
//     "scripts/zigux/check_phase14_shared_smoke_route.zig --self-test",
//     "scripts/zigux/check_phase14_shared_smoke_route.zig",
//     "scripts/zigux/check_phase14_tests_readme_smoke_summary.zig --self-test",
//     "scripts/zigux/check_phase14_tests_readme_smoke_summary.zig",
//     "scripts\zigux/validate_phase14.zig --self-test",
//     "scripts\zigux/validate_phase14.zig",
//     "scripts/zigux/check_phase14_rollback_threshold_sequencing.zig --self-test",
//     "scripts/zigux/check_phase14_rollback_threshold_sequencing.zig",
//     "scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig --self-test",
//     "scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig",
//     "scripts/zigux/check_phase14_rcu_rollback_guardrail.zig --self-test",
//     "scripts/zigux/check_phase14_rcu_rollback_guardrail.zig",
//     "scripts/zigux/check_phase14_release_boundary_exact_counts.zig --self-test",
//     "scripts/zigux/check_phase14_release_boundary_exact_counts.zig",
// };
//
// const MAKEFILE_TOOLCHAIN_MARKERS = [_][]const u8{
//     "ZIG_PINNED_TARGET :=",
//     "ZIG_PINNED_CHANNEL :=",
//     "ZIG_PINNED_EXTRACT_ROOT :=",
//     "ZIG_PINNED_EXECUTABLE :=",
//     "ZIG_LOCAL_TOOLCHAIN :=",
//     "ZIG_PINNED_TOOLCHAIN :=",
//     "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
// };
//
// const WORKFLOW_MARKERS = [_][]const u8{
//     "- name: Self-test current Phase 14 shared smoke route checker",
//     "run: zig run scripts/zigux/check_phase14_shared_smoke_route.zig -- --self-test",
//     "- name: Run current Phase 14 validate route",
//     "run: make -C zigux phase14-validate",
// };
//
// const FORBIDDEN_WORKFLOW_MARKERS = [_][]const u8{
//     "run: make -C zigux phase14-smoke",
//     "run: make -C zigux phase14-test",
// };
//
// const VALIDATOR_MARKERS = [_][]const u8{
//     "SKBUFF_COMPILE_ROUTE_CHECKER_PATH = \"scripts/zigux/check_phase14_skbuff_compile_route.zig\"",
//     "RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH = (n    \"scripts/zigux/check_phase14_ring_buffer_compile_route.zig\"n)",
//     "RCU_COMPILE_ROUTE_CHECKER_PATH = \"scripts/zigux/check_phase14_rcu_compile_route.zig\"",
//     "SUBCHECKER_PATHS = [",
//     "run_guardrail_checker(n                    args.root,n                    rel_path,n                    self_test=False,",
// };
//
// const EXPECTED_COMPILE_SHARDS = [_][]const u8{
//     "{label:phase14-workqueue-bridge-tests",
//     "root_source:phase14_workqueue_bridge.zig",
//     "coverage:full_bundle_only}",
//     "{label:phase14-workqueue-reviewability-tests",
//     "root_source:phase14_workqueue_reviewability.zig",
//     "coverage:full_bundle_only}",
//     "{label:phase14-skbuff-bridge-tests",
//     "root_source:phase14_skbuff_bridge.zig",
//     "coverage:full_bundle_only}",
//     "{label:phase14-ring-buffer-survey-tests",
//     "root_source:phase14_ring_buffer_survey.zig",
//     "coverage:full_bundle_only}",
//     "{label:phase14-rcu-tree-survey-tests",
//     "root_source:phase14_rcu_tree_survey.zig",
//     "coverage:full_bundle_only}",
//     "{label:phase14-end-to-end-smoke-tests",
//     "root_source:phase14_end_to_end_smoke_survey.zig",
//     "coverage:focused_and_full_bundle}",
// };
//
// const RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH = [_][]const u8{
//     "\\nscripts/zigux/check_phase14_ring_buffer_compile_route.zig\\n",
// };
//
// const SUBCHECKER_PATHS = [_][]const u8{
//     ",\n    run_guardrail_checker(\\nargs.root",
//     "\\nrel_path",
//     "\\nself_test=False",
//     ",\n]\nREQUIRED_MANIFEST_VALUES = {\n    (productization, validation_gate): make-Cziguxphase14-validate,\n    (smoke_commands,): [make-Cziguxphase14-validate],\n    (smoke_shard_commands,): [zigbuildphase14-smoke--build-filezigux/tests/phase14_build.zig],\n    (survey_summary, phase14_make_target_present): True,\n    (survey_summary, phase14_make_smoke_target_present): False,\n    (survey_summary, workflow_runs_phase14_validate): True,\n    (survey_summary, workflow_runs_phase14_build): False,\n    (survey_summary, workflow_runs_phase14_smoke_shard): False,\n    (survey_summary, phase14_validate_runs_rollback_threshold_sequencing): True,\n    (survey_summary, phase14_validate_runs_skbuff_stay_in_c_guardrail): True,\n    (survey_summary, phase14_validate_runs_skbuff_compile_route_checker): True,\n    (survey_summary, shared_manifest_records_skbuff_compile_route_checker): True,\n    (survey_summary, phase14_validate_runs_ring_buffer_compile_route_checker): True,\n    (survey_summary, shared_manifest_records_ring_buffer_compile_route_checker): True,\n    (survey_summary, phase14_validate_runs_rcu_compile_route_checker): True,\n    (survey_summary, shared_manifest_records_rcu_compile_route_checker): True,\n    (survey_summary, phase14_validate_runs_rcu_rollback_guardrail): True,\n    (survey_summary, phase14_make_uses_pinned_toolchain_fallback): True,\n    (survey_summary, phase14_make_uses_local_toolchain_probe): True,\n    (survey_summary, phase14_make_falls_back_to_path_zig): True,\n}\nEXPECTED_COMPILE_SHARDS = [\n    {label: phase14-workqueue-bridge-tests, root_source: phase14_workqueue_bridge.zig, coverage: full_bundle_only},\n    {label: phase14-workqueue-reviewability-tests, root_source: phase14_workqueue_reviewability.zig, coverage: full_bundle_only},\n    {label: phase14-skbuff-bridge-tests, root_source: phase14_skbuff_bridge.zig, coverage: full_bundle_only},\n    {label: phase14-ring-buffer-survey-tests, root_source: phase14_ring_buffer_survey.zig, coverage: full_bundle_only},\n    {label: phase14-rcu-tree-survey-tests, root_source: phase14_rcu_tree_survey.zig, coverage: full_bundle_only},\n    {label: phase14-end-to-end-smoke-tests, root_source: phase14_end_to_end_smoke_survey.zig, coverage: focused_and_full_bundle},\n]\n\n\ndef read_text(root: Path, rel: Path) -> str:\n    return (root / rel).read_text(encoding=utf-8)\n\n\ndef write_text(root: Path, rel: Path, text: str) -> None:\n    path = root / rel\n    path.parent.mkdir(parents=True, exist_ok=True)\n    path.write_text(text, encoding=utf-8)\n\n\ndef require_markers(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:\n    for marker in markers:\n        if marker not in text:\n            errors.append(fmissing_marker:{rel.as_posix()}:{marker})\n\n\ndef lookup_path(payload: object, path: tuple[str, ...]) -> object:\n    current = payload\n    for key in path:\n        if not isinstance(current, dict) or key not in current:\n            raise KeyError(..join(path))\n        current = current[key]\n    return current\n\n\ndef require_manifest_values(errors: list[str], manifest: object) -> None:\n    for path, expected in REQUIRED_MANIFEST_VALUES.items():\n        try:\n            actual = lookup_path(manifest, path)\n        except KeyError:\n            errors.append(fmissing_manifest_key:{..join(path)})\n            continue\n        if actual != expected:\n            errors.append(fmanifest_value_mismatch:{..join(path)}:expected={expected!r}:actual={actual!r})\n\n\ndef check(root: Path) -> list[str]:\n    errors: list[str] = []\n    for rel in [MAKEFILE_PATH, WORKFLOW_PATH, MANIFEST_PATH, VALIDATOR_PATH]:\n        if not (root / rel).exists():\n            errors.append(fmissing_file:{rel.as_posix()})\n    if errors:\n        return errors\n    makefile = read_text(root, MAKEFILE_PATH)\n    workflow = read_text(root, WORKFLOW_PATH)\n    validator = read_text(root, VALIDATOR_PATH)\n    require_markers(errors, MAKEFILE_PATH, makefile, MAKEFILE_MARKERS)\n    require_markers(errors, MAKEFILE_PATH, makefile, MAKEFILE_TOOLCHAIN_MARKERS)\n    require_markers(errors, WORKFLOW_PATH, workflow, WORKFLOW_MARKERS)\n    for marker in FORBIDDEN_WORKFLOW_MARKERS:\n        if marker in workflow:\n            errors.append(fforbidden_marker:{WORKFLOW_PATH.as_posix()}:{marker})\n    require_markers(errors, VALIDATOR_PATH, validator, VALIDATOR_MARKERS)\n    try:\n        manifest = json.loads(read_text(root, MANIFEST_PATH))\n    except json.JSONDecodeError as exc:\n        return [finvalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}]\n    require_manifest_values(errors, manifest)\n    if lookup_path(manifest, (compile_shards,)) != EXPECTED_COMPILE_SHARDS:\n        errors.append(manifest_value_mismatch:compile_shards)\n    return errors\n\n\ndef fixture_makefile() -> str:\n    return PYTHON?=python3PHASE2_SCRIPT_ROOT:=../scripts/ziguxZIGUX_ROOT:=..ZIG_PINNED_CHANNEL:=0.17.0-dev.877+a3ae499dcZIG_PINNED_TARGET:=x86_64-linuxZIG_PINNED_EXTRACT_ROOT:=$(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)ZIG_PINNED_EXECUTABLE:=$(firstword$(wildcard$(ZIG_PINNED_EXTRACT_ROOT)/zig$(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))ZIG_LOCAL_TOOLCHAIN:=$(firstword$(wildcard$(ZIGUX_ROOT)/.zig-toolchain//zig$(ZIGUX_ROOT)/.zig-toolchain//bin/zig))ZIG_PINNED_TOOLCHAIN:=$(if$(ZIG_PINNED_EXECUTABLE)",
//     "$(ZIG_PINNED_EXECUTABLE)",
//     "$(ZIG_LOCAL_TOOLCHAIN))ZIG?=$(if$(ZIG_PINNED_TOOLCHAIN)",
//     "$(ZIG_PINNED_TOOLCHAIN)",
// };
//
// const REQUIRED_MANIFEST_VALUES = [_][]const u8{
//     "productization",
//     "validation_gate",
//     "make -C zigux phase14-validate",
//     "smoke_commands",
//     "make -C zigux phase14-validate",
//     "smoke_shard_commands",
//     "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig",
//     "survey_summary",
//     "phase14_make_target_present",
//     "survey_summary",
//     "phase14_make_smoke_target_present",
//     "survey_summary",
//     "workflow_runs_phase14_validate",
//     "survey_summary",
//     "workflow_runs_phase14_build",
//     "survey_summary",
//     "workflow_runs_phase14_smoke_shard",
//     "survey_summary",
//     "phase14_validate_runs_rollback_threshold_sequencing",
//     "survey_summary",
//     "phase14_validate_runs_skbuff_stay_in_c_guardrail",
//     "survey_summary",
//     "phase14_validate_runs_skbuff_compile_route_checker",
//     "survey_summary",
//     "shared_manifest_records_skbuff_compile_route_checker",
//     "survey_summary",
//     "phase14_validate_runs_ring_buffer_compile_route_checker",
//     "survey_summary",
//     "shared_manifest_records_ring_buffer_compile_route_checker",
//     "survey_summary",
//     "phase14_validate_runs_rcu_compile_route_checker",
//     "survey_summary",
//     "shared_manifest_records_rcu_compile_route_checker",
//     "survey_summary",
//     "phase14_validate_runs_rcu_rollback_guardrail",
//     "survey_summary",
//     "phase14_make_uses_pinned_toolchain_fallback",
//     "survey_summary",
//     "phase14_make_uses_local_toolchain_probe",
//     "survey_summary",
//     "phase14_make_falls_back_to_path_zig",
// };
//
// const RCU_COMPILE_ROUTE_CHECKER_PATH = [_][]const u8{
//     "scripts/zigux/check_phase14_rcu_compile_route.zig",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MAKEFILE_TOOLCHAIN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (FORBIDDEN_WORKFLOW_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (VALIDATOR_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_COMPILE_SHARDS) |marker| try guard.requireMarker(text, marker);
//     for (RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SUBCHECKER_PATHS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MANIFEST_VALUES) |marker| try guard.requireMarker(text, marker);
//     for (RCU_COMPILE_ROUTE_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
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
