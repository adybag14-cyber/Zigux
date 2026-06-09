const std = @import("std");

const elf64_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
};
const invalid_class_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 0xfe, 1, 1, 0,
    0,    0,   0,   0,   0,    0, 0, 0,
};
const not_elf_ident = [_]u8{
    'n', 'o', 't', 0, 1, 1, 1, 0,
    0,   0,   0,   0, 0, 0, 0, 0,
};
const magic_mismatch_then_truncated = [_]u8{
    0x7f, 'E', 'L', 'x', 1, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
    0x7f, 'E', 'L', 'F', 1, 1,
};
const truncated_ident = "\x7fELF\x02\x01";

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
        "mk-elfconfig-executable-stderr-sequence-contract",
        "Verify mk_elfconfig executable stderr failures stay exact across adjacent runs",
    );

    addCase(b, contract, mk_elfconfig, "stderr-sequence-1-not-elf", &not_elf_ident, "", not_elf_text, 1);
    addCase(b, contract, mk_elfconfig, "stderr-sequence-2-truncated", truncated_ident, "", truncated_text, 1);
    addCase(b, contract, mk_elfconfig, "stderr-sequence-3-not-elf-no-trunc-tail", &magic_mismatch_then_truncated, "", not_elf_text, 1);
    addCase(b, contract, mk_elfconfig, "stderr-sequence-4-invalid-class-silent", &invalid_class_ident, "", "", 1);
    addCase(b, contract, mk_elfconfig, "stderr-sequence-5-success-after-failures", &elf64_ident, elf64_define, "", 0);

    const test_step = b.step("test", "Run mk_elfconfig executable stderr sequence contract");
    test_step.dependOn(contract);
    b.default_step.dependOn(test_step);
}

fn addCase(
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

test "stderr sequence fixtures keep full-header and tail boundaries intentional" {
    try std.testing.expectEqual(@as(usize, 16), elf64_ident.len);
    try std.testing.expectEqual(@as(usize, 16), invalid_class_ident.len);
    try std.testing.expectEqual(@as(usize, 16), not_elf_ident.len);
    try std.testing.expectEqual(@as(usize, 22), magic_mismatch_then_truncated.len);
    try std.testing.expectEqual(@as(usize, 6), truncated_ident.len);
    try std.testing.expectEqualStrings(not_elf_text, "Error: not ELF\n");
    try std.testing.expectEqualStrings(truncated_text, "Error: input truncated\n");
}
