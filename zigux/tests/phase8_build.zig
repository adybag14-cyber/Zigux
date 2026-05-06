const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const io = b.graph.io;
    const phase8_help_slice = std.Io.Dir.cwd().readFileAlloc(
        io,
        "Documentation/zigux/phase8-help-slice.md",
        b.allocator,
        .limited(64 * 1024),
    ) catch @panic("unable to read Documentation/zigux/phase8-help-slice.md");
    const phase8_kallsyms_slice = std.Io.Dir.cwd().readFileAlloc(
        io,
        "Documentation/zigux/phase8-kallsyms-slice.md",
        b.allocator,
        .limited(64 * 1024),
    ) catch @panic("unable to read Documentation/zigux/phase8-kallsyms-slice.md");

    const exec_cmd_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/subcmd/exec-cmd.zig"),
        .target = target,
        .optimize = optimize,
    });
    const exec_cmd_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_exec_cmd.zig"),
        .target = target,
        .optimize = optimize,
    });
    exec_cmd_root_module.addImport("exec_cmd", exec_cmd_module);

    const help_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/subcmd/help.zig"),
        .target = target,
        .optimize = optimize,
    });
    const help_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_help.zig"),
        .target = target,
        .optimize = optimize,
    });
    help_root_module.addImport("help", help_module);
    const help_options = b.addOptions();
    help_options.addOption([]const u8, "phase8_help_slice", phase8_help_slice);
    help_root_module.addImport("phase8_help_options", help_options.createModule());
    const kallsyms_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/symbol/kallsyms.zig"),
        .target = target,
        .optimize = optimize,
    });
    const kallsyms_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_kallsyms.zig"),
        .target = target,
        .optimize = optimize,
    });
    kallsyms_root_module.addImport("kallsyms", kallsyms_module);
    const kallsyms_options = b.addOptions();
    kallsyms_options.addOption([]const u8, "phase8_kallsyms_slice", phase8_kallsyms_slice);
    kallsyms_root_module.addImport("phase8_kallsyms_options", kallsyms_options.createModule());
    const cpu_mask_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/cpu_mask.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpu_mask_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_cpu_mask.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpu_mask_root_module.addImport("cpu_mask", cpu_mask_module);
    const logging_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/logging.zig"),
        .target = target,
        .optimize = optimize,
    });
    const logging_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_logging.zig"),
        .target = target,
        .optimize = optimize,
    });
    logging_root_module.addImport("logging", logging_module);
    const pin_path_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/pin_path.zig"),
        .target = target,
        .optimize = optimize,
    });
    const pin_path_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_pin_path.zig"),
        .target = target,
        .optimize = optimize,
    });
    pin_path_root_module.addImport("pin_path", pin_path_module);
    const libbpf_segments_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_libbpf_segments.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bpf_type_names_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/type_names.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bpf_type_names_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_bpf_type_names.zig"),
        .target = target,
        .optimize = optimize,
    });
    bpf_type_names_root_module.addImport("bpf_type_names", bpf_type_names_module);
    const file_path_handle_bridge_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"),
        .target = target,
        .optimize = optimize,
    });
    const file_path_handle_bridge_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_file_path_handle_bridge.zig"),
        .target = target,
        .optimize = optimize,
    });
    file_path_handle_bridge_root_module.addImport("file_path_handle_bridge", file_path_handle_bridge_module);
    const perf_buffer_poll_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
        .target = target,
        .optimize = optimize,
    });
    const perf_buffer_poll_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_perf_buffer_poll.zig"),
        .target = target,
        .optimize = optimize,
    });
    perf_buffer_poll_root_module.addImport("perf_buffer_poll", perf_buffer_poll_module);

    const exec_cmd_tests = b.addTest(.{
        .name = "phase8-exec-cmd-tests",
        .root_module = exec_cmd_root_module,
    });
    const help_tests = b.addTest(.{
        .name = "phase8-help-tests",
        .root_module = help_root_module,
    });
    const kallsyms_tests = b.addTest(.{
        .name = "phase8-kallsyms-tests",
        .root_module = kallsyms_root_module,
    });
    const cpu_mask_tests = b.addTest(.{
        .name = "phase8-cpu-mask-tests",
        .root_module = cpu_mask_root_module,
    });
    const logging_tests = b.addTest(.{
        .name = "phase8-logging-tests",
        .root_module = logging_root_module,
    });
    const pin_path_tests = b.addTest(.{
        .name = "phase8-pin-path-tests",
        .root_module = pin_path_root_module,
    });
    const libbpf_segments_tests = b.addTest(.{
        .name = "phase8-libbpf-segment-tests",
        .root_module = libbpf_segments_root_module,
    });
    const bpf_type_names_tests = b.addTest(.{
        .name = "phase8-bpf-type-names-tests",
        .root_module = bpf_type_names_root_module,
    });
    const file_path_handle_bridge_tests = b.addTest(.{
        .name = "phase8-file-path-handle-bridge-tests",
        .root_module = file_path_handle_bridge_root_module,
    });
    const perf_buffer_poll_tests = b.addTest(.{
        .name = "phase8-perf-buffer-poll-tests",
        .root_module = perf_buffer_poll_root_module,
    });

    const run_exec_cmd_tests = b.addRunArtifact(exec_cmd_tests);
    const run_help_tests = b.addRunArtifact(help_tests);
    const run_kallsyms_tests = b.addRunArtifact(kallsyms_tests);
    const run_cpu_mask_tests = b.addRunArtifact(cpu_mask_tests);
    const run_logging_tests = b.addRunArtifact(logging_tests);
    const run_pin_path_tests = b.addRunArtifact(pin_path_tests);
    const run_libbpf_segments_tests = b.addRunArtifact(libbpf_segments_tests);
    const run_bpf_type_names_tests = b.addRunArtifact(bpf_type_names_tests);
    const run_file_path_handle_bridge_tests = b.addRunArtifact(file_path_handle_bridge_tests);
    const run_perf_buffer_poll_tests = b.addRunArtifact(perf_buffer_poll_tests);

    const test_step = b.step("test", "Run Phase 8 tooling expansion tests");
    test_step.dependOn(&run_exec_cmd_tests.step);
    test_step.dependOn(&run_help_tests.step);
    test_step.dependOn(&run_kallsyms_tests.step);
    test_step.dependOn(&run_cpu_mask_tests.step);
    test_step.dependOn(&run_logging_tests.step);
    test_step.dependOn(&run_pin_path_tests.step);
    test_step.dependOn(&run_libbpf_segments_tests.step);
    test_step.dependOn(&run_bpf_type_names_tests.step);
    test_step.dependOn(&run_file_path_handle_bridge_tests.step);
    test_step.dependOn(&run_perf_buffer_poll_tests.step);
}