"""Example showing future black string reformatting."""

my_dict = {
    "a key in my dict": a_very_long_variable  # noqa: F821
    * and_a_very_long_function_call()  # noqa: F821
    / 100000.0,
    "another key": (short_value),  # noqa: F821
}
