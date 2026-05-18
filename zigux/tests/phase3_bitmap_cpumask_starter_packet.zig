const std = @import("std");
const testing = std.testing;

const binding = @import("bitmap_cpumask_binding");
const bitmap_view = @import("bitmap_view_helper");
const cpumask_view = @import("cpumask_view_helper");
const version = @import("uapi_version");

test "bitmap cpumask starter binding preserves the helper-local layout" {
    try testing.expectEqual(@as(u32, 1), binding.bitmap_view_abi_version);
    try testing.expectEqual(@as(u32, 1), binding.bitmap_summary_abi_version);
    try testing.expectEqual(@as(u32, 1), binding.cpumask_view_abi_version);

    try testing.expectEqual(@as(usize, 0), binding.bitmap_view_words_addr_offset);
    try testing.expectEqual(@as(usize, @sizeOf(usize)), binding.bitmap_view_nbits_offset);
    try testing.expectEqual(@as(usize, @sizeOf(usize) + 4), binding.bitmap_view_word_count_offset);

    try testing.expectEqual(@as(usize, 0), binding.bitmap_summary_first_set_offset);
    try testing.expectEqual(@as(usize, 4), binding.bitmap_summary_first_zero_offset);
    try testing.expectEqual(@as(usize, 8), binding.bitmap_summary_weight_offset);
    try testing.expectEqual(@as(usize, 12), binding.bitmap_summary_reserved_offset);

    try testing.expectEqual(@as(usize, 0), binding.cpumask_view_words_addr_offset);
    try testing.expectEqual(@as(usize, @sizeOf(usize)), binding.cpumask_view_nbits_offset);
    try testing.expectEqual(@as(usize, @sizeOf(usize) + 4), binding.cpumask_view_word_count_offset);
    try testing.expectEqual(@as(usize, @sizeOf(usize) + 8), binding.cpumask_view_nr_cpu_ids_offset);
    try testing.expectEqual(@as(usize, @sizeOf(usize) + 12), binding.cpumask_view_reserved_offset);
}

test "bitmap starter helpers keep first set first zero and weight aligned" {
    var backing = [_]usize{
        (@as(usize, 1) << 1) | (@as(usize, 1) << 3) | (@as(usize, 1) << 5),
        (@as(usize, 1) << 2),
    };
    const view = bitmap_view.viewFromWords(backing[0..], bitmap_view.bits_per_word + 6);
    const summary = bitmap_view.summarize(view);

    try testing.expect(bitmap_view.isValid(view));
    try testing.expect(bitmap_view.testBit(view, 3));
    try testing.expect(bitmap_view.testBit(view, bitmap_view.bits_per_word + 2));
    try testing.expect(!bitmap_view.testBit(view, 4));
    try testing.expect(!bitmap_view.testBit(view, bitmap_view.bits_per_word + 5));
    try testing.expectEqual(@as(u32, 1), summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 4), summary.weight);
}

test "bitmap starter helpers keep an all-clear bounded window distinct from the empty sentinel" {
    var backing = [_]usize{0};
    const view = bitmap_view.viewFromWords(backing[0..], 16);
    const summary = bitmap_view.summarize(view);

    try testing.expect(bitmap_view.isValid(view));
    try testing.expect(!bitmap_view.testBit(view, 0));
    try testing.expect(!bitmap_view.testBit(view, 15));
    try testing.expectEqual(@as(u32, 16), summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 0), summary.weight);
}

test "bitmap starter helpers keep a full bounded bitmap from leaking tail zeros" {
    var backing = [_]usize{
        ~@as(usize, 0),
        bitmap_view.lastWordMask(bitmap_view.bits_per_word + 11),
    };
    const view = bitmap_view.viewFromWords(backing[0..], bitmap_view.bits_per_word + 11);
    const summary = bitmap_view.summarize(view);

    try testing.expect(bitmap_view.isValid(view));
    try testing.expect(bitmap_view.testBit(view, bitmap_view.bits_per_word + 10));
    try testing.expect(!bitmap_view.testBit(view, bitmap_view.bits_per_word + 11));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(bitmap_view.bits_per_word + 11, summary.first_zero);
    try testing.expectEqual(bitmap_view.bits_per_word + 11, summary.weight);
}

test "bitmap starter helpers ignore out-of-range tail bits when no bounded bits are set" {
    var backing = [_]usize{
        0,
        @as(usize, 1) << (11 + 3),
    };
    const view = bitmap_view.viewFromWords(backing[0..], bitmap_view.bits_per_word + 11);
    const summary = bitmap_view.summarize(view);

    try testing.expect(bitmap_view.isValid(view));
    try testing.expect(!bitmap_view.testBit(view, bitmap_view.bits_per_word + 10));
    try testing.expect(!bitmap_view.testBit(view, bitmap_view.bits_per_word + 11));
    try testing.expectEqual(bitmap_view.bits_per_word + 11, summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 0), summary.weight);
}

test "bitmap starter helpers keep exact-word windows explicit" {
    var backing = [_]usize{
        ~@as(usize, 0),
        (@as(usize, 1) << 5),
    };
    const view = bitmap_view.viewFromWords(backing[0..], bitmap_view.bits_per_word * 2);
    const summary = bitmap_view.summarize(view);

    try testing.expect(bitmap_view.isValid(view));
    try testing.expectEqual(~@as(usize, 0), bitmap_view.lastWordMask(bitmap_view.bits_per_word * 2));
    try testing.expect(bitmap_view.testBit(view, bitmap_view.bits_per_word + 5));
    try testing.expect(!bitmap_view.testBit(view, bitmap_view.bits_per_word + 6));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(bitmap_view.bits_per_word, summary.first_zero);
    try testing.expectEqual(bitmap_view.bits_per_word + 1, summary.weight);
}

test "bitmap starter helpers keep large bounded word counts predictable" {
    const max_nbits = std.math.maxInt(u32);
    const expected: u32 = @intCast((@as(u64, max_nbits) + @as(u64, bitmap_view.bits_per_word) - 1) / @as(u64, bitmap_view.bits_per_word));
    const invalid = binding.initBitmapView(1, max_nbits, expected - 1);
    const summary = bitmap_view.summarize(invalid);

    try testing.expectEqual(expected, bitmap_view.wordCount(max_nbits));
    try testing.expect(!bitmap_view.isValid(invalid));
    try testing.expect(!bitmap_view.testBit(invalid, 0));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 0), summary.weight);
}

test "bitmap starter helpers fail closed on malformed views" {
    const invalid = binding.initBitmapView(0, bitmap_view.bits_per_word + 1, 1);
    const summary = bitmap_view.summarize(invalid);

    try testing.expect(!bitmap_view.isValid(invalid));
    try testing.expect(!bitmap_view.testBit(invalid, 0));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 0), summary.weight);
}

test "bitmap starter helpers fail closed on zero-bit stray storage" {
    const invalid = binding.initBitmapView(1, 0, 1);
    const summary = bitmap_view.summarize(invalid);

    try testing.expect(!bitmap_view.isValid(invalid));
    try testing.expect(!bitmap_view.testBit(invalid, 0));
    try testing.expectEqual(@as(u32, 0), bitmap_view.firstSet(invalid));
    try testing.expectEqual(@as(u32, 0), bitmap_view.firstZero(invalid));
    try testing.expectEqual(@as(u32, 0), bitmap_view.weight(invalid));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask starter helpers keep cpu membership reviewable" {
    var backing = [_]usize{
        (@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 7),
    };
    const view = cpumask_view.viewFromWords(backing[0..], 16);
    const summary = cpumask_view.summarize(view);

    try testing.expect(cpumask_view.isValid(view));
    try testing.expect(cpumask_view.cpuIsSet(view, 0));
    try testing.expect(cpumask_view.cpuIsSet(view, 7));
    try testing.expect(!cpumask_view.cpuIsSet(view, 1));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstCpu(view));
    try testing.expectEqual(@as(u32, 1), cpumask_view.firstAbsentCpu(view));
    try testing.expectEqual(@as(u32, 3), cpumask_view.weight(view));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(@as(u32, 1), summary.first_zero);
    try testing.expectEqual(@as(u32, 3), summary.weight);
}

test "cpumask starter helpers keep an all-clear bounded window distinct from the empty sentinel" {
    var backing = [_]usize{0};
    const view = cpumask_view.viewFromWords(backing[0..], 16);
    const summary = cpumask_view.summarize(view);

    try testing.expect(cpumask_view.isValid(view));
    try testing.expect(!cpumask_view.cpuIsSet(view, 0));
    try testing.expect(!cpumask_view.cpuIsSet(view, 15));
    try testing.expectEqual(@as(u32, 16), cpumask_view.firstCpu(view));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstAbsentCpu(view));
    try testing.expectEqual(@as(u32, 0), cpumask_view.weight(view));
    try testing.expectEqual(@as(u32, 16), summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask starter helpers cover cross-word windows and tail masking" {
    var backing = [_]usize{
        (@as(usize, 1) << 5) | (@as(usize, 1) << (bitmap_view.bits_per_word - 1)),
        (@as(usize, 1) << 1) | (@as(usize, 1) << 6) | (@as(usize, 1) << 10),
    };
    const view = cpumask_view.viewFromWords(backing[0..], bitmap_view.bits_per_word + 11);
    const summary = cpumask_view.summarize(view);

    try testing.expect(cpumask_view.isValid(view));
    try testing.expect(cpumask_view.cpuIsSet(view, 5));
    try testing.expect(cpumask_view.cpuIsSet(view, bitmap_view.bits_per_word - 1));
    try testing.expect(cpumask_view.cpuIsSet(view, bitmap_view.bits_per_word + 10));
    try testing.expect(!cpumask_view.cpuIsSet(view, bitmap_view.bits_per_word + 11));
    try testing.expectEqual(@as(u32, 5), cpumask_view.firstCpu(view));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstAbsentCpu(view));
    try testing.expectEqual(@as(u32, 5), cpumask_view.weight(view));
    try testing.expectEqual(@as(u32, 5), summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 5), summary.weight);
}

test "cpumask starter helpers keep a full bounded mask from leaking tail zeros" {
    var backing = [_]usize{
        ~@as(usize, 0),
        bitmap_view.lastWordMask(bitmap_view.bits_per_word + 11),
    };
    const view = cpumask_view.viewFromWords(backing[0..], bitmap_view.bits_per_word + 11);
    const summary = cpumask_view.summarize(view);

    try testing.expect(cpumask_view.isValid(view));
    try testing.expect(cpumask_view.cpuIsSet(view, bitmap_view.bits_per_word + 10));
    try testing.expect(!cpumask_view.cpuIsSet(view, bitmap_view.bits_per_word + 11));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstCpu(view));
    try testing.expectEqual(bitmap_view.bits_per_word + 11, cpumask_view.firstAbsentCpu(view));
    try testing.expectEqual(bitmap_view.bits_per_word + 11, cpumask_view.weight(view));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(bitmap_view.bits_per_word + 11, summary.first_zero);
    try testing.expectEqual(bitmap_view.bits_per_word + 11, summary.weight);
}

test "cpumask starter helpers ignore out-of-range tail bits when no bounded cpus are set" {
    var backing = [_]usize{
        0,
        @as(usize, 1) << (11 + 3),
    };
    const view = cpumask_view.viewFromWords(backing[0..], bitmap_view.bits_per_word + 11);
    const summary = cpumask_view.summarize(view);

    try testing.expect(cpumask_view.isValid(view));
    try testing.expect(!cpumask_view.cpuIsSet(view, bitmap_view.bits_per_word + 10));
    try testing.expect(!cpumask_view.cpuIsSet(view, bitmap_view.bits_per_word + 11));
    try testing.expectEqual(bitmap_view.bits_per_word + 11, summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask starter helpers keep exact-word windows explicit" {
    var backing = [_]usize{
        ~@as(usize, 0),
        (@as(usize, 1) << 5),
    };
    const view = cpumask_view.viewFromWords(backing[0..], bitmap_view.bits_per_word * 2);
    const summary = cpumask_view.summarize(view);

    try testing.expect(cpumask_view.isValid(view));
    try testing.expectEqual(~@as(usize, 0), bitmap_view.lastWordMask(bitmap_view.bits_per_word * 2));
    try testing.expect(cpumask_view.cpuIsSet(view, bitmap_view.bits_per_word + 5));
    try testing.expect(!cpumask_view.cpuIsSet(view, bitmap_view.bits_per_word + 6));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstCpu(view));
    try testing.expectEqual(bitmap_view.bits_per_word, cpumask_view.firstAbsentCpu(view));
    try testing.expectEqual(bitmap_view.bits_per_word + 1, cpumask_view.weight(view));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(bitmap_view.bits_per_word, summary.first_zero);
    try testing.expectEqual(bitmap_view.bits_per_word + 1, summary.weight);
}

test "cpumask starter helpers keep large bounded word counts predictable" {
    const max_nbits = std.math.maxInt(u32);
    const expected = bitmap_view.wordCount(max_nbits);
    const invalid = binding.initCpumaskView(1, max_nbits, expected - 1, max_nbits);
    const summary = cpumask_view.summarize(invalid);

    try testing.expectEqual(expected, bitmap_view.wordCount(max_nbits));
    try testing.expect(!cpumask_view.isValid(invalid));
    try testing.expect(!cpumask_view.cpuIsSet(invalid, 0));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstCpu(invalid));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstAbsentCpu(invalid));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask starter helpers fail closed on malformed views" {
    const invalid = binding.initCpumaskView(0, bitmap_view.bits_per_word + 1, 1, bitmap_view.bits_per_word + 1);
    const summary = cpumask_view.summarize(invalid);

    try testing.expect(!cpumask_view.isValid(invalid));
    try testing.expect(!cpumask_view.cpuIsSet(invalid, 0));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstCpu(invalid));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstAbsentCpu(invalid));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask starter helpers fail closed on zero-bit stray storage" {
    const invalid = binding.initCpumaskView(1, 0, 1, 0);
    const summary = cpumask_view.summarize(invalid);

    try testing.expect(!cpumask_view.isValid(invalid));
    try testing.expect(!cpumask_view.cpuIsSet(invalid, 0));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstCpu(invalid));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstAbsentCpu(invalid));
    try testing.expectEqual(@as(u32, 0), cpumask_view.weight(invalid));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask starter helpers fail closed when nr_cpu_ids drifts from nbits" {
    const invalid = binding.initCpumaskView(0, 4, 0, 3);
    const summary = cpumask_view.summarize(invalid);

    try testing.expect(!cpumask_view.isValid(invalid));
    try testing.expect(!cpumask_view.cpuIsSet(invalid, 0));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstCpu(invalid));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstAbsentCpu(invalid));
    try testing.expectEqual(@as(u32, 0), cpumask_view.weight(invalid));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 0), summary.weight);
}

test "cpumask starter helpers keep empty sentinel behavior explicit" {
    const view = cpumask_view.viewFromWords(&.{}, 0);
    const summary = cpumask_view.summarize(view);

    try testing.expect(cpumask_view.isValid(view));
    try testing.expect(!cpumask_view.cpuIsSet(view, 0));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstCpu(view));
    try testing.expectEqual(@as(u32, 0), cpumask_view.firstAbsentCpu(view));
    try testing.expectEqual(@as(u32, 0), cpumask_view.weight(view));
    try testing.expectEqual(@as(u32, 0), summary.first_set);
    try testing.expectEqual(@as(u32, 0), summary.first_zero);
    try testing.expectEqual(@as(u32, 0), summary.weight);
}

test "starter packet stays aligned with the live Linux-facing header family version" {
    const current = version.current();

    try testing.expectEqual(@as(u32, 0), version.abi_major);
    try testing.expectEqual(@as(u32, 1), version.abi_minor);
    try testing.expectEqual(@as(u32, 1), version.header_family_revision);
    try testing.expectEqual(@as(u32, 0), current.abi_major);
    try testing.expectEqual(@as(u32, 1), current.abi_minor);
    try testing.expectEqual(@as(u32, 1), current.header_family_revision);
}
