// SPDX-License-Identifier: (GPL-2.0 OR MIT)
const std = @import("std");

const ClassResult = struct {
    valid: bool,
    matched: bool = false,
    next: usize = 0,
};

pub fn globMatch(pattern: []const u8, str: []const u8) bool {
    return matchAt(pattern, 0, str, 0);
}

fn matchAt(pattern: []const u8, pat_start: usize, str: []const u8, str_start: usize) bool {
    var pat_idx = pat_start;
    var str_idx = str_start;

    while (true) {
        if (pat_idx == pattern.len) return str_idx == str.len;

        var token = pattern[pat_idx];
        pat_idx += 1;

        switch (token) {
            '?' => {
                if (str_idx == str.len) return false;
                str_idx += 1;
            },
            '*' => {
                while (pat_idx < pattern.len and pattern[pat_idx] == '*') pat_idx += 1;
                if (pat_idx == pattern.len) return true;

                var scan = str_idx;
                while (scan <= str.len) : (scan += 1) {
                    if (matchAt(pattern, pat_idx, str, scan)) return true;
                    if (scan == str.len) break;
                }
                return false;
            },
            '[' => {
                if (str_idx == str.len) return false;
                const parsed = parseClass(pattern, pat_idx, str[str_idx]);
                if (!parsed.valid) {
                    if (str[str_idx] != '[') return false;
                    str_idx += 1;
                } else {
                    if (!parsed.matched) return false;
                    pat_idx = parsed.next;
                    str_idx += 1;
                }
            },
            '\\' => {
                if (pat_idx < pattern.len) {
                    token = pattern[pat_idx];
                    pat_idx += 1;
                    if (str_idx == str.len or str[str_idx] != token) return false;
                    str_idx += 1;
                } else {
                    return str_idx == str.len;
                }
            },
            else => {
                if (str_idx == str.len or str[str_idx] != token) return false;
                str_idx += 1;
            },
        }
    }
}

fn parseClass(pattern: []const u8, start: usize, ch: u8) ClassResult {
    var idx = start;
    var inverted = false;
    if (idx < pattern.len and pattern[idx] == '!') {
        inverted = true;
        idx += 1;
    }
    if (idx >= pattern.len) return .{ .valid = false };

    var matched = false;
    var a = pattern[idx];
    idx += 1;

    while (true) {
        var b = a;
        if (idx < pattern.len and pattern[idx] == '-' and (idx + 1 >= pattern.len or pattern[idx + 1] != ']')) {
            if (idx + 1 >= pattern.len) return .{ .valid = false };
            b = pattern[idx + 1];
            idx += 2;
        }

        if (a <= ch and ch <= b) matched = true;
        if (idx >= pattern.len) return .{ .valid = false };
        a = pattern[idx];
        idx += 1;
        if (a == ']') break;
    }

    return .{ .valid = true, .matched = matched != inverted, .next = idx };
}

test "globMatch handles wildcards and whole-string matching" {
    try std.testing.expect(globMatch("*.zig", "phase16.zig"));
    try std.testing.expect(globMatch("file-??", "file-ab"));
    try std.testing.expect(globMatch("*aaaaa", "aaaaaaaaaa"));
    try std.testing.expect(!globMatch("*.zig", "phase16.c"));
    try std.testing.expect(!globMatch("file-??", "file-a"));
}

test "globMatch handles classes inversion ranges and escaping" {
    try std.testing.expect(globMatch("dev[0-9]", "dev7"));
    try std.testing.expect(globMatch("dev[!a-z]", "dev7"));
    try std.testing.expect(!globMatch("dev[!0-9]", "dev7"));
    try std.testing.expect(globMatch("literal\\*", "literal*"));
    try std.testing.expect(globMatch("[]]", "]"));
}

test "malformed opening bracket is matched literally" {
    try std.testing.expect(globMatch("[abc", "[abc"));
    try std.testing.expect(!globMatch("[abc", "a"));
}
