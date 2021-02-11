from unittest import TestCase
from parameterized import parameterized
from nck.utils.list_comparator import (
    get_difference_two_list_order,
    get_intersection_two_lists
)


class TestIntersectionTwoLists(TestCase):
    @parameterized.expand(
        [
            ([], [], []),
            ([], ["1"], []),
            (["1", "2", "3"], ["4", "5", "6"], []),
            (["1", "2", "3"], ["4", "2", "6"], ["2"]),
            (["1", "2", "3"], ["2", "5", "1"], ["1", "2"]),
            (["1", "2", "3"], ["2", "2", "1"], ["1", "2"]),
            (["1", "2", "1"], ["2", "2", "1"], ["1", "2"]),
            (["1", "2", "3"], ["3", "2", "1"], ["1", "2", "3"]),
            (["1", "2", "3"], ["3", "2", "1", "4"], ["1", "2", "3"])
        ]
    )
    def test_get_intersection_two_lists(self, input_list_a, input_list_b, expected):
        self.assertEqual(sorted(get_intersection_two_lists(input_list_a, input_list_b)), expected)


class TestDifferenceTwoListOrder(TestCase):
    @parameterized.expand(
        [
            ([], [], []),
            ([], ["1"], []),
            (["1", "2", "1"], ["2", "2", "1"], []),
            (["1", "2", "3"], ["3", "2", "1"], []),
            (["1", "2", "3"], ["4", "3", "2", "1"], []),
            (["1", "2", "3"], ["2", "5", "1"], ["3"]),
            (["1", "2", "3"], ["2", "2", "1"], ["3"]),
            (["1", "1", "1"], ["3", "2", "2"], ["1"]),
            (["1", "2", "3", "4"], ["3", "2", "1"], ["4"]),
            (["1", "2", "3"], ["4", "2", "6"], ["1", "3"]),
            (["1", "2", "3"], ["4", "5", "6"], ["1", "2", "3"]),
            (["1", "2", "3"], ["4", "5", "6", "7"], ["1", "2", "3"]),
        ]
    )
    def test_get_difference_two_list_order(self, input_list_a, input_list_b, expected):
        self.assertEqual(sorted(get_difference_two_list_order(input_list_a, input_list_b)), expected)
