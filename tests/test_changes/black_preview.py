"""Example showing future black string reformatting."""

a_very_long_variable = 17.3
short_value = 1234567890


def and_a_very_long_function_call():
    """Deep thought."""
    return 42


my_dict = {
    "a key in my dict": a_very_long_variable
    * and_a_very_long_function_call()
    / 100000.0,
    "another key": (short_value),
}
