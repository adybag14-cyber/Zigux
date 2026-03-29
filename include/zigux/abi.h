#ifndef _ZIGUX_ABI_H
#define _ZIGUX_ABI_H

#ifdef __KERNEL__
#include <linux/types.h>
typedef __u8 zigux_u8;
typedef __u16 zigux_u16;
typedef __u32 zigux_u32;
typedef __u64 zigux_u64;
typedef __s32 zigux_s32;
#else
#include <stdint.h>
typedef uint8_t zigux_u8;
typedef uint16_t zigux_u16;
typedef uint32_t zigux_u32;
typedef uint64_t zigux_u64;
typedef int32_t zigux_s32;
#endif

#define ZIGUX_ABI_VERSION 1U

#define ZIGUX_FACILITY_KERNEL 1U
#define ZIGUX_FACILITY_HELPERS 2U
#define ZIGUX_FACILITY_DRIVERS 3U

#define ZIGUX_STATUS_FLAG_ERROR 1U

#define ZIGUX_PANIC_ABORT 0U
#define ZIGUX_PANIC_BUG 1U
#define ZIGUX_PANIC_WARN 2U

#define ZIGUX_ALLOC_CALLER_PROVIDED 0U
#define ZIGUX_ALLOC_KERNEL_HEAP 1U
#define ZIGUX_ALLOC_ARENA 2U

#define ZIGUX_UNSAFE_NONE 0U
#define ZIGUX_UNSAFE_VOLATILE_MMIO 1U
#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U

#define ZIGUX_LIST_FLAG_EMPTY 1U
#define ZIGUX_LIST_FLAG_SINGULAR 2U
#define ZIGUX_LIST_FLAG_CIRCULAR 4U
#define ZIGUX_LIST_FLAG_TRUNCATED 8U

#define ZIGUX_HLIST_FLAG_EMPTY 1U
#define ZIGUX_HLIST_FLAG_SINGULAR 2U
#define ZIGUX_HLIST_FLAG_TERMINATED 4U
#define ZIGUX_HLIST_FLAG_TRUNCATED 8U

#define ZIGUX_ERR_PTR_FLAG_ERROR 1U
#define ZIGUX_ERR_PTR_FLAG_NULL 2U

#define ZIGUX_XA_VALUE_FLAG_VALUE 1U
#define ZIGUX_XA_VALUE_FLAG_PLAIN 2U

#define ZIGUX_XA_SLOT_FLAG_TRUNCATED 1U
#define ZIGUX_IDR_SLOT_FLAG_TRUNCATED 1U
#define ZIGUX_IDA_BITMAP_FLAG_TRUNCATED 1U
#define ZIGUX_IDA_BITMAP_FLAG_EXHAUSTED 2U
#define ZIGUX_IDA_ALLOC_FLAG_TRUNCATED 1U
#define ZIGUX_IDA_ALLOC_FLAG_FOUND 2U
#define ZIGUX_IDA_ALLOC_FLAG_EXHAUSTED 4U
#define ZIGUX_IDA_RANGE_FLAG_TRUNCATED 1U
#define ZIGUX_IDA_RANGE_FLAG_FOUND 2U
#define ZIGUX_IDA_RANGE_FLAG_EXHAUSTED 4U
#define ZIGUX_IDA_RANGE_SET_FLAG_TRUNCATED 1U
#define ZIGUX_IDA_RANGE_SET_FLAG_FOUND 2U
#define ZIGUX_IDA_RANGE_SET_FLAG_EXHAUSTED 4U
#define ZIGUX_IDA_RANGE_SET_FLAG_SELECTED 8U
#define ZIGUX_IDA_POLICY_FIRST_FIT 1U
#define ZIGUX_IDA_POLICY_LAST_FIT 2U
#define ZIGUX_IDA_POLICY_FLAG_TRUNCATED 1U
#define ZIGUX_IDA_POLICY_FLAG_FOUND 2U
#define ZIGUX_IDA_POLICY_FLAG_EXHAUSTED 4U
#define ZIGUX_MINOR_ALLOC_FLAG_TRUNCATED 1U
#define ZIGUX_MINOR_ALLOC_FLAG_FOUND 2U
#define ZIGUX_MINOR_ALLOC_FLAG_EXHAUSTED 4U
#define ZIGUX_DEV_REGION_FLAG_TRUNCATED 1U
#define ZIGUX_DEV_REGION_FLAG_FOUND 2U
#define ZIGUX_DEV_REGION_FLAG_EXHAUSTED 4U
#define ZIGUX_CDEV_ADD_FLAG_TRUNCATED 1U
#define ZIGUX_CDEV_ADD_FLAG_FOUND 2U
#define ZIGUX_CDEV_ADD_FLAG_EXHAUSTED 4U
#define ZIGUX_CDEV_LOOKUP_FLAG_TRUNCATED 1U
#define ZIGUX_CDEV_LOOKUP_FLAG_FOUND 2U
#define ZIGUX_CDEV_LOOKUP_FLAG_EXHAUSTED 4U
#define ZIGUX_CDEV_LOOKUP_FLAG_HIT 8U
#define ZIGUX_CDEV_LOOKUP_INDEX_NONE 0xffffffffU
#define ZIGUX_CHRDEV_MODE_READ 1U
#define ZIGUX_CHRDEV_MODE_WRITE 2U
#define ZIGUX_CHRDEV_OPEN_FLAG_TRUNCATED 1U
#define ZIGUX_CHRDEV_OPEN_FLAG_FOUND 2U
#define ZIGUX_CHRDEV_OPEN_FLAG_EXHAUSTED 4U
#define ZIGUX_CHRDEV_OPEN_FLAG_HIT 8U
#define ZIGUX_CHRDEV_OPEN_FLAG_PERMITTED 16U
#define ZIGUX_CHRDEV_OPEN_FLAG_DENIED 32U
#define ZIGUX_CHRDEV_OPEN_INDEX_NONE 0xffffffffU
#define ZIGUX_CHRDEV_FOP_OPEN 1U
#define ZIGUX_CHRDEV_FOP_RELEASE 2U
#define ZIGUX_CHRDEV_FOP_READ 4U
#define ZIGUX_CHRDEV_FOP_WRITE 8U
#define ZIGUX_CHRDEV_FOPS_FLAG_TRUNCATED 1U
#define ZIGUX_CHRDEV_FOPS_FLAG_FOUND 2U
#define ZIGUX_CHRDEV_FOPS_FLAG_EXHAUSTED 4U
#define ZIGUX_CHRDEV_FOPS_FLAG_HIT 8U
#define ZIGUX_CHRDEV_FOPS_FLAG_PERMITTED 16U
#define ZIGUX_CHRDEV_FOPS_FLAG_DENIED 32U
#define ZIGUX_CHRDEV_FOPS_FLAG_ROUTABLE 64U
#define ZIGUX_CHRDEV_FOPS_FLAG_MISSING_OPS 128U
#define ZIGUX_CHRDEV_FOPS_INDEX_NONE 0xffffffffU
#define ZIGUX_CHRDEV_ROUTE_FLAG_TRUNCATED 1U
#define ZIGUX_CHRDEV_ROUTE_FLAG_FOUND 2U
#define ZIGUX_CHRDEV_ROUTE_FLAG_EXHAUSTED 4U
#define ZIGUX_CHRDEV_ROUTE_FLAG_HIT 8U
#define ZIGUX_CHRDEV_ROUTE_FLAG_PERMITTED 16U
#define ZIGUX_CHRDEV_ROUTE_FLAG_DENIED 32U
#define ZIGUX_CHRDEV_ROUTE_FLAG_ROUTABLE 64U
#define ZIGUX_CHRDEV_ROUTE_FLAG_BLOCKED 128U
#define ZIGUX_CHRDEV_ROUTE_INDEX_NONE 0xffffffffU
#define ZIGUX_CHRDEV_IO_OP_READ 1U
#define ZIGUX_CHRDEV_IO_OP_WRITE 2U
#define ZIGUX_CHRDEV_IO_FLAG_TRUNCATED 1U
#define ZIGUX_CHRDEV_IO_FLAG_FOUND 2U
#define ZIGUX_CHRDEV_IO_FLAG_EXHAUSTED 4U
#define ZIGUX_CHRDEV_IO_FLAG_HIT 8U
#define ZIGUX_CHRDEV_IO_FLAG_PERMITTED 16U
#define ZIGUX_CHRDEV_IO_FLAG_DENIED 32U
#define ZIGUX_CHRDEV_IO_FLAG_ROUTABLE 64U
#define ZIGUX_CHRDEV_IO_FLAG_BLOCKED 128U
#define ZIGUX_CHRDEV_IO_FLAG_DISPATCHABLE 256U
#define ZIGUX_CHRDEV_IO_INDEX_NONE 0xffffffffU
#define ZIGUX_CHRDEV_XFER_FLAG_TRUNCATED 1U
#define ZIGUX_CHRDEV_XFER_FLAG_FOUND 2U
#define ZIGUX_CHRDEV_XFER_FLAG_EXHAUSTED 4U
#define ZIGUX_CHRDEV_XFER_FLAG_HIT 8U
#define ZIGUX_CHRDEV_XFER_FLAG_PERMITTED 16U
#define ZIGUX_CHRDEV_XFER_FLAG_DENIED 32U
#define ZIGUX_CHRDEV_XFER_FLAG_ROUTABLE 64U
#define ZIGUX_CHRDEV_XFER_FLAG_BLOCKED 128U
#define ZIGUX_CHRDEV_XFER_FLAG_DISPATCHABLE 256U
#define ZIGUX_CHRDEV_XFER_FLAG_RESUMED 512U
#define ZIGUX_CHRDEV_XFER_FLAG_CONTINUABLE 1024U
#define ZIGUX_CHRDEV_XFER_FLAG_COMPLETES 2048U
#define ZIGUX_CHRDEV_XFER_INDEX_NONE 0xffffffffU
#define ZIGUX_CHRDEV_RESUME_FLAG_TRUNCATED 1U
#define ZIGUX_CHRDEV_RESUME_FLAG_FOUND 2U
#define ZIGUX_CHRDEV_RESUME_FLAG_EXHAUSTED 4U
#define ZIGUX_CHRDEV_RESUME_FLAG_HIT 8U
#define ZIGUX_CHRDEV_RESUME_FLAG_PERMITTED 16U
#define ZIGUX_CHRDEV_RESUME_FLAG_DENIED 32U
#define ZIGUX_CHRDEV_RESUME_FLAG_ROUTABLE 64U
#define ZIGUX_CHRDEV_RESUME_FLAG_BLOCKED 128U
#define ZIGUX_CHRDEV_RESUME_FLAG_DISPATCHABLE 256U
#define ZIGUX_CHRDEV_RESUME_FLAG_RESUMED 512U
#define ZIGUX_CHRDEV_RESUME_FLAG_CONTINUABLE 1024U
#define ZIGUX_CHRDEV_RESUME_FLAG_COMPLETES 2048U
#define ZIGUX_CHRDEV_RESUME_FLAG_PROGRESSED 4096U
#define ZIGUX_CHRDEV_RESUME_FLAG_STALLED 8192U
#define ZIGUX_CHRDEV_RESUME_FLAG_COMPLETE_OK 16384U
#define ZIGUX_CHRDEV_RESUME_INDEX_NONE 0xffffffffU
#define ZIGUX_CHRDEV_RETRY_FLAG_TRUNCATED 1U
#define ZIGUX_CHRDEV_RETRY_FLAG_FOUND 2U
#define ZIGUX_CHRDEV_RETRY_FLAG_EXHAUSTED 4U
#define ZIGUX_CHRDEV_RETRY_FLAG_HIT 8U
#define ZIGUX_CHRDEV_RETRY_FLAG_PERMITTED 16U
#define ZIGUX_CHRDEV_RETRY_FLAG_DENIED 32U
#define ZIGUX_CHRDEV_RETRY_FLAG_ROUTABLE 64U
#define ZIGUX_CHRDEV_RETRY_FLAG_BLOCKED 128U
#define ZIGUX_CHRDEV_RETRY_FLAG_DISPATCHABLE 256U
#define ZIGUX_CHRDEV_RETRY_FLAG_RESUMED 512U
#define ZIGUX_CHRDEV_RETRY_FLAG_CONTINUABLE 1024U
#define ZIGUX_CHRDEV_RETRY_FLAG_COMPLETES 2048U
#define ZIGUX_CHRDEV_RETRY_FLAG_PROGRESSED 4096U
#define ZIGUX_CHRDEV_RETRY_FLAG_STALLED 8192U
#define ZIGUX_CHRDEV_RETRY_FLAG_COMPLETE_OK 16384U
#define ZIGUX_CHRDEV_RETRY_FLAG_RETRYABLE 32768U
#define ZIGUX_CHRDEV_RETRY_FLAG_RETRY_PLANNED 65536U
#define ZIGUX_CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED 131072U
#define ZIGUX_CHRDEV_RETRY_FLAG_BACKOFF_APPLIED 262144U
#define ZIGUX_CHRDEV_RETRY_FLAG_FAILS 524288U
#define ZIGUX_CHRDEV_RETRY_INDEX_NONE 0xffffffffU
#define ZIGUX_CHRDEV_REQUEUE_FLAG_TRUNCATED 1U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_FOUND 2U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_EXHAUSTED 4U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_HIT 8U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_PERMITTED 16U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_DENIED 32U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_ROUTABLE 64U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_BLOCKED 128U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_DISPATCHABLE 256U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_RESUMED 512U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_CONTINUABLE 1024U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_COMPLETES 2048U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_PROGRESSED 4096U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_STALLED 8192U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_COMPLETE_OK 16384U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_RETRYABLE 32768U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_RETRY_PLANNED 65536U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_RETRY_EXHAUSTED 131072U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_BACKOFF_APPLIED 262144U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_FAILS 524288U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_REQUEUEABLE 1048576U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_REQUEUE_PLANNED 2097152U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_DELAYED 4194304U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_SATURATED 8388608U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_DROPPED 16777216U
#define ZIGUX_CHRDEV_REQUEUE_FLAG_COMPLETE 33554432U
#define ZIGUX_CHRDEV_REQUEUE_INDEX_NONE 0xffffffffU
#define ZIGUX_CHRDEV_COMPLETE_FLAG_TRUNCATED 1U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_FOUND 2U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_EXHAUSTED 4U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_HIT 8U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_PERMITTED 16U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_DENIED 32U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_ROUTABLE 64U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_BLOCKED 128U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_DISPATCHABLE 256U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_RESUMED 512U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_CONTINUABLE 1024U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETES 2048U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_PROGRESSED 4096U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_STALLED 8192U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETE_OK 16384U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_RETRYABLE 32768U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_RETRY_PLANNED 65536U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_RETRY_EXHAUSTED 131072U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_BACKOFF_APPLIED 262144U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_FAILS 524288U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_REQUEUEABLE 1048576U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_REQUEUE_PLANNED 2097152U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_DELAYED 4194304U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_SATURATED 8388608U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_DROPPED 16777216U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETE 33554432U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETION_PLANNED 67108864U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION 134217728U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_FAILURE_COMPLETION 268435456U
#define ZIGUX_CHRDEV_COMPLETE_FLAG_FINALIZED 536870912U
#define ZIGUX_CHRDEV_COMPLETE_INDEX_NONE 0xffffffffU
#define ZIGUX_CHRDEV_COMPLETE_STATUS_NONE 0U
#define ZIGUX_CHRDEV_COMPLETE_STATUS_OK 1U
#define ZIGUX_CHRDEV_COMPLETE_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_COMPLETE_STATUS_FAILED 3U
#define ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS 1U
#define ZIGUX_CHRDEV_NOTIFY_MASK_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE 4U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_TRUNCATED 1U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_FOUND 2U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_EXHAUSTED 4U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_HIT 8U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_PERMITTED 16U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_DENIED 32U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_ROUTABLE 64U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_BLOCKED 128U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_DISPATCHABLE 256U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_RESUMED 512U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_CONTINUABLE 1024U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_COMPLETES 2048U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_PROGRESSED 4096U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_STALLED 8192U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_COMPLETE_OK 16384U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_RETRYABLE 32768U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_RETRY_PLANNED 65536U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_RETRY_EXHAUSTED 131072U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_BACKOFF_APPLIED 262144U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_FAILS 524288U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_REQUEUEABLE 1048576U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_REQUEUE_PLANNED 2097152U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_DELAYED 4194304U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_SATURATED 8388608U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_DROPPED 16777216U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_COMPLETE 33554432U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_COMPLETION_PLANNED 67108864U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_DEFERRED_COMPLETION 134217728U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_FAILURE_COMPLETION 268435456U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_FINALIZED 536870912U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_MATCHED_NOTIFY 1073741824U
#define ZIGUX_CHRDEV_NOTIFY_FLAG_NOTIFY_PLANNED 2147483648U
#define ZIGUX_CHRDEV_NOTIFY_INDEX_NONE 0xffffffffU
#define ZIGUX_CHRDEV_NOTIFY_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_STATUS_DELIVERED 1U
#define ZIGUX_CHRDEV_NOTIFY_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_STATUS_DROPPED 3U
#define ZIGUX_CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED 1U
#define ZIGUX_CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE 2U
#define ZIGUX_CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE 4U
#define ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_DELIVERED 1U
#define ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED 3U
#define ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_COALESCED 4U
#define ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_BUDGET_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_DELIVERY_BUDGET_USED 2U
#define ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_DEFERRED_BUDGET_USED 4U
#define ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_DELIVERY_BUDGET_EXHAUSTED 8U
#define ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_DEFERRED_BUDGET_EXHAUSTED 16U
#define ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_ISSUED 1U
#define ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_DROPPED 3U
#define ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_SUPPRESSED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_MASK_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_MASK_DROPPED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_MASK_SUPPRESSED 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_APPLICABLE 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_ACKED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_DEFERRED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_EXPIRED 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_SKIPPED 16U
#define ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_WINDOW_USED 32U
#define ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_WINDOW_EXHAUSTED 64U
#define ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_EXPIRED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_SKIPPED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_SUPPRESS_EXPIRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_COALESCE_COOKIE 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_SUPPRESSED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_COALESCED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_EXPIRED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_SKIPPED 6U
#define ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_BUDGET_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_ACK_BUDGET_USED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_DEFERRED_ACK_BUDGET_USED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_ACK_BUDGET_EXHAUSTED 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_DEFERRED_ACK_BUDGET_EXHAUSTED 16U
#define ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DROPPED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_SUPPRESSED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_SKIPPED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_FLAG_WINDOW_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_FLAG_WINDOW_USED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_FLAG_WINDOW_EXHAUSTED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_FLAG_FLOOR_HELD 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_FLAG_FLOOR_BLOCKED 16U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_DROPPED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_SUPPRESSED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_SKIPPED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SUPPRESSED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_COALESCED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DROPPED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SKIPPED 6U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_BUDGET_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_WINDOW_POLICY_BUDGET_USED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_WINDOW_POLICY_BUDGET_USED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_WINDOW_POLICY_BUDGET_EXHAUSTED 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_WINDOW_POLICY_BUDGET_EXHAUSTED 16U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_SUPPRESSED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_COALESCED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DROPPED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_SKIPPED 6U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_USED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_FLAG_FLOOR_HELD 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_FLAG_FLOOR_BLOCKED 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_EXHAUSTED 16U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SUPPRESSED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_COALESCED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DROPPED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SKIPPED 6U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_BUDGET_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_WINDOW_DELIVERY_BUDGET_USED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_USED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_WINDOW_DELIVERY_BUDGET_EXHAUSTED 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_EXHAUSTED 16U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_SUPPRESSED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_SKIPPED 6U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_USED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_FLOOR_HELD 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_FLOOR_BLOCKED 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_EXHAUSTED 16U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SUPPRESSED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_COALESCED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED 6U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_WINDOW_DELIVERY_WINDOW_BUDGET_USED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_USED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED 16U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SUPPRESSED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_COALESCED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SKIPPED 6U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_USED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_FLOOR_HELD 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_FLOOR_BLOCKED 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_EXHAUSTED 16U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SUPPRESSED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_COALESCED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DROPPED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED 6U

struct zigux_boundary_header {
	zigux_u32 size;
	zigux_u16 abi_version;
	zigux_u16 flags;
};

struct zigux_export_status {
	zigux_s32 code;
	zigux_u16 facility;
	zigux_u16 flags;
};

struct zigux_bitmap_view {
	unsigned long words_addr;
	zigux_u32 nbits;
	zigux_u32 word_count;
};

struct zigux_cpumask_view {
	unsigned long bits_addr;
	zigux_u32 nr_cpu_ids;
	zigux_u32 reserved;
};

struct zigux_bitmap_summary {
	zigux_u32 first_set;
	zigux_u32 first_zero;
	zigux_u32 weight;
	zigux_u32 reserved;
};

struct zigux_cpumask_summary {
	zigux_u32 first_cpu;
	zigux_u32 next_cpu;
	zigux_u32 weight;
	zigux_u32 reserved;
};

struct zigux_list_head_ref {
	unsigned long next_addr;
	unsigned long prev_addr;
};

struct zigux_list_view {
	unsigned long head_addr;
	zigux_u32 max_nodes;
	zigux_u32 reserved;
};

struct zigux_list_summary {
	zigux_u32 length;
	zigux_u32 flags;
};

struct zigux_hlist_head_ref {
	unsigned long first_addr;
};

struct zigux_hlist_node_ref {
	unsigned long next_addr;
	unsigned long pprev_addr;
};

struct zigux_hlist_view {
	unsigned long head_addr;
	zigux_u32 max_nodes;
	zigux_u32 reserved;
};

struct zigux_hlist_summary {
	zigux_u32 length;
	zigux_u32 flags;
};

struct zigux_err_ptr_summary {
	zigux_s32 errno_code;
	zigux_u16 flags;
	zigux_u16 reserved;
};

struct zigux_xa_value_summary {
	unsigned long raw_addr;
	zigux_u32 decoded_value;
	zigux_u32 flags;
};

struct zigux_xa_slot_view {
	unsigned long slots_addr;
	zigux_u32 slot_count;
	zigux_u32 max_scan;
};

struct zigux_xa_slot_summary {
	zigux_u32 scanned_count;
	zigux_u32 null_count;
	zigux_u32 value_count;
	zigux_u32 error_count;
	zigux_u32 plain_count;
	zigux_u32 flags;
};

struct zigux_idr_slot_view {
	unsigned long slots_addr;
	zigux_u32 base_id;
	zigux_u32 slot_count;
	zigux_u32 max_scan;
	zigux_u32 reserved;
};

struct zigux_idr_slot_summary {
	zigux_u32 scanned_count;
	zigux_u32 present_count;
	zigux_u32 value_count;
	zigux_u32 error_count;
	zigux_u32 plain_count;
	zigux_u32 first_present_id;
	zigux_u32 next_free_id;
	zigux_u32 flags;
};

struct zigux_ida_bitmap_view {
	unsigned long bits_addr;
	zigux_u32 base_id;
	zigux_u32 nbits;
	zigux_u32 max_scan;
	zigux_u32 reserved;
};

struct zigux_ida_bitmap_summary {
	zigux_u32 scanned_count;
	zigux_u32 allocated_count;
	zigux_u32 first_allocated_id;
	zigux_u32 first_free_id;
	zigux_u32 flags;
	zigux_u32 reserved;
};

struct zigux_ida_alloc_view {
	unsigned long bits_addr;
	zigux_u32 base_id;
	zigux_u32 nbits;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 reserved;
};

struct zigux_ida_alloc_summary {
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 first_fit_id;
	zigux_u32 longest_free_run;
	zigux_u32 flags;
	zigux_u32 reserved;
};

struct zigux_ida_range_view {
	unsigned long bits_addr;
	zigux_u32 base_id;
	zigux_u32 nbits;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 max_ranges;
	zigux_u32 reserved;
};

struct zigux_ida_range_summary {
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 candidate_range_count;
	zigux_u32 first_range_id;
	zigux_u32 last_range_id;
	zigux_u32 flags;
};

struct zigux_ida_range_set_view {
	unsigned long bits_addr;
	zigux_u32 base_id;
	zigux_u32 nbits;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 max_ranges;
	zigux_u32 max_selected;
	zigux_u32 reserved;
};

struct zigux_ida_range_set_summary {
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 candidate_range_count;
	zigux_u32 selected_range_count;
	zigux_u32 first_selected_id;
	zigux_u32 last_selected_id;
	zigux_u32 flags;
	zigux_u32 reserved;
};

struct zigux_ida_policy_view {
	unsigned long bits_addr;
	zigux_u32 base_id;
	zigux_u32 nbits;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 reserved;
};

struct zigux_ida_policy_summary {
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 selected_fit_id;
	zigux_u32 alternate_fit_id;
	zigux_u32 longest_free_run;
	zigux_u32 flags;
};

struct zigux_minor_alloc_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 reserved;
};

struct zigux_minor_alloc_summary {
	zigux_u32 major;
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 selected_minor_start;
	zigux_u32 selected_minor_end;
	zigux_u32 alternate_minor_start;
	zigux_u32 longest_free_run;
	zigux_u32 flags;
};

struct zigux_dev_region_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 reserved;
};

struct zigux_dev_region_summary {
	zigux_u32 major;
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 selected_minor_start;
	zigux_u32 selected_minor_end;
	zigux_u32 first_dev;
	zigux_u32 last_dev;
	zigux_u32 flags;
};

struct zigux_cdev_add_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 reserved;
};

struct zigux_cdev_add_summary {
	zigux_u32 major;
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 selected_count;
	zigux_u32 first_minor;
	zigux_u32 first_dev;
	zigux_u32 last_dev;
	zigux_u32 flags;
};

struct zigux_cdev_lookup_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 reserved;
};

struct zigux_cdev_lookup_summary {
	zigux_u32 major;
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 selected_count;
	zigux_u32 first_minor;
	zigux_u32 target_minor;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 flags;
};

struct zigux_chrdev_open_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 reserved;
};

struct zigux_chrdev_open_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 granted_mode;
	zigux_u32 denied_mode;
	zigux_u32 flags;
};

struct zigux_chrdev_fops_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 reserved;
};

struct zigux_chrdev_fops_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 available_ops;
	zigux_u32 required_ops;
	zigux_u32 missing_ops;
	zigux_u32 flags;
};

struct zigux_chrdev_route_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 reserved;
};

struct zigux_chrdev_route_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 flags;
};

struct zigux_chrdev_io_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u32 reserved;
};

struct zigux_chrdev_io_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 chunk_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 flags;
};

struct zigux_chrdev_xfer_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 reserved;
};

struct zigux_chrdev_xfer_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 bytes_completed;
	zigux_u32 requested_remaining;
	zigux_u32 segment_count;
	zigux_u32 first_chunk_bytes;
	zigux_u32 final_chunk_bytes;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 flags;
};

struct zigux_chrdev_resume_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 reserved;
};

struct zigux_chrdev_resume_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 flags;
};

struct zigux_chrdev_retry_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 reserved;
};

struct zigux_chrdev_retry_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 remaining_retry_budget;
	zigux_u32 backoff_ticks;
	zigux_u32 flags;
};

struct zigux_chrdev_requeue_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u32 reserved;
};

struct zigux_chrdev_requeue_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u32 flags;
};

struct zigux_chrdev_complete_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 reserved;
};

struct zigux_chrdev_complete_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 flags;
};

struct zigux_chrdev_notify_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
};

struct zigux_chrdev_notify_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
};

struct zigux_chrdev_notify_policy_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
};

struct zigux_chrdev_notify_policy_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
};

struct zigux_chrdev_notify_budget_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
};

struct zigux_chrdev_notify_budget_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
};

struct zigux_chrdev_notify_ack_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
};

struct zigux_chrdev_notify_ack_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
};

struct zigux_chrdev_notify_ack_policy_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
};

struct zigux_chrdev_notify_ack_policy_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
};

struct zigux_chrdev_notify_ack_budget_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
	zigux_u32 ack_budget;
	zigux_u32 deferred_ack_budget;
	zigux_u32 ack_budget_reserved;
};

struct zigux_chrdev_notify_ack_budget_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
	zigux_u32 ack_budget_flags;
	zigux_u32 ack_budget_before;
	zigux_u32 ack_budget_after;
	zigux_u32 deferred_ack_budget_before;
	zigux_u32 deferred_ack_budget_after;
	zigux_u32 ack_budget_status;
	zigux_u32 budget_acked_count;
	zigux_u32 budget_deferred_ack_count;
	zigux_u32 budget_dropped_ack_count;
	zigux_u32 budget_suppressed_ack_count;
	zigux_u32 budget_skipped_ack_count;
};

struct zigux_chrdev_notify_ack_window_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
	zigux_u32 ack_budget;
	zigux_u32 deferred_ack_budget;
	zigux_u32 ack_budget_reserved;
	zigux_u32 window_floor;
	zigux_u32 window_reserved;
};

struct zigux_chrdev_notify_ack_window_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
	zigux_u32 ack_budget_flags;
	zigux_u32 ack_budget_before;
	zigux_u32 ack_budget_after;
	zigux_u32 deferred_ack_budget_before;
	zigux_u32 deferred_ack_budget_after;
	zigux_u32 ack_budget_status;
	zigux_u32 budget_acked_count;
	zigux_u32 budget_deferred_ack_count;
	zigux_u32 budget_dropped_ack_count;
	zigux_u32 budget_suppressed_ack_count;
	zigux_u32 budget_skipped_ack_count;
	zigux_u32 window_flags;
	zigux_u32 window_before;
	zigux_u32 window_after;
	zigux_u32 window_floor;
	zigux_u32 window_status;
	zigux_u32 window_acked_count;
	zigux_u32 window_deferred_count;
	zigux_u32 window_dropped_count;
	zigux_u32 window_suppressed_count;
	zigux_u32 window_skipped_count;
};

struct zigux_chrdev_notify_ack_window_policy_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
	zigux_u32 ack_budget;
	zigux_u32 deferred_ack_budget;
	zigux_u32 ack_budget_reserved;
	zigux_u32 window_floor;
	zigux_u32 window_reserved;
	zigux_u32 window_policy_flags;
	zigux_u32 window_policy_reserved;
};

struct zigux_chrdev_notify_ack_window_policy_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
	zigux_u32 ack_budget_flags;
	zigux_u32 ack_budget_before;
	zigux_u32 ack_budget_after;
	zigux_u32 deferred_ack_budget_before;
	zigux_u32 deferred_ack_budget_after;
	zigux_u32 ack_budget_status;
	zigux_u32 budget_acked_count;
	zigux_u32 budget_deferred_ack_count;
	zigux_u32 budget_dropped_ack_count;
	zigux_u32 budget_suppressed_ack_count;
	zigux_u32 budget_skipped_ack_count;
	zigux_u32 window_flags;
	zigux_u32 window_before;
	zigux_u32 window_after;
	zigux_u32 window_floor;
	zigux_u32 window_status;
	zigux_u32 window_acked_count;
	zigux_u32 window_deferred_count;
	zigux_u32 window_dropped_count;
	zigux_u32 window_suppressed_count;
	zigux_u32 window_skipped_count;
	zigux_u32 window_policy_flags;
	zigux_u32 effective_window_policy_flags;
	zigux_u64 effective_window_cookie;
	zigux_u32 window_policy_status;
	zigux_u32 policy_window_acked_count;
	zigux_u32 policy_window_deferred_count;
	zigux_u32 policy_window_suppressed_count;
	zigux_u32 policy_window_coalesced_count;
	zigux_u32 policy_window_dropped_count;
	zigux_u32 policy_window_skipped_count;
};

struct zigux_chrdev_notify_ack_window_policy_budget_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
	zigux_u32 ack_budget;
	zigux_u32 deferred_ack_budget;
	zigux_u32 ack_budget_reserved;
	zigux_u32 window_floor;
	zigux_u32 window_reserved;
	zigux_u32 window_policy_flags;
	zigux_u32 window_policy_reserved;
	zigux_u32 window_policy_budget;
	zigux_u32 deferred_window_policy_budget;
	zigux_u32 window_policy_budget_reserved;
};

struct zigux_chrdev_notify_ack_window_policy_budget_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
	zigux_u32 ack_budget_flags;
	zigux_u32 ack_budget_before;
	zigux_u32 ack_budget_after;
	zigux_u32 deferred_ack_budget_before;
	zigux_u32 deferred_ack_budget_after;
	zigux_u32 ack_budget_status;
	zigux_u32 budget_acked_count;
	zigux_u32 budget_deferred_ack_count;
	zigux_u32 budget_dropped_ack_count;
	zigux_u32 budget_suppressed_ack_count;
	zigux_u32 budget_skipped_ack_count;
	zigux_u32 window_flags;
	zigux_u32 window_before;
	zigux_u32 window_after;
	zigux_u32 window_floor;
	zigux_u32 window_status;
	zigux_u32 window_acked_count;
	zigux_u32 window_deferred_count;
	zigux_u32 window_dropped_count;
	zigux_u32 window_suppressed_count;
	zigux_u32 window_skipped_count;
	zigux_u32 window_policy_flags;
	zigux_u32 effective_window_policy_flags;
	zigux_u64 effective_window_cookie;
	zigux_u32 window_policy_status;
	zigux_u32 policy_window_acked_count;
	zigux_u32 policy_window_deferred_count;
	zigux_u32 policy_window_suppressed_count;
	zigux_u32 policy_window_coalesced_count;
	zigux_u32 policy_window_dropped_count;
	zigux_u32 policy_window_skipped_count;
	zigux_u32 window_policy_budget_flags;
	zigux_u32 window_policy_budget_before;
	zigux_u32 window_policy_budget_after;
	zigux_u32 deferred_window_policy_budget_before;
	zigux_u32 deferred_window_policy_budget_after;
	zigux_u32 window_policy_budget_status;
	zigux_u32 budget_window_acked_count;
	zigux_u32 budget_window_deferred_count;
	zigux_u32 budget_window_suppressed_count;
	zigux_u32 budget_window_coalesced_count;
	zigux_u32 budget_window_dropped_count;
	zigux_u32 budget_window_skipped_count;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
	zigux_u32 ack_budget;
	zigux_u32 deferred_ack_budget;
	zigux_u32 ack_budget_reserved;
	zigux_u32 window_floor;
	zigux_u32 window_reserved;
	zigux_u32 window_policy_flags;
	zigux_u32 window_policy_reserved;
	zigux_u32 window_policy_budget;
	zigux_u32 deferred_window_policy_budget;
	zigux_u32 window_policy_budget_reserved;
	zigux_u32 window_policy_budget_window;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_reserved;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
	zigux_u32 ack_budget_flags;
	zigux_u32 ack_budget_before;
	zigux_u32 ack_budget_after;
	zigux_u32 deferred_ack_budget_before;
	zigux_u32 deferred_ack_budget_after;
	zigux_u32 ack_budget_status;
	zigux_u32 budget_acked_count;
	zigux_u32 budget_deferred_ack_count;
	zigux_u32 budget_dropped_ack_count;
	zigux_u32 budget_suppressed_ack_count;
	zigux_u32 budget_skipped_ack_count;
	zigux_u32 window_flags;
	zigux_u32 window_before;
	zigux_u32 window_after;
	zigux_u32 window_floor;
	zigux_u32 window_status;
	zigux_u32 window_acked_count;
	zigux_u32 window_deferred_count;
	zigux_u32 window_dropped_count;
	zigux_u32 window_suppressed_count;
	zigux_u32 window_skipped_count;
	zigux_u32 window_policy_flags;
	zigux_u32 effective_window_policy_flags;
	zigux_u64 effective_window_cookie;
	zigux_u32 window_policy_status;
	zigux_u32 policy_window_acked_count;
	zigux_u32 policy_window_deferred_count;
	zigux_u32 policy_window_suppressed_count;
	zigux_u32 policy_window_coalesced_count;
	zigux_u32 policy_window_dropped_count;
	zigux_u32 policy_window_skipped_count;
	zigux_u32 window_policy_budget_flags;
	zigux_u32 window_policy_budget_before;
	zigux_u32 window_policy_budget_after;
	zigux_u32 deferred_window_policy_budget_before;
	zigux_u32 deferred_window_policy_budget_after;
	zigux_u32 window_policy_budget_status;
	zigux_u32 budget_window_acked_count;
	zigux_u32 budget_window_deferred_count;
	zigux_u32 budget_window_suppressed_count;
	zigux_u32 budget_window_coalesced_count;
	zigux_u32 budget_window_dropped_count;
	zigux_u32 budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_flags;
	zigux_u32 window_policy_budget_window_before;
	zigux_u32 window_policy_budget_window_after;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_status;
	zigux_u32 window_policy_budget_window_acked_count;
	zigux_u32 window_policy_budget_window_deferred_count;
	zigux_u32 window_policy_budget_window_suppressed_count;
	zigux_u32 window_policy_budget_window_coalesced_count;
	zigux_u32 window_policy_budget_window_dropped_count;
	zigux_u32 window_policy_budget_window_skipped_count;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
	zigux_u32 ack_budget;
	zigux_u32 deferred_ack_budget;
	zigux_u32 ack_budget_reserved;
	zigux_u32 window_floor;
	zigux_u32 window_reserved;
	zigux_u32 window_policy_flags;
	zigux_u32 window_policy_reserved;
	zigux_u32 window_policy_budget;
	zigux_u32 deferred_window_policy_budget;
	zigux_u32 window_policy_budget_reserved;
	zigux_u32 window_policy_budget_window;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_budget;
	zigux_u32 window_policy_budget_window_delivery_reserved;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
	zigux_u32 ack_budget;
	zigux_u32 deferred_ack_budget;
	zigux_u32 ack_budget_reserved;
	zigux_u32 window_floor;
	zigux_u32 window_reserved;
	zigux_u32 window_policy_flags;
	zigux_u32 window_policy_reserved;
	zigux_u32 window_policy_budget;
	zigux_u32 deferred_window_policy_budget;
	zigux_u32 window_policy_budget_reserved;
	zigux_u32 window_policy_budget_window;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_budget;
	zigux_u32 window_policy_budget_window_delivery_reserved;
	zigux_u32 window_policy_budget_window_delivery_window;
	zigux_u32 window_policy_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_reserved;
};
struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
	zigux_u32 ack_budget;
	zigux_u32 deferred_ack_budget;
	zigux_u32 ack_budget_reserved;
	zigux_u32 window_floor;
	zigux_u32 window_reserved;
	zigux_u32 window_policy_flags;
	zigux_u32 window_policy_reserved;
	zigux_u32 window_policy_budget;
	zigux_u32 deferred_window_policy_budget;
	zigux_u32 window_policy_budget_reserved;
	zigux_u32 window_policy_budget_window;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_budget;
	zigux_u32 window_policy_budget_window_delivery_reserved;
	zigux_u32 window_policy_budget_window_delivery_window;
	zigux_u32 window_policy_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget;
	zigux_u32 window_policy_budget_window_delivery_window_budget_reserved;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
	zigux_u32 ack_budget;
	zigux_u32 deferred_ack_budget;
	zigux_u32 ack_budget_reserved;
	zigux_u32 window_floor;
	zigux_u32 window_reserved;
	zigux_u32 window_policy_flags;
	zigux_u32 window_policy_reserved;
	zigux_u32 window_policy_budget;
	zigux_u32 deferred_window_policy_budget;
	zigux_u32 window_policy_budget_reserved;
	zigux_u32 window_policy_budget_window;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_budget;
	zigux_u32 window_policy_budget_window_delivery_reserved;
	zigux_u32 window_policy_budget_window_delivery_window;
	zigux_u32 window_policy_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget;
	zigux_u32 window_policy_budget_window_delivery_window_budget_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_reserved;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
	zigux_u32 ack_budget_flags;
	zigux_u32 ack_budget_before;
	zigux_u32 ack_budget_after;
	zigux_u32 deferred_ack_budget_before;
	zigux_u32 deferred_ack_budget_after;
	zigux_u32 ack_budget_status;
	zigux_u32 budget_acked_count;
	zigux_u32 budget_deferred_ack_count;
	zigux_u32 budget_dropped_ack_count;
	zigux_u32 budget_suppressed_ack_count;
	zigux_u32 budget_skipped_ack_count;
	zigux_u32 window_flags;
	zigux_u32 window_before;
	zigux_u32 window_after;
	zigux_u32 window_floor;
	zigux_u32 window_status;
	zigux_u32 window_acked_count;
	zigux_u32 window_deferred_count;
	zigux_u32 window_dropped_count;
	zigux_u32 window_suppressed_count;
	zigux_u32 window_skipped_count;
	zigux_u32 window_policy_flags;
	zigux_u32 effective_window_policy_flags;
	zigux_u64 effective_window_cookie;
	zigux_u32 window_policy_status;
	zigux_u32 policy_window_acked_count;
	zigux_u32 policy_window_deferred_count;
	zigux_u32 policy_window_suppressed_count;
	zigux_u32 policy_window_coalesced_count;
	zigux_u32 policy_window_dropped_count;
	zigux_u32 policy_window_skipped_count;
	zigux_u32 window_policy_budget_flags;
	zigux_u32 window_policy_budget_before;
	zigux_u32 window_policy_budget_after;
	zigux_u32 deferred_window_policy_budget_before;
	zigux_u32 deferred_window_policy_budget_after;
	zigux_u32 window_policy_budget_status;
	zigux_u32 budget_window_acked_count;
	zigux_u32 budget_window_deferred_count;
	zigux_u32 budget_window_suppressed_count;
	zigux_u32 budget_window_coalesced_count;
	zigux_u32 budget_window_dropped_count;
	zigux_u32 budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_flags;
	zigux_u32 window_policy_budget_window_before;
	zigux_u32 window_policy_budget_window_after;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_status;
	zigux_u32 window_policy_budget_window_acked_count;
	zigux_u32 window_policy_budget_window_deferred_count;
	zigux_u32 window_policy_budget_window_suppressed_count;
	zigux_u32 window_policy_budget_window_coalesced_count;
	zigux_u32 window_policy_budget_window_dropped_count;
	zigux_u32 window_policy_budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_flags;
	zigux_u32 window_policy_budget_window_delivery_before;
	zigux_u32 window_policy_budget_window_delivery_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_after;
	zigux_u32 window_policy_budget_window_delivery_status;
	zigux_u32 window_policy_budget_window_delivery_acked_count;
	zigux_u32 window_policy_budget_window_delivery_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_flags;
	zigux_u32 window_policy_budget_window_delivery_window_before;
	zigux_u32 window_policy_budget_window_delivery_window_after;
	zigux_u32 window_policy_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_status;
	zigux_u32 window_policy_budget_window_delivery_window_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_skipped_count;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
	zigux_u32 ack_budget_flags;
	zigux_u32 ack_budget_before;
	zigux_u32 ack_budget_after;
	zigux_u32 deferred_ack_budget_before;
	zigux_u32 deferred_ack_budget_after;
	zigux_u32 ack_budget_status;
	zigux_u32 budget_acked_count;
	zigux_u32 budget_deferred_ack_count;
	zigux_u32 budget_dropped_ack_count;
	zigux_u32 budget_suppressed_ack_count;
	zigux_u32 budget_skipped_ack_count;
	zigux_u32 window_flags;
	zigux_u32 window_before;
	zigux_u32 window_after;
	zigux_u32 window_floor;
	zigux_u32 window_status;
	zigux_u32 window_acked_count;
	zigux_u32 window_deferred_count;
	zigux_u32 window_dropped_count;
	zigux_u32 window_suppressed_count;
	zigux_u32 window_skipped_count;
	zigux_u32 window_policy_flags;
	zigux_u32 effective_window_policy_flags;
	zigux_u64 effective_window_cookie;
	zigux_u32 window_policy_status;
	zigux_u32 policy_window_acked_count;
	zigux_u32 policy_window_deferred_count;
	zigux_u32 policy_window_suppressed_count;
	zigux_u32 policy_window_coalesced_count;
	zigux_u32 policy_window_dropped_count;
	zigux_u32 policy_window_skipped_count;
	zigux_u32 window_policy_budget_flags;
	zigux_u32 window_policy_budget_before;
	zigux_u32 window_policy_budget_after;
	zigux_u32 deferred_window_policy_budget_before;
	zigux_u32 deferred_window_policy_budget_after;
	zigux_u32 window_policy_budget_status;
	zigux_u32 budget_window_acked_count;
	zigux_u32 budget_window_deferred_count;
	zigux_u32 budget_window_suppressed_count;
	zigux_u32 budget_window_coalesced_count;
	zigux_u32 budget_window_dropped_count;
	zigux_u32 budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_flags;
	zigux_u32 window_policy_budget_window_before;
	zigux_u32 window_policy_budget_window_after;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_status;
	zigux_u32 window_policy_budget_window_acked_count;
	zigux_u32 window_policy_budget_window_deferred_count;
	zigux_u32 window_policy_budget_window_suppressed_count;
	zigux_u32 window_policy_budget_window_coalesced_count;
	zigux_u32 window_policy_budget_window_dropped_count;
	zigux_u32 window_policy_budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_flags;
	zigux_u32 window_policy_budget_window_delivery_before;
	zigux_u32 window_policy_budget_window_delivery_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_after;
	zigux_u32 window_policy_budget_window_delivery_status;
	zigux_u32 window_policy_budget_window_delivery_acked_count;
	zigux_u32 window_policy_budget_window_delivery_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_flags;
	zigux_u32 window_policy_budget_window_delivery_window_before;
	zigux_u32 window_policy_budget_window_delivery_window_after;
	zigux_u32 window_policy_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_status;
	zigux_u32 window_policy_budget_window_delivery_window_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_skipped_count;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
	zigux_u32 ack_budget_flags;
	zigux_u32 ack_budget_before;
	zigux_u32 ack_budget_after;
	zigux_u32 deferred_ack_budget_before;
	zigux_u32 deferred_ack_budget_after;
	zigux_u32 ack_budget_status;
	zigux_u32 budget_acked_count;
	zigux_u32 budget_deferred_ack_count;
	zigux_u32 budget_dropped_ack_count;
	zigux_u32 budget_suppressed_ack_count;
	zigux_u32 budget_skipped_ack_count;
	zigux_u32 window_flags;
	zigux_u32 window_before;
	zigux_u32 window_after;
	zigux_u32 window_floor;
	zigux_u32 window_status;
	zigux_u32 window_acked_count;
	zigux_u32 window_deferred_count;
	zigux_u32 window_dropped_count;
	zigux_u32 window_suppressed_count;
	zigux_u32 window_skipped_count;
	zigux_u32 window_policy_flags;
	zigux_u32 effective_window_policy_flags;
	zigux_u64 effective_window_cookie;
	zigux_u32 window_policy_status;
	zigux_u32 policy_window_acked_count;
	zigux_u32 policy_window_deferred_count;
	zigux_u32 policy_window_suppressed_count;
	zigux_u32 policy_window_coalesced_count;
	zigux_u32 policy_window_dropped_count;
	zigux_u32 policy_window_skipped_count;
	zigux_u32 window_policy_budget_flags;
	zigux_u32 window_policy_budget_before;
	zigux_u32 window_policy_budget_after;
	zigux_u32 deferred_window_policy_budget_before;
	zigux_u32 deferred_window_policy_budget_after;
	zigux_u32 window_policy_budget_status;
	zigux_u32 budget_window_acked_count;
	zigux_u32 budget_window_deferred_count;
	zigux_u32 budget_window_suppressed_count;
	zigux_u32 budget_window_coalesced_count;
	zigux_u32 budget_window_dropped_count;
	zigux_u32 budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_flags;
	zigux_u32 window_policy_budget_window_before;
	zigux_u32 window_policy_budget_window_after;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_status;
	zigux_u32 window_policy_budget_window_acked_count;
	zigux_u32 window_policy_budget_window_deferred_count;
	zigux_u32 window_policy_budget_window_suppressed_count;
	zigux_u32 window_policy_budget_window_coalesced_count;
	zigux_u32 window_policy_budget_window_dropped_count;
	zigux_u32 window_policy_budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_flags;
	zigux_u32 window_policy_budget_window_delivery_before;
	zigux_u32 window_policy_budget_window_delivery_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_after;
	zigux_u32 window_policy_budget_window_delivery_status;
	zigux_u32 window_policy_budget_window_delivery_acked_count;
	zigux_u32 window_policy_budget_window_delivery_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_skipped_count;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
	zigux_u32 ack_budget_flags;
	zigux_u32 ack_budget_before;
	zigux_u32 ack_budget_after;
	zigux_u32 deferred_ack_budget_before;
	zigux_u32 deferred_ack_budget_after;
	zigux_u32 ack_budget_status;
	zigux_u32 budget_acked_count;
	zigux_u32 budget_deferred_ack_count;
	zigux_u32 budget_dropped_ack_count;
	zigux_u32 budget_suppressed_ack_count;
	zigux_u32 budget_skipped_ack_count;
	zigux_u32 window_flags;
	zigux_u32 window_before;
	zigux_u32 window_after;
	zigux_u32 window_floor;
	zigux_u32 window_status;
	zigux_u32 window_acked_count;
	zigux_u32 window_deferred_count;
	zigux_u32 window_dropped_count;
	zigux_u32 window_suppressed_count;
	zigux_u32 window_skipped_count;
	zigux_u32 window_policy_flags;
	zigux_u32 effective_window_policy_flags;
	zigux_u64 effective_window_cookie;
	zigux_u32 window_policy_status;
	zigux_u32 policy_window_acked_count;
	zigux_u32 policy_window_deferred_count;
	zigux_u32 policy_window_suppressed_count;
	zigux_u32 policy_window_coalesced_count;
	zigux_u32 policy_window_dropped_count;
	zigux_u32 policy_window_skipped_count;
	zigux_u32 window_policy_budget_flags;
	zigux_u32 window_policy_budget_before;
	zigux_u32 window_policy_budget_after;
	zigux_u32 deferred_window_policy_budget_before;
	zigux_u32 deferred_window_policy_budget_after;
	zigux_u32 window_policy_budget_status;
	zigux_u32 budget_window_acked_count;
	zigux_u32 budget_window_deferred_count;
	zigux_u32 budget_window_suppressed_count;
	zigux_u32 budget_window_coalesced_count;
	zigux_u32 budget_window_dropped_count;
	zigux_u32 budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_flags;
	zigux_u32 window_policy_budget_window_before;
	zigux_u32 window_policy_budget_window_after;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_status;
	zigux_u32 window_policy_budget_window_acked_count;
	zigux_u32 window_policy_budget_window_deferred_count;
	zigux_u32 window_policy_budget_window_suppressed_count;
	zigux_u32 window_policy_budget_window_coalesced_count;
	zigux_u32 window_policy_budget_window_dropped_count;
	zigux_u32 window_policy_budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_flags;
	zigux_u32 window_policy_budget_window_delivery_before;
	zigux_u32 window_policy_budget_window_delivery_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_after;
	zigux_u32 window_policy_budget_window_delivery_status;
	zigux_u32 window_policy_budget_window_delivery_acked_count;
	zigux_u32 window_policy_budget_window_delivery_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_flags;
	zigux_u32 window_policy_budget_window_delivery_window_before;
	zigux_u32 window_policy_budget_window_delivery_window_after;
	zigux_u32 window_policy_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_status;
	zigux_u32 window_policy_budget_window_delivery_window_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_skipped_count;
};

#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_BUDGET_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_WINDOW_DELIVERY_BUDGET_USED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_USED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_WINDOW_DELIVERY_BUDGET_EXHAUSTED 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_EXHAUSTED 16U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_SUPPRESSED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_SKIPPED 6U

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
	zigux_u32 ack_budget;
	zigux_u32 deferred_ack_budget;
	zigux_u32 ack_budget_reserved;
	zigux_u32 window_floor;
	zigux_u32 window_reserved;
	zigux_u32 window_policy_flags;
	zigux_u32 window_policy_reserved;
	zigux_u32 window_policy_budget;
	zigux_u32 deferred_window_policy_budget;
	zigux_u32 window_policy_budget_reserved;
	zigux_u32 window_policy_budget_window;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_budget;
	zigux_u32 window_policy_budget_window_delivery_reserved;
	zigux_u32 window_policy_budget_window_delivery_window;
	zigux_u32 window_policy_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget;
	zigux_u32 window_policy_budget_window_delivery_window_budget_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_reserved;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
	zigux_u32 ack_budget_flags;
	zigux_u32 ack_budget_before;
	zigux_u32 ack_budget_after;
	zigux_u32 deferred_ack_budget_before;
	zigux_u32 deferred_ack_budget_after;
	zigux_u32 ack_budget_status;
	zigux_u32 budget_acked_count;
	zigux_u32 budget_deferred_ack_count;
	zigux_u32 budget_dropped_ack_count;
	zigux_u32 budget_suppressed_ack_count;
	zigux_u32 budget_skipped_ack_count;
	zigux_u32 window_flags;
	zigux_u32 window_before;
	zigux_u32 window_after;
	zigux_u32 window_floor;
	zigux_u32 window_status;
	zigux_u32 window_acked_count;
	zigux_u32 window_deferred_count;
	zigux_u32 window_dropped_count;
	zigux_u32 window_suppressed_count;
	zigux_u32 window_skipped_count;
	zigux_u32 window_policy_flags;
	zigux_u32 effective_window_policy_flags;
	zigux_u64 effective_window_cookie;
	zigux_u32 window_policy_status;
	zigux_u32 policy_window_acked_count;
	zigux_u32 policy_window_deferred_count;
	zigux_u32 policy_window_suppressed_count;
	zigux_u32 policy_window_coalesced_count;
	zigux_u32 policy_window_dropped_count;
	zigux_u32 policy_window_skipped_count;
	zigux_u32 window_policy_budget_flags;
	zigux_u32 window_policy_budget_before;
	zigux_u32 window_policy_budget_after;
	zigux_u32 deferred_window_policy_budget_before;
	zigux_u32 deferred_window_policy_budget_after;
	zigux_u32 window_policy_budget_status;
	zigux_u32 budget_window_acked_count;
	zigux_u32 budget_window_deferred_count;
	zigux_u32 budget_window_suppressed_count;
	zigux_u32 budget_window_coalesced_count;
	zigux_u32 budget_window_dropped_count;
	zigux_u32 budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_flags;
	zigux_u32 window_policy_budget_window_before;
	zigux_u32 window_policy_budget_window_after;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_status;
	zigux_u32 window_policy_budget_window_acked_count;
	zigux_u32 window_policy_budget_window_deferred_count;
	zigux_u32 window_policy_budget_window_suppressed_count;
	zigux_u32 window_policy_budget_window_coalesced_count;
	zigux_u32 window_policy_budget_window_dropped_count;
	zigux_u32 window_policy_budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_flags;
	zigux_u32 window_policy_budget_window_delivery_before;
	zigux_u32 window_policy_budget_window_delivery_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_after;
	zigux_u32 window_policy_budget_window_delivery_status;
	zigux_u32 window_policy_budget_window_delivery_acked_count;
	zigux_u32 window_policy_budget_window_delivery_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_flags;
	zigux_u32 window_policy_budget_window_delivery_window_before;
	zigux_u32 window_policy_budget_window_delivery_window_after;
	zigux_u32 window_policy_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_status;
	zigux_u32 window_policy_budget_window_delivery_window_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_skipped_count;	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_skipped_count;
};


#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_USED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_FLOOR_HELD 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_FLOOR_BLOCKED 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_EXHAUSTED 16U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SUPPRESSED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_COALESCED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED 6U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_WINDOW_DELIVERY_WINDOW_BUDGET_USED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_USED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED 8U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED 16U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE 0U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SUPPRESSED 3U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_COALESCED 4U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED 5U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SKIPPED 6U

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
	zigux_u32 ack_budget;
	zigux_u32 deferred_ack_budget;
	zigux_u32 ack_budget_reserved;
	zigux_u32 window_floor;
	zigux_u32 window_reserved;
	zigux_u32 window_policy_flags;
	zigux_u32 window_policy_reserved;
	zigux_u32 window_policy_budget;
	zigux_u32 deferred_window_policy_budget;
	zigux_u32 window_policy_budget_reserved;
	zigux_u32 window_policy_budget_window;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_budget;
	zigux_u32 window_policy_budget_window_delivery_reserved;
	zigux_u32 window_policy_budget_window_delivery_window;
	zigux_u32 window_policy_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget;
	zigux_u32 window_policy_budget_window_delivery_window_budget_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_reserved;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
	zigux_u32 ack_budget_flags;
	zigux_u32 ack_budget_before;
	zigux_u32 ack_budget_after;
	zigux_u32 deferred_ack_budget_before;
	zigux_u32 deferred_ack_budget_after;
	zigux_u32 ack_budget_status;
	zigux_u32 budget_acked_count;
	zigux_u32 budget_deferred_ack_count;
	zigux_u32 budget_dropped_ack_count;
	zigux_u32 budget_suppressed_ack_count;
	zigux_u32 budget_skipped_ack_count;
	zigux_u32 window_flags;
	zigux_u32 window_before;
	zigux_u32 window_after;
	zigux_u32 window_floor;
	zigux_u32 window_status;
	zigux_u32 window_acked_count;
	zigux_u32 window_deferred_count;
	zigux_u32 window_dropped_count;
	zigux_u32 window_suppressed_count;
	zigux_u32 window_skipped_count;
	zigux_u32 window_policy_flags;
	zigux_u32 effective_window_policy_flags;
	zigux_u64 effective_window_cookie;
	zigux_u32 window_policy_status;
	zigux_u32 policy_window_acked_count;
	zigux_u32 policy_window_deferred_count;
	zigux_u32 policy_window_suppressed_count;
	zigux_u32 policy_window_coalesced_count;
	zigux_u32 policy_window_dropped_count;
	zigux_u32 policy_window_skipped_count;
	zigux_u32 window_policy_budget_flags;
	zigux_u32 window_policy_budget_before;
	zigux_u32 window_policy_budget_after;
	zigux_u32 deferred_window_policy_budget_before;
	zigux_u32 deferred_window_policy_budget_after;
	zigux_u32 window_policy_budget_status;
	zigux_u32 budget_window_acked_count;
	zigux_u32 budget_window_deferred_count;
	zigux_u32 budget_window_suppressed_count;
	zigux_u32 budget_window_coalesced_count;
	zigux_u32 budget_window_dropped_count;
	zigux_u32 budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_flags;
	zigux_u32 window_policy_budget_window_before;
	zigux_u32 window_policy_budget_window_after;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_status;
	zigux_u32 window_policy_budget_window_acked_count;
	zigux_u32 window_policy_budget_window_deferred_count;
	zigux_u32 window_policy_budget_window_suppressed_count;
	zigux_u32 window_policy_budget_window_coalesced_count;
	zigux_u32 window_policy_budget_window_dropped_count;
	zigux_u32 window_policy_budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_flags;
	zigux_u32 window_policy_budget_window_delivery_before;
	zigux_u32 window_policy_budget_window_delivery_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_after;
	zigux_u32 window_policy_budget_window_delivery_status;
	zigux_u32 window_policy_budget_window_delivery_acked_count;
	zigux_u32 window_policy_budget_window_delivery_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_flags;
	zigux_u32 window_policy_budget_window_delivery_window_before;
	zigux_u32 window_policy_budget_window_delivery_window_after;
	zigux_u32 window_policy_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_status;
	zigux_u32 window_policy_budget_window_delivery_window_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_skipped_count;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 requested_mode;
	zigux_u32 supported_mode;
	zigux_u32 available_ops;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u32 max_chunk_bytes;
	zigux_u64 file_offset;
	zigux_u32 bytes_completed;
	zigux_u32 max_segments;
	zigux_u32 resume_passes;
	zigux_u32 retry_budget;
	zigux_u32 stall_budget;
	zigux_u32 backoff_quanta;
	zigux_u32 queue_depth;
	zigux_u32 queue_capacity;
	zigux_u32 requeue_budget;
	zigux_u64 completion_cookie;
	zigux_u32 completion_budget;
	zigux_u32 notify_mask;
	zigux_u64 notify_cookie;
	zigux_u32 notify_budget;
	zigux_u32 reserved;
	zigux_u32 policy_flags;
	zigux_u32 policy_reserved;
	zigux_u32 delivery_budget;
	zigux_u32 deferred_budget;
	zigux_u32 ack_mask;
	zigux_u32 ack_window;
	zigux_u64 ack_cookie;
	zigux_u32 ack_observed;
	zigux_u32 ack_reserved;
	zigux_u32 ack_policy_flags;
	zigux_u32 ack_policy_reserved;
	zigux_u32 ack_budget;
	zigux_u32 deferred_ack_budget;
	zigux_u32 ack_budget_reserved;
	zigux_u32 window_floor;
	zigux_u32 window_reserved;
	zigux_u32 window_policy_flags;
	zigux_u32 window_policy_reserved;
	zigux_u32 window_policy_budget;
	zigux_u32 deferred_window_policy_budget;
	zigux_u32 window_policy_budget_reserved;
	zigux_u32 window_policy_budget_window;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_budget;
	zigux_u32 window_policy_budget_window_delivery_reserved;
	zigux_u32 window_policy_budget_window_delivery_window;
	zigux_u32 window_policy_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget;
	zigux_u32 window_policy_budget_window_delivery_window_budget_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_reserved;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_reserved;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_summary {
	zigux_u32 major;
	zigux_u32 target_minor;
	zigux_u32 selected_count;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 granted_mode;
	zigux_u32 io_op;
	zigux_u32 requested_bytes;
	zigux_u64 start_offset;
	zigux_u64 next_offset;
	zigux_u32 initial_bytes_completed;
	zigux_u32 final_bytes_completed;
	zigux_u32 pass_count;
	zigux_u32 issued_bytes;
	zigux_u32 remaining_bytes;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 entry_ops;
	zigux_u32 data_ops;
	zigux_u32 exit_ops;
	zigux_u32 blocked_ops;
	zigux_u32 retry_count;
	zigux_u32 stall_count;
	zigux_u32 requeue_count;
	zigux_u32 queue_depth_before;
	zigux_u32 queue_depth_after;
	zigux_u32 remaining_retry_budget;
	zigux_u32 remaining_requeue_budget;
	zigux_u32 backoff_ticks;
	zigux_u64 completion_cookie;
	zigux_u32 completion_status;
	zigux_u32 completion_count;
	zigux_u32 deferred_count;
	zigux_u32 failure_count;
	zigux_u32 remaining_completion_budget;
	zigux_u32 notify_mask;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status;
	zigux_u32 notify_count;
	zigux_u32 deferred_notify_count;
	zigux_u32 dropped_notify_count;
	zigux_u32 remaining_notify_budget;
	zigux_u64 notify_cookie;
	zigux_u32 flags;
	zigux_u32 policy_flags;
	zigux_u32 effective_policy_flags;
	zigux_u64 effective_notify_cookie;
	zigux_u32 policy_status;
	zigux_u32 policy_notify_count;
	zigux_u32 policy_deferred_count;
	zigux_u32 policy_suppressed_count;
	zigux_u32 policy_coalesced_count;
	zigux_u32 budget_flags;
	zigux_u32 delivery_budget_before;
	zigux_u32 delivery_budget_after;
	zigux_u32 deferred_budget_before;
	zigux_u32 deferred_budget_after;
	zigux_u32 budget_status;
	zigux_u32 budget_notify_count;
	zigux_u32 budget_deferred_count;
	zigux_u32 budget_dropped_count;
	zigux_u32 budget_suppressed_count;
	zigux_u32 ack_mask;
	zigux_u32 matched_ack_mask;
	zigux_u32 ack_status;
	zigux_u32 ack_count;
	zigux_u32 deferred_ack_count;
	zigux_u32 expired_ack_count;
	zigux_u32 skipped_ack_count;
	zigux_u32 ack_window_before;
	zigux_u32 ack_window_after;
	zigux_u64 ack_cookie;
	zigux_u32 ack_flags;
	zigux_u32 ack_policy_flags;
	zigux_u32 effective_ack_policy_flags;
	zigux_u64 effective_ack_cookie;
	zigux_u32 ack_policy_status;
	zigux_u32 policy_acked_count;
	zigux_u32 policy_deferred_ack_count;
	zigux_u32 policy_suppressed_ack_count;
	zigux_u32 policy_coalesced_ack_count;
	zigux_u32 policy_expired_ack_count;
	zigux_u32 policy_skipped_ack_count;
	zigux_u32 ack_budget_flags;
	zigux_u32 ack_budget_before;
	zigux_u32 ack_budget_after;
	zigux_u32 deferred_ack_budget_before;
	zigux_u32 deferred_ack_budget_after;
	zigux_u32 ack_budget_status;
	zigux_u32 budget_acked_count;
	zigux_u32 budget_deferred_ack_count;
	zigux_u32 budget_dropped_ack_count;
	zigux_u32 budget_suppressed_ack_count;
	zigux_u32 budget_skipped_ack_count;
	zigux_u32 window_flags;
	zigux_u32 window_before;
	zigux_u32 window_after;
	zigux_u32 window_floor;
	zigux_u32 window_status;
	zigux_u32 window_acked_count;
	zigux_u32 window_deferred_count;
	zigux_u32 window_dropped_count;
	zigux_u32 window_suppressed_count;
	zigux_u32 window_skipped_count;
	zigux_u32 window_policy_flags;
	zigux_u32 effective_window_policy_flags;
	zigux_u64 effective_window_cookie;
	zigux_u32 window_policy_status;
	zigux_u32 policy_window_acked_count;
	zigux_u32 policy_window_deferred_count;
	zigux_u32 policy_window_suppressed_count;
	zigux_u32 policy_window_coalesced_count;
	zigux_u32 policy_window_dropped_count;
	zigux_u32 policy_window_skipped_count;
	zigux_u32 window_policy_budget_flags;
	zigux_u32 window_policy_budget_before;
	zigux_u32 window_policy_budget_after;
	zigux_u32 deferred_window_policy_budget_before;
	zigux_u32 deferred_window_policy_budget_after;
	zigux_u32 window_policy_budget_status;
	zigux_u32 budget_window_acked_count;
	zigux_u32 budget_window_deferred_count;
	zigux_u32 budget_window_suppressed_count;
	zigux_u32 budget_window_coalesced_count;
	zigux_u32 budget_window_dropped_count;
	zigux_u32 budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_flags;
	zigux_u32 window_policy_budget_window_before;
	zigux_u32 window_policy_budget_window_after;
	zigux_u32 window_policy_budget_window_floor;
	zigux_u32 window_policy_budget_window_status;
	zigux_u32 window_policy_budget_window_acked_count;
	zigux_u32 window_policy_budget_window_deferred_count;
	zigux_u32 window_policy_budget_window_suppressed_count;
	zigux_u32 window_policy_budget_window_coalesced_count;
	zigux_u32 window_policy_budget_window_dropped_count;
	zigux_u32 window_policy_budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_flags;
	zigux_u32 window_policy_budget_window_delivery_before;
	zigux_u32 window_policy_budget_window_delivery_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_after;
	zigux_u32 window_policy_budget_window_delivery_status;
	zigux_u32 window_policy_budget_window_delivery_acked_count;
	zigux_u32 window_policy_budget_window_delivery_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_flags;
	zigux_u32 window_policy_budget_window_delivery_window_before;
	zigux_u32 window_policy_budget_window_delivery_window_after;
	zigux_u32 window_policy_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_status;
	zigux_u32 window_policy_budget_window_delivery_window_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_floor;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_skipped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_flags;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_before;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_before;
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_acked_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_deferred_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_suppressed_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_coalesced_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dropped_count;
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_skipped_count;
};

struct zigux_mmio_range {
	unsigned long base_addr;
	zigux_u32 length;
	zigux_u32 stride;
};

struct zigux_interop_policy {
	zigux_u8 panic_mode;
	zigux_u8 allocator_mode;
	zigux_u8 unsafe_scope;
	zigux_u8 reserved;
};

#endif
