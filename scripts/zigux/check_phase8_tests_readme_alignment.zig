const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_TESTS_README_ALIGNMENT=pass";
pub const self_test_pass_marker = "PHASE8_TESTS_README_ALIGNMENT_SELF_TEST=pass";

const SCRIPT_PATH = [_][]const u8{
    "scripts\\zigux/check_phase8_tests_readme_alignment.zig",
};

const TESTS_README_PATH = [_][]const u8{
    "zigux/tests/README.md",
};

const EXEC_CMD_SLICE_PATH = [_][]const u8{
    "Documentation/zigux/phase8-exec-cmd-slice.md",
};

const EXEC_CMD_HELPER_PATH = [_][]const u8{
    "tools/lib/subcmd/exec-cmd.zig",
};

const EXEC_CMD_TEST_PATH = [_][]const u8{
    "zigux/tests/phase8_exec_cmd.zig",
};

const EXEC_CMD_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase8_exec_cmd_only_build.zig",
};

const PHASE8_VALIDATE_PATH = [_][]const u8{
    "scripts\\zigux/validate_phase8.zig",
};

const REQUIRED_MARKERS__zigux_tests_README_md = [_][]const u8{
    "current direct-readback Phase 8 anchors:",
    "`scripts\\zigux/check_phase8_tests_readme_alignment.zig`",
    "`scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig`",
    "`scripts\\zigux/validate_phase8.zig`",
    "`zigux/tests/phase8_exec_cmd.zig`",
    "`zigux/tests/phase8_exec_cmd_only_build.zig`",
    "`zigux/tests/phase8_perf_buffer_poll.zig`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
    "Keep the currently returned help-and-kallsyms focused packet explicit too; current `master` now rematerializes the dedicated shard files and their route-level companions even though the broader note still treats them as public-tree-backed companion evidence:",
    "`Documentation/zigux/phase8-help-slice.md`",
    "`Documentation/zigux/phase8-kallsyms-slice.md`",
    "`zigux/tests/phase8_help_only_build.zig`",
    "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
    "`zigux/tests/phase8_kallsyms_only_build.zig`",
    "`make -C zigux phase8-help-test`",
    "`make -C zigux phase8-help-kallsyms-test`",
    "`make -C zigux phase8-kallsyms-test`",
    "current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:",
    "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
    "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
    "`scripts\\zigux/validate_phase8.zig`",
    "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
    "`zigux/tests/phase8_file_path_handle_boundary_guard.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`",
    "`zigux/tests/phase8_build.zig`",
    "`make -C zigux phase8-exec-cmd-test`",
    "`make -C zigux phase8-file-path-handle-bridge-test`",
    "current `zigux/tests/phase8_build.zig` also keeps the landed boundary-guard and manifest-sync witnesses inside the shared aggregate replay, so this tests-root reminder should treat both checks as current current-`master` evidence instead of leaving them implied only by the aggregate build route",
    "repo-reality warning for the broader remaining Phase 8 tooling packet:",
    "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
    "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`",
    "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
    "`Documentation/zigux/phase8-help-slice.md`",
    "`Documentation/zigux/phase8-kallsyms-slice.md`",
    "`tools/lib/bpf/zigux_segments/verify.zig`",
    "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
    "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
    "`zigux/tests/phase8_verify_routing_gap.zig`",
    "`zigux/tests/phase8_verify_routing_gap_only_build.zig`",
    "`zigux/tests/phase8_libbpf_segments.zig`",
    "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
    "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase8-help-kallsyms-test`",
    "`make -C zigux phase8-libbpf-segments-test`",
    "`make -C zigux phase8-perf-buffer-poll-test`",
    "`make -C zigux phase8-test`",
    "keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence",
    "current public-tree rereads now rematerialize the broader help, kallsyms, and libbpf-segment companions on `master`, so treat those returned paths as public-tree-backed broader packet evidence rather than as part of the narrow direct-readback anchor set",
    "if future same-lane work rematerializes the remaining broader docs, focused perf-buffer build shard, shared libbpf segment replay, or Makefile routes, or changes the focused bridge shard, the shared build replay, or the libbpf segment review packet, refresh this tests-root summary only after rereading the current direct-readback anchors together with the mixed-source file-path-handle bridge packet on current `master`",
};

const REQUIRED_MARKERS__Documentation_zigux_phase8-exec-cmd-slice_md = [_][]const u8{
    "buildDeferredExeclCall()",
    "buildDeferredExecvCall()",
    "make -C zigux phase8-validate",
};

const REQUIRED_MARKERS__zigux_tests_phase8_exec_cmd_zig = [_][]const u8{
    "phase 8 exec-cmd review witness keeps the surviving shared reminder surfaces explicit",
    "scripts\\zigux/validate_phase8.zig",
    "Run focused Phase 8 exec-cmd tests",
};

const REQUIRED_MARKERS__zigux_tests_phase8_exec_cmd_only_build_zig = [_][]const u8{
    "phase8_exec_cmd.zig",
    "phase8-exec-cmd-tests",
    "Run focused Phase 8 exec-cmd tests",
};

const REQUIRED_MARKERS__scripts_zigux_validate-phase8_py = [_][]const u8{
    "EXEC_CMD_HELPER = Path(\"tools/lib/subcmd/exec-cmd.zig\")",
    "EXEC_CMD_TEST = Path(\"zigux/tests/phase8_exec_cmd.zig\")",
    "EXEC_CMD_BUILD = Path(\"zigux/tests/phase8_exec_cmd_only_build.zig\")",
    "Run focused Phase 8 exec-cmd tests",
    "phase8-exec-cmd",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_script_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_tests_readme_alignment.zig");
    defer allocator.free(text_script_path_path);
    const text_script_path = try guard.readUtf8File(io, allocator, text_script_path_path);
    defer allocator.free(text_script_path);
    for (SCRIPT_PATH) |marker| try guard.requireMarker(text_script_path, marker);
    const text_tests_readme_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_tests_readme_alignment.zig");
    defer allocator.free(text_tests_readme_path_path);
    const text_tests_readme_path = try guard.readUtf8File(io, allocator, text_tests_readme_path_path);
    defer allocator.free(text_tests_readme_path);
    for (TESTS_README_PATH) |marker| try guard.requireMarker(text_tests_readme_path, marker);
    const text_exec_cmd_slice_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_tests_readme_alignment.zig");
    defer allocator.free(text_exec_cmd_slice_path_path);
    const text_exec_cmd_slice_path = try guard.readUtf8File(io, allocator, text_exec_cmd_slice_path_path);
    defer allocator.free(text_exec_cmd_slice_path);
    for (EXEC_CMD_SLICE_PATH) |marker| try guard.requireMarker(text_exec_cmd_slice_path, marker);
    const text_exec_cmd_helper_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_tests_readme_alignment.zig");
    defer allocator.free(text_exec_cmd_helper_path_path);
    const text_exec_cmd_helper_path = try guard.readUtf8File(io, allocator, text_exec_cmd_helper_path_path);
    defer allocator.free(text_exec_cmd_helper_path);
    for (EXEC_CMD_HELPER_PATH) |marker| try guard.requireMarker(text_exec_cmd_helper_path, marker);
    const text_exec_cmd_test_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_tests_readme_alignment.zig");
    defer allocator.free(text_exec_cmd_test_path_path);
    const text_exec_cmd_test_path = try guard.readUtf8File(io, allocator, text_exec_cmd_test_path_path);
    defer allocator.free(text_exec_cmd_test_path);
    for (EXEC_CMD_TEST_PATH) |marker| try guard.requireMarker(text_exec_cmd_test_path, marker);
    const text_exec_cmd_build_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_tests_readme_alignment.zig");
    defer allocator.free(text_exec_cmd_build_path_path);
    const text_exec_cmd_build_path = try guard.readUtf8File(io, allocator, text_exec_cmd_build_path_path);
    defer allocator.free(text_exec_cmd_build_path);
    for (EXEC_CMD_BUILD_PATH) |marker| try guard.requireMarker(text_exec_cmd_build_path, marker);
    const text_phase8_validate_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_tests_readme_alignment.zig");
    defer allocator.free(text_phase8_validate_path_path);
    const text_phase8_validate_path = try guard.readUtf8File(io, allocator, text_phase8_validate_path_path);
    defer allocator.free(text_phase8_validate_path);
    for (PHASE8_VALIDATE_PATH) |marker| try guard.requireMarker(text_phase8_validate_path, marker);
    const text_required_markers__zigux_tests_readme_md_path = try guard.joinPath(allocator, root, "zigux/tests/README/md");
    defer allocator.free(text_required_markers__zigux_tests_readme_md_path);
    const text_required_markers__zigux_tests_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_readme_md_path);
    defer allocator.free(text_required_markers__zigux_tests_readme_md);
    for (REQUIRED_MARKERS__zigux_tests_README_md) |marker| try guard.requireMarker(text_required_markers__zigux_tests_readme_md, marker);
    const text_required_markers__documentation_zigux_phase8-exec-cmd-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-exec-cmd-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase8-exec-cmd-slice_md_path);
    const text_required_markers__documentation_zigux_phase8-exec-cmd-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase8-exec-cmd-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase8-exec-cmd-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase8-exec-cmd-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase8-exec-cmd-slice_md, marker);
    const text_required_markers__zigux_tests_phase8_exec_cmd_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase8/exec/cmd/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase8_exec_cmd_zig_path);
    const text_required_markers__zigux_tests_phase8_exec_cmd_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase8_exec_cmd_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase8_exec_cmd_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase8_exec_cmd_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase8_exec_cmd_zig, marker);
    const text_required_markers__zigux_tests_phase8_exec_cmd_only_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase8/exec/cmd/only/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase8_exec_cmd_only_build_zig_path);
    const text_required_markers__zigux_tests_phase8_exec_cmd_only_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase8_exec_cmd_only_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase8_exec_cmd_only_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase8_exec_cmd_only_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase8_exec_cmd_only_build_zig, marker);
    const text_required_markers__scripts_zigux_validate-phase8_py_path = try guard.joinPath(allocator, root, "scripts/zigux/validate-phase8/py");
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase8_py_path);
    const text_required_markers__scripts_zigux_validate-phase8_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_validate-phase8_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase8_py);
    for (REQUIRED_MARKERS__scripts_zigux_validate-phase8_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_validate-phase8_py, marker);
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
