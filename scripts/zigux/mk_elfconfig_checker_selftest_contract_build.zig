const std = @import("std");

const expected_self_test_stdout =
    \\MK_ELFCONFIG_DIFF_SELF_TEST=pass
    \\MK_ELFCONFIG_DIFF_SELF_TEST_CASE_COUNT=5
    \\
;

pub fn build(b: *std.Build) void {
    const contract = b.step(
        "mk-elfconfig-checker-selftest-contract",
        "Verify the mk_elfconfig checker self-test route keeps its pass and case-count markers",
    );

    const run_self_test = b.addSystemCommand(&.{
        "python3",
        "check-mk-elfconfig-diff.py",
        "--self-test",
    });
    run_self_test.setName("mk-elfconfig-checker-self-test");
    run_self_test.setCwd(b.path("."));
    run_self_test.addCheck(.{ .expect_stdout_exact = expected_self_test_stdout });
    run_self_test.addCheck(.{ .expect_stderr_exact = "" });
    run_self_test.expectExitCode(0);
    contract.dependOn(&run_self_test.step);

    const test_step = b.step("test", "Run mk_elfconfig checker self-test contract");
    test_step.dependOn(contract);
    b.default_step.dependOn(test_step);
}

test "self-test contract stdout pins pass marker before count marker" {
    const pass = "MK_ELFCONFIG_DIFF_SELF_TEST=pass\n";
    const count = "MK_ELFCONFIG_DIFF_SELF_TEST_CASE_COUNT=5\n";
    const pass_index = std.mem.indexOf(u8, expected_self_test_stdout, pass) orelse return error.MissingPassMarker;
    const count_index = std.mem.indexOf(u8, expected_self_test_stdout, count) orelse return error.MissingCountMarker;

    try std.testing.expect(pass_index < count_index);
    try std.testing.expectEqualStrings(pass ++ count, expected_self_test_stdout);
}
