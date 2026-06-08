const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("confdata_bridge_invalid_symbol_json_cli_surface_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(unit_tests);
    run_tests.setCwd(b.path("../../.."));

    const named_step = b.step(
        "lane20-confdata-bridge-invalid-symbol-json-cli-surface",
        "Run Lane 20 confdata_bridge invalid-symbol JSON CLI surface proof",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 20 confdata_bridge invalid-symbol JSON CLI surface proof");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
