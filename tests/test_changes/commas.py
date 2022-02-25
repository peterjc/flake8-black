"""Example of black and magic commas."""

vegetables = {
    "carrot",
    "parsnip",
    "potato",
    "swede",
    "leak",
    "aubergine",
    "tomato",
    "peas",
    "beans",
}

# This set would easily fit on one line, but a trailing comma
# after the final entry tells black (by default) to leave this
# with one entry per line:
yucky = {
    "aubergine",
    "squid",
    "snails",
}

print("I dislike these vegetables: %s." % ", ".join(vegetables.intersection(yucky)))
