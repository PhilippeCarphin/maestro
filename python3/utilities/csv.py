
def get_dictionary_list_from_csv(path,
                                 delimiter="\t",
                                 ignore_hash_lines=True,
                                 key_row_index=0):
    """
    For a CSV like this:

    # animals are fun
    name      noise
    sparkle   meow
    george    woof

    Returns this list:
        [
            {"name":"sparkle","noise":"meow"},
            {"name":"george","noise":"woof"}
        ]

    key_row_index is the index of the row to use for keys in the 
    dictionary, ignoring comment lines. Ignore all data rows before this index row.
    """

    with open(path, "r") as f:
        lines = f.readlines()

    if ignore_hash_lines:
        lines = [line for line in lines if not line.strip().startswith("#")]

    results = []
    keys = lines[key_row_index].strip().split(delimiter)

    for i, line in enumerate(lines):

        stripped = line.strip()
        if not stripped:
            continue

        if i == key_row_index:
            continue

        cells = stripped.split(delimiter)
        result = {keys[i]: cells[i] for i in range(len(cells))}
        results.append(result)

    return results
