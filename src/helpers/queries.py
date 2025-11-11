def query_yes_no(question):
    """
    Ask a yes/no question via input() and return their answer.
    Repeatedly ask until a proper answer is given.
    """
    match input(question + " [y/n]: ").lower().strip()[:1]:
        case "y":
            return True
        case "n":
            return False
        case _:
            print(f'Sorry, I did not understand that. Let me ask again:')
            return query_yes_no(question)


def query_options(question: str, options: list[str], can_be_canceled=True) -> str | None:
    options_dict = {index + 1: option for index, option in enumerate(options)}
    if can_be_canceled:
        options_dict.update({0: 'Cancel'})
    print(question + "\nYour options are: \n" + "\n".join(f"{i}: {o}" for i, o in options_dict.items()))
    match input(f'Enter your selection [{1} - {len(options)}]: ').lower().strip():
        case '0':
            return None
        case n if n.isdigit() and 1 <= int(n) <= len(options):
            return options_dict[int(n)]
        case _:
            print(f'Sorry, I did not understand that. Let me ask again:')
            return query_options(question, options)


def query_unique(question: str, exclusions: list[str]):
    match input(question):
        case answer if answer.strip() in exclusions:
            print(f'Sorry, {answer} is already in use!')
            return query_unique(question, exclusions)
        case answer if answer.strip() not in exclusions:
            return answer.strip()
        case _:
            # Should be unreachable
            print(f'Sorry, I did not understand that. Let me ask again:')
            return query_unique(question, exclusions)


def query_bounded(question: str, min_value: float, max_value: float):
    answer = input(question)
    try:
        answer = float(answer)
    except ValueError:
        print(f'Sorry, {answer} is not a number!')
        return query_bounded(question, min_value, max_value)
    else:
        if answer < min_value or answer > max_value:
            print(f'Sorry, {answer} is not in the valid range of {min_value} to {max_value}!')
            return query_bounded(question, min_value, max_value)
        else:
            return answer


def query_bounded_int(question: str, min_value: int, max_value: int):
    answer = input(question)
    try:
        answer = int(answer)
    except ValueError:
        print(f'Sorry, {answer} is not an integer!')
        return query_bounded_int(question, min_value, max_value)
    else:
        if answer < min_value or answer > max_value:
            print(f'Sorry, {answer} is not in the valid range of {min_value} to {max_value}!')
            return query_bounded_int(question, min_value, max_value)
        else:
            return answer


def query_bounded_list(question: str, min_value: float, max_value: float, n_elements: int):
    answer = input(question)
    _list = []
    try:
        _list = [float(flow.strip()) for flow in answer.split(',')]
    except ValueError:
        print(f'Sorry, {answer} could not be converted to floats!')
        return query_bounded_list(question, min_value, max_value, n_elements)
    else:
        if len(_list) == n_elements and min_value <= min(_list) <= max_value and min_value <= max(_list) <= max_value:
            return _list
        else:
            print(f'Sorry, {answer} contains values not in the valid range of {min_value} to {max_value}!')
            return query_bounded_list(question, min_value, max_value, n_elements)