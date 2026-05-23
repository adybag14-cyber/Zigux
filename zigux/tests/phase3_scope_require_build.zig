const std = @import("std");

fn addScopeRequireTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_unsafe = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_unsafe.addImport("abi_bindings", abi_bindings);
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
    unsafe_policy.addImport("narrow", narrow_unsafe);
    const scope_require = b.createModule(.{
        .root_source_file = b.path("../unsafe/scope_require.zig"),
        .target = target,
        .optimize = optimize,
    });
    scope_require.addImport("abi_bindings", abi_bindings);
    scope_require.addImport("narrow_unsafe", narrow_unsafe);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_scope_require_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("narrow_unsafe", narrow_unsafe);
    root_module.addImport("scope_require", scope_require);
    root_module.addImport("unsafe_policy", unsafe_policy);

    const tests = b.addTest(.{
        .name = "phase3-scope-require-test",
        .root_module = root_module,
    });

    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const scope_require = addScopeRequireTest(b, target, optimize);

    const scope_require_step = b.step(
        "phase3-scope-require-test",
        "Run the focused Phase 3 unsafe scope-require replay",
    );
    scope_require_step.dependOn(&scope_require.step);
}
