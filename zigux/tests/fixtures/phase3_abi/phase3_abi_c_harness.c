#include <stddef.h>
#include <stdio.h>

#include <linux/zigux.h>

struct layout_field {
    const char *name;
    size_t offset;
};

struct layout_desc {
    const char *name;
    size_t size;
    size_t align;
    size_t field_count;
    const struct layout_field *fields;
};

#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))

static void emit_layout(FILE *out, const struct layout_desc *layout, int comma)
{
    fprintf(out, "\"%s\":{\"size\":%zu,\"align\":%zu,\"offsets\":{", layout->name, layout->size, layout->align);
    for (size_t i = 0; i < layout->field_count; ++i) {
        fprintf(out, "\"%s\":%zu%s", layout->fields[i].name, layout->fields[i].offset, (i + 1 < layout->field_count) ? "," : "");
    }
    fprintf(out, "}}%s", comma ? "," : "");
}

static const struct layout_field zigux_boundary_header_fields[] = {
    {"size", offsetof(struct zigux_boundary_header, size)},
    {"abi_version", offsetof(struct zigux_boundary_header, abi_version)},
    {"flags", offsetof(struct zigux_boundary_header, flags)},
};

static const struct layout_field zigux_export_status_fields[] = {
    {"code", offsetof(struct zigux_export_status, code)},
    {"facility", offsetof(struct zigux_export_status, facility)},
    {"flags", offsetof(struct zigux_export_status, flags)},
};

static const struct layout_field zigux_mmio_range_fields[] = {
    {"base_addr", offsetof(struct zigux_mmio_range, base_addr)},
    {"length", offsetof(struct zigux_mmio_range, length)},
    {"stride", offsetof(struct zigux_mmio_range, stride)},
};

static const struct layout_field zigux_interop_policy_fields[] = {
    {"panic_mode", offsetof(struct zigux_interop_policy, panic_mode)},
    {"allocator_mode", offsetof(struct zigux_interop_policy, allocator_mode)},
    {"unsafe_scope", offsetof(struct zigux_interop_policy, unsafe_scope)},
    {"reserved", offsetof(struct zigux_interop_policy, reserved)},
};

static const struct layout_field zigux_bitmap_view_fields[] = {
    {"words_addr", offsetof(struct zigux_bitmap_view, words_addr)},
    {"nbits", offsetof(struct zigux_bitmap_view, nbits)},
    {"word_count", offsetof(struct zigux_bitmap_view, word_count)},
};

static const struct layout_field zigux_cpumask_view_fields[] = {
    {"bits_addr", offsetof(struct zigux_cpumask_view, bits_addr)},
    {"nr_cpu_ids", offsetof(struct zigux_cpumask_view, nr_cpu_ids)},
    {"reserved", offsetof(struct zigux_cpumask_view, reserved)},
};

static const struct layout_field zigux_list_head_ref_fields[] = {
    {"next_addr", offsetof(struct zigux_list_head_ref, next_addr)},
    {"prev_addr", offsetof(struct zigux_list_head_ref, prev_addr)},
};

static const struct layout_field zigux_list_view_fields[] = {
    {"head_addr", offsetof(struct zigux_list_view, head_addr)},
    {"max_nodes", offsetof(struct zigux_list_view, max_nodes)},
    {"reserved", offsetof(struct zigux_list_view, reserved)},
};

static const struct layout_field zigux_list_summary_fields[] = {
    {"length", offsetof(struct zigux_list_summary, length)},
    {"flags", offsetof(struct zigux_list_summary, flags)},
};

static const struct layout_field zigux_hlist_head_ref_fields[] = {
    {"first_addr", offsetof(struct zigux_hlist_head_ref, first_addr)},
};

static const struct layout_field zigux_hlist_node_ref_fields[] = {
    {"next_addr", offsetof(struct zigux_hlist_node_ref, next_addr)},
    {"pprev_addr", offsetof(struct zigux_hlist_node_ref, pprev_addr)},
};

static const struct layout_field zigux_hlist_view_fields[] = {
    {"head_addr", offsetof(struct zigux_hlist_view, head_addr)},
    {"max_nodes", offsetof(struct zigux_hlist_view, max_nodes)},
    {"reserved", offsetof(struct zigux_hlist_view, reserved)},
};

static const struct layout_field zigux_hlist_summary_fields[] = {
    {"length", offsetof(struct zigux_hlist_summary, length)},
    {"flags", offsetof(struct zigux_hlist_summary, flags)},
};

static const struct layout_field zigux_rbtree_root_view_fields[] = {
    {"root_addr", offsetof(struct zigux_rbtree_root_view, root_addr)},
    {"leftmost_addr", offsetof(struct zigux_rbtree_root_view, leftmost_addr)},
    {"flags", offsetof(struct zigux_rbtree_root_view, flags)},
    {"reserved", offsetof(struct zigux_rbtree_root_view, reserved)},
};

static const struct layout_desc layouts[] = {
    {"zigux_boundary_header", sizeof(struct zigux_boundary_header), _Alignof(struct zigux_boundary_header), ARRAY_SIZE(zigux_boundary_header_fields), zigux_boundary_header_fields},
    {"zigux_export_status", sizeof(struct zigux_export_status), _Alignof(struct zigux_export_status), ARRAY_SIZE(zigux_export_status_fields), zigux_export_status_fields},
    {"zigux_mmio_range", sizeof(struct zigux_mmio_range), _Alignof(struct zigux_mmio_range), ARRAY_SIZE(zigux_mmio_range_fields), zigux_mmio_range_fields},
    {"zigux_interop_policy", sizeof(struct zigux_interop_policy), _Alignof(struct zigux_interop_policy), ARRAY_SIZE(zigux_interop_policy_fields), zigux_interop_policy_fields},
    {"zigux_bitmap_view", sizeof(struct zigux_bitmap_view), _Alignof(struct zigux_bitmap_view), ARRAY_SIZE(zigux_bitmap_view_fields), zigux_bitmap_view_fields},
    {"zigux_cpumask_view", sizeof(struct zigux_cpumask_view), _Alignof(struct zigux_cpumask_view), ARRAY_SIZE(zigux_cpumask_view_fields), zigux_cpumask_view_fields},
    {"zigux_list_head_ref", sizeof(struct zigux_list_head_ref), _Alignof(struct zigux_list_head_ref), ARRAY_SIZE(zigux_list_head_ref_fields), zigux_list_head_ref_fields},
    {"zigux_list_view", sizeof(struct zigux_list_view), _Alignof(struct zigux_list_view), ARRAY_SIZE(zigux_list_view_fields), zigux_list_view_fields},
    {"zigux_list_summary", sizeof(struct zigux_list_summary), _Alignof(struct zigux_list_summary), ARRAY_SIZE(zigux_list_summary_fields), zigux_list_summary_fields},
    {"zigux_hlist_head_ref", sizeof(struct zigux_hlist_head_ref), _Alignof(struct zigux_hlist_head_ref), ARRAY_SIZE(zigux_hlist_head_ref_fields), zigux_hlist_head_ref_fields},
    {"zigux_hlist_node_ref", sizeof(struct zigux_hlist_node_ref), _Alignof(struct zigux_hlist_node_ref), ARRAY_SIZE(zigux_hlist_node_ref_fields), zigux_hlist_node_ref_fields},
    {"zigux_hlist_view", sizeof(struct zigux_hlist_view), _Alignof(struct zigux_hlist_view), ARRAY_SIZE(zigux_hlist_view_fields), zigux_hlist_view_fields},
    {"zigux_hlist_summary", sizeof(struct zigux_hlist_summary), _Alignof(struct zigux_hlist_summary), ARRAY_SIZE(zigux_hlist_summary_fields), zigux_hlist_summary_fields},
    {"zigux_rbtree_root_view", sizeof(struct zigux_rbtree_root_view), _Alignof(struct zigux_rbtree_root_view), ARRAY_SIZE(zigux_rbtree_root_view_fields), zigux_rbtree_root_view_fields},
};

int main(void)
{
    fputs("{\"abi_version\":", stdout);
    fprintf(stdout, "%u", ZIGUX_ABI_VERSION);
    fputs(",\"constants\":{\"facility_kernel\":", stdout);
    fprintf(stdout, "%u", ZIGUX_FACILITY_KERNEL);
    fputs(",\"facility_helpers\":", stdout);
    fprintf(stdout, "%u", ZIGUX_FACILITY_HELPERS);
    fputs(",\"facility_drivers\":", stdout);
    fprintf(stdout, "%u", ZIGUX_FACILITY_DRIVERS);
    fputs(",\"status_flag_error\":", stdout);
    fprintf(stdout, "%u", ZIGUX_STATUS_FLAG_ERROR);
    fputs(",\"panic_abort\":", stdout);
    fprintf(stdout, "%u", ZIGUX_PANIC_ABORT);
    fputs(",\"panic_bug\":", stdout);
    fprintf(stdout, "%u", ZIGUX_PANIC_BUG);
    fputs(",\"panic_warn\":", stdout);
    fprintf(stdout, "%u", ZIGUX_PANIC_WARN);
    fputs(",\"allocator_caller_provided\":", stdout);
    fprintf(stdout, "%u", ZIGUX_ALLOC_CALLER_PROVIDED);
    fputs(",\"allocator_kernel_heap\":", stdout);
    fprintf(stdout, "%u", ZIGUX_ALLOC_KERNEL_HEAP);
    fputs(",\"allocator_arena\":", stdout);
    fprintf(stdout, "%u", ZIGUX_ALLOC_ARENA);
    fputs(",\"unsafe_scope_none\":", stdout);
    fprintf(stdout, "%u", ZIGUX_UNSAFE_NONE);
    fputs(",\"unsafe_scope_volatile_mmio\":", stdout);
    fprintf(stdout, "%u", ZIGUX_UNSAFE_VOLATILE_MMIO);
    fputs(",\"unsafe_scope_raw_pointer_bridge\":", stdout);
    fprintf(stdout, "%u", ZIGUX_UNSAFE_RAW_POINTER_BRIDGE);
    fputs(",\"list_flag_empty\":", stdout);
    fprintf(stdout, "%u", ZIGUX_LIST_FLAG_EMPTY);
    fputs(",\"list_flag_singular\":", stdout);
    fprintf(stdout, "%u", ZIGUX_LIST_FLAG_SINGULAR);
    fputs(",\"list_flag_circular\":", stdout);
    fprintf(stdout, "%u", ZIGUX_LIST_FLAG_CIRCULAR);
    fputs(",\"list_flag_truncated\":", stdout);
    fprintf(stdout, "%u", ZIGUX_LIST_FLAG_TRUNCATED);
    fputs(",\"hlist_flag_empty\":", stdout);
    fprintf(stdout, "%u", ZIGUX_HLIST_FLAG_EMPTY);
    fputs(",\"hlist_flag_singular\":", stdout);
    fprintf(stdout, "%u", ZIGUX_HLIST_FLAG_SINGULAR);
    fputs(",\"hlist_flag_terminated\":", stdout);
    fprintf(stdout, "%u", ZIGUX_HLIST_FLAG_TERMINATED);
    fputs(",\"hlist_flag_truncated\":", stdout);
    fprintf(stdout, "%u", ZIGUX_HLIST_FLAG_TRUNCATED);
    fputs(",\"root_flag_empty\":", stdout);
    fprintf(stdout, "%u", ZIGUX_RBTREE_ROOT_FLAG_EMPTY);
    fputs(",\"root_flag_cached\":", stdout);
    fprintf(stdout, "%u", ZIGUX_RBTREE_ROOT_FLAG_CACHED);
    fputs(",\"root_flag_leftmost_valid\":", stdout);
    fprintf(stdout, "%u", ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID);
    fputs(",\"minor_alloc_flag_truncated\":", stdout);
    fprintf(stdout, "%u", ZIGUX_MINOR_ALLOC_FLAG_TRUNCATED);
    fputs(",\"minor_alloc_flag_found\":", stdout);
    fprintf(stdout, "%u", ZIGUX_MINOR_ALLOC_FLAG_FOUND);
    fputs(",\"minor_alloc_flag_exhausted\":", stdout);
    fprintf(stdout, "%u", ZIGUX_MINOR_ALLOC_FLAG_EXHAUSTED);
    fputs("},\"records\":{\"rbtree_empty_root\":{\"root_addr\":", stdout);
    fprintf(stdout, "%lu", 0UL);
    fputs(",\"leftmost_addr\":0,\"flags\":", stdout);
    fprintf(stdout, "%u", ZIGUX_RBTREE_ROOT_FLAG_EMPTY);
    fputs(",\"reserved\":0},\"rbtree_cached_leftmost_root\":{\"root_addr\":", stdout);
    fprintf(stdout, "%lu", 0x2000UL);
    fputs(",\"leftmost_addr\":", stdout);
    fprintf(stdout, "%lu", 0x1800UL);
    fputs(",\"flags\":", stdout);
    fprintf(stdout, "%u", ZIGUX_RBTREE_ROOT_FLAG_CACHED | ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID);
    fputs(",\"reserved\":0},\"rbtree_uncached_root\":{\"root_addr\":", stdout);
    fprintf(stdout, "%lu", 0x2400UL);
    fputs(",\"leftmost_addr\":0,\"flags\":0,\"reserved\":0}},\"structs\":{", stdout);
    for (size_t i = 0; i < ARRAY_SIZE(layouts); ++i)
        emit_layout(stdout, &layouts[i], i + 1 < ARRAY_SIZE(layouts));
    fputs("}}\n", stdout);
    return 0;
}
