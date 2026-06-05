const std = @import("std");

const elf32_header = [_]u8{
    0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const invalid_class_header = [_]u8{
    0x7f, 'E', 'L', 'F', 3, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const non_elf_header = [_]u8{
    0x00, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};

fn addCase(
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

    const executable_stdin = b.step(
        "mk-elfconfig-executable-stdin-contract",
        "Run mk_elfconfig as a process and check stdin/stdout/stderr/exit behavior",
    );
    addCase(
        b,
        executable_stdin,
        mk_elfconfig,
        "mk_elfconfig executable stdin: elf32",
        &elf32_header,
        "#define KERNEL_ELFCLASS ELFCLASS32\n",
        "",
        0,
    );
    addCase(
        b,
        executable_stdin,
        mk_elfconfig,
        "mk_elfconfig executable stdin: invalid class",
        &invalid_class_header,
        "",
        "",
        1,
    );
    addCase(
        b,
        executable_stdin,
        mk_elfconfig,
        "mk_elfconfig executable stdin: non-ELF",
        &non_elf_header,
        "",
        "Error: not ELF\n",
        1,
    );
    addCase(
        b,
        executable_stdin,
        mk_elfconfig,
        "mk_elfconfig executable stdin: truncated",
        "\x7fELF\x01\x01\x01",
        "",
        "Error: input truncated\n",
        1,
    );

    const test_step = b.step("test", "Run mk_elfconfig executable stdin contract");
    test_step.dependOn(executable_stdin);
}
