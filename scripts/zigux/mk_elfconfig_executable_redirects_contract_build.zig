const std = @import("std");

const elf32_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const elf64_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const invalid_class_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 3, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const non_elf_ident = [_]u8{
    0x00, 'E', 'L', 'F', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const truncated_ident = "\x7fELF\x02\x01\x01\x00";

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const not_elf_text = "Error: not ELF\n";
const truncated_text = "Error: input truncated\n";

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

    const contract = b.step(
        "mk-elfconfig-executable-redirects-contract",
        "Verify mk_elfconfig remains stdin-driven when stdout/stderr are captured separately",
    );

    addRedirectCase(
        b,
        contract,
        mk_elfconfig,
        "redirect-elf32-stdout-success",
        &elf32_ident,
        elf32_define,
        "",
        0,
    );
    addRedirectCase(
        b,
        contract,
        mk_elfconfig,
        "redirect-non-elf-stderr-failure",
        &non_elf_ident,
        "",
        not_elf_text,
        1,
    );
    addRedirectCase(
        b,
        contract,
        mk_elfconfig,
        "redirect-elf64-after-stderr-failure",
        &elf64_ident,
        elf64_define,
        "",
        0,
    );
    addRedirectCase(
        b,
        contract,
        mk_elfconfig,
        "redirect-invalid-class-silent-failure",
        &invalid_class_ident,
        "",
        "",
        1,
    );
    addRedirectCase(
        b,
        contract,
        mk_elfconfig,
        "redirect-truncated-stderr-failure",
        truncated_ident,
        "",
        truncated_text,
        1,
    );

    const test_step = b.step("test", "Run mk_elfconfig executable redirects contract");
    test_step.dependOn(contract);
}

fn addRedirectCase(
    b: *std.Build,
    contract: *std.Build.Step,
    mk_elfconfig: *std.Build.Step.Compile,
    name: []const u8,
    stdin_bytes: []const u8,
    stdout_bytes: []const u8,
    stderr_bytes: []const u8,
    exit_code: u8,
) void {
    const run = b.addRunArtifact(mk_elfconfig);
    run.setName(name);
    run.setStdIn(.{ .bytes = stdin_bytes });
    run.addCheck(.{ .expect_stdout_exact = stdout_bytes });
    run.addCheck(.{ .expect_stderr_exact = stderr_bytes });
    run.expectExitCode(exit_code);
    contract.dependOn(&run.step);
}

test "redirect contract fixture byte lengths stay intentional" {
    try std.testing.expectEqual(@as(usize, 16), elf32_ident.len);
    try std.testing.expectEqual(@as(usize, 16), elf64_ident.len);
    try std.testing.expectEqual(@as(usize, 16), invalid_class_ident.len);
    try std.testing.expectEqual(@as(usize, 16), non_elf_ident.len);
    try std.testing.expectEqual(@as(usize, 8), truncated_ident.len);
}
