const std = @import("std");

pub const ABI_VERSION: u16 = 1;
pub const STATUS_FLAG_ERROR: u16 = 1;
pub const LIST_FLAG_EMPTY: u32 = 1;
pub const LIST_FLAG_SINGULAR: u32 = 2;
pub const LIST_FLAG_CIRCULAR: u32 = 4;
pub const LIST_FLAG_TRUNCATED: u32 = 8;
pub const HLIST_FLAG_EMPTY: u32 = 1;
pub const HLIST_FLAG_SINGULAR: u32 = 2;
pub const HLIST_FLAG_TERMINATED: u32 = 4;
pub const HLIST_FLAG_TRUNCATED: u32 = 8;
pub const ERR_PTR_FLAG_ERROR: u16 = 1;
pub const ERR_PTR_FLAG_NULL: u16 = 2;
pub const XA_VALUE_FLAG_VALUE: u32 = 1;
pub const XA_VALUE_FLAG_PLAIN: u32 = 2;
pub const XA_SLOT_FLAG_TRUNCATED: u32 = 1;
pub const IDR_SLOT_FLAG_TRUNCATED: u32 = 1;
pub const IDA_BITMAP_FLAG_TRUNCATED: u32 = 1;
pub const IDA_BITMAP_FLAG_EXHAUSTED: u32 = 2;
pub const IDA_ALLOC_FLAG_TRUNCATED: u32 = 1;
pub const IDA_ALLOC_FLAG_FOUND: u32 = 2;
pub const IDA_ALLOC_FLAG_EXHAUSTED: u32 = 4;
pub const IDA_RANGE_FLAG_TRUNCATED: u32 = 1;
pub const IDA_RANGE_FLAG_FOUND: u32 = 2;
pub const IDA_RANGE_FLAG_EXHAUSTED: u32 = 4;
pub const IDA_RANGE_SET_FLAG_TRUNCATED: u32 = 1;
pub const IDA_RANGE_SET_FLAG_FOUND: u32 = 2;
pub const IDA_RANGE_SET_FLAG_EXHAUSTED: u32 = 4;
pub const IDA_RANGE_SET_FLAG_SELECTED: u32 = 8;
pub const IDA_POLICY_FIRST_FIT: u32 = 1;
pub const IDA_POLICY_LAST_FIT: u32 = 2;
pub const IDA_POLICY_FLAG_TRUNCATED: u32 = 1;
pub const IDA_POLICY_FLAG_FOUND: u32 = 2;
pub const IDA_POLICY_FLAG_EXHAUSTED: u32 = 4;
pub const MINOR_ALLOC_FLAG_TRUNCATED: u32 = 1;
pub const MINOR_ALLOC_FLAG_FOUND: u32 = 2;
pub const MINOR_ALLOC_FLAG_EXHAUSTED: u32 = 4;
pub const DEV_REGION_FLAG_TRUNCATED: u32 = 1;
pub const DEV_REGION_FLAG_FOUND: u32 = 2;
pub const DEV_REGION_FLAG_EXHAUSTED: u32 = 4;
pub const CDEV_ADD_FLAG_TRUNCATED: u32 = 1;
pub const CDEV_ADD_FLAG_FOUND: u32 = 2;
pub const CDEV_ADD_FLAG_EXHAUSTED: u32 = 4;
pub const CDEV_LOOKUP_FLAG_TRUNCATED: u32 = 1;
pub const CDEV_LOOKUP_FLAG_FOUND: u32 = 2;
pub const CDEV_LOOKUP_FLAG_EXHAUSTED: u32 = 4;
pub const CDEV_LOOKUP_FLAG_HIT: u32 = 8;
pub const CDEV_LOOKUP_INDEX_NONE: u32 = 0xffffffff;
pub const CHRDEV_MODE_READ: u32 = 1;
pub const CHRDEV_MODE_WRITE: u32 = 2;
pub const CHRDEV_OPEN_FLAG_TRUNCATED: u32 = 1;
pub const CHRDEV_OPEN_FLAG_FOUND: u32 = 2;
pub const CHRDEV_OPEN_FLAG_EXHAUSTED: u32 = 4;
pub const CHRDEV_OPEN_FLAG_HIT: u32 = 8;
pub const CHRDEV_OPEN_FLAG_PERMITTED: u32 = 16;
pub const CHRDEV_OPEN_FLAG_DENIED: u32 = 32;
pub const CHRDEV_OPEN_INDEX_NONE: u32 = 0xffffffff;
pub const CHRDEV_FOP_OPEN: u32 = 1;
pub const CHRDEV_FOP_RELEASE: u32 = 2;
pub const CHRDEV_FOP_READ: u32 = 4;
pub const CHRDEV_FOP_WRITE: u32 = 8;
pub const CHRDEV_FOPS_FLAG_TRUNCATED: u32 = 1;
pub const CHRDEV_FOPS_FLAG_FOUND: u32 = 2;
pub const CHRDEV_FOPS_FLAG_EXHAUSTED: u32 = 4;
pub const CHRDEV_FOPS_FLAG_HIT: u32 = 8;
pub const CHRDEV_FOPS_FLAG_PERMITTED: u32 = 16;
pub const CHRDEV_FOPS_FLAG_DENIED: u32 = 32;
pub const CHRDEV_FOPS_FLAG_ROUTABLE: u32 = 64;
pub const CHRDEV_FOPS_FLAG_MISSING_OPS: u32 = 128;
pub const CHRDEV_FOPS_INDEX_NONE: u32 = 0xffffffff;
pub const CHRDEV_ROUTE_FLAG_TRUNCATED: u32 = 1;
pub const CHRDEV_ROUTE_FLAG_FOUND: u32 = 2;
pub const CHRDEV_ROUTE_FLAG_EXHAUSTED: u32 = 4;
pub const CHRDEV_ROUTE_FLAG_HIT: u32 = 8;
pub const CHRDEV_ROUTE_FLAG_PERMITTED: u32 = 16;
pub const CHRDEV_ROUTE_FLAG_DENIED: u32 = 32;
pub const CHRDEV_ROUTE_FLAG_ROUTABLE: u32 = 64;
pub const CHRDEV_ROUTE_FLAG_BLOCKED: u32 = 128;
pub const CHRDEV_ROUTE_INDEX_NONE: u32 = 0xffffffff;
pub const CHRDEV_IO_OP_READ: u32 = 1;
pub const CHRDEV_IO_OP_WRITE: u32 = 2;
pub const CHRDEV_IO_FLAG_TRUNCATED: u32 = 1;
pub const CHRDEV_IO_FLAG_FOUND: u32 = 2;
pub const CHRDEV_IO_FLAG_EXHAUSTED: u32 = 4;
pub const CHRDEV_IO_FLAG_HIT: u32 = 8;
pub const CHRDEV_IO_FLAG_PERMITTED: u32 = 16;
pub const CHRDEV_IO_FLAG_DENIED: u32 = 32;
pub const CHRDEV_IO_FLAG_ROUTABLE: u32 = 64;
pub const CHRDEV_IO_FLAG_BLOCKED: u32 = 128;
pub const CHRDEV_IO_FLAG_DISPATCHABLE: u32 = 256;
pub const CHRDEV_IO_INDEX_NONE: u32 = 0xffffffff;
pub const CHRDEV_XFER_FLAG_TRUNCATED: u32 = 1;
pub const CHRDEV_XFER_FLAG_FOUND: u32 = 2;
pub const CHRDEV_XFER_FLAG_EXHAUSTED: u32 = 4;
pub const CHRDEV_XFER_FLAG_HIT: u32 = 8;
pub const CHRDEV_XFER_FLAG_PERMITTED: u32 = 16;
pub const CHRDEV_XFER_FLAG_DENIED: u32 = 32;
pub const CHRDEV_XFER_FLAG_ROUTABLE: u32 = 64;
pub const CHRDEV_XFER_FLAG_BLOCKED: u32 = 128;
pub const CHRDEV_XFER_FLAG_DISPATCHABLE: u32 = 256;
pub const CHRDEV_XFER_FLAG_RESUMED: u32 = 512;
pub const CHRDEV_XFER_FLAG_CONTINUABLE: u32 = 1024;
pub const CHRDEV_XFER_FLAG_COMPLETES: u32 = 2048;
pub const CHRDEV_XFER_INDEX_NONE: u32 = 0xffffffff;
pub const CHRDEV_RESUME_FLAG_TRUNCATED: u32 = 1;
pub const CHRDEV_RESUME_FLAG_FOUND: u32 = 2;
pub const CHRDEV_RESUME_FLAG_EXHAUSTED: u32 = 4;
pub const CHRDEV_RESUME_FLAG_HIT: u32 = 8;
pub const CHRDEV_RESUME_FLAG_PERMITTED: u32 = 16;
pub const CHRDEV_RESUME_FLAG_DENIED: u32 = 32;
pub const CHRDEV_RESUME_FLAG_ROUTABLE: u32 = 64;
pub const CHRDEV_RESUME_FLAG_BLOCKED: u32 = 128;
pub const CHRDEV_RESUME_FLAG_DISPATCHABLE: u32 = 256;
pub const CHRDEV_RESUME_FLAG_RESUMED: u32 = 512;
pub const CHRDEV_RESUME_FLAG_CONTINUABLE: u32 = 1024;
pub const CHRDEV_RESUME_FLAG_COMPLETES: u32 = 2048;
pub const CHRDEV_RESUME_FLAG_PROGRESSED: u32 = 4096;
pub const CHRDEV_RESUME_FLAG_STALLED: u32 = 8192;
pub const CHRDEV_RESUME_FLAG_COMPLETE_OK: u32 = 16384;
pub const CHRDEV_RESUME_INDEX_NONE: u32 = 0xffffffff;
pub const CHRDEV_RETRY_FLAG_TRUNCATED: u32 = 1;
pub const CHRDEV_RETRY_FLAG_FOUND: u32 = 2;
pub const CHRDEV_RETRY_FLAG_EXHAUSTED: u32 = 4;
pub const CHRDEV_RETRY_FLAG_HIT: u32 = 8;
pub const CHRDEV_RETRY_FLAG_PERMITTED: u32 = 16;
pub const CHRDEV_RETRY_FLAG_DENIED: u32 = 32;
pub const CHRDEV_RETRY_FLAG_ROUTABLE: u32 = 64;
pub const CHRDEV_RETRY_FLAG_BLOCKED: u32 = 128;
pub const CHRDEV_RETRY_FLAG_DISPATCHABLE: u32 = 256;
pub const CHRDEV_RETRY_FLAG_RESUMED: u32 = 512;
pub const CHRDEV_RETRY_FLAG_CONTINUABLE: u32 = 1024;
pub const CHRDEV_RETRY_FLAG_COMPLETES: u32 = 2048;
pub const CHRDEV_RETRY_FLAG_PROGRESSED: u32 = 4096;
pub const CHRDEV_RETRY_FLAG_STALLED: u32 = 8192;
pub const CHRDEV_RETRY_FLAG_COMPLETE_OK: u32 = 16384;
pub const CHRDEV_RETRY_FLAG_RETRYABLE: u32 = 32768;
pub const CHRDEV_RETRY_FLAG_RETRY_PLANNED: u32 = 65536;
pub const CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED: u32 = 131072;
pub const CHRDEV_RETRY_FLAG_BACKOFF_APPLIED: u32 = 262144;
pub const CHRDEV_RETRY_FLAG_FAILS: u32 = 524288;
pub const CHRDEV_RETRY_INDEX_NONE: u32 = 0xffffffff;
pub const CHRDEV_REQUEUE_FLAG_TRUNCATED: u32 = 1;
pub const CHRDEV_REQUEUE_FLAG_FOUND: u32 = 2;
pub const CHRDEV_REQUEUE_FLAG_EXHAUSTED: u32 = 4;
pub const CHRDEV_REQUEUE_FLAG_HIT: u32 = 8;
pub const CHRDEV_REQUEUE_FLAG_PERMITTED: u32 = 16;
pub const CHRDEV_REQUEUE_FLAG_DENIED: u32 = 32;
pub const CHRDEV_REQUEUE_FLAG_ROUTABLE: u32 = 64;
pub const CHRDEV_REQUEUE_FLAG_BLOCKED: u32 = 128;
pub const CHRDEV_REQUEUE_FLAG_DISPATCHABLE: u32 = 256;
pub const CHRDEV_REQUEUE_FLAG_RESUMED: u32 = 512;
pub const CHRDEV_REQUEUE_FLAG_CONTINUABLE: u32 = 1024;
pub const CHRDEV_REQUEUE_FLAG_COMPLETES: u32 = 2048;
pub const CHRDEV_REQUEUE_FLAG_PROGRESSED: u32 = 4096;
pub const CHRDEV_REQUEUE_FLAG_STALLED: u32 = 8192;
pub const CHRDEV_REQUEUE_FLAG_COMPLETE_OK: u32 = 16384;
pub const CHRDEV_REQUEUE_FLAG_RETRYABLE: u32 = 32768;
pub const CHRDEV_REQUEUE_FLAG_RETRY_PLANNED: u32 = 65536;
pub const CHRDEV_REQUEUE_FLAG_RETRY_EXHAUSTED: u32 = 131072;
pub const CHRDEV_REQUEUE_FLAG_BACKOFF_APPLIED: u32 = 262144;
pub const CHRDEV_REQUEUE_FLAG_FAILS: u32 = 524288;
pub const CHRDEV_REQUEUE_FLAG_REQUEUEABLE: u32 = 1048576;
pub const CHRDEV_REQUEUE_FLAG_REQUEUE_PLANNED: u32 = 2097152;
pub const CHRDEV_REQUEUE_FLAG_DELAYED: u32 = 4194304;
pub const CHRDEV_REQUEUE_FLAG_SATURATED: u32 = 8388608;
pub const CHRDEV_REQUEUE_FLAG_DROPPED: u32 = 16777216;
pub const CHRDEV_REQUEUE_FLAG_COMPLETE: u32 = 33554432;
pub const CHRDEV_REQUEUE_INDEX_NONE: u32 = 0xffffffff;
pub const CHRDEV_COMPLETE_FLAG_TRUNCATED: u32 = 1;
pub const CHRDEV_COMPLETE_FLAG_FOUND: u32 = 2;
pub const CHRDEV_COMPLETE_FLAG_EXHAUSTED: u32 = 4;
pub const CHRDEV_COMPLETE_FLAG_HIT: u32 = 8;
pub const CHRDEV_COMPLETE_FLAG_PERMITTED: u32 = 16;
pub const CHRDEV_COMPLETE_FLAG_DENIED: u32 = 32;
pub const CHRDEV_COMPLETE_FLAG_ROUTABLE: u32 = 64;
pub const CHRDEV_COMPLETE_FLAG_BLOCKED: u32 = 128;
pub const CHRDEV_COMPLETE_FLAG_DISPATCHABLE: u32 = 256;
pub const CHRDEV_COMPLETE_FLAG_RESUMED: u32 = 512;
pub const CHRDEV_COMPLETE_FLAG_CONTINUABLE: u32 = 1024;
pub const CHRDEV_COMPLETE_FLAG_COMPLETES: u32 = 2048;
pub const CHRDEV_COMPLETE_FLAG_PROGRESSED: u32 = 4096;
pub const CHRDEV_COMPLETE_FLAG_STALLED: u32 = 8192;
pub const CHRDEV_COMPLETE_FLAG_COMPLETE_OK: u32 = 16384;
pub const CHRDEV_COMPLETE_FLAG_RETRYABLE: u32 = 32768;
pub const CHRDEV_COMPLETE_FLAG_RETRY_PLANNED: u32 = 65536;
pub const CHRDEV_COMPLETE_FLAG_RETRY_EXHAUSTED: u32 = 131072;
pub const CHRDEV_COMPLETE_FLAG_BACKOFF_APPLIED: u32 = 262144;
pub const CHRDEV_COMPLETE_FLAG_FAILS: u32 = 524288;
pub const CHRDEV_COMPLETE_FLAG_REQUEUEABLE: u32 = 1048576;
pub const CHRDEV_COMPLETE_FLAG_REQUEUE_PLANNED: u32 = 2097152;
pub const CHRDEV_COMPLETE_FLAG_DELAYED: u32 = 4194304;
pub const CHRDEV_COMPLETE_FLAG_SATURATED: u32 = 8388608;
pub const CHRDEV_COMPLETE_FLAG_DROPPED: u32 = 16777216;
pub const CHRDEV_COMPLETE_FLAG_COMPLETE: u32 = 33554432;
pub const CHRDEV_COMPLETE_FLAG_COMPLETION_PLANNED: u32 = 67108864;
pub const CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION: u32 = 134217728;
pub const CHRDEV_COMPLETE_FLAG_FAILURE_COMPLETION: u32 = 268435456;
pub const CHRDEV_COMPLETE_FLAG_FINALIZED: u32 = 536870912;
pub const CHRDEV_COMPLETE_INDEX_NONE: u32 = 0xffffffff;
pub const CHRDEV_COMPLETE_STATUS_NONE: u32 = 0;
pub const CHRDEV_COMPLETE_STATUS_OK: u32 = 1;
pub const CHRDEV_COMPLETE_STATUS_DEFERRED: u32 = 2;
pub const CHRDEV_COMPLETE_STATUS_FAILED: u32 = 3;
pub const CHRDEV_NOTIFY_MASK_SUCCESS: u32 = 1;
pub const CHRDEV_NOTIFY_MASK_DEFERRED: u32 = 2;
pub const CHRDEV_NOTIFY_MASK_FAILURE: u32 = 4;
pub const CHRDEV_NOTIFY_FLAG_TRUNCATED: u32 = 1;
pub const CHRDEV_NOTIFY_FLAG_FOUND: u32 = 2;
pub const CHRDEV_NOTIFY_FLAG_EXHAUSTED: u32 = 4;
pub const CHRDEV_NOTIFY_FLAG_HIT: u32 = 8;
pub const CHRDEV_NOTIFY_FLAG_PERMITTED: u32 = 16;
pub const CHRDEV_NOTIFY_FLAG_DENIED: u32 = 32;
pub const CHRDEV_NOTIFY_FLAG_ROUTABLE: u32 = 64;
pub const CHRDEV_NOTIFY_FLAG_BLOCKED: u32 = 128;
pub const CHRDEV_NOTIFY_FLAG_DISPATCHABLE: u32 = 256;
pub const CHRDEV_NOTIFY_FLAG_RESUMED: u32 = 512;
pub const CHRDEV_NOTIFY_FLAG_CONTINUABLE: u32 = 1024;
pub const CHRDEV_NOTIFY_FLAG_COMPLETES: u32 = 2048;
pub const CHRDEV_NOTIFY_FLAG_PROGRESSED: u32 = 4096;
pub const CHRDEV_NOTIFY_FLAG_STALLED: u32 = 8192;
pub const CHRDEV_NOTIFY_FLAG_COMPLETE_OK: u32 = 16384;
pub const CHRDEV_NOTIFY_FLAG_RETRYABLE: u32 = 32768;
pub const CHRDEV_NOTIFY_FLAG_RETRY_PLANNED: u32 = 65536;
pub const CHRDEV_NOTIFY_FLAG_RETRY_EXHAUSTED: u32 = 131072;
pub const CHRDEV_NOTIFY_FLAG_BACKOFF_APPLIED: u32 = 262144;
pub const CHRDEV_NOTIFY_FLAG_FAILS: u32 = 524288;
pub const CHRDEV_NOTIFY_FLAG_REQUEUEABLE: u32 = 1048576;
pub const CHRDEV_NOTIFY_FLAG_REQUEUE_PLANNED: u32 = 2097152;
pub const CHRDEV_NOTIFY_FLAG_DELAYED: u32 = 4194304;
pub const CHRDEV_NOTIFY_FLAG_SATURATED: u32 = 8388608;
pub const CHRDEV_NOTIFY_FLAG_DROPPED: u32 = 16777216;
pub const CHRDEV_NOTIFY_FLAG_COMPLETE: u32 = 33554432;
pub const CHRDEV_NOTIFY_FLAG_COMPLETION_PLANNED: u32 = 67108864;
pub const CHRDEV_NOTIFY_FLAG_DEFERRED_COMPLETION: u32 = 134217728;
pub const CHRDEV_NOTIFY_FLAG_FAILURE_COMPLETION: u32 = 268435456;
pub const CHRDEV_NOTIFY_FLAG_FINALIZED: u32 = 536870912;
pub const CHRDEV_NOTIFY_FLAG_MATCHED_NOTIFY: u32 = 1073741824;
pub const CHRDEV_NOTIFY_FLAG_NOTIFY_PLANNED: u32 = 2147483648;
pub const CHRDEV_NOTIFY_INDEX_NONE: u32 = 0xffffffff;
pub const CHRDEV_NOTIFY_STATUS_NONE: u32 = 0;
pub const CHRDEV_NOTIFY_STATUS_DELIVERED: u32 = 1;
pub const CHRDEV_NOTIFY_STATUS_DEFERRED: u32 = 2;
pub const CHRDEV_NOTIFY_STATUS_DROPPED: u32 = 3;
pub const CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED: u32 = 1;
pub const CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE: u32 = 2;
pub const CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE: u32 = 4;
pub const CHRDEV_NOTIFY_POLICY_STATUS_NONE: u32 = 0;
pub const CHRDEV_NOTIFY_POLICY_STATUS_DELIVERED: u32 = 1;
pub const CHRDEV_NOTIFY_POLICY_STATUS_DEFERRED: u32 = 2;
pub const CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED: u32 = 3;
pub const CHRDEV_NOTIFY_POLICY_STATUS_COALESCED: u32 = 4;
pub const CHRDEV_NOTIFY_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;
pub const CHRDEV_NOTIFY_BUDGET_FLAG_DELIVERY_BUDGET_USED: u32 = 2;
pub const CHRDEV_NOTIFY_BUDGET_FLAG_DEFERRED_BUDGET_USED: u32 = 4;
pub const CHRDEV_NOTIFY_BUDGET_FLAG_DELIVERY_BUDGET_EXHAUSTED: u32 = 8;
pub const CHRDEV_NOTIFY_BUDGET_FLAG_DEFERRED_BUDGET_EXHAUSTED: u32 = 16;
pub const CHRDEV_NOTIFY_BUDGET_STATUS_NONE: u32 = 0;
pub const CHRDEV_NOTIFY_BUDGET_STATUS_ISSUED: u32 = 1;
pub const CHRDEV_NOTIFY_BUDGET_STATUS_DEFERRED: u32 = 2;
pub const CHRDEV_NOTIFY_BUDGET_STATUS_DROPPED: u32 = 3;
pub const CHRDEV_NOTIFY_BUDGET_STATUS_SUPPRESSED: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_MASK_ISSUED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_MASK_DEFERRED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_MASK_DROPPED: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_MASK_SUPPRESSED: u32 = 8;
pub const CHRDEV_NOTIFY_ACK_FLAG_APPLICABLE: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_FLAG_ACKED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_FLAG_DEFERRED: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_FLAG_EXPIRED: u32 = 8;
pub const CHRDEV_NOTIFY_ACK_FLAG_SKIPPED: u32 = 16;
pub const CHRDEV_NOTIFY_ACK_FLAG_WINDOW_USED: u32 = 32;
pub const CHRDEV_NOTIFY_ACK_FLAG_WINDOW_EXHAUSTED: u32 = 64;
pub const CHRDEV_NOTIFY_ACK_STATUS_NONE: u32 = 0;
pub const CHRDEV_NOTIFY_ACK_STATUS_ACKED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_STATUS_DEFERRED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_STATUS_EXPIRED: u32 = 3;
pub const CHRDEV_NOTIFY_ACK_STATUS_SKIPPED: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_POLICY_SUPPRESS_EXPIRED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_POLICY_COALESCE_COOKIE: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE: u32 = 0;
pub const CHRDEV_NOTIFY_ACK_POLICY_STATUS_ACKED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_POLICY_STATUS_DEFERRED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_POLICY_STATUS_SUPPRESSED: u32 = 3;
pub const CHRDEV_NOTIFY_ACK_POLICY_STATUS_COALESCED: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_POLICY_STATUS_EXPIRED: u32 = 5;
pub const CHRDEV_NOTIFY_ACK_POLICY_STATUS_SKIPPED: u32 = 6;
pub const CHRDEV_NOTIFY_ACK_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_BUDGET_FLAG_ACK_BUDGET_USED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_BUDGET_FLAG_DEFERRED_ACK_BUDGET_USED: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_BUDGET_FLAG_ACK_BUDGET_EXHAUSTED: u32 = 8;
pub const CHRDEV_NOTIFY_ACK_BUDGET_FLAG_DEFERRED_ACK_BUDGET_EXHAUSTED: u32 = 16;
pub const CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE: u32 = 0;
pub const CHRDEV_NOTIFY_ACK_BUDGET_STATUS_ACKED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DEFERRED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DROPPED: u32 = 3;
pub const CHRDEV_NOTIFY_ACK_BUDGET_STATUS_SUPPRESSED: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_BUDGET_STATUS_SKIPPED: u32 = 5;
pub const CHRDEV_NOTIFY_ACK_WINDOW_FLAG_WINDOW_APPLIED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_WINDOW_FLAG_WINDOW_USED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_WINDOW_FLAG_WINDOW_EXHAUSTED: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_WINDOW_FLAG_FLOOR_HELD: u32 = 8;
pub const CHRDEV_NOTIFY_ACK_WINDOW_FLAG_FLOOR_BLOCKED: u32 = 16;
pub const CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE: u32 = 0;
pub const CHRDEV_NOTIFY_ACK_WINDOW_STATUS_ACKED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_WINDOW_STATUS_DEFERRED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_WINDOW_STATUS_DROPPED: u32 = 3;
pub const CHRDEV_NOTIFY_ACK_WINDOW_STATUS_SUPPRESSED: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_WINDOW_STATUS_SKIPPED: u32 = 5;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE: u32 = 0;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_ACKED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DEFERRED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SUPPRESSED: u32 = 3;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_COALESCED: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DROPPED: u32 = 5;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SKIPPED: u32 = 6;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_WINDOW_POLICY_BUDGET_USED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_WINDOW_POLICY_BUDGET_USED: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_WINDOW_POLICY_BUDGET_EXHAUSTED: u32 = 8;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_WINDOW_POLICY_BUDGET_EXHAUSTED: u32 = 16;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE: u32 = 0;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_ACKED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DEFERRED: u32 = 2;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_SUPPRESSED: u32 = 3;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_COALESCED: u32 = 4;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DROPPED: u32 = 5;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_SKIPPED: u32 = 6;
pub const DEV_MINOR_BITS: u32 = 20;
pub const DEV_MINOR_MASK: u32 = (1 << DEV_MINOR_BITS) - 1;

pub const Facility = enum(u16) {
    kernel = 1,
    helpers = 2,
    drivers = 3,
};

pub const PanicMode = enum(u8) {
    abort = 0,
    bug = 1,
    warn = 2,
};

pub const AllocatorMode = enum(u8) {
    caller_provided = 0,
    kernel_heap = 1,
    arena = 2,
};

pub const UnsafeScope = enum(u8) {
    none = 0,
    volatile_mmio = 1,
    raw_pointer_bridge = 2,
};

pub const BoundaryHeader = extern struct {
    size: u32,
    abi_version: u16,
    flags: u16,
};

pub const ExportStatus = extern struct {
    code: i32,
    facility: u16,
    flags: u16,
};

pub const BitmapView = extern struct {
    words_addr: usize,
    nbits: u32,
    word_count: u32,
};

pub const CpuMaskView = extern struct {
    bits_addr: usize,
    nr_cpu_ids: u32,
    reserved: u32,
};

pub const BitmapSummary = extern struct {
    first_set: u32,
    first_zero: u32,
    weight: u32,
    reserved: u32,
};

pub const CpuMaskSummary = extern struct {
    first_cpu: u32,
    next_cpu: u32,
    weight: u32,
    reserved: u32,
};

pub const ListHeadRef = extern struct {
    next_addr: usize,
    prev_addr: usize,
};

pub const ListView = extern struct {
    head_addr: usize,
    max_nodes: u32,
    reserved: u32,
};

pub const ListSummary = extern struct {
    length: u32,
    flags: u32,
};

pub const HListHeadRef = extern struct {
    first_addr: usize,
};

pub const HListNodeRef = extern struct {
    next_addr: usize,
    pprev_addr: usize,
};

pub const HListView = extern struct {
    head_addr: usize,
    max_nodes: u32,
    reserved: u32,
};

pub const HListSummary = extern struct {
    length: u32,
    flags: u32,
};

pub const ErrPtrSummary = extern struct {
    errno_code: i32,
    flags: u16,
    reserved: u16,
};

pub const XaValueSummary = extern struct {
    raw_addr: usize,
    decoded_value: u32,
    flags: u32,
};

pub const XaSlotView = extern struct {
    slots_addr: usize,
    slot_count: u32,
    max_scan: u32,
};

pub const XaSlotSummary = extern struct {
    scanned_count: u32,
    null_count: u32,
    value_count: u32,
    error_count: u32,
    plain_count: u32,
    flags: u32,
};

pub const IdrSlotView = extern struct {
    slots_addr: usize,
    base_id: u32,
    slot_count: u32,
    max_scan: u32,
    reserved: u32,
};

pub const IdrSlotSummary = extern struct {
    scanned_count: u32,
    present_count: u32,
    value_count: u32,
    error_count: u32,
    plain_count: u32,
    first_present_id: u32,
    next_free_id: u32,
    flags: u32,
};

pub const IdaBitmapView = extern struct {
    bits_addr: usize,
    base_id: u32,
    nbits: u32,
    max_scan: u32,
    reserved: u32,
};

pub const IdaBitmapSummary = extern struct {
    scanned_count: u32,
    allocated_count: u32,
    first_allocated_id: u32,
    first_free_id: u32,
    flags: u32,
    reserved: u32,
};

pub const IdaAllocView = extern struct {
    bits_addr: usize,
    base_id: u32,
    nbits: u32,
    max_scan: u32,
    request_count: u32,
    reserved: u32,
};

pub const IdaAllocSummary = extern struct {
    scanned_count: u32,
    request_count: u32,
    first_fit_id: u32,
    longest_free_run: u32,
    flags: u32,
    reserved: u32,
};

pub const IdaRangeView = extern struct {
    bits_addr: usize,
    base_id: u32,
    nbits: u32,
    max_scan: u32,
    request_count: u32,
    max_ranges: u32,
    reserved: u32,
};

pub const IdaRangeSummary = extern struct {
    scanned_count: u32,
    request_count: u32,
    candidate_range_count: u32,
    first_range_id: u32,
    last_range_id: u32,
    flags: u32,
};

pub const IdaRangeSetView = extern struct {
    bits_addr: usize,
    base_id: u32,
    nbits: u32,
    max_scan: u32,
    request_count: u32,
    max_ranges: u32,
    max_selected: u32,
    reserved: u32,
};

pub const IdaRangeSetSummary = extern struct {
    scanned_count: u32,
    request_count: u32,
    candidate_range_count: u32,
    selected_range_count: u32,
    first_selected_id: u32,
    last_selected_id: u32,
    flags: u32,
    reserved: u32,
};

pub const IdaPolicyView = extern struct {
    bits_addr: usize,
    base_id: u32,
    nbits: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    reserved: u32,
};

pub const IdaPolicySummary = extern struct {
    scanned_count: u32,
    request_count: u32,
    selected_fit_id: u32,
    alternate_fit_id: u32,
    longest_free_run: u32,
    flags: u32,
};

pub const MinorAllocView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    reserved: u32,
};

pub const MinorAllocSummary = extern struct {
    major: u32,
    scanned_count: u32,
    request_count: u32,
    selected_minor_start: u32,
    selected_minor_end: u32,
    alternate_minor_start: u32,
    longest_free_run: u32,
    flags: u32,
};

pub const DevRegionView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    reserved: u32,
};

pub const DevRegionSummary = extern struct {
    major: u32,
    scanned_count: u32,
    request_count: u32,
    selected_minor_start: u32,
    selected_minor_end: u32,
    first_dev: u32,
    last_dev: u32,
    flags: u32,
};

pub const CdevAddView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    reserved: u32,
};

pub const CdevAddSummary = extern struct {
    major: u32,
    scanned_count: u32,
    request_count: u32,
    selected_count: u32,
    first_minor: u32,
    first_dev: u32,
    last_dev: u32,
    flags: u32,
};

pub const CdevLookupView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    reserved: u32,
};

pub const CdevLookupSummary = extern struct {
    major: u32,
    scanned_count: u32,
    request_count: u32,
    selected_count: u32,
    first_minor: u32,
    target_minor: u32,
    resolved_index: u32,
    resolved_dev: u32,
    flags: u32,
};

pub const ChrdevOpenView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    reserved: u32,
};

pub const ChrdevOpenSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    requested_mode: u32,
    supported_mode: u32,
    granted_mode: u32,
    denied_mode: u32,
    flags: u32,
};

pub const ChrdevFopsView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    reserved: u32,
};

pub const ChrdevFopsSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    available_ops: u32,
    required_ops: u32,
    missing_ops: u32,
    flags: u32,
};

pub const ChrdevRouteView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    reserved: u32,
};

pub const ChrdevRouteSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    flags: u32,
};

pub const ChrdevIoView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    reserved: u32,
};

pub const ChrdevIoSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    chunk_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    flags: u32,
};

pub const ChrdevXferView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    reserved: u32,
};

pub const ChrdevXferSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    bytes_completed: u32,
    requested_remaining: u32,
    segment_count: u32,
    first_chunk_bytes: u32,
    final_chunk_bytes: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    flags: u32,
};

pub const ChrdevResumeView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    reserved: u32,
};

pub const ChrdevResumeSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    flags: u32,
};

pub const ChrdevRetryView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    reserved: u32,
};

pub const ChrdevRetrySummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    retry_count: u32,
    stall_count: u32,
    remaining_retry_budget: u32,
    backoff_ticks: u32,
    flags: u32,
};

pub const ChrdevRequeueView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    queue_depth: u32,
    queue_capacity: u32,
    requeue_budget: u32,
    reserved: u32,
};

pub const ChrdevRequeueSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    projected_remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    retry_count: u32,
    stall_count: u32,
    requeue_count: u32,
    queue_depth_before: u32,
    queue_depth_after: u32,
    remaining_retry_budget: u32,
    remaining_requeue_budget: u32,
    backoff_ticks: u32,
    flags: u32,
};

pub const ChrdevCompleteView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    queue_depth: u32,
    queue_capacity: u32,
    requeue_budget: u32,
    completion_cookie: u64,
    completion_budget: u32,
    reserved: u32,
};

pub const ChrdevCompleteSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    projected_remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    retry_count: u32,
    stall_count: u32,
    requeue_count: u32,
    queue_depth_before: u32,
    queue_depth_after: u32,
    remaining_retry_budget: u32,
    remaining_requeue_budget: u32,
    backoff_ticks: u32,
    completion_cookie: u64,
    completion_status: u32,
    completion_count: u32,
    deferred_count: u32,
    failure_count: u32,
    remaining_completion_budget: u32,
    flags: u32,
};

pub const ChrdevNotifyView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    queue_depth: u32,
    queue_capacity: u32,
    requeue_budget: u32,
    completion_cookie: u64,
    completion_budget: u32,
    notify_mask: u32,
    notify_cookie: u64,
    notify_budget: u32,
    reserved: u32,
};

pub const ChrdevNotifySummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    projected_remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    retry_count: u32,
    stall_count: u32,
    requeue_count: u32,
    queue_depth_before: u32,
    queue_depth_after: u32,
    remaining_retry_budget: u32,
    remaining_requeue_budget: u32,
    backoff_ticks: u32,
    completion_cookie: u64,
    completion_status: u32,
    completion_count: u32,
    deferred_count: u32,
    failure_count: u32,
    remaining_completion_budget: u32,
    notify_mask: u32,
    matched_notify_mask: u32,
    notify_status: u32,
    notify_count: u32,
    deferred_notify_count: u32,
    dropped_notify_count: u32,
    remaining_notify_budget: u32,
    notify_cookie: u64,
    flags: u32,
};

pub const ChrdevNotifyPolicyView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    queue_depth: u32,
    queue_capacity: u32,
    requeue_budget: u32,
    completion_cookie: u64,
    completion_budget: u32,
    notify_mask: u32,
    notify_cookie: u64,
    notify_budget: u32,
    reserved: u32,
    policy_flags: u32,
    policy_reserved: u32,
};

pub const ChrdevNotifyPolicySummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    projected_remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    retry_count: u32,
    stall_count: u32,
    requeue_count: u32,
    queue_depth_before: u32,
    queue_depth_after: u32,
    remaining_retry_budget: u32,
    remaining_requeue_budget: u32,
    backoff_ticks: u32,
    completion_cookie: u64,
    completion_status: u32,
    completion_count: u32,
    deferred_count: u32,
    failure_count: u32,
    remaining_completion_budget: u32,
    notify_mask: u32,
    matched_notify_mask: u32,
    notify_status: u32,
    notify_count: u32,
    deferred_notify_count: u32,
    dropped_notify_count: u32,
    remaining_notify_budget: u32,
    notify_cookie: u64,
    flags: u32,
    policy_flags: u32,
    effective_policy_flags: u32,
    effective_notify_cookie: u64,
    policy_status: u32,
    policy_notify_count: u32,
    policy_deferred_count: u32,
    policy_suppressed_count: u32,
    policy_coalesced_count: u32,
};

pub const ChrdevNotifyBudgetView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    queue_depth: u32,
    queue_capacity: u32,
    requeue_budget: u32,
    completion_cookie: u64,
    completion_budget: u32,
    notify_mask: u32,
    notify_cookie: u64,
    notify_budget: u32,
    reserved: u32,
    policy_flags: u32,
    policy_reserved: u32,
    delivery_budget: u32,
    deferred_budget: u32,
};

pub const ChrdevNotifyBudgetSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    projected_remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    retry_count: u32,
    stall_count: u32,
    requeue_count: u32,
    queue_depth_before: u32,
    queue_depth_after: u32,
    remaining_retry_budget: u32,
    remaining_requeue_budget: u32,
    backoff_ticks: u32,
    completion_cookie: u64,
    completion_status: u32,
    completion_count: u32,
    deferred_count: u32,
    failure_count: u32,
    remaining_completion_budget: u32,
    notify_mask: u32,
    matched_notify_mask: u32,
    notify_status: u32,
    notify_count: u32,
    deferred_notify_count: u32,
    dropped_notify_count: u32,
    remaining_notify_budget: u32,
    notify_cookie: u64,
    flags: u32,
    policy_flags: u32,
    effective_policy_flags: u32,
    effective_notify_cookie: u64,
    policy_status: u32,
    policy_notify_count: u32,
    policy_deferred_count: u32,
    policy_suppressed_count: u32,
    policy_coalesced_count: u32,
    budget_flags: u32,
    delivery_budget_before: u32,
    delivery_budget_after: u32,
    deferred_budget_before: u32,
    deferred_budget_after: u32,
    budget_status: u32,
    budget_notify_count: u32,
    budget_deferred_count: u32,
    budget_dropped_count: u32,
    budget_suppressed_count: u32,
};

pub const ChrdevNotifyAckView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    queue_depth: u32,
    queue_capacity: u32,
    requeue_budget: u32,
    completion_cookie: u64,
    completion_budget: u32,
    notify_mask: u32,
    notify_cookie: u64,
    notify_budget: u32,
    reserved: u32,
    policy_flags: u32,
    policy_reserved: u32,
    delivery_budget: u32,
    deferred_budget: u32,
    ack_mask: u32,
    ack_window: u32,
    ack_cookie: u64,
    ack_observed: u32,
    ack_reserved: u32,
};

pub const ChrdevNotifyAckSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    projected_remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    retry_count: u32,
    stall_count: u32,
    requeue_count: u32,
    queue_depth_before: u32,
    queue_depth_after: u32,
    remaining_retry_budget: u32,
    remaining_requeue_budget: u32,
    backoff_ticks: u32,
    completion_cookie: u64,
    completion_status: u32,
    completion_count: u32,
    deferred_count: u32,
    failure_count: u32,
    remaining_completion_budget: u32,
    notify_mask: u32,
    matched_notify_mask: u32,
    notify_status: u32,
    notify_count: u32,
    deferred_notify_count: u32,
    dropped_notify_count: u32,
    remaining_notify_budget: u32,
    notify_cookie: u64,
    flags: u32,
    policy_flags: u32,
    effective_policy_flags: u32,
    effective_notify_cookie: u64,
    policy_status: u32,
    policy_notify_count: u32,
    policy_deferred_count: u32,
    policy_suppressed_count: u32,
    policy_coalesced_count: u32,
    budget_flags: u32,
    delivery_budget_before: u32,
    delivery_budget_after: u32,
    deferred_budget_before: u32,
    deferred_budget_after: u32,
    budget_status: u32,
    budget_notify_count: u32,
    budget_deferred_count: u32,
    budget_dropped_count: u32,
    budget_suppressed_count: u32,
    ack_mask: u32,
    matched_ack_mask: u32,
    ack_status: u32,
    ack_count: u32,
    deferred_ack_count: u32,
    expired_ack_count: u32,
    skipped_ack_count: u32,
    ack_window_before: u32,
    ack_window_after: u32,
    ack_cookie: u64,
    ack_flags: u32,
};

pub const ChrdevNotifyAckPolicyView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    queue_depth: u32,
    queue_capacity: u32,
    requeue_budget: u32,
    completion_cookie: u64,
    completion_budget: u32,
    notify_mask: u32,
    notify_cookie: u64,
    notify_budget: u32,
    reserved: u32,
    policy_flags: u32,
    policy_reserved: u32,
    delivery_budget: u32,
    deferred_budget: u32,
    ack_mask: u32,
    ack_window: u32,
    ack_cookie: u64,
    ack_observed: u32,
    ack_reserved: u32,
    ack_policy_flags: u32,
    ack_policy_reserved: u32,
};

pub const ChrdevNotifyAckPolicySummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    projected_remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    retry_count: u32,
    stall_count: u32,
    requeue_count: u32,
    queue_depth_before: u32,
    queue_depth_after: u32,
    remaining_retry_budget: u32,
    remaining_requeue_budget: u32,
    backoff_ticks: u32,
    completion_cookie: u64,
    completion_status: u32,
    completion_count: u32,
    deferred_count: u32,
    failure_count: u32,
    remaining_completion_budget: u32,
    notify_mask: u32,
    matched_notify_mask: u32,
    notify_status: u32,
    notify_count: u32,
    deferred_notify_count: u32,
    dropped_notify_count: u32,
    remaining_notify_budget: u32,
    notify_cookie: u64,
    flags: u32,
    policy_flags: u32,
    effective_policy_flags: u32,
    effective_notify_cookie: u64,
    policy_status: u32,
    policy_notify_count: u32,
    policy_deferred_count: u32,
    policy_suppressed_count: u32,
    policy_coalesced_count: u32,
    budget_flags: u32,
    delivery_budget_before: u32,
    delivery_budget_after: u32,
    deferred_budget_before: u32,
    deferred_budget_after: u32,
    budget_status: u32,
    budget_notify_count: u32,
    budget_deferred_count: u32,
    budget_dropped_count: u32,
    budget_suppressed_count: u32,
    ack_mask: u32,
    matched_ack_mask: u32,
    ack_status: u32,
    ack_count: u32,
    deferred_ack_count: u32,
    expired_ack_count: u32,
    skipped_ack_count: u32,
    ack_window_before: u32,
    ack_window_after: u32,
    ack_cookie: u64,
    ack_flags: u32,
    ack_policy_flags: u32,
    effective_ack_policy_flags: u32,
    effective_ack_cookie: u64,
    ack_policy_status: u32,
    policy_acked_count: u32,
    policy_deferred_ack_count: u32,
    policy_suppressed_ack_count: u32,
    policy_coalesced_ack_count: u32,
    policy_expired_ack_count: u32,
    policy_skipped_ack_count: u32,
};

pub const ChrdevNotifyAckBudgetView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    queue_depth: u32,
    queue_capacity: u32,
    requeue_budget: u32,
    completion_cookie: u64,
    completion_budget: u32,
    notify_mask: u32,
    notify_cookie: u64,
    notify_budget: u32,
    reserved: u32,
    policy_flags: u32,
    policy_reserved: u32,
    delivery_budget: u32,
    deferred_budget: u32,
    ack_mask: u32,
    ack_window: u32,
    ack_cookie: u64,
    ack_observed: u32,
    ack_reserved: u32,
    ack_policy_flags: u32,
    ack_policy_reserved: u32,
    ack_budget: u32,
    deferred_ack_budget: u32,
    ack_budget_reserved: u32,
};

pub const ChrdevNotifyAckBudgetSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    projected_remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    retry_count: u32,
    stall_count: u32,
    requeue_count: u32,
    queue_depth_before: u32,
    queue_depth_after: u32,
    remaining_retry_budget: u32,
    remaining_requeue_budget: u32,
    backoff_ticks: u32,
    completion_cookie: u64,
    completion_status: u32,
    completion_count: u32,
    deferred_count: u32,
    failure_count: u32,
    remaining_completion_budget: u32,
    notify_mask: u32,
    matched_notify_mask: u32,
    notify_status: u32,
    notify_count: u32,
    deferred_notify_count: u32,
    dropped_notify_count: u32,
    remaining_notify_budget: u32,
    notify_cookie: u64,
    flags: u32,
    policy_flags: u32,
    effective_policy_flags: u32,
    effective_notify_cookie: u64,
    policy_status: u32,
    policy_notify_count: u32,
    policy_deferred_count: u32,
    policy_suppressed_count: u32,
    policy_coalesced_count: u32,
    budget_flags: u32,
    delivery_budget_before: u32,
    delivery_budget_after: u32,
    deferred_budget_before: u32,
    deferred_budget_after: u32,
    budget_status: u32,
    budget_notify_count: u32,
    budget_deferred_count: u32,
    budget_dropped_count: u32,
    budget_suppressed_count: u32,
    ack_mask: u32,
    matched_ack_mask: u32,
    ack_status: u32,
    ack_count: u32,
    deferred_ack_count: u32,
    expired_ack_count: u32,
    skipped_ack_count: u32,
    ack_window_before: u32,
    ack_window_after: u32,
    ack_cookie: u64,
    ack_flags: u32,
    ack_policy_flags: u32,
    effective_ack_policy_flags: u32,
    effective_ack_cookie: u64,
    ack_policy_status: u32,
    policy_acked_count: u32,
    policy_deferred_ack_count: u32,
    policy_suppressed_ack_count: u32,
    policy_coalesced_ack_count: u32,
    policy_expired_ack_count: u32,
    policy_skipped_ack_count: u32,
    ack_budget_flags: u32,
    ack_budget_before: u32,
    ack_budget_after: u32,
    deferred_ack_budget_before: u32,
    deferred_ack_budget_after: u32,
    ack_budget_status: u32,
    budget_acked_count: u32,
    budget_deferred_ack_count: u32,
    budget_dropped_ack_count: u32,
    budget_suppressed_ack_count: u32,
    budget_skipped_ack_count: u32,
};

pub const ChrdevNotifyAckWindowView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    queue_depth: u32,
    queue_capacity: u32,
    requeue_budget: u32,
    completion_cookie: u64,
    completion_budget: u32,
    notify_mask: u32,
    notify_cookie: u64,
    notify_budget: u32,
    reserved: u32,
    policy_flags: u32,
    policy_reserved: u32,
    delivery_budget: u32,
    deferred_budget: u32,
    ack_mask: u32,
    ack_window: u32,
    ack_cookie: u64,
    ack_observed: u32,
    ack_reserved: u32,
    ack_policy_flags: u32,
    ack_policy_reserved: u32,
    ack_budget: u32,
    deferred_ack_budget: u32,
    ack_budget_reserved: u32,
    window_floor: u32,
    window_reserved: u32,
};

pub const ChrdevNotifyAckWindowPolicyView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    queue_depth: u32,
    queue_capacity: u32,
    requeue_budget: u32,
    completion_cookie: u64,
    completion_budget: u32,
    notify_mask: u32,
    notify_cookie: u64,
    notify_budget: u32,
    reserved: u32,
    policy_flags: u32,
    policy_reserved: u32,
    delivery_budget: u32,
    deferred_budget: u32,
    ack_mask: u32,
    ack_window: u32,
    ack_cookie: u64,
    ack_observed: u32,
    ack_reserved: u32,
    ack_policy_flags: u32,
    ack_policy_reserved: u32,
    ack_budget: u32,
    deferred_ack_budget: u32,
    ack_budget_reserved: u32,
    window_floor: u32,
    window_reserved: u32,
    window_policy_flags: u32,
    window_policy_reserved: u32,
};

pub const ChrdevNotifyAckWindowSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    projected_remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    retry_count: u32,
    stall_count: u32,
    requeue_count: u32,
    queue_depth_before: u32,
    queue_depth_after: u32,
    remaining_retry_budget: u32,
    remaining_requeue_budget: u32,
    backoff_ticks: u32,
    completion_cookie: u64,
    completion_status: u32,
    completion_count: u32,
    deferred_count: u32,
    failure_count: u32,
    remaining_completion_budget: u32,
    notify_mask: u32,
    matched_notify_mask: u32,
    notify_status: u32,
    notify_count: u32,
    deferred_notify_count: u32,
    dropped_notify_count: u32,
    remaining_notify_budget: u32,
    notify_cookie: u64,
    flags: u32,
    policy_flags: u32,
    effective_policy_flags: u32,
    effective_notify_cookie: u64,
    policy_status: u32,
    policy_notify_count: u32,
    policy_deferred_count: u32,
    policy_suppressed_count: u32,
    policy_coalesced_count: u32,
    budget_flags: u32,
    delivery_budget_before: u32,
    delivery_budget_after: u32,
    deferred_budget_before: u32,
    deferred_budget_after: u32,
    budget_status: u32,
    budget_notify_count: u32,
    budget_deferred_count: u32,
    budget_dropped_count: u32,
    budget_suppressed_count: u32,
    ack_mask: u32,
    matched_ack_mask: u32,
    ack_status: u32,
    ack_count: u32,
    deferred_ack_count: u32,
    expired_ack_count: u32,
    skipped_ack_count: u32,
    ack_window_before: u32,
    ack_window_after: u32,
    ack_cookie: u64,
    ack_flags: u32,
    ack_policy_flags: u32,
    effective_ack_policy_flags: u32,
    effective_ack_cookie: u64,
    ack_policy_status: u32,
    policy_acked_count: u32,
    policy_deferred_ack_count: u32,
    policy_suppressed_ack_count: u32,
    policy_coalesced_ack_count: u32,
    policy_expired_ack_count: u32,
    policy_skipped_ack_count: u32,
    ack_budget_flags: u32,
    ack_budget_before: u32,
    ack_budget_after: u32,
    deferred_ack_budget_before: u32,
    deferred_ack_budget_after: u32,
    ack_budget_status: u32,
    budget_acked_count: u32,
    budget_deferred_ack_count: u32,
    budget_dropped_ack_count: u32,
    budget_suppressed_ack_count: u32,
    budget_skipped_ack_count: u32,
    window_flags: u32,
    window_before: u32,
    window_after: u32,
    window_floor: u32,
    window_status: u32,
    window_acked_count: u32,
    window_deferred_count: u32,
    window_dropped_count: u32,
    window_suppressed_count: u32,
    window_skipped_count: u32,
};

pub const ChrdevNotifyAckWindowPolicySummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    projected_remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    retry_count: u32,
    stall_count: u32,
    requeue_count: u32,
    queue_depth_before: u32,
    queue_depth_after: u32,
    remaining_retry_budget: u32,
    remaining_requeue_budget: u32,
    backoff_ticks: u32,
    completion_cookie: u64,
    completion_status: u32,
    completion_count: u32,
    deferred_count: u32,
    failure_count: u32,
    remaining_completion_budget: u32,
    notify_mask: u32,
    matched_notify_mask: u32,
    notify_status: u32,
    notify_count: u32,
    deferred_notify_count: u32,
    dropped_notify_count: u32,
    remaining_notify_budget: u32,
    notify_cookie: u64,
    flags: u32,
    policy_flags: u32,
    effective_policy_flags: u32,
    effective_notify_cookie: u64,
    policy_status: u32,
    policy_notify_count: u32,
    policy_deferred_count: u32,
    policy_suppressed_count: u32,
    policy_coalesced_count: u32,
    budget_flags: u32,
    delivery_budget_before: u32,
    delivery_budget_after: u32,
    deferred_budget_before: u32,
    deferred_budget_after: u32,
    budget_status: u32,
    budget_notify_count: u32,
    budget_deferred_count: u32,
    budget_dropped_count: u32,
    budget_suppressed_count: u32,
    ack_mask: u32,
    matched_ack_mask: u32,
    ack_status: u32,
    ack_count: u32,
    deferred_ack_count: u32,
    expired_ack_count: u32,
    skipped_ack_count: u32,
    ack_window_before: u32,
    ack_window_after: u32,
    ack_cookie: u64,
    ack_flags: u32,
    ack_policy_flags: u32,
    effective_ack_policy_flags: u32,
    effective_ack_cookie: u64,
    ack_policy_status: u32,
    policy_acked_count: u32,
    policy_deferred_ack_count: u32,
    policy_suppressed_ack_count: u32,
    policy_coalesced_ack_count: u32,
    policy_expired_ack_count: u32,
    policy_skipped_ack_count: u32,
    ack_budget_flags: u32,
    ack_budget_before: u32,
    ack_budget_after: u32,
    deferred_ack_budget_before: u32,
    deferred_ack_budget_after: u32,
    ack_budget_status: u32,
    budget_acked_count: u32,
    budget_deferred_ack_count: u32,
    budget_dropped_ack_count: u32,
    budget_suppressed_ack_count: u32,
    budget_skipped_ack_count: u32,
    window_flags: u32,
    window_before: u32,
    window_after: u32,
    window_floor: u32,
    window_status: u32,
    window_acked_count: u32,
    window_deferred_count: u32,
    window_dropped_count: u32,
    window_suppressed_count: u32,
    window_skipped_count: u32,
    window_policy_flags: u32,
    effective_window_policy_flags: u32,
    effective_window_cookie: u64,
    window_policy_status: u32,
    policy_window_acked_count: u32,
    policy_window_deferred_count: u32,
    policy_window_suppressed_count: u32,
    policy_window_coalesced_count: u32,
    policy_window_dropped_count: u32,
    policy_window_skipped_count: u32,
};

pub const ChrdevNotifyAckWindowPolicyBudgetView = extern struct {
    bits_addr: usize,
    major: u32,
    first_minor: u32,
    minor_count: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    target_minor: u32,
    requested_mode: u32,
    supported_mode: u32,
    available_ops: u32,
    io_op: u32,
    requested_bytes: u32,
    max_chunk_bytes: u32,
    file_offset: u64,
    bytes_completed: u32,
    max_segments: u32,
    resume_passes: u32,
    retry_budget: u32,
    stall_budget: u32,
    backoff_quanta: u32,
    queue_depth: u32,
    queue_capacity: u32,
    requeue_budget: u32,
    completion_cookie: u64,
    completion_budget: u32,
    notify_mask: u32,
    notify_cookie: u64,
    notify_budget: u32,
    reserved: u32,
    policy_flags: u32,
    policy_reserved: u32,
    delivery_budget: u32,
    deferred_budget: u32,
    ack_mask: u32,
    ack_window: u32,
    ack_cookie: u64,
    ack_observed: u32,
    ack_reserved: u32,
    ack_policy_flags: u32,
    ack_policy_reserved: u32,
    ack_budget: u32,
    deferred_ack_budget: u32,
    ack_budget_reserved: u32,
    window_floor: u32,
    window_reserved: u32,
    window_policy_flags: u32,
    window_policy_reserved: u32,
    window_policy_budget: u32,
    deferred_window_policy_budget: u32,
    window_policy_budget_reserved: u32,
};

pub const ChrdevNotifyAckWindowPolicyBudgetSummary = extern struct {
    major: u32,
    target_minor: u32,
    selected_count: u32,
    resolved_index: u32,
    resolved_dev: u32,
    granted_mode: u32,
    io_op: u32,
    requested_bytes: u32,
    start_offset: u64,
    next_offset: u64,
    initial_bytes_completed: u32,
    final_bytes_completed: u32,
    pass_count: u32,
    issued_bytes: u32,
    remaining_bytes: u32,
    projected_remaining_bytes: u32,
    entry_ops: u32,
    data_ops: u32,
    exit_ops: u32,
    blocked_ops: u32,
    retry_count: u32,
    stall_count: u32,
    requeue_count: u32,
    queue_depth_before: u32,
    queue_depth_after: u32,
    remaining_retry_budget: u32,
    remaining_requeue_budget: u32,
    backoff_ticks: u32,
    completion_cookie: u64,
    completion_status: u32,
    completion_count: u32,
    deferred_count: u32,
    failure_count: u32,
    remaining_completion_budget: u32,
    notify_mask: u32,
    matched_notify_mask: u32,
    notify_status: u32,
    notify_count: u32,
    deferred_notify_count: u32,
    dropped_notify_count: u32,
    remaining_notify_budget: u32,
    notify_cookie: u64,
    flags: u32,
    policy_flags: u32,
    effective_policy_flags: u32,
    effective_notify_cookie: u64,
    policy_status: u32,
    policy_notify_count: u32,
    policy_deferred_count: u32,
    policy_suppressed_count: u32,
    policy_coalesced_count: u32,
    budget_flags: u32,
    delivery_budget_before: u32,
    delivery_budget_after: u32,
    deferred_budget_before: u32,
    deferred_budget_after: u32,
    budget_status: u32,
    budget_notify_count: u32,
    budget_deferred_count: u32,
    budget_dropped_count: u32,
    budget_suppressed_count: u32,
    ack_mask: u32,
    matched_ack_mask: u32,
    ack_status: u32,
    ack_count: u32,
    deferred_ack_count: u32,
    expired_ack_count: u32,
    skipped_ack_count: u32,
    ack_window_before: u32,
    ack_window_after: u32,
    ack_cookie: u64,
    ack_flags: u32,
    ack_policy_flags: u32,
    effective_ack_policy_flags: u32,
    effective_ack_cookie: u64,
    ack_policy_status: u32,
    policy_acked_count: u32,
    policy_deferred_ack_count: u32,
    policy_suppressed_ack_count: u32,
    policy_coalesced_ack_count: u32,
    policy_expired_ack_count: u32,
    policy_skipped_ack_count: u32,
    ack_budget_flags: u32,
    ack_budget_before: u32,
    ack_budget_after: u32,
    deferred_ack_budget_before: u32,
    deferred_ack_budget_after: u32,
    ack_budget_status: u32,
    budget_acked_count: u32,
    budget_deferred_ack_count: u32,
    budget_dropped_ack_count: u32,
    budget_suppressed_ack_count: u32,
    budget_skipped_ack_count: u32,
    window_flags: u32,
    window_before: u32,
    window_after: u32,
    window_floor: u32,
    window_status: u32,
    window_acked_count: u32,
    window_deferred_count: u32,
    window_dropped_count: u32,
    window_suppressed_count: u32,
    window_skipped_count: u32,
    window_policy_flags: u32,
    effective_window_policy_flags: u32,
    effective_window_cookie: u64,
    window_policy_status: u32,
    policy_window_acked_count: u32,
    policy_window_deferred_count: u32,
    policy_window_suppressed_count: u32,
    policy_window_coalesced_count: u32,
    policy_window_dropped_count: u32,
    policy_window_skipped_count: u32,
    window_policy_budget_flags: u32,
    window_policy_budget_before: u32,
    window_policy_budget_after: u32,
    deferred_window_policy_budget_before: u32,
    deferred_window_policy_budget_after: u32,
    window_policy_budget_status: u32,
    budget_window_acked_count: u32,
    budget_window_deferred_count: u32,
    budget_window_suppressed_count: u32,
    budget_window_coalesced_count: u32,
    budget_window_dropped_count: u32,
    budget_window_skipped_count: u32,
};

pub const MmioRange = extern struct {
    base_addr: usize,
    length: u32,
    stride: u32,
};

pub const InteropPolicy = extern struct {
    panic_mode: u8,
    allocator_mode: u8,
    unsafe_scope: u8,
    reserved: u8,
};

pub fn defaultHeader(flags: u16) BoundaryHeader {
    return .{
        .size = @sizeOf(BoundaryHeader),
        .abi_version = ABI_VERSION,
        .flags = flags,
    };
}

test "phase3 abi constants stay stable" {
    try std.testing.expectEqual(@as(u16, 1), ABI_VERSION);
    try std.testing.expectEqual(@as(u16, 1), @intFromEnum(Facility.kernel));
    try std.testing.expectEqual(@as(u8, 0), @intFromEnum(PanicMode.abort));
    try std.testing.expectEqual(@as(u8, 0), @intFromEnum(AllocatorMode.caller_provided));
    try std.testing.expectEqual(@as(u8, 2), @intFromEnum(UnsafeScope.raw_pointer_bridge));
    try std.testing.expectEqual(@as(u32, 4), LIST_FLAG_CIRCULAR);
    try std.testing.expectEqual(@as(u32, 4), HLIST_FLAG_TERMINATED);
    try std.testing.expectEqual(@as(u16, 1), ERR_PTR_FLAG_ERROR);
    try std.testing.expectEqual(@as(u32, 1), XA_VALUE_FLAG_VALUE);
    try std.testing.expectEqual(@as(u32, 1), XA_SLOT_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 1), IDR_SLOT_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 1), IDA_BITMAP_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 2), IDA_BITMAP_FLAG_EXHAUSTED);
    try std.testing.expectEqual(@as(u32, 1), IDA_ALLOC_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 2), IDA_ALLOC_FLAG_FOUND);
    try std.testing.expectEqual(@as(u32, 4), IDA_ALLOC_FLAG_EXHAUSTED);
    try std.testing.expectEqual(@as(u32, 1), IDA_RANGE_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 2), IDA_RANGE_FLAG_FOUND);
    try std.testing.expectEqual(@as(u32, 4), IDA_RANGE_FLAG_EXHAUSTED);
    try std.testing.expectEqual(@as(u32, 1), IDA_RANGE_SET_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 2), IDA_RANGE_SET_FLAG_FOUND);
    try std.testing.expectEqual(@as(u32, 4), IDA_RANGE_SET_FLAG_EXHAUSTED);
    try std.testing.expectEqual(@as(u32, 8), IDA_RANGE_SET_FLAG_SELECTED);
    try std.testing.expectEqual(@as(u32, 1), IDA_POLICY_FIRST_FIT);
    try std.testing.expectEqual(@as(u32, 2), IDA_POLICY_LAST_FIT);
    try std.testing.expectEqual(@as(u32, 1), IDA_POLICY_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 2), IDA_POLICY_FLAG_FOUND);
    try std.testing.expectEqual(@as(u32, 4), IDA_POLICY_FLAG_EXHAUSTED);
}

test "phase3 abi layouts stay stable" {
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(ExportStatus));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(BitmapView));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(CpuMaskView));
    try std.testing.expectEqual(@as(usize, 16), @sizeOf(BitmapSummary));
    try std.testing.expectEqual(@as(usize, 16), @sizeOf(CpuMaskSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(ListHeadRef));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(ListView));
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(ListSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @sizeOf(HListHeadRef));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(HListNodeRef));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(HListView));
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(HListSummary));
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(ErrPtrSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(XaValueSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(XaSlotView));
    try std.testing.expectEqual(@as(usize, 24), @sizeOf(XaSlotSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 16), @sizeOf(IdrSlotView));
    try std.testing.expectEqual(@as(usize, 32), @sizeOf(IdrSlotSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 16), @sizeOf(IdaBitmapView));
    try std.testing.expectEqual(@as(usize, 24), @sizeOf(IdaBitmapSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 24), @sizeOf(IdaAllocView));
    try std.testing.expectEqual(@as(usize, 24), @sizeOf(IdaAllocSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 24), @sizeOf(IdaRangeView));
    try std.testing.expectEqual(@as(usize, 24), @sizeOf(IdaRangeSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 32), @sizeOf(IdaRangeSetView));
    try std.testing.expectEqual(@as(usize, 32), @sizeOf(IdaRangeSetSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 24), @sizeOf(IdaPolicyView));
    try std.testing.expectEqual(@as(usize, 24), @sizeOf(IdaPolicySummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(MmioRange));
    try std.testing.expectEqual(@as(usize, 4), @sizeOf(InteropPolicy));
}
