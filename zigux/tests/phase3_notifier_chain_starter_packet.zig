const std = @import("std");
const testing = std.testing;

const notifier_chain_view = @import("notifier_chain_view");

test "notifier starter packet keeps a null head explicit" {
    const view = notifier_chain_view.NotifierChainView.init(null);

    try testing.expect(view.isEmpty());
    try testing.expectEqual(@as(usize, 0), view.len());
    try testing.expectEqual(@as(?*const notifier_chain_view.NotifierBlock, null), view.first());
    try testing.expectEqual(@as(?*const notifier_chain_view.NotifierBlock, null), view.last());
    try testing.expect(view.hasNonincreasingPriority());
    try testing.expectEqual(@as(?notifier_chain_view.PriorityIncrease, null), view.firstPriorityIncrease());
}

test "notifier starter packet keeps ordered priority chains reviewable" {
    const third = notifier_chain_view.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 4,
    };
    const second = notifier_chain_view.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 6,
    };
    const first = notifier_chain_view.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 6,
    };
    const view = notifier_chain_view.NotifierChainView.init(&first);

    try testing.expect(!view.isEmpty());
    try testing.expectEqual(@as(usize, 3), view.len());
    try testing.expectEqual(@as(?*const notifier_chain_view.NotifierBlock, &first), view.first());
    try testing.expectEqual(@as(?*const notifier_chain_view.NotifierBlock, &third), view.last());
    try testing.expect(view.hasNonincreasingPriority());

    var it = view.iterator();
    try testing.expectEqual(@as(?*const notifier_chain_view.NotifierBlock, &first), it.next());
    try testing.expectEqual(@as(?*const notifier_chain_view.NotifierBlock, &second), it.next());
    try testing.expectEqual(@as(?*const notifier_chain_view.NotifierBlock, &third), it.next());
    try testing.expectEqual(@as(?*const notifier_chain_view.NotifierBlock, null), it.next());
}

test "notifier starter packet reports the first priority increase witness" {
    const fourth = notifier_chain_view.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 5,
    };
    const third = notifier_chain_view.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&fourth),
        .priority = 2,
    };
    const second = notifier_chain_view.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 3,
    };
    const first = notifier_chain_view.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 6,
    };

    const view = notifier_chain_view.NotifierChainView.init(&first);
    const increase = view.firstPriorityIncrease().?;

    try testing.expect(!view.hasNonincreasingPriority());
    try testing.expectEqual(@as(usize, 2), increase.previous_index);
    try testing.expectEqual(@as(usize, 3), increase.current_index);
    try testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try testing.expectEqual(@as(i32, 5), increase.current_priority);
}
