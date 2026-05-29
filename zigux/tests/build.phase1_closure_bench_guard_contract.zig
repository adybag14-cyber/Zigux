const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const closure_note = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        "../../Documentation/zigux/phase1-closure.md",
        b.allocator,
        .limited(256 * 1024),
    ) catch @panic("failed to read Phase 1 closure note");
    const closure_validator = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        "../../scripts/zigux/validate-phase1-closure.py",
        b.allocator,
        .limited(512 * 1024),
    ) catch @panic("failed to read Phase 1 closure validator");
    const bench_checker = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        "../../scripts/zigux/check-phase1-bench.py",
        b.allocator,
        .limited(512 * 1024),
    ) catch @panic("failed to read Phase 1 bench checker");

    const contract_data = b.addOptions();
    contract_data.addOption([]const u8, "closure_note", closure_note);
    contract_data.addOption([]const u8, "closure_validator", closure_validator);
    contract_data.addOption([]const u8, "bench_checker", bench_checker);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_closure_bench_guard_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("phase1_closure_bench_guard_data", contract_data);

    const tests = b.addTest(.{
        .name = "phase1-closure-bench-guard-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route_step = b.step(
        "phase1-closure-bench-guard-contract",
        "Run the Phase 1 closure bench guard contract",
    );
    route_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 closure bench guard contract");
    test_step.dependOn(&run_tests.step);
}
