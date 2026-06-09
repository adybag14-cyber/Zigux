const std = @import("std");

const elf32_header = [_]u8{
    0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const elf64_header = [_]u8{
    0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const invalid_class_header = [_]u8{
    0x7f, 'E', 'L', 'F', 0, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const truncated_header = [_]u8{
    0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0,
};

fn addCwdCase(
    b: *std.Build,
    step: *std.Build.Step,
    executable: *std.Build.Step.Compile,
    cwd: std.Build.LazyPath,
    name: []const u8,
    stdin: []const u8,
    stdout: []const u8,
    stderr: []const u8,
    exit_code: u8,
) void {
    const run = b.addRunArtifact(executable);
    run.setName(name);
    run.setCwd(cwd);
    run.setStdIn(.{ .bytes = stdin });
    run.addCheck(.{ .expect_stdout_exact = stdout });
    run.addCheck(.{ .expect_stderr_exact = stderr });
    run.expectExitCode(exit_code);
    step.dependOn(&run.step);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const mk_elfconfig = b.addExecutable(.{
        .name = "mk_elfconfig",
        .root_module = b.createModule(.{
            .root_source_file = b.path("mk_elfconfig.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const fixture_cwd = b.path("../../zigux/tests/fixtures/mk_elfconfig");
    const executable_cwd = b.step(
        "mk-elfconfig-executable-cwd-contract",
        "Run mk_elfconfig from fixture cwd and check stdin remains authoritative",
    );
    addCwdCase(
        b,
        executable_cwd,
        mk_elfconfig,
        fixture_cwd,
        "mk_elfconfig executable cwd: elf32 from stdin",
        &elf32_header,
        "#define KERNEL_ELFCLASS ELFCLASS32\n",
        "",
        0,
    );
    addCwdCase(
        b,
        executable_cwd,
        mk_elfconfig,
        fixture_cwd,
        "mk_elfconfig executable cwd: elf64 from stdin",
        &elf64_header,
        "#define KERNEL_ELFCLASS ELFCLASS64\n",
        "",
        0,
    );
    addCwdCase(
        b,
        executable_cwd,
        mk_elfconfig,
        fixture_cwd,
        "mk_elfconfig executable cwd: invalid class stays silent",
        &invalid_class_header,
        "",
        "",
        1,
    );
    addCwdCase(
        b,
        executable_cwd,
        mk_elfconfig,
        fixture_cwd,
        "mk_elfconfig executable cwd: truncation reports stderr",
        &truncated_header,
        "",
        "Error: input truncated\n",
        1,
    );

    const test_step = b.step("test", "Run mk_elfconfig executable cwd contract");
    test_step.dependOn(executable_cwd);
    b.default_step.dependOn(test_step);
}
