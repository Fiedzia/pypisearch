def validate_int(v, vmin=None, vmax=None, default=0):
    value = v
    try:
        value = int(v)
    except ValueError:
        return default
    if vmin is not None and value < vmin:
        return default
    if vmax is not None and value > vmax:
        return default

    return value


def get_page_no(start_idx, total, base=1):
    """
    Return page position for an item wih given index within set of total items
    """
    page_no = start_idx // total + int(bool(start_idx % total))
    if base == 1:
        page_no += 1
    return page_no
