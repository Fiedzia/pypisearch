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
