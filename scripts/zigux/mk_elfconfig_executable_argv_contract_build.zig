const std = @import("std");

const elf64_header = [_]u8{
    0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const invalid_class_header = [_]u8{
    0x7f, 'E', 'L', 'F', 0xff, 1, 1, 0,
    0,    0,   0,   0,   0,    0, 0, 0,
};
const non_elf_header = [_]u8{
    0x7f, 'E', 'L', 0, 2, 1, 1, 0,
    0,    0,   0,   0, 0, 0, 0, 0,
};

fn addArgvCase(
    b: *std.Build,
    step: *std.Build.Step,
    executable: *std.Build.Step.Compile,
    name: []const u8,
    argv: []const []const u8,
    stdin: []const u8,
    stdout: []const u8,
    stderr: []const u8,
    exit_code: u8,
) void {
    const run = b.addRunArtifact(executable);
    run.setName(name);
    run.addArgs(argv);
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

    const executable_argv = b.step(
        "mk-elfconfig-executable-argv-contract",
        "Run mk_elfconfig with extra argv and check stdin remains authoritative",
    );
    addArgvCase(
        b,
        executable_argv,
        mk_elfconfig,
        "mk_elfconfig executable argv: elf64 ignores flags",
        &.{ "--help", "--version", "ignored.elf" },
        &elf64_header,
        "#define KERNEL_ELFCLASS ELFCLASS64\n",
        "",
        0,
    );
    addArgvCase(
        b,
        executable_argv,
        mk_elfconfig,
        "mk_elfconfig executable argv: invalid class stays silent",
        &.{ "-m", "ELFCLASS64", "--" },
        &invalid_class_header,
        "",
        "",
        1,
    );
    addArgvCase(
        b,
        executable_argv,
        mk_elfconfig,
        "mk_elfconfig executable argv: non-ELF still reports stderr",
        &.{ "valid-looking-name.o", "--input", "later" },
        &non_elf_header,
        "",
        "Error: not ELF\n",
        1,
    );
    addArgvCase(
        b,
        executable_argv,
        mk_elfconfig,
        "mk_elfconfig executable argv: empty stdin is truncated",
        &.{"ignored-empty-input"},
        "",
        "",
        "Error: input truncated\n",
        1,
    );

    const test_step = b.step("test", "Run mk_elfconfig executable argv contract");
    test_step.dependOn(executable_argv);
}
