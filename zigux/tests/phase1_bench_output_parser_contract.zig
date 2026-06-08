const std = @import("std");

const checker_source =
    \\def parse_output(stdout: str) -> tuple[dict[str, str], dict[str, int]]:
    \\    parsed: dict[str, str] = {}
    \\    counts: dict[str, int] = {}
    \\    for raw_line in stdout.splitlines():
    \\        line = raw_line.strip()
    \\        if not line or "=" not in line:
    \\            continue
    \\        key, value = line.split("=", 1)
    \\        parsed[key] = value
    \\        counts[key] = counts.get(key, 0) + 1
    \\    return parsed, counts
    \\
    \\def validate_output(expectations: dict[str, object], stdout: str) -> tuple[str, object]:
    \\    parsed, counts = parse_output(stdout)
    \\    required_keys = {
    \\        "PHASE1_BENCH",
    \\        *expectations["iterations"],
    \\        *expectations["checksums"],
    \\        *expectations["exact_checksums"],
    \\    }
    \\    duplicate = sorted(key for key in required_keys if counts.get(key, 0) > 1)
    \\    if duplicate:
    \\        return ("duplicate", duplicate)
    \\    unexpected = sorted(
    \\        key for key in parsed if key.startswith("PHASE1_BENCH") and key not in required_keys
    \\    )
    \\    if unexpected:
    \\        return ("unexpected", unexpected)
    \\    if parsed.get("PHASE1_BENCH") != expectations["status"]:
    \\        return ("status", (expectations["status"], parsed.get("PHASE1_BENCH")))
    \\    for key, expected in expectations["iterations"].items():
    \\        actual = parsed.get(key)
    \\        if actual is None:
    \\            continue
    \\        try:
    \\            value = int(actual)
    \\        except ValueError:
    \\            return ("iteration_value_type", (key, actual))
    \\        if value != expected:
    \\            return ("iteration_mismatch", (key, expected, actual))
    \\    for key in expectations["checksums"]:
    \\        actual = parsed.get(key)
    \\        if actual is None:
    \\            continue
    \\        try:
    \\            value = int(actual)
    \\        except ValueError:
    \\            return ("checksum_value_type", (key, actual))
    \\        if value <= 0:
    \\            return ("nonpositive_checksum", (key, actual))
    \\
;

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn expectContainsAny(needles: []const []const u8) !void {
    for (needles) |needle| {
        if (std.mem.indexOf(u8, checker_source, needle) != null) {
            return;
        }
    }
    return error.MissingExpectedMarker;
}

fn expectBefore(earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, checker_source, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, checker_source, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn expectAnyBefore(earlier: []const u8, later_options: []const []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, checker_source, earlier) orelse return error.MissingEarlierMarker;
    for (later_options) |later| {
        if (std.mem.indexOf(u8, checker_source, later)) |later_index| {
            try std.testing.expect(earlier_index < later_index);
            return;
        }
    }
    return error.MissingLaterMarker;
}

fn expectAnyPairBefore(earlier_options: []const []const u8, later_options: []const []const u8) !void {
    for (earlier_options) |earlier| {
        if (std.mem.indexOf(u8, checker_source, earlier)) |earlier_index| {
            for (later_options) |later| {
                if (std.mem.indexOf(u8, checker_source, later)) |later_index| {
                    try std.testing.expect(earlier_index < later_index);
                    return;
                }
            }
        }
    }
    return error.MissingOrderedMarkers;
}

test "bench output parser strips noise and counts duplicate keys" {
    try expectContains("def parse_output(stdout: str) -> tuple[dict[str, str], dict[str, int]]:");
    try expectContains("for raw_line in stdout.splitlines():");
    try expectContains("line = raw_line.strip()");
    try expectContainsAny(&.{
        "if not line or \"=\" not in line:",
        "if not line or '=' not in line:",
    });
    try expectContains("line.split(");
    try expectContains(", 1)");
    try expectContains("parsed[key] = value");
    try expectContains("counts[key] = counts.get(key, 0) + 1");
    try expectContains("return parsed, counts");
}

test "bench output validator rejects duplicate keys before unexpected keys" {
    try expectContains("def validate_output(expectations: dict[str, object], stdout: str) -> tuple[str, object]:");
    try expectContains("parsed, counts = parse_output(stdout)");
    try expectContains("required_keys = {");
    try expectContains("duplicate = sorted(");
    try expectContains("counts.get(key, 0) > 1");
    try expectContainsAny(&.{
        "return (\"duplicate\", duplicate)",
        "return ('duplicate', duplicate)",
    });
    try expectContains("unexpected = sorted(");
    try expectContains("key.startswith(");
    try expectContainsAny(&.{
        "key.startswith(\"PHASE1_BENCH\")",
        "key.startswith('PHASE1_BENCH')",
    });
    try expectContainsAny(&.{
        "return (\"unexpected\", unexpected)",
        "return ('unexpected', unexpected)",
    });
    try expectBefore("duplicate = sorted(", "unexpected = sorted(");
    try expectAnyPairBefore(&.{
        "return (\"duplicate\", duplicate)",
        "return ('duplicate', duplicate)",
    }, &.{
        "return (\"unexpected\", unexpected)",
        "return ('unexpected', unexpected)",
    });
}

test "bench output validator keeps status and numeric failures fail closed" {
    try expectContainsAny(&.{
        "parsed.get(\"PHASE1_BENCH\")",
        "parsed.get('PHASE1_BENCH')",
    });
    try expectContainsAny(&.{
        "return (\"status\", (expectations[\"status\"], parsed.get(\"PHASE1_BENCH\")))",
        "return ('status', (expectations['status'], actual_status))",
    });
    try expectContains("except ValueError:");
    try expectContainsAny(&.{
        "return (\"iteration_value_type\", (key, actual))",
        "return ('iteration_value_type', (key, actual))",
    });
    try expectContainsAny(&.{
        "return (\"checksum_value_type\", (key, actual))",
        "return ('checksum_value_type', (key, actual))",
    });
    try expectContains(" <= 0:");
    try expectContainsAny(&.{
        "return (\"nonpositive_checksum\", (key, actual))",
        "return ('nonpositive_checksum', (key, actual))",
    });
    try expectAnyBefore("except ValueError:", &.{
        "return (\"nonpositive_checksum\", (key, actual))",
        "return ('nonpositive_checksum', (key, actual))",
    });
}
