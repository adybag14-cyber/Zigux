const std = @import("std");
const binding = @import("bitmap_cpumask_binding");
const bitmap = @import("bitmap_view_helper");

pub const Word = bitmap.Word;

pub fn viewFromWords(backing: []const Word, nr_cpu_ids: u32) binding.CpumaskView {
    std.debug.assert(backing.len == bitmap.wordCount(nr_cpu_ids));
    return binding.initCpumaskView(
        if (backing.len == 0) 0 else @intFromPtr(backing.ptr),
        nr_cpu_ids,
        @intCast(backing.len),
        nr_cpu_ids,
    );
}

pub fn isValid(view: binding.CpumaskView) bool {
    if (view.nr_cpu_ids != view.nbits) return false;
    if (view.reserved != 0) return false;
    return bitmap.isValid(binding.asBitmap(view));
}

pub fn cpuIsSet(view: binding.CpumaskView, cpu: u32) bool {
    if (!isValid(view)) return false;
    return bitmap.testBit(binding.asBitmap(view), cpu);
}

pub fn firstCpu(view: binding.CpumaskView) u32 {
    if (!isValid(view)) return 0;
    return bitmap.firstSet(binding.asBitmap(view));
}

pub fn firstAbsentCpu(view: binding.CpumaskView) u32 {
    if (!isValid(view)) return 0;
    return bitmap.firstZero(binding.asBitmap(view));
}

pub fn weight(view: binding.CpumaskView) u32 {
    if (!isValid(view)) return 0;
    return bitmap.weight(binding.asBitmap(view));
}

pub fn summarize(view: binding.CpumaskView) binding.BitmapSummary {
    if (!isValid(view)) return binding.initBitmapSummary(0, 0, 0);
    return bitmap.summarize(binding.asBitmap(view));
}

test "cpumask view helpers keep cpu windows reviewable" {
    var backing = [_]Word{
        (@as(Word, 1) << 0) | (@as(Word, 1) << 2) | (@as(Word, 1) << 7),
    };
    const view = viewFromWords(backing[0..], 16);
    const summary = summarize(view);

    try std.testing.expect(isValid(view));
    try std.testing.expect(cpuIsSet(view, 0));
    try std.testing.expect(cpuIsSet(view, 7));
    try std.testing.expect(!cpuIsSet(view, 1));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(view));
    try std.testing.expectEqual(@as(u32, 1), firstAbsentCpu(view));
    try std.testing.expectEqual(@as(u32, 3), weight(view));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 3), summary.weight);
}

test "cpumask helpers keep an all-clear bounded window distinct from the empty sentinel" {
    var backing = [_]Word{0};
    const view = viewFromWords(backing[0..], 16);
    const summary = summarize(view);

    try std.testing.expect(isValid(view));
    try std.testing.expect(!cpuIsSet(view, 0));
    try std.testing.expect(!cpuIsSet(view, 15));
    try std.testing.expectEqual(@as(u32, 16), firstCpu(view));
    try std.testing.expectEqual(@as(u32, 0), firstAbsentCpu(view));
    try std.testing.expectEqual(@as(u32, 0), weight(view));
    try std.testing.expectEqual(@as(u32, 16), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask helpers track cross-word cpu windows without leaking tail bits" {
    var backing = [_]Word{
        (@as(Word, 1) << 5) | (@as(Word, 1) << (bitmap.bits_per_word - 1)),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 6) | (@as(Word, 1) << 10),
    };
    const view = viewFromWords(backing[0..], bitmap.bits_per_word + 11);
    const summary = summarize(view);

    try std.testing.expect(isValid(view));
    try std.testing.expect(cpuIsSet(view, 5));
    try std.testing.expect(cpuIsSet(view, bitmap.bits_per_word - 1));
    try std.testing.expect(cpuIsSet(view, bitmap.bits_per_word + 10));
    try std.testing.expect(!cpuIsSet(view, bitmap.bits_per_word + 11));
    try std.testing.expectEqual(@as(u32, 5), firstCpu(view));
    try std.testing.expectEqual(@as(u32, 0), firstAbsentCpu(view));
    try std.testing.expectEqual(@as(u32, 5), weight(view));
    try std.testing.expectEqual(@as(u32, 5), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 5), summary.weight);
}

test "cpumask tail masking keeps a full bounded mask from leaking absent cpus" {
    var backing = [_]Word{
        ~@as(Word, 0),
        bitmap.lastWordMask(bitmap.bits_per_word + 11),
    };
    const view = viewFromWords(backing[0..], bitmap.bits_per_word + 11);
    const summary = summarize(view);

    try std.testing.expect(isValid(view));
    try std.testing.expect(cpuIsSet(view, bitmap.bits_per_word + 10));
    try std.testing.expect(!cpuIsSet(view, bitmap.bits_per_word + 11));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(view));
    try std.testing.expectEqual(bitmap.bits_per_word + 11, firstAbsentCpu(view));
    try std.testing.expectEqual(bitmap.bits_per_word + 11, weight(view));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(bitmap.bits_per_word + 11, summary.first_zero);
    try std.testing.expectEqual(bitmap.bits_per_word + 11, summary.weight);
}

test "cpumask tail masking ignores out-of-range set bits in the last word" {
    var backing = [_]Word{
        0,
        @as(Word, 1) << (11 + 3),
    };
    const view = viewFromWords(backing[0..], bitmap.bits_per_word + 11);
    const summary = summarize(view);

    try std.testing.expect(isValid(view));
    try std.testing.expect(!cpuIsSet(view, bitmap.bits_per_word + 10));
    try std.testing.expect(!cpuIsSet(view, bitmap.bits_per_word + 11));
    try std.testing.expectEqual(bitmap.bits_per_word + 11, firstCpu(view));
    try std.testing.expectEqual(@as(u32, 0), firstAbsentCpu(view));
    try std.testing.expectEqual(@as(u32, 0), weight(view));
    try std.testing.expectEqual(bitmap.bits_per_word + 11, summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask exact-word windows keep full-word masks explicit" {
    var backing = [_]Word{
        ~@as(Word, 0),
        (@as(Word, 1) << 5),
    };
    const view = viewFromWords(backing[0..], bitmap.bits_per_word * 2);
    const summary = summarize(view);

    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(~@as(Word, 0), bitmap.lastWordMask(bitmap.bits_per_word * 2));
    try std.testing.expect(cpuIsSet(view, bitmap.bits_per_word + 5));
    try std.testing.expect(!cpuIsSet(view, bitmap.bits_per_word + 6));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(view));
    try std.testing.expectEqual(bitmap.bits_per_word, firstAbsentCpu(view));
    try std.testing.expectEqual(bitmap.bits_per_word + 1, weight(view));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(bitmap.bits_per_word, summary.first_zero);
    try std.testing.expectEqual(bitmap.bits_per_word + 1, summary.weight);
}

test "cpumask full tail-masked windows project to bitmap windows unchanged" {
    var backing = [_]Word{
        ~@as(Word, 0),
        bitmap.lastWordMask(bitmap.bits_per_word + 11),
    };
    const view = viewFromWords(backing[0..], bitmap.bits_per_word + 11);
    const projected = binding.asBitmap(view);
    const cpumask_summary = summarize(view);
    const bitmap_summary = bitmap.summarize(projected);

    try std.testing.expect(isValid(view));
    try std.testing.expect(bitmap.isValid(projected));
    try std.testing.expectEqual(view.words_addr, projected.words_addr);
    try std.testing.expectEqual(view.nbits, projected.nbits);
    try std.testing.expectEqual(view.word_count, projected.word_count);
    try std.testing.expectEqual(
        cpuIsSet(view, bitmap.bits_per_word + 10),
        bitmap.testBit(projected, bitmap.bits_per_word + 10),
    );
    try std.testing.expectEqual(
        cpuIsSet(view, bitmap.bits_per_word + 11),
        bitmap.testBit(projected, bitmap.bits_per_word + 11),
    );
    try std.testing.expectEqual(firstCpu(view), bitmap.firstSet(projected));
    try std.testing.expectEqual(firstAbsentCpu(view), bitmap.firstZero(projected));
    try std.testing.expectEqual(weight(view), bitmap.weight(projected));
    try std.testing.expectEqual(cpumask_summary.first_set, bitmap_summary.first_set);
    try std.testing.expectEqual(cpumask_summary.first_zero, bitmap_summary.first_zero);
    try std.testing.expectEqual(cpumask_summary.weight, bitmap_summary.weight);
    try std.testing.expectEqual(cpumask_summary.reserved, bitmap_summary.reserved);
}

test "cpumask word counts stay predictable for large bounded windows" {
    const max_nbits = std.math.maxInt(u32);
    const expected = bitmap.wordCount(max_nbits);
    const invalid = binding.initCpumaskView(1, max_nbits, expected - 1, max_nbits);
    const summary = summarize(invalid);

    try std.testing.expectEqual(expected, bitmap.wordCount(max_nbits));
    try std.testing.expect(!isValid(invalid));
    try std.testing.expect(!cpuIsSet(invalid, 0));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(invalid));
    try std.testing.expectEqual(@as(u32, 0), firstAbsentCpu(invalid));
    try std.testing.expectEqual(@as(u32, 0), weight(invalid));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask validity rejects non-empty views without backing storage" {
    const invalid = binding.initCpumaskView(0, 1, 1, 1);
    const summary = summarize(invalid);

    try std.testing.expect(!isValid(invalid));
    try std.testing.expect(!cpuIsSet(invalid, 0));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(invalid));
    try std.testing.expectEqual(@as(u32, 0), firstAbsentCpu(invalid));
    try std.testing.expectEqual(@as(u32, 0), weight(invalid));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask validity rejects malformed word counts and closes helpers" {
    const invalid = binding.initCpumaskView(0, bitmap.bits_per_word + 1, 1, bitmap.bits_per_word + 1);
    const summary = summarize(invalid);

    try std.testing.expect(!isValid(invalid));
    try std.testing.expect(!cpuIsSet(invalid, 0));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(invalid));
    try std.testing.expectEqual(@as(u32, 0), firstAbsentCpu(invalid));
    try std.testing.expectEqual(@as(u32, 0), weight(invalid));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask validity rejects zero-bit stray storage and closes helpers" {
    const invalid = binding.initCpumaskView(1, 0, 1, 0);
    const summary = summarize(invalid);

    try std.testing.expect(!isValid(invalid));
    try std.testing.expect(!cpuIsSet(invalid, 0));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(invalid));
    try std.testing.expectEqual(@as(u32, 0), firstAbsentCpu(invalid));
    try std.testing.expectEqual(@as(u32, 0), weight(invalid));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask empty sentinels stay stable even with a stray non-zero address" {
    const empty = binding.initCpumaskView(1, 0, 0, 0);
    const summary = summarize(empty);

    try std.testing.expect(isValid(empty));
    try std.testing.expect(!cpuIsSet(empty, 0));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(empty));
    try std.testing.expectEqual(@as(u32, 0), firstAbsentCpu(empty));
    try std.testing.expectEqual(@as(u32, 0), weight(empty));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask validity rejects non-zero reserved bytes and closes helpers" {
    var backing = [_]Word{@as(Word, 1) << 3};
    var invalid = viewFromWords(backing[0..], 8);
    invalid.reserved = 1;
    const projected = binding.asBitmap(invalid);
    const summary = summarize(invalid);

    try std.testing.expect(bitmap.isValid(projected));
    try std.testing.expect(bitmap.testBit(projected, 3));
    try std.testing.expect(!isValid(invalid));
    try std.testing.expect(!cpuIsSet(invalid, 3));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(invalid));
    try std.testing.expectEqual(@as(u32, 0), firstAbsentCpu(invalid));
    try std.testing.expectEqual(@as(u32, 0), weight(invalid));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
    try std.testing.expectEqual(@as(u32, 0), summary.reserved);
}

test "cpumask summaries keep reserved bytes zero for valid and invalid views" {
    var backing = [_]Word{
        (@as(Word, 1) << 0) | (@as(Word, 1) << 2),
    };
    const valid = summarize(viewFromWords(backing[0..], 8));
    const invalid = summarize(binding.initCpumaskView(0, bitmap.bits_per_word + 1, 1, bitmap.bits_per_word + 1));

    try std.testing.expectEqual(@as(u32, 0), valid.first_set);
    try std.testing.expectEqual(@as(u32, 1), valid.first_zero);
    try std.testing.expectEqual(@as(u32, 2), valid.weight);
    try std.testing.expectEqual(@as(u32, 0), valid.reserved);

    try std.testing.expectEqual(@as(u32, 0), invalid.first_set);
    try std.testing.expectEqual(@as(u32, 0), invalid.first_zero);
    try std.testing.expectEqual(@as(u32, 0), invalid.weight);
    try std.testing.expectEqual(@as(u32, 0), invalid.reserved);
}

test "cpumask projection stays aligned with bitmap helpers on bounded windows" {
    var backing = [_]Word{
        (@as(Word, 1) << 5) | (@as(Word, 1) << (bitmap.bits_per_word - 1)),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 6) | (@as(Word, 1) << 10),
    };
    const view = viewFromWords(backing[0..], bitmap.bits_per_word + 11);
    const projected = binding.asBitmap(view);
    const cpumask_summary = summarize(view);
    const bitmap_summary = bitmap.summarize(projected);

    try std.testing.expect(isValid(view));
    try std.testing.expect(bitmap.isValid(projected));
    try std.testing.expectEqual(firstCpu(view), bitmap.firstSet(projected));
    try std.testing.expectEqual(firstAbsentCpu(view), bitmap.firstZero(projected));
    try std.testing.expectEqual(weight(view), bitmap.weight(projected));
    try std.testing.expectEqual(cpumask_summary.first_set, bitmap_summary.first_set);
    try std.testing.expectEqual(cpumask_summary.first_zero, bitmap_summary.first_zero);
    try std.testing.expectEqual(cpumask_summary.weight, bitmap_summary.weight);
    try std.testing.expectEqual(cpumask_summary.reserved, bitmap_summary.reserved);
}

test "cpumask empty sentinels project to bitmap empty sentinels unchanged" {
    const empty = binding.initCpumaskView(1, 0, 0, 0);
    const projected = binding.asBitmap(empty);
    const cpumask_summary = summarize(empty);
    const bitmap_summary = bitmap.summarize(projected);

    try std.testing.expect(isValid(empty));
    try std.testing.expect(bitmap.isValid(projected));
    try std.testing.expectEqual(firstCpu(empty), bitmap.firstSet(projected));
    try std.testing.expectEqual(firstAbsentCpu(empty), bitmap.firstZero(projected));
    try std.testing.expectEqual(weight(empty), bitmap.weight(projected));
    try std.testing.expectEqual(cpumask_summary.first_set, bitmap_summary.first_set);
    try std.testing.expectEqual(cpumask_summary.first_zero, bitmap_summary.first_zero);
    try std.testing.expectEqual(cpumask_summary.weight, bitmap_summary.weight);
    try std.testing.expectEqual(cpumask_summary.reserved, bitmap_summary.reserved);
}

test "cpumask view empty sentinel behavior stays explicit" {
    const empty = viewFromWords(&.{}, 0);
    const summary = summarize(empty);

    try std.testing.expect(isValid(empty));
    try std.testing.expect(!cpuIsSet(empty, 0));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(empty));
    try std.testing.expectEqual(@as(u32, 0), firstAbsentCpu(empty));
    try std.testing.expectEqual(@as(u32, 0), weight(empty));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask validity requires nr_cpu_ids to match the bounded bit count" {
    var backing = [_]Word{@as(Word, 1) << 4};
    var invalid = viewFromWords(backing[0..], 8);
    invalid.nr_cpu_ids = 7;
    const projected = binding.asBitmap(invalid);
    const summary = summarize(invalid);

    try std.testing.expect(bitmap.isValid(projected));
    try std.testing.expect(bitmap.testBit(projected, 4));
    try std.testing.expect(!isValid(invalid));
    try std.testing.expect(!cpuIsSet(invalid, 4));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(invalid));
    try std.testing.expectEqual(@as(u32, 0), firstAbsentCpu(invalid));
    try std.testing.expectEqual(@as(u32, 0), weight(invalid));
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}
