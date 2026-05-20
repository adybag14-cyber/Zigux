const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");

fn retagRejectedValue(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

fn rejectedValueForOddErrRaw(raw: usize) usize {
    std.debug.assert(err_ptr.isErrValue(raw));
    std.debug.assert((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
    return raw >> 1;
}

test "representative odd err_ptr raws alias rejected tagged values across the band" {
    const samples = [_]isize{ -4095, -2049, -3, -1 };

    for (samples) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const rejected_value = rejectedValueForOddErrRaw(raw);

        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expect((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try std.testing.expectEqual(code, err_ptr.toErrorCode(raw));
        try std.testing.expect(!xa_value.canRepresent(rejected_value));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
        try std.testing.expectEqual(raw, retagRejectedValue(rejected_value));
        try std.testing.expect(!xa_value.isValue(raw));
    }
}

test "rejected tagged values cover every odd err_ptr raw exactly once" {
    var odd_err_raw_count: usize = 0;
    var previous_rejected_value: ?usize = null;
    var raw = err_ptr.err_floor;

    while (true) {
        if ((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask) {
            const rejected_value = rejectedValueForOddErrRaw(raw);

            try std.testing.expect(!xa_value.canRepresent(rejected_value));
            try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
            try std.testing.expectEqual(raw, retagRejectedValue(rejected_value));

            if (previous_rejected_value) |previous| {
                try std.testing.expectEqual(previous + 1, rejected_value);
            }

            previous_rejected_value = rejected_value;
            odd_err_raw_count += 1;
        }

        if (raw == std.math.maxInt(usize)) {
            break;
        }
        raw += 1;
    }

    try std.testing.expectEqual(@as(usize, (err_ptr.max_errno + 1) / 2), odd_err_raw_count);
    try std.testing.expect(previous_rejected_value != null);
    try std.testing.expectEqual(
        err_ptr.fromErrorCode(-1) >> 1,
        previous_rejected_value.?,
    );
}

test "even err_ptr raws stay between neighboring rejected tagged aliases" {
    const samples = [_]isize{ -4094, -2048, -2 };

    for (samples) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const retagged_neighbor = retagRejectedValue(raw >> 1);
        const previous_rejected_value = rejectedValueForOddErrRaw(raw - 1);
        const next_rejected_value = rejectedValueForOddErrRaw(raw + 1);

        try std.testing.expect(err_ptr.isErrValue(raw));
        try std.testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
        try std.testing.expectEqual(code, err_ptr.toErrorCode(raw));
        try std.testing.expect(!xa_value.isValue(raw));
        try std.testing.expectEqual(raw + 1, retagged_neighbor);
        try std.testing.expect(!xa_value.canRepresent(raw >> 1));
        try std.testing.expectEqual(raw - 1, retagRejectedValue(previous_rejected_value));
        try std.testing.expectEqual(raw + 1, retagRejectedValue(next_rejected_value));
        try std.testing.expectEqual(previous_rejected_value + 1, next_rejected_value);
    }
}
