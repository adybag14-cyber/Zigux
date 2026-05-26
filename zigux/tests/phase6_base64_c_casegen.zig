const std = @import("std");
const shared = @import("fixtures/phase6_base64_vectors.zig");
const parity = @import("fixtures/phase6_base64_c_parity_vectors.zig");

fn variantCaseByNameAndInput(name: []const u8, padding: bool, input: []const u8) ?shared.VariantCase {
    for (shared.variant_cases) |case| {
        if (std.mem.eql(u8, name, case.variant_name) and case.padding == padding and std.mem.eql(u8, input, case.input)) {
            return case;
        }
    }
    return null;
}

fn standardCaseByInputAndPadding(input: []const u8, padding: bool) ?shared.EncodeCase {
    for (shared.standard_cases) |case| {
        if (case.padding == padding and std.mem.eql(u8, input, case.input)) {
            return case;
        }
    }
    return null;
}

fn decodeCaseByInputAndVariant(input: []const u8, padding: bool, name: []const u8) ?shared.DecodeCase {
    for (shared.standard_decode_cases) |case| {
        if (case.padding == padding and std.mem.eql(u8, name, case.variant_name) and std.mem.eql(u8, input, case.input)) {
            return case;
        }
    }
    for (shared.variant_decode_cases) |case| {
        if (case.padding == padding and std.mem.eql(u8, name, case.variant_name) and std.mem.eql(u8, input, case.input)) {
            return case;
        }
    }
    return null;
}

fn appendHex(list: *std.ArrayList(u8), allocator: std.mem.Allocator, bytes: []const u8) !void {
    const hex = "0123456789abcdef";
    for (bytes) |byte| {
        try list.append(allocator, hex[byte >> 4]);
        try list.append(allocator, hex[byte & 0x0f]);
    }
}

fn appendCaseLine(list: *std.ArrayList(u8), allocator: std.mem.Allocator, prefix: []const u8, variant_name: []const u8, padding: bool, lhs: []const u8, rhs: []const u8) !void {
    try list.appendSlice(allocator, prefix);
    try list.append(allocator, '\t');
    try list.appendSlice(allocator, variant_name);
    try list.append(allocator, '\t');
    try list.append(allocator, if (padding) '1' else '0');
    try list.append(allocator, '\t');
    try appendHex(list, allocator, lhs);
    try list.append(allocator, '\t');
    try appendHex(list, allocator, rhs);
    try list.append(allocator, '\n');
}

fn appendInvalidLine(list: *std.ArrayList(u8), allocator: std.mem.Allocator, variant_name: []const u8, padding: bool, input: []const u8) !void {
    try list.appendSlice(allocator, "inv");
    try list.append(allocator, '\t');
    try list.appendSlice(allocator, variant_name);
    try list.append(allocator, '\t');
    try list.append(allocator, if (padding) '1' else '0');
    try list.append(allocator, '\t');
    try appendHex(list, allocator, input);
    try list.appendSlice(allocator, "\tInvalidInput\tInvalidInput\n");
}

pub fn generate(allocator: std.mem.Allocator) ![]u8 {
    try parity.validate();
    var lines = try std.ArrayList(u8).initCapacity(allocator, 512);
    errdefer lines.deinit(allocator);

    for (parity.encode_cases) |case| {
        if (std.mem.eql(u8, case.variant_name, "std")) {
            const standard = standardCaseByInputAndPadding(case.input, case.padding) orelse return error.MissingCase;
            try appendCaseLine(&lines, allocator, "enc", case.variant_name, case.padding, case.input, standard.expected);
        } else {
            const variant = variantCaseByNameAndInput(case.variant_name, case.padding, case.input) orelse return error.MissingCase;
            try appendCaseLine(&lines, allocator, "enc", case.variant_name, case.padding, case.input, variant.expected);
        }
    }

    for (parity.decode_cases) |case| {
        const decode_case = decodeCaseByInputAndVariant(case.input, case.padding, case.variant_name) orelse return error.MissingCase;
        try appendCaseLine(&lines, allocator, "dec", case.variant_name, case.padding, case.input, decode_case.expected);
    }

    for (parity.invalid_cases) |case| {
        try appendInvalidLine(&lines, allocator, case.variant_name, case.padding, case.input);
    }

    return lines.toOwnedSlice(allocator);
}

pub fn main() !void {
    const output = try generate(std.heap.page_allocator);
    defer std.heap.page_allocator.free(output);
    try std.io.getStdOut().writeAll(output);
}

test "phase 6 base64 c casegen emits the bounded 40-line parity packet" {
    const output = try generate(std.testing.allocator);
    defer std.testing.allocator.free(output);

    var line_count: usize = 0;
    var it = std.mem.splitScalar(u8, output, '\n');
    while (it.next()) |line| {
        if (line.len != 0) {
            line_count += 1;
        }
    }

    try std.testing.expectEqual(@as(usize, 40), line_count);
    try std.testing.expect(std.mem.startsWith(u8, output, "enc\tstd\t1\t\t\n"));
    try std.testing.expect(std.mem.indexOf(u8, output, "enc\turlsafe\t0\t00fbff7f80\t4150765f663441\n") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "dec\timap\t0\t2c2c41\tfff0\n") != null);
    try std.testing.expect(std.mem.endsWith(u8, output, "inv\timap\t0\t5a673d3d\tInvalidInput\tInvalidInput\n"));
}
