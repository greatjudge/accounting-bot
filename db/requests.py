from keyboards.for_options import Option


async def save_option_value(option: str, value: str):
    Option.option2storage()[option].append(value)


async def remove_option_value(option: str, value: str):
    Option.option2storage()[option].remove(value)