from typing import List, Any, Callable, Optional


def sort_list(
    data: List[Any],
    key: Optional[Callable] = None,
    reverse: bool = False
) -> List[Any]:
    """通螨SortFunction
    
    Args:
        data: 要Sort的List
        key: Sort键Function (Optional)
        reverse: YesNo降序排Column，Default升序
    
    Returns:
        SortAfter的NewList
    """
    return sorted(data, key=key, reverse=reverse)


def quick_sort(arr: List[int]) -> List[int]:
    """FastSortImplement"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)


if __name__ == "__main__":
    test = [64, 34, 25, 12, 22, 11, 90]
    print(f"Original: {test}")
    print(f"Sort: {sort_list(test)}")
    print(f"快排: {quick_sort(test)}")