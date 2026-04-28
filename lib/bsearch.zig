// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub fn Comparator(comptime Key: type, comptime T: type) type {
    return *const fn (*const Key, *const T) i32;
}

pub fn searchIndex(
    comptime Key: type,
    comptime T: type,
    key: *const Key,
    items: []const T,
    compare: Comparator(Key, T),
) ?usize {
    var base: usize = 0;
    var num = items.len;

    while (num > 0) {
        const pivot_index = base + (num >> 1);
        const pivot: *const T = &items[pivot_index];
        const result = compare(key, pivot);

        if (result == 0) {
            return pivot_index;
        }
        if (result > 0) {
            base = pivot_index + 1;
            num -= 1;
        }
        num >>= 1;
    }

    return null;
}

pub fn search(
    comptime Key: type,
    comptime T: type,
    key: *const Key,
    items: []const T,
    compare: Comparator(Key, T),
) ?*const T {
    const index = searchIndex(Key, T, key, items, compare) orelse return null;
    return &items[index];
}

pub fn searchMutable(
    comptime Key: type,
    comptime T: type,
    key: *const Key,
    items: []T,
    compare: Comparator(Key, T),
) ?*T {
    const index = searchIndex(Key, T, key, items, compare) orelse return null;
    return &items[index];
}

fn compareInt(key: *const i32, item: *const i32) i32 {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDescendingInt(key: *const i32, item: *const i32) i32 {
    return compareInt(item, key);
}

var counted_compare_calls: usize = 0;

fn compareCountedInt(key: *const i32, item: *const i32) i32 {
    counted_compare_calls += 1;
    return compareInt(key, item);
}

const Entry = struct {
    name: []const u8,
    value: u32,
};

fn compareName(key: *const []const u8, item: *const Entry) i32 {
    return switch (std.mem.order(u8, key.*, item.name)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

test "searchIndex finds values at the beginning middle and end of a sorted slice" {
    const values = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };

    try std.testing.expectEqual(@as(?usize, 0), searchIndex(i32, i32, &@as(i32, 2), values[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, 3), searchIndex(i32, i32, &@as(i32, 11), values[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, 6), searchIndex(i32, i32, &@as(i32, 42), values[0..], compareInt));
}

test "searchIndex returns null for empty slices and missing values" {
    const values = [_]i32{ 3, 5, 8, 13, 21 };
    const empty = [_]i32{};

    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 8), empty[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 1), values[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 9), values[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 34), values[0..], compareInt));
}

test "searchIndex handles singleton slices without widening the contract" {
    const singleton = [_]i32{21};

    try std.testing.expectEqual(@as(?usize, 0), searchIndex(i32, i32, &@as(i32, 21), singleton[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 20), singleton[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 22), singleton[0..], compareInt));
}

test "search returns a pointer to the matching element" {
    const values = [_]i32{ 5, 9, 12, 18, 27 };
    const found = search(i32, i32, &@as(i32, 18), values[0..], compareInt) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(i32, 18), found.*);
    try std.testing.expectEqual(@intFromPtr(&values[3]), @intFromPtr(found));
}

test "searchMutable returns a writable pointer to the matching element" {
    var values = [_]i32{ 5, 9, 12, 18, 27 };
    const found = searchMutable(i32, i32, &@as(i32, 18), values[0..], compareInt) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@intFromPtr(&values[3]), @intFromPtr(found));
    found.* = 19;
    try std.testing.expectEqual(@as(i32, 19), values[3]);
}

test "search and searchMutable keep singleton and empty slices on the found-or-null boundary" {
    const empty = [_]i32{};
    var singleton = [_]i32{21};

    const found = search(i32, i32, &@as(i32, 21), singleton[0..], compareInt) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@intFromPtr(&singleton[0]), @intFromPtr(found));

    const found_mutable = searchMutable(i32, i32, &@as(i32, 21), singleton[0..], compareInt) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@intFromPtr(&singleton[0]), @intFromPtr(found_mutable));
    found_mutable.* = 22;
    try std.testing.expectEqual(@as(i32, 22), singleton[0]);

    try std.testing.expect(search(i32, i32, &@as(i32, 21), empty[0..], compareInt) == null);
    try std.testing.expect(searchMutable(i32, i32, &@as(i32, 21), singleton[0..0], compareInt) == null);
}

test "search accepts duplicate keys without claiming stable selection" {
    const values = [_]i32{ 1,²H†@Lƒ„–çB’“°¢G'’7FBçFW7F–æræW‡V7B†6÷VçFVEö6ö×&Uö6ÆÇ2ÃÒB“° ¢6÷VçFVEö6ö×&Uö6ÆÇ2Ò°¢G'’7FBçFW7F–æræW‡V7DWVÂ„2ƒ÷W6—¦RÂçVÆÂ’Â6V&6„–æFW‚†“3"Â“3"Âd2†“3"ÂSr’ÂfÇVW5³âåÒÂ6ö×&T6÷VçFVD–çB’“°¢G'’7FBçFW7F–æræW‡V7B†6÷VçFVEö6ö×&Uö6ÆÇ2ÃÒB“° ¢6÷VçFVEö6ö×&Uö6ÆÇ2Ò°¢G'’7FBçFW7F–æræW‡V7DWVÂ„2ƒ÷W6—¦RÂçVÆÂ’Â6V&6„–æFW‚†“3"Â“3"Âd2†“3"Â3’ÂfÇVW5³âåÒÂ6ö×&T6÷VçFVD–çB’“°¢G'’7FBçFW7F–æræW‡V7B†6÷VçFVEö6ö×&Uö6ÆÇ2ÃÒB“°§Ğ §FW7B'6V&6‚7W÷'G2†WFW&övVæV÷W2¶W—2F‡&÷Vv‚F†R6ö×&F÷""°¢6öç7BVçG&–W2ÒµõÔVçG'—°¢ç²ææÖRÒ&Ç†"ÂçfÇVRÒÒÀ¢ç²ææÖRÒ&&WF"ÂçfÇVRÒ"ÒÀ¢ç²ææÖRÒ&FVÇF"ÂçfÇVRÒBÒÀ¢ç²ææÖRÒ&öÖVv"ÂçfÇVRÒ#BÒÀ¢Ó° ¢6öç7B&WFÒ6V&6‚…µÖ6öç7BS‚ÂVçG'’Âd2…µÖ6öç7BS‚Â&&WF"’ÂVçG&–W5³âåÒÂ6ö×&TæÖR’÷&VÇ6R&WGW&âW'&÷"åFW7EVæW‡V7FVE&W7VÇC°¢G'’7FBçFW7F–æræW‡V7DWVÂ„2‡S3"Â"’Â&WFçfÇVR“°¢G'’7FBçFW7F–æræW‡V7B‡6V&6‚…µÖ6öç7BS‚ÂVçG'’Âd2…µÖ6öç7BS‚Â&vÖÖ"’ÂVçG&–W5³âåÒÂ6ö×&TæÖR’ÓÒçVÆÂ“°§Ğ §FW7B'6V&6‚66WG2'VçF–ÖR×6VÆV7FVB6ö×&F÷"gVæ7F–öâö–çFW'2"°¢6öç7B66VæF–ærÒµõÖ“3'²"ÂBÂrÂÂbÂ#2ÂC"Ó°¢6öç7BFW66VæF–ærÒµõÖ“3'²C"Â#2ÂbÂÂrÂBÂ"Ó°¢6öç7B6ö×&F÷'2ÒµõÔ6ö×&F÷"†“3"Â“3"—²6ö×&T–çBÂ6ö×&TFW66VæF–æt–çBÓ°¢6öç7B6Æ–6W2ÒµõÕµÖ6öç7B“3'²66VæF–æu³âåÒÂFW66VæF–æu³âåÒÓ°¢6öç7BF&vWG2ÒµõÖ“3'²#2ÂrÓ° ¢f÷"†6ö×&F÷'2Â6Æ–6W2ÂF&vWG2’Æ6ö×&RÂ—FV×2ÂF&vWGÂ°¢6öç7Bf÷VæBÒ6V&6‚†“3"Â“3"ÂgF&vWBÂ—FV×2Â6ö×&R’÷&VÇ6R&WGW&âW'&÷"åFW7EVæW‡V7FVE&W7VÇC°¢G'’7FBçFW7F–æræW‡V7DWVÂ‡F&vWBÂf÷VæBâ¢“°¢Ğ§Ğ 