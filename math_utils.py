def hadamard_product(list_a, list_b):
    """
        compute element-wise product
    """
    if len(list_a) != len(list_b):
        raise ValueError("Lists must have the same length")

    return [a * b for a, b in zip(list_a, list_b)]
