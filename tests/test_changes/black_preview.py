"""Example showing future black string reformatting."""


def hello():
    """Print variations on 'Hello World'."""
    # black v22.1.0 (first stable release) does not edit string literals,
    # so the following is untouched unless enable preview mode:
    print("hello " "world")  # noqa: ISC001


hello()
