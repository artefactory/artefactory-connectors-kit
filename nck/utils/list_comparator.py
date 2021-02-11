from typing import List


def get_intersection_two_lists(list_a: List[str], list_b: List[str]) -> List[str]:
    return list(set(list_a) & set(list_b))


def get_difference_two_list_order(list_a: List[str], list_b: List[str]) -> List[str]:
    """This function will return a list of elements from list a which are not in list b."""
    return list(set(list_a).difference(list_b))
