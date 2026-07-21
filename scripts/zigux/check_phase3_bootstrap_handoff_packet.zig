const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_BOOTSTRAP_HANDOFF_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_BOOTSTRAP_HANDOFF_PACKET_SELF_TEST=pass";

const WORKFLOW_BOUNDARY_BEFORE = [_][]const u8{
    "Check current Phase 1 closure packet",
    "run: zig run scripts\\zigux/validate_phase1_closure.zig",
};

const WORKFLOW_BOUNDARY_AFTER = [_][]const u8{
    "Run current Phase 1 shared tests-root smoke",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

const MAKEFILE_LINES = [_][]const u8{
    "phase3-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.zig",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run_phase3_checks.zig",
    "phase3-dump:",
    "phase3-low-level-wrappers-test:",
    "phase3-policy-starter-packet-test:",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "- Phase 3 flow - the current scripts-root ABI/runtime packet stays reviewable through the bounded `dev_t` starter packet, the focused helper-local `err_ptr` / `xarray` slice, the directly readable `xarray_slot` starter-and-checker packet, the focused policy slice with the returned notifier binding companion plus the dedicated policy-dump and policy-unsafe survey guards, the dedicated validator-support and selftest reminder guards, the adjacent low-level-wrapper packet, the packet-local export/UAPI survey note plus validator, the directly readable catalog helper, and the dedicated export/UAPI layout replay pair instead of rebuilding the broader export/UAPI, catalog-selftest, closure, or shared replay story from routes that current `master` still does not serve",
    "- `zig run scripts\\zigux/check_phase3_readme_tooling_inventory.zig -- --self-test`, `zig run scripts\\zigux/check_phase3_selftest_surface.zig -- --self-test`, `zig run scripts\\zigux/validate_phase3_validator_support_surface.zig -- --self-test`, and `zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig -- --self-test` replay the shipped Phase 3 scripts-root reminder checks",
    "- `zig run scripts\\zigux/check_phase3_readme_tooling_inventory.zig`, `scripts\\zigux/check_phase3_selftest_surface.zig`, `scripts\\zigux/check_phase3_shared_tests_routes.zig`, `scripts\\zigux/validate_phase3_validator_support_surface.zig`, `scripts\\zigux/validate_phase3_export_uapi_survey.zig`, `scripts\\zigux/validate_phase3_abi_header_family_survey.zig`, `scripts\\zigux/validate_phase3_policy_unsafe_survey.zig`, `scripts/zigux/validate_phase3_selftest.zig`, `scripts/zigux/run_phase3_checks.zig`, `scripts\\zigux/validate_phase3.zig`, `scripts/zigux/phase3_catalog.zig`, `scripts\\zigux/check_phase3_catalog_selftest.zig`, `scripts\\zigux/check_phase3_dev_t_starter_packet.zig`, `scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig`, `scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig`, `scripts\\zigux/check_phase3_policy_starter_packet.zig`, `scripts\\zigux/check_phase3_policy_dump.zig`, and `scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig` keep the shipped scripts-root validation packet explicit on current `master`",
    "- `zigux/tests/phase3_dev_t_starter_packet.zig`, `zigux/tests/phase3_dev_t_starter_packet_build.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`, `zigux/tests/phase3_xarray_slot_starter_packet.zig`, `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`, `zigux/tests/build.zig`, `zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig`, `zigux/tests/phase3_policy_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet_build.zig`, `zigux/tests/phase3_policy_dump.zig`, `zigux/tests/phase3_policy_dump_build.zig`, `zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, and `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`, and `.github/workflows/zigux-bootstrap.yml` keep the current starter-packet, policy-dump replay, wrapper replay, focused export/UAPI layout replay, and CI-backed reminder surfaces explicit",
};

const PHASE3_SELFTEST_MARKERS = [_][]const u8{
    "Path(\"scripts/zigux/run_phase3_checks.zig\")",
    "\"PHASE3_CHECK_RUNNER_SELF_TEST=pass\",",
    "\"PHASE3_CHECK_RUNNER_SELF_TEST_CASE_COUNT=\",",
    "Path(\"scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig\")",
    "\"PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass\",",
    "\"PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=\",",
    "Path(\"scripts\\zigux/validate_phase3.zig\")",
    "\"PHASE3_VALIDATION_SELF_TEST=pass\",",
    "\"PHASE3_VALIDATION_SELF_TEST_CASE_COUNT=\",",
};

const PHASE3_RUNNER_MARKERS = [_][]const u8{
    "Path(\"scripts\\zigux/validate_phase3.zig\")",
    "(\"PHASE3_VALIDATION=pass\",),",
    "Path(\"scripts\\zigux/check_phase3_shared_tests_routes.zig\")",
    "\"validated zigux/tests/build.zig\",",
    "\"validated scripts/zigux/validate_phase3_selftest.zig\",",
    "Path(\"scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig\")",
    "\"validated Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md\",",
    "\"PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass\",",
    "Path(\"scripts\\zigux/check_phase3_selftest_surface.zig\")",
    "(\"validated scripts/zigux/README.md\",),",
};

const SAMPLE_WORKFLOW = [_][]const u8{
    "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - name: Check current Phase 1 closure packet\n        run: zig run scripts\\zigux/validate_phase1_closure.zig\n      - name: Self-test current Phase 3 interop packet\n        run: zig run scripts/zigux/validate_phase3_selftest.zig\n      - name: Check current Phase 3 interop packet\n        run: zig run scripts/zigux/run_phase3_checks.zig\n      - name: Run current Phase 3 policy starter-packet replay\n        run: make -C zigux phase3-policy-starter-packet-test\n      - name: Run current Phase 3 policy dump replay\n        run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig\n      - name: Self-test current Phase 3 low-level wrapper survey validator\n        run: zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig -- --self-test\n      - name: Check current Phase 3 low-level wrapper survey packet\n        run: zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig\n      - name: Run current Phase 3 low-level wrapper replay\n        run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig\n      - name: Run current Phase 3 shared tests-root packet\n        run: zig build phase3-test --build-file zigux/tests/build.zig\n      - name: Run current Phase 3 ABI dump replay\n        run: zig build phase3-dump --build-file zigux/tests/build.zig\n      - name: Run current Phase 1 shared tests-root smoke\n        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
};

const SAMPLE_MAKEFILE = [_][]const u8{
    "PYTHON ?= python3\nZIGUX_ROOT := ..\n\nphase3-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.zig\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run_phase3_checks.zig\n\nphase3-dump:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig\n\nphase3-low-level-wrappers-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig\n\nphase3-policy-starter-packet-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig\n\nphase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump\n",
};

const PHASE3_LOW_LEVEL_SURVEY = [_][]const u8{
    "ROOT/scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
};

const WORKFLOW_PACKET_STEPS = [_][]const u8{
    "Self-test current Phase 3 interop packetrun: zig run scripts/zigux/validate_phase3_selftest.zig",
    "Check current Phase 3 interop packetrun: zig run scripts/zigux/run_phase3_checks.zig",
    "Run current Phase 3 policy starter-packet replayrun: make -C zigux phase3-policy-starter-packet-test",
    "Run current Phase 3 policy dump replayrun: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "Self-test current Phase 3 low-level wrapper survey validatorrun: zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig -- --self-test",
    "Check current Phase 3 low-level wrapper survey packetrun: zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "Run current Phase 3 low-level wrapper replayrun: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "Run current Phase 3 shared tests-root packetrun: zig build phase3-test --build-file zigux/tests/build.zig",
    "Run current Phase 3 ABI dump replayrun: zig build phase3-dump --build-file zigux/tests/build.zig",
};

const SURFACE_PATHS = [_][]const u8{
    "WORKFLOW",
    "MAKEFILE",
    "SCRIPTS_README",
    "PHASE3_SELFTEST",
    "PHASE3_RUNNER",
    "PHASE3_VALIDATOR",
    "PHASE3_SHARED_ROUTES",
    "PHASE3_SELFTEST_SURFACE",
    "PHASE3_LOW_LEVEL_SURVEY",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_boundary_before_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_boundary_before_path);
    const text_workflow_boundary_before = try guard.readUtf8File(io, allocator, text_workflow_boundary_before_path);
    defer allocator.free(text_workflow_boundary_before);
    for (WORKFLOW_BOUNDARY_BEFORE) |marker| try guard.requireMarker(text_workflow_boundary_before, marker);
    const text_workflow_boundary_after_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_boundary_after_path);
    const text_workflow_boundary_after = try guard.readUtf8File(io, allocator, text_workflow_boundary_after_path);
    defer allocator.free(text_workflow_boundary_after);
    for (WORKFLOW_BOUNDARY_AFTER) |marker| try guard.requireMarker(text_workflow_boundary_after, marker);
    const text_makefile_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_lines_path);
    const text_makefile_lines = try guard.readUtf8File(io, allocator, text_makefile_lines_path);
    defer allocator.free(text_makefile_lines);
    for (MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_makefile_lines, marker, 1);
    const text_scripts_readme_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_scripts_readme_markers_path);
    const text_scripts_readme_markers = try guard.readUtf8File(io, allocator, text_scripts_readme_markers_path);
    defer allocator.free(text_scripts_readme_markers);
    for (SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text_scripts_readme_markers, marker);
    const text_phase3_selftest_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/validate_phase3_selftest.zig");
    defer allocator.free(text_phase3_selftest_markers_path);
    const text_phase3_selftest_markers = try guard.readUtf8File(io, allocator, text_phase3_selftest_markers_path);
    defer allocator.free(text_phase3_selftest_markers);
    for (PHASE3_SELFTEST_MARKERS) |marker| try guard.requireMarker(text_phase3_selftest_markers, marker);
    const text_phase3_runner_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/run_phase3_checks.zig");
    defer allocator.free(text_phase3_runner_markers_path);
    const text_phase3_runner_markers = try guard.readUtf8File(io, allocator, text_phase3_runner_markers_path);
    defer allocator.free(text_phase3_runner_markers);
    for (PHASE3_RUNNER_MARKERS) |marker| try guard.requireMarker(text_phase3_runner_markers, marker);
    const text_sample_workflow_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_sample_workflow_path);
    const text_sample_workflow = try guard.readUtf8File(io, allocator, text_sample_workflow_path);
    defer allocator.free(text_sample_workflow);
    for (SAMPLE_WORKFLOW) |marker| try guard.requireMarker(text_sample_workflow, marker);
    const text_sample_makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_sample_makefile_path);
    const text_sample_makefile = try guard.readUtf8File(io, allocator, text_sample_makefile_path);
    defer allocator.free(text_sample_makefile);
    for (SAMPLE_MAKEFILE) |marker| try guard.requireMarker(text_sample_makefile, marker);
    const text_phase3_low_level_survey_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_phase3_low_level_survey_path);
    const text_phase3_low_level_survey = try guard.readUtf8File(io, allocator, text_phase3_low_level_survey_path);
    defer allocator.free(text_phase3_low_level_survey);
    for (PHASE3_LOW_LEVEL_SURVEY) |marker| try guard.requireMarker(text_phase3_low_level_survey, marker);
    const text_workflow_packet_steps_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_packet_steps_path);
    const text_workflow_packet_steps = try guard.readUtf8File(io, allocator, text_workflow_packet_steps_path);
    defer allocator.free(text_workflow_packet_steps);
    for (WORKFLOW_PACKET_STEPS) |marker| try guard.requireExactLineCount(text_workflow_packet_steps, marker, 1);
    for (SURFACE_PATHS) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) return guard.GuardError.IOError;
    }
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
