def circle_search(array: list, index_from: int = 0, search_value=1):
    try:
        ind = array.index(search_value, index_from)
        return ind - index_from
    except ValueError:
        ind = array.index(search_value, 0, index_from + 1)
        return len(array) - index_from + ind


