def fibonacci(n):
    """
    计算斐波那契数Column的第 n 项
    """
    if n < 0:
        raise ValueError('n 必须Yes非负Integer')
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fibonacci_sequence(n):
    """
    生成斐波那契数Column的Before n 项
    """
    if n <= 0:
        return []
    if n == 1:
        return [0]
    seq = [0, 1]
    for _ in range(2, n):
        seq.append(seq[-1] + seq[-2])
    return seq


if __name__ == '__main__':
    print('斐波那契数ColumnBefore 10 项:', fibonacci_sequence(10))
    print('第 10 项的值:', fibonacci(10))
