"""Print 'Hello world' to the terminal.

This is a simple test script which in the formal form has a missing final
line break - which black will add.

The point of this is the edit position will be at the very end of the file,
which is a corner case.
"""


print("Hello world")