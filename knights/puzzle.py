from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Or(And(AKnight, AKnave), AKnave)
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Or(And(AKnave, BKnave, AKnight), And(AKnave, BKnight))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(And(AKnight, BKnight), And(AKnave, BKnight)),
    Or(And(BKnight, AKnave), And(BKnave, AKnave))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(AKnight, And(AKnave, AKnight)),
    Or(And(BKnight, And(AKnave, AKnight), CKnave), And(BKnave, CKnight)),
    Or(And(CKnight, AKnight), And(CKnave, AKnave))
)

game_knowledge = And(
    Or(And(AKnave, Not(AKnight)), And(AKnight, Not(AKnave))),
    Or(And(BKnave, Not(BKnight)), And(BKnight, Not(BKnave))),
    Or(And(CKnave, Not(CKnight)), And(CKnight, Not(CKnave))),
)
knowledge0.add(game_knowledge)
knowledge1.add(game_knowledge)
knowledge2.add(game_knowledge)
knowledge3.add(game_knowledge)

def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
