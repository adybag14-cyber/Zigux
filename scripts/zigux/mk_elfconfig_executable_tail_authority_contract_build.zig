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
const non_elf_header = [_]u8{
    0x00, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};

const elf32_then_elf64 = elf32_header ++ elf64_header;
const elf64_then_non_elf = elf64_header ++ non_elf_header;
const invalid_class_then_elf32 = invalid_class_header ++ elf32_header;
const non_elf_then_elf32 = non_elf_header ++ elf32_header;

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

    const executable_tail_authority = b.step(
        "mk-elfconfig-executable-tail-authority-contract",
        "Run mk_elfconfig as a process and check the first stdin ELF ident stays authoritative",
    );
    addCase(
        b,
        executable_tail_authority,
        mk_elfconfig,
        "mk_elfconfig executable tail authority: elf32 before elf64",
        &elf32_then_elf64,
        "#define KERNEL_ELFCLASS ELFCLASS32\n",
        "",
        0,
    );
    addCase(
        b,
        executable_tail_authority,
        mk_elfconfig,
        "mk_elfconfig executable tail authority: elf64 before non-ELF",
        &elf64_then_non_elf,
        "#define KERNEL_ELFCLASS ELFCLASS64\n",
        "",
        0,
    );
    addCase(
        b,
        executable_tail_authority,
        mk_elfconfig,
        "mk_elfconfig executable tail authority: invalid class before elf32",
        &invalid_class_then_elf32,
        "",
        "",
        1,
    );
    addCase(
        b,
        executable_tail_authority,
        mk_elfconfig,
        "mk_elfconfig executable tail authority: non-ELF before elf32",
        &non_elf_then_elf32,
        "",
        "Error: not ELF\n",
        1,
    );

    const test_step = b.step("test", "Run mk_elfconfig executable tail authority contract");
    test_step.dependOn(executable_tail_authority);
    b.default_step.dependOn(executable_tail_authority);
}
