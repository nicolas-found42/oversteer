"""Decode BDL draw indices using the topology word at descriptor +12."""


def triangles(indices, topology):
    if topology == 1:
        if len(indices) % 3 or 65535 in indices:
            raise ValueError("Invalid triangle-list draw")
        return list(indices)
    if topology != 0:
        raise ValueError(f"Unknown BDL draw topology: {topology}")
    result = []
    strip = []
    for index in indices:
        if index == 65535:
            strip = []
            continue
        strip.append(index)
        if len(strip) >= 3:
            a, b, c = strip[-3:]
            if len(strip) % 2 == 0:
                a, b = b, a
            if len({a, b, c}) == 3:
                result.extend((a, b, c))
    return result
