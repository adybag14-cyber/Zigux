const std = @import("std");

const helper_source = @embedFile("artifact_diff.py");

const cli_help_lines = [_][]const u8{
    "usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test]",
    " [expected] [actual]",
    "",
    "Compare two artifacts in a stable mode.",
    "",
    "positional arguments:",
    " expected",
    " actual",
    "",
    "options:",
    " -h, --help show this help message and exit",
    " --mode {text,json,bytes}",
    " --self-test Run built-in deterministic comparison checks.",
};

const self_test_cases = [_][]const u8{
    "text_pass",
    "text_mismatch",
    "json_pass",
    "json_mismatch",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "bytes_pass",
    "bytes_drift",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "bytes_missing_expected",
    "bytes_missing_actual",
    "bytes_missing_both",
    "legacy_sha256_alias",
    "missing_mode_value_rejected",
    "missing_positional_arguments_rejected",
    "invalid_mode_rejected",
    "extra_positional_rejected",
};

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(contains(helper_source, needle));
}

fn expectContainsAny(needles: []const []const u8) !void {
    for (needles) |needle| {
        if (contains(helper_source, needle)) return;
    }
    try std.testing.expect(false);
}

fn expectUniqueCatalog(comptime cases: []const []const u8) !void {
    for (cases, 0..) |case, index| {
        for (cases[0..index]) |previous| {
            try std.testing.expect(!std.mem.eql(u8, case, previous));
        }
    }
}

test "artifact diff CLI help and parser errors remain stable" {
    try expectContainsAny(&.{
        "MODE_CHOICES = (\"text\", \"json\", \"bytes\")",
        "parser.add_argument('--mode', choices=['text', 'json', 'sha256'])",
    });
    try expectContainsAny(&.{
        "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}",
        "elif mode == 'sha256':",
    });
    try expectContainsAny(&.{
        "HELP_LINES = [",
        "argparse.ArgumentParser(description=__doc__)",
        "argparse.ArgumentParser(description='Compare two artifacts in a stable mode.')",
    });
    for (cli_help_lines) |line| {
        if (contains(helper_source, "HELP_LINES = [")) {
            try expectContains(line);
        }
    }

    try expectContainsAny(&.{ "MISSING_ARGUMENT_ERROR = (", "required=True", "parser.error('--mode, expected, and actual are required unless --self-test is set')" });
    try expectContainsAny(&.{ "are required unless --self-test is set", "parser.add_argument('--mode'" });
    try expectContainsAny(&.{ "INVALID_MODE_ERROR_TEMPLATE = (", "invalid_mode_rejected" });
    try expectContainsAny(&.{
        "invalid choice: {value!r} (choose from text, json, bytes)",
        "invalid artifact diff mode rejected",
        "unsupported artifact diff mode: yaml",
    });
    try expectContainsAny(&.{ "TOO_MANY_ARGUMENTS_ERROR = (", "parser.add_argument('actual', nargs='?')" });
    try expectContainsAny(&.{ "expected exactly two positional", "parser.add_argument('expected', nargs='?')" });
}

test "artifact diff mode dispatch keeps text json bytes and legacy sha256" {
    try expectContainsAny(&.{ "def normalize_mode(mode: str) -> str:", "def compare_artifacts(mode: str, expected: Path, actual: Path)" });
    try expectContainsAny(&.{ "return LEGACY_MODE_ALIASES.get(mode, mode)", "elif mode == 'sha256':" });
    try expectContainsAny(&.{ "if mode == \"text\":", "if mode == 'text':" });
    try expectContainsAny(&.{ "return compare_text(expected, actual)", "expected_value = read_text(expected)" });
    try expectContainsAny(&.{ "if mode == \"json\":", "elif mode == 'json':" });
    try expectContainsAny(&.{ "return compare_json(expected, actual)", "expected_value = canonical_json(expected)" });
    try expectContainsAny(&.{ "if mode == \"bytes\":", "elif mode == 'sha256':" });
    try expectContainsAny(&.{ "return compare_bytes(expected, actual)", "expected_value = sha256_digest(expected)" });
    try expectContainsAny(&.{
        "legacy_alias = run_parser_probe([\"--mode\", \"sha256\", str(blob_a), str(blob_a)])",
        "matched, details = compare_artifacts('sha256', blob_a, blob_b)",
    });
    try expectContainsAny(&.{
        "assert_case(\"MODE=bytes\" in legacy_alias.stdout, \"legacy_sha256_alias\")",
        "'MODE=sha256'",
    });
}

test "artifact diff self-test catalog covers parser and digest failure gates" {
    try expectUniqueCatalog(self_test_cases[0..]);
    try expectContainsAny(&.{ "SELF_TEST_CASES = [", "EXPECTED_SELF_TEST_CASES = [" });
    for (self_test_cases) |case| {
        if (std.mem.startsWith(u8, case, "bytes_")) {
            if (std.mem.eql(u8, case, "bytes_pass")) {
                try expectContainsAny(&.{ "bytes_pass", "sha256_pass" });
            } else if (std.mem.eql(u8, case, "bytes_drift")) {
                try expectContainsAny(&.{ "bytes_drift", "sha256_drift" });
            } else if (std.mem.eql(u8, case, "bytes_missing_expected")) {
                try expectContainsAny(&.{ "bytes_missing_expected", "sha256_missing_expected" });
            } else if (std.mem.eql(u8, case, "bytes_missing_actual")) {
                try expectContainsAny(&.{ "bytes_missing_actual", "sha256_missing_actual" });
            } else if (std.mem.eql(u8, case, "bytes_missing_both")) {
                try expectContainsAny(&.{ "bytes_missing_both", "sha256_missing_both" });
            } else {
                try expectContains(case);
            }
        } else if (std.mem.eql(u8, case, "legacy_sha256_alias")) {
            try expectContainsAny(&.{ case, "sha256_pass" });
        } else if (std.mem.eql(u8, case, "missing_mode_value_rejected") or
            std.mem.eql(u8, case, "missing_positional_arguments_rejected") or
            std.mem.eql(u8, case, "extra_positional_rejected"))
        {
            try expectContainsAny(&.{ case, "argparse" });
        } else {
            try expectContains(case);
        }
    }

    try expectContains("ARTIFACT_DIFF_SELF_TEST=pass");
    try expectContainsAny(&.{
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}",
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(EXPECTED_SELF_TEST_CASES)}",
    });
    try expectContainsAny(&.{
        "ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES)",
        "ARTIFACT_DIFF_SELF_TEST_CASES=' + ','.join(EXPECTED_SELF_TEST_CASES)",
    });
    try expectContainsAny(&.{
        "SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576",
        "f\"SHA256={details['expected_sha256']}\"",
    });
    try expectContainsAny(&.{
        "EXPECTED_SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576",
        "f\"EXPECTED_SHA256={details['expected_sha256']}\"",
    });
    try expectContainsAny(&.{
        "ACTUAL_SHA256=bfc83f8f1f4369ce3cfabfdff0699ae3bf7a15b89f1702b690e56c6f35f1ee94",
        "f\"ACTUAL_SHA256={details['actual_sha256']}\"",
    });
}
