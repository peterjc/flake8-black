"""Invalid under Python 3, example with mixed indentation."""

if True:
    print("This line was indented with four spaces!")
    if True:
        print("This line was indented with eight spaces.")
    if True:
	print("This line was indented with a tab!")
