#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

struct list_head {
    uintptr_t next;
    uintptr_t prev;
};

struct hlist_head {
    uintptr_t first;
};

struct hlist_node {
    uintptr_t next;
    uintptr_t pprev;
};

static uintptr_t ptr_of(const void *ptr) {
    return (uintptr_t)ptr;
}

static const char *list_label(
    const struct list_head *head,
    const struct list_head *first,
    const struct list_head *second,
    uintptr_t raw
) {
    if (raw == 0) return "null";
    if (raw == ptr_of(head)) return "head";
    if (raw == ptr_of(first)) return "node0";
    if (raw == ptr_of(second)) return "node1";
    return "unknown";
}

static const char *hlist_label(
    const struct hlist_head *head,
    const struct hlist_node *first,
    const struct hlist_node *second,
    uintptr_t raw
) {
    if (raw == 0) return "null";
    if (raw == ptr_of(&head->first)) return "head.first";
    if (raw == ptr_of(&first->next)) return "node0.next";
    if (raw == ptr_of(first)) return "node0";
    if (raw == ptr_of(second)) return "node1";
    return "unknown";
}

static void write_optional_index(int value) {
    if (value < 0) {
        fputs("null", stdout);
        return;
    }
    printf("%d", value);
}

static void write_optional_label(const char *value) {
    if (value == NULL) {
        fputs("null", stdout);
        return;
    }
    printf("\"%s\"", value);
}

static int list_index(
    const struct list_head *head,
    const struct list_head *first,
    const struct list_head *second,
    const struct list_head *node
) {
    if (node == NULL || node == head) return -1;
    if (node == first) return 0;
    if (node == second) return 1;
    return -1;
}

static void write_list_case(
    const char *name,
    const struct list_head *head,
    const struct list_head *first,
    const struct list_head *second,
    bool trailing_comma
) {
    bool is_empty = head->next == ptr_of(head) && head->prev == ptr_of(head);
    const struct list_head *first_node = NULL;
    const struct list_head *last_node = NULL;
    size_t len = 0;
    bool backlinks_consistent = true;
    int broken_index = -1;
    const char *expected_label = NULL;
    const char *actual_label = NULL;
    uintptr_t expected_prev = ptr_of(head);
    const struct list_head *cursor = (head->next == 0) ? NULL : (const struct list_head *)head->next;

    if (cursor != NULL && cursor != head) {
        first_node = cursor;
        while (cursor != head) {
            if (cursor->prev != expected_prev && broken_index < 0) {
                backlinks_consistent = false;
                broken_index = (int)len;
                expected_label = list_label(head, first, second, expected_prev);
                actual_label = list_label(head, first, second, cursor->prev);
            }
            last_node = cursor;
            expected_prev = ptr_of(cursor);
            len += 1;
            cursor = (cursor->next == 0) ? NULL : (const struct list_head *)cursor->next;
            if (cursor == NULL) {
                if (broken_index < 0) {
                    backlinks_consistent = false;
                    broken_index = (int)len;
                    expected_label = list_label(head, first, second, expected_prev);
                    actual_label = "null";
                }
                break;
            }
        }
        if (cursor == head && head->prev != expected_prev && broken_index < 0) {
            backlinks_consistent = false;
            broken_index = (int)len;
            expected_label = list_label(head, first, second, expected_prev);
            actual_label = list_label(head, first, second, head->prev);
        }
    }

    printf(
        "    {\n"
        "      \"name\": \"%s\",\n"
        "      \"is_empty\": %s,\n"
        "      \"len\": %zu,\n"
        "      \"first_index\": ",
        name,
        is_empty ? "true" : "false",
        len
    );
    write_optional_index(list_index(head, first, second, first_node));
    fputs(",\n      \"last_index\": ", stdout);
    write_optional_index(list_index(head, first, second, last_node));
    printf(
        ",\n"
        "      \"backlinks_consistent\": %s,\n"
        "      \"first_broken_index\": ",
        backlinks_consistent ? "true" : "false"
    );
    write_optional_index(broken_index);
    fputs(",\n      \"expected_prev_label\": ", stdout);
    write_optional_label(expected_label);
    fputs(",\n      \"actual_prev_label\": ", stdout);
    write_optional_label(actual_label);
    fputs("\n    }", stdout);
    if (trailing_comma) {
        fputc(',', stdout);
    }
    fputc('\n', stdout);
}

static int hlist_index(
    const struct hlist_node *first,
    const struct hlist_node *second,
    const struct hlist_node *node
) {
    if (node == NULL) return -1;
    if (node == first) return 0;
    if (node == second) return 1;
    return -1;
}

static void write_hlist_case(
    const char *name,
    const struct hlist_head *head,
    const struct hlist_node *first,
    const struct hlist_node *second,
    bool trailing_comma
) {
    bool is_empty = head->first == 0;
    const struct hlist_node *first_node = head->first == 0 ? NULL : (const struct hlist_node *)head->first;
    size_t len = 0;
    bool first_pprev_matches_head = true;
    bool prev_links_consistent = true;
    bool tail_next_is_null = true;
    int broken_index = -1;
    const char *expected_label = NULL;
    const char *actual_label = NULL;
    uintptr_t expected_pprev = ptr_of(&head->first);
    const struct hlist_node *cursor = first_node;
    const struct hlist_node *tail = NULL;

    if (first_node != NULL) {
        first_pprev_matches_head = first_node->pprev == ptr_of(&head->first);
    }

    while (cursor != NULL) {
        if (cursor->pprev != expected_pprev && broken_index < 0) {
            prev_links_consistent = false;
            broken_index = (int)len;
            expected_label = hlist_label(head, first, second, expected_pprev);
            actual_label = hlist_label(head, first, second, cursor->pprev);
        }
        tail = cursor;
        expected_pprev = ptr_of(&cursor->next);
        len += 1;
        cursor = cursor->next == 0 ? NULL : (const struct hlist_node *)cursor->next;
    }

    if (tail != NULL) {
        tail_next_is_null = tail->next == 0;
    }

    printf(
        "    {\n"
        "      \"name\": \"%s\",\n"
        "      \"is_empty\": %s,\n"
        "      \"len\": %zu,\n"
        "      \"first_index\": ",
        name,
        is_empty ? "true" : "false",
        len
    );
    write_optional_index(hlist_index(first, second, first_node));
    printf(
        ",\n"
        "      \"first_pprev_matches_head\": %s,\n"
        "      \"prev_links_consistent\": %s,\n"
        "      \"tail_next_is_null\": %s,\n"
        "      \"first_broken_index\": ",
        first_pprev_matches_head ? "true" : "false",
        prev_links_consistent ? "true" : "false",
        tail_next_is_null ? "true" : "false"
    );
    write_optional_index(broken_index);
    fputs(",\n      \"expected_pprev_label\": ", stdout);
    write_optional_label(expected_label);
    fputs(",\n      \"actual_pprev_label\": ", stdout);
    write_optional_label(actual_label);
    fputs("\n    }", stdout);
    if (trailing_comma) {
        fputc(',', stdout);
    }
    fputc('\n', stdout);
}

int main(void) {
    struct list_head list_empty_head = {0, 0};
    list_empty_head.next = ptr_of(&list_empty_head);
    list_empty_head.prev = ptr_of(&list_empty_head);

    struct list_head list_ordered_head = {0, 0};
    struct list_head list_ordered_first = {0, 0};
    struct list_head list_ordered_second = {0, 0};
    list_ordered_head.next = ptr_of(&list_ordered_first);
    list_ordered_head.prev = ptr_of(&list_ordered_second);
    list_ordered_first.next = ptr_of(&list_ordered_second);
    list_ordered_first.prev = ptr_of(&list_ordered_head);
    list_ordered_second.next = ptr_of(&list_ordered_head);
    list_ordered_second.prev = ptr_of(&list_ordered_first);

    struct list_head list_broken_head = {0, 0};
    struct list_head list_broken_first = {0, 0};
    struct list_head list_broken_second = {0, 0};
    list_broken_head.next = ptr_of(&list_broken_first);
    list_broken_head.prev = ptr_of(&list_broken_second);
    list_broken_first.next = ptr_of(&list_broken_second);
    list_broken_first.prev = ptr_of(&list_broken_head);
    list_broken_second.next = ptr_of(&list_broken_head);
    list_broken_second.prev = ptr_of(&list_broken_head);

    struct hlist_head hlist_empty_head = {0};

    struct hlist_head hlist_ordered_head = {0};
    struct hlist_node hlist_ordered_first = {0, 0};
    struct hlist_node hlist_ordered_second = {0, 0};
    hlist_ordered_head.first = ptr_of(&hlist_ordered_first);
    hlist_ordered_first.next = ptr_of(&hlist_ordered_second);
    hlist_ordered_first.pprev = ptr_of(&hlist_ordered_head.first);
    hlist_ordered_second.next = 0;
    hlist_ordered_second.pprev = ptr_of(&hlist_ordered_first.next);

    struct hlist_head hlist_broken_head = {0};
    struct hlist_node hlist_broken_first = {0, 0};
    struct hlist_node hlist_broken_second = {0, 0};
    hlist_broken_head.first = ptr_of(&hlist_broken_first);
    hlist_broken_first.next = ptr_of(&hlist_broken_second);
    hlist_broken_first.pprev = ptr_of(&hlist_broken_head.first);
    hlist_broken_second.next = 0;
    hlist_broken_second.pprev = ptr_of(&hlist_broken_head.first);

    printf("{\n  \"word_bits\": %zu,\n  \"list_cases\": [\n", sizeof(uintptr_t) * 8U);
    write_list_case("empty", &list_empty_head, &list_empty_head, &list_empty_head, true);
    write_list_case("ordered_two", &list_ordered_head, &list_ordered_first, &list_ordered_second, true);
    write_list_case("broken_backlink", &list_broken_head, &list_broken_first, &list_broken_second, false);
    fputs("  ],\n  \"hlist_cases\": [\n", stdout);
    write_hlist_case("empty", &hlist_empty_head, &hlist_ordered_first, &hlist_ordered_second, true);
    write_hlist_case("ordered_two", &hlist_ordered_head, &hlist_ordered_first, &hlist_ordered_second, true);
    write_hlist_case("broken_prev_link", &hlist_broken_head, &hlist_broken_first, &hlist_broken_second, false);
    fputs("  ]\n}\n", stdout);
    return 0;
}
