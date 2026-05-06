const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 cmdline survey keeps the roadmap-backed helper packet reviewable" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-cmdline-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "lib/cmdline.c");
    try expectContains(slice_note, "lib/cmdline.zig");
    try expectContains(slice_note, "zigux/tests/phase7_cmdline.zig");
    try expectContains(slice_note, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(slice_note, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    try expectContains(slice_note, "zig build test --build-file zigux/tests/phase7_build.zig --summary all");
    try expectContains(slice_note, "runtime-safe parsing helpers that:");
    try expectContains(slice_note, "- do not allocate");
    try expectContains(slice_note, "Linux-style hyphen range expansion, validation-only counting, and leading-plus numeric acceptance for `get_option()` and `get_options()`");
    try expectContains(slice_note, "memory-size suffix scaling, leading-plus numeric acceptance, and accurate parse-stop reporting in `memparse()`");
    try expectContains(slice_note, "serialized `next_arg()` edge cases covering quoted values, quoted bare tokens, empty quoted bare tokens, leading quoted tokens that contain `=` and still split at the first equals, empty quoted or whitespace-only values, unquoted punctuation-rich values, first-equals splitting, leading-equals sentinel handling, unterminated quoted values, mixed-whitespace rest trimming, and empty-rest termination");
    try expectContains(slice_note, "the dedicated survey gate, the committed `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig` fixture module, the exact `zig build test --build-file zigux/tests/phase7_build.zig --summary all` shared compile-check replay, and the shared `validate-phase7.py`, `check-phase7-make-wrapper.py`, `phase7_build.zig`, and `make -C zigux phase7-validate` plus `make -C zigux phase7` routes keep the roadmap anchor, the leading-plus numeric replay, serialized `next_arg()` replay, focused helper replay, and Linux-style validator-first packet aligned around the same parked cmdline slice");

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);
    try expectContains(docs_root, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectContains(docs_root, "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample");
    try expectContains(docs_root, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(docs_root, "zigux/tests/phase7_build.zig");
    try expectContains(docs_root, "scripts/zigux/check-phase7-build-wiring.py");

    const scripts_root = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_root);
    try expectContains(scripts_root, "scripts/zigux/validate-phase7.py");
    try expectContains(scripts_root, "scripts/zigux/check-phase7-make-wrapper.py");
    try expectContains(scripts_root, "scripts/zigux/check-phase7-build-wiring.py");
    try expectContains(scripts_root, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(scripts_root, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    try expectContains(scripts_root, "make -C zigux phase7-validate");
    try expectContains(scripts_root, "make -C zigux phase7");

    const validate_phase7 = try readRepoFile(allocator, "scripts/zigux/validate-phase7.py");
    defer allocator.free(validate_phase7);
    try expectContains(validate_phase7, "\"zigux/tests/phase7_cmdline.zig\"");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_cmdline_survey.zig\"");
    try expectContains(validate_phase7, "\"zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig\"");
    try expectContains(validate_phase7, "\"scripts/zigux/check-phase7-make-wrapper.py\"");
    try expectContains(validate_phase7, "\"scripts/zigux/check-phase7-build-wiring.py\"");

    const samples_root = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_root);
    try expectContains(samples_root, "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;");
    try expectContains(samples_root, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectContains(samples_root, "zigux/tests/phase7_cmdline.zig");
    try expectContains(samples_root, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(samples_root, "zigux/tests/phase7_build.zig");

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_cmdline.zig\"");
    try expectContains(build_file, "\"phase7_cmdline_survey.zig\"");
    try expectContains(build_file, "\"phase7-cmdline-tests\"");
    try expectContains(build_file, "\"phase7-cmdline-survey-tests\"");
    try expectContains(build_file, "run_cmdline_survey_tests.setCwd(b.path(\"../..\"));");

    const tests_root = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_root);
    try expectContains(tests_root, "`scripts/zigux/validate-phase7.py`");
    try expectContains(tests_root, "`scripts/zigux/check-phase7-make-wrapper.py`");
    try expectContains(tests_root, "`scripts/zigux/check-phase7-build-wiring.py`");
    try expectContains(tests_root, "the dedicated `zigux/tests/phase7_cmdline_survey.zig` cmdline survey gate");
    try expectContains(tests_root, "`make -C zigux phase7-validate`");
    try expectContains(tests_root, "`make -C zigux phase7`");

    const zigux_makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(zigux_makefile);
    try expectContains(zigux_makefile, "phase7-validate:");
    try expectContains(zigux_makefile, "scripts/zigux/validate-phase7.py --self-test");
    try expectContains(zigux_makefile, "scripts/zigux/check-phase7-make-wrapper.py --self-test");
    try expectContains(zigux_makefile, "scripts/zigux/check-phase7-build-wiring.py --self-test");
    try expectContains(zigux_makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py");
    try expectContains(zigux_makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py");
    try expectContains(zigux_makefile, "phase7: phase7-validate phase7-test");

    const cmdline_tests = try readRepoFile(allocator, "zigux/tests/phase7_cmdline.zig");
    defer allocator.free(cmdline_tests);
    try expectContains(cmdline_tests, "const next_arg_vectors = @import(\"fixtures/phase7_cmdline_next_arg_vectors.zig\");");
    try expectContains(cmdline_tests, "phase 7 getOption and getOptions preserve Linux-style range parsing");
    try expectContains(cmdline_tests, "const plus_rest = cmdline.getOptions(\"+7\", plus_values.len, &plus_values);");
    try expectContains(cmdline_tests, "const plus_validate_rest = cmdline.getOptions(\"+7\", 0, &plus_validate);");
    try expectContains(cmdline_tests, "const single_rest = cmdline.getOptions(\"1-1\", single.len, &single);");
    try expectContains(cmdline_tests, "const single_validate_rest = cmdline.getOptions(\"1-1\", 0, &single_validate);");
    try expectContains(cmdline_tests, "phase 7 memparse preserves suffix scaling, leading plus, and stop index semantics");
    try expectContains(cmdline_tests, "cmdline.memparse(\"+1K\", &index)");
    try expectContains(cmdline_tests, "phase 7 parseOptionStr matches only exact bare options");
    try expectContains(cmdline_tests, "phase 7 nextArg matches serialized edge fixtures");
    try expectContains(cmdline_tests, "for (next_arg_vectors.next_arg_cases) |fixture| {");
    try expectContains(cmdline_tests, "cmdline.nextArg");

    const next_arg_fixture = try readRepoFile(allocator, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    defer allocator.free(next_arg_fixture);
    try expectContains(next_arg_fixture, ".name = \"quoted value with trailing token\",");
    try expectContains(next_arg_fixture, ".name = \"quoted value keeps embedded equals inside the value\",");
    try expectContains(next_arg_fixture, ".name = \"quoted bare token with trailing token\",");
    try expectContains(next_arg_fixture, ".name = \"empty quoted bare token stays empty and unsplit\",");
    try expectContains(next_arg_fixture, ".name = \"leading quoted token with equals splits like Linux\",");
    try expectContains(next_arg_fixture, ".name = \"empty whitespace-separated value stays on the current token\",");
    try expectContains(next_arg_fixture, ".name = \"first equals wins inside the value\",");
    try expectContains(next_arg_fixture, ".name = \"leading equals sign stays in the parameter token\",");
    try expectContains(next_arg_fixture, ".expected_param = \"\",");
    try expectContains(next_arg_fixture, ".expected_param = \"key\",");
    try expectContains(next_arg_fixture, ".expected_value = \"fast=boot\",");
    try expectContains(next_arg_fixture, ".expected_value = \"value\",");
    try expectContains(next_arg_fixture, ".expected_param = \"=bad\",");
    try expectContains(next_arg_fixture, ".expected_value = \"alpha=beta\",");
}
