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
    0x7f, 'E', 'L', 'F', 0xfe, 1, 1, 0,
    0,    0,   0,   0,   0,    0, 0, 0,
};
const non_elf_header = [_]u8{
    'Z', 'I', 'G', 'X', 2, 1, 1, 0,
    0,   0,   0,   0,   0, 0, 0, 0,
};

fn addRepeatedRunCase(
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

    const executable_repeated_runs = b.step(
        "mk-elfconfig-executable-repeated-runs-contract",
        "Run mk_elfconfig repeatedly and check process output isolation",
    );
    addRepeatedRunCase(
        b,
        executable_repeated_runs,
        mk_elfconfig,
        "mk_elfconfig repeated run 1: elf32 stdout only",
        &elf32_header,
        "#define KERNEL_ELFCLASS ELFCLASS32\n",
        "",
        0,
    );
    addRepeatedRunCase(
        b,
        executable_repeated_runs,
        mk_elfconfig,
        "mk_elfconfig repeated run 2: non-ELF stderr only",
        &non_elf_header,
        "",
        "Error: not ELF\n",
        1,
    );
    addRepeatedRunCase(
        b,
        executable_repeated_runs,
        mk_elfconfig,
        "mk_elfconfig repeated run 3: elf64 stdout after failure",
        &elf64_header,
        "#define KERNEL_ELFCLASS ELFCLASS64\n",
        "",
        0,
    );
    addRepeatedRunCase(
        b,
        executable_repeated_runs,
        mk_elfconfig,
        "mk_elfconfig repeated run 4: invalid class stays silent",
        &invalid_class_header,
        "",
        "",
        1,
    );
    addRepeatedRunCase(
        b,
        executable_repeated_runs,
        mk_elfconfig,
        "mk_elfconfig repeated run 5: truncation stderr after silence",
        "\x7fELF\x01\x01",
        "",
        "Error: input truncated\n",
        1,
    );
    addRepeatedRunCase(
        b,
        executable_repeated_runs,
        mk_elfconfig,
        "mk_elfconfig repeated run 6: elf32 stdout after errors",
        &elf32_header,
        "#define KERNEL_ELFCLASS ELFCLASS32\n",
        "",
        0,
    );

    const test_step = b.step("test", "Run mk_elfconfig executable repeated-runs contract");
    test_step.dependOn(executable_repeated_runs);
}
