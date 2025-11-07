def parse_options_query(query_param: str) -> dict[str, str]:
    """
    Converts a query string like:
        'color:red,memory:64GB'
    into:
        {'color': 'red', 'memory': '64GB'}
    """
    if not query_param:
        return {}

    options = {}
    pairs = query_param.split(',')
    for pair in pairs:
        if ':' not in pair:
            continue
        option, value = pair.split(':', 1)
        options[option.strip()] = value.strip()
    return options