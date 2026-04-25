const std = @import("std");

pub const CmdName = struct {
    name: []u8,

    pub fn len(self: CmdName) usize {
        return self.name.len;
    }

    pub fn deinit(self: *CmdName, allocator: std.mem.Allocator) void {
        allocator.free(self.name);
        self.* = undefined;
    }
};

pub const CmdNames = struct {
    allocator: std.mem.Allocator,
    names: std.ArrayList(CmdName),

    pub fn init(allocator: std.mem.Allocator) CmdNames {
        return .{
            .allocator = allocator,
            .names = .empty,
        };
    }

    pub fn deinit(self: *CmdNames) void {
        for (self.names.items) |*entry| {
            entry.deinit(self.allocator);
        }
        self.names.deinit(self.allocator);
        self.* = undefined;
    }

    pub fn count(self: CmdNames) usize {
        return self.names.items.len;
    }

    pub fn addCmdName(self: *CmdNames, name: []const u8, len: usize) !void {
        if (len > name.len) {
            return error.InvalidCommandLength;
        }

        try self.names.append(self.allocator, .{
            .name = try self.allocator.dupe(u8, name[0..len]),
        });
    }

    pub fn sort(self: *CmdNames) void {
        std.mem.sort(CmdName, self.names.items, {}, lessThan);
    }

    pub fn uniq(self: *CmdNames) void {
        if (self.names.items.len == 0) {
            return;
        }

        var write_index: usize = 1;
        var read_index: usize = 1;
        while (read_index < self.names.items.len) : (read_index += 1) {
            const previous = &self.names.items[write_index - 1];
            const current = &self.names.items[read_index];
            if (std.mem.eql(u8, previous.name, current.name)) {
                current.deinit(self.allocator);
                continue;
            }

            if (write_index != read_index) {
                self.names.items[write_index] = current.*;
            }
            write_index += 1;
        }

        self.names.shrinkRetainingCapacity(write_index);
    }

    pub fn excludeCmds(self: *CmdNames, excludes: CmdNames) void {
        if (self.names.items.len == 0 or excludes.names.items.len == 0) {
            return;
        }

        var write_index: usize = 0;
        var read_index: usize = 0;
        var exclude_index: usize = 0;

        while (read_index < self.names.items.len and exclude_index < excludes.names.items.len) {
            const ordering = std.mem.order(u8, self.names.items[read_index].name, excludes.names.items[exclude_index].name);
            switch (ordering) {
                .lt => {
                    if (write_index != read_index) {
                        self.names.items[write_index] = self.names.items[read_index];
                    }
                    write_index += 1;
                    read_index += 1;
                },
                .eq => {
                    self.names.items[read_index].deinit(self.allocator);
                    read_index += 1;
                    exclude_index += 1;
                },
                .gt => exclude_index += 1,
            }
        }

        while (read_index < self.names.items.len) : (read_index += 1) {
            if (write_index != read_index) {
                self.names.items[write_index] = self.names.items[read_index];
            }
            write_index += 1;
        }

        self.names.shrinkRetainingCapacity(write_index);
    }

    pub fn isInCmdList(self: CmdNames, name: []const u8) bool {
        for (self.names.items) |entry| {
            if (std.mem.eql(u8, entry.name, name)) {
                return true;
            }
        }
        return false;
    }

    pub fn longestNameLen(self: CmdNames) usize {
        var longest: usize = 0;
        for (self.names.items) |entry| {
            longest = @max(longest, entry.len());
        }
        return longest;
    }
};

fn lessThan(_: void, lhs: CmdName, rhs: CmdName) bool {
    return std.mem.order(u8, lhs.name, rhs.name) == .lt;
}

pub const PrettyPrintLayout = struct {
    cols: usize,
    rows: usize,
    spacing: usize,
};

pub fn planPrettyPrint(count: usize, longest: usize, terminal_cols: usize) PrettyPrintLayout {
    const spacing = longest + 1;
    if (count == 0) {
        return .{
            .cols = 1,
            .rows = 0,
            .spacing = spacing,
        };
    }

    var cols: usize = 1;
    const max_cols = if (terminal_cols > 0) terminal_cols - 1 else 0;
    if (spacing < max_cols and spacing != 0) {
        cols = max_cols / spacing;
        if (cols == 0) {
            cols = 1;
        }
    }

    return .{
        .cols = cols,
        .rows = std.math.divCeil(usize, count, cols) catch unreachable,
        .spacing = spacing,
    };
}

test "addCmdName owns a copied slice and preserves the requested length" {
    var cmds = CmdNames.init(std.testing.allocator);
    defer cmds.deinit();

    var backing = [_]u8{ 's', 't', 'a', 't', 'u', 's' };
    try cmds.addCmdName(&backing, 4);
    backing[0] = 'x';

    try std.testing.expectEqual(@as(usize, 1), cmds.count());
    try std.testing.expectEqualStrings("stat", cmds.names.items[0].name);
    try std.testing.expectEqual(@as(usize, 4), cmds.names.items[0].len());
}

test "uniq removes adjacent duplicates after sorting" {
    var cmds = CmdNames.init(std.testing.allocator);
    defer cmds.deinit();

    try cmds.addCmdName("test", 4);
    try cmds.addCmdName("annotate", 8);
    try cmds.addCmdName("test", 4);
    try cmds.addCmdName("bench", 5);

    cmds.sort();
    cmds.uniq();

    try std.testing.expectEqual(@as(usize, 3), cmds.count());
    try std.testing.expectEqualStrings("annotate", cmds.names.items[0].name);
    try std.testing.expectEqualStrings("bench", cmds.names.items[1].name);
    try std.testing.expectEqualStrings("test", cmds.names.items[2].name);
}

test "excludeCmds removes matching sorted commands without disturbing survivors" {
    var cmds = CmdNames.init(std.testing.allocator);
    defer cmds.deinit();
    try cmds.addCmdName("annotate", 8);
    try cmds.addCmdName("bench", 5);
    try cmds.addCmdName("test", 4);
    cmds.sort();

    var excludes = CmdNames.init(std.testing.allocator);
    defer excludes.deinit();
    try excludes.addCmdName("bench", 5);
    try excludes.addCmdName("trace", 5);
    excludes.sort();

    cmds.excludeCmds(excludes);

    try std.testing.expectEqual(@as(usize, 2), cmds.count());
    try std.testing.expectEqualStrings("annotate", cmds.names.items[0].name);
    try std.testing.expectEqualStrings("test", cmds.names.items[1].name);
}

test "membership and longest-name helpers stay aligned with the stored list" {
    var cmds = CmdNames.init(std.testing.allocator);
    defer cmds.deinit();
    try cmds.addCmdName("report", 6);
    try cmds.addCmdName("sched", 5);

    try std.testing.expect(cmds.isInCmdList("report"));
    try std.testing.expect(!cmds.isInCmdList("record"));
    try std.testing.expectEqual(@as(usize, 6), cmds.longestNameLen());
}

test "pretty-print layout follows the same column math as help.c" {
    const layout = planPrettyPrint(5, 7, 33);
    try std.testing.expectEqual(@as(usize, 4), layout.cols);
    try std.testing.expectEqual(@as(usize, 2), layout.rows);
    try std.testing.expectEqual(@as(usize, 8), layout.spacing);

    const empty = planPrettyPrint(0, 5, 20);
    try std.testing.expectEqual(@as(usize, 1), empty.cols);
    try std.testing.expectEqual(@as(usize, 0), empty.rows);
    try std.testing.expectEqual(@as(usize, 6), empty.spacing);
}
