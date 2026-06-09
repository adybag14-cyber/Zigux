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
    0x7f, 'E', 'L', 'F', 0xff, 1, 1, 0,
    0,    0,   0,   0,   0,    0, 0, 0,
};
const non_elf_header = [_]u8{
    0, 'E', 'L', 'F', 2, 1, 1, 0,
    0, 0,   0,   0,   0, 0, 0, 0,
};

fn addEnvCase(
    b: *std.Build,
    step: *std.Build.Step,
    executable: *std.Build.Step.Compile,
    name: []const u8,
    stdin: []const u8,
    stdout: []const u8,
    stderr: []const u8,
    exit_code: u8,
) void {
    const run = b.addRunArtifact(executable);
    run.setName(name);
    run.setEnvironmentVariable("KERNEL_ELFCLASS", "ELFCLASS64");
    run.setEnvironmentVariable("ELFCLASS", "ELFCLASS32");
    run.setEnvironmentVariable("MK_ELFCONFIG_INPUT", "not-stdin");
    run.setEnvironmentVariable("ZIGUX_MK_ELFCONFIG_EXPECTED", "invalid-class");
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

    const executable_env = b.step(
        "mk-elfconfig-executable-env-contract",
        "Run mk_elfconfig with misleading environment variables and check stdin remains authoritative",
    );
    addEnvCase(
        b,
        executable_env,
        mk_elfconfig,
        "mk_elfconfig executable env: elf32 wins over env",
        &elf32_header,
        "#define KERNEL_ELFCLASS ELFCLASS32\n",
        "",
        0,
    );
    addEnvCase(
        b,
        executable_env,
        mk_elfconfig,
        "mk_elfconfig executable env: elf64 wins over env",
        &elf64_header,
        "#define KERNEL_ELFCLASS ELFCLASS64\n",
        "",
        0,
    );
    addEnvCase(
        b,
        executable_env,
        mk_elfconfig,
        "mk_elfconfig executable env: invalid class stays silent",
        &invalid_class_header,
        "",
        "",
        1,
    );
    addEnvCase(
        b,
        executable_env,
        mk_elfconfig,
        "mk_elfconfig executable env: non-ELF reports stderr",
        &non_elf_header,
        "",
        "Error: not ELF\n",
        1,
    );

    const test_step = b.step("test", "Run mk_elfconfig executable environment contract");
    test_step.dependOn(executable_env);
    b.default_step.dependOn(test_step);
}
