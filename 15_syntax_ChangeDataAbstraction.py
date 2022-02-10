def leaves(t):
    if is_leaf(t):
        return [t]
    else:
        return sum([leaves(b) for b in branches(t)], [])


treebank_examples = """
(ROOT (SBARQ (WHNP (WP what))
    (SQ (VP (AUX is)) (NP (DT the) (NN rabbit)) (VP (VBG doing)))
    (. ?)))

(ROOT (SQ (AUX is) (NP (PRP he)) (VP (VBG hopping)) (. ?)))

""".split(
    "\n"
)


def phrase(tag, branches):
    return ['(', tag] + sum(branches, []) + [')']


def word(tag, text):
    return ['(', tag, text, ')']


def tag(t):
    """Return the tag of a phrase or word."""
    return t[1]


def text(w):
    return w[2]


def branches(t):
    if is_leaf(t):
        return []
    branch = []
    branches = []
    opened = 1
    for token in t[2:]:
        branch.append(token)
        if token == '(':
            opened += 1
        if token == ')':
            opened -= 1
            if opened == 1:
                branches.append(branch)
                branch = []
    return branches


def is_leaf(t):
    return len(t) == 4


def read_sentences(input):
    """Yield parsed sentences as lists of tokens for a list of lines.

    >>> for s in read_sentences(treebank_examplews):
    ...     print(' '.join(s[:20]), '...')
    ( ROOT ( SBARQ ( WHNP ( WP what ) ) ( SQ ( VP ( AUX is ) ) ...
    ( ROOT ( SQ ( AUX is ) ( NP ( PRP he ) ) ( VP ( VBG hopping ...
    """
    sentences = []
    tokens = []
    for line in input:
        if line.strip():
            tokens.extend(line.replace("(", " ( ").replace(")", " ) ").split())
            if tokens.count("(") == tokens.count(")"):
                sentences.append(tokens)
                tokens = []
    return sentences
            

def all_sentences():
    return read_sentences(open("suppes.parsed").readlines())


def tokens_to_parse_tree(tokens):
    return tokens


def is_valid_tree(t):
    return t and tag(t)


def print_parse_tree(t):
    """Print the parse tree in its original format.

    >>> print_parse_tree(tokens_to_parse_tree(read_sentences(treebank_examples)[0]))
    '(ROOT (SBARQ (WHNP (WP what)) (SQ (VP (AUX is)) (NP (DT the) (NN rabbit)) (VP (VBG doing))) (. ?)))'
    """
    if is_leaf(t):
        return "("  + tag(t) + " " + text(t) + ")"
    else:
        result = "(" + tag(t)
        for b in branches(t):
            result += " " + print_parse_tree(b)
        result += ")"
        return result


from string import punctuation


def words(t):
    """Return the words of a tree as a string.

    >>> words(tokens_to_parse_tree(read_sentences(treebank_examples)[0]))
    'what is the rabbit doing?'
    """
    s = ""
    for leaf in leaves(t):
        w = text(leaf)
        if (
            not s
            or (w in punctuation and w not in "$")
            or w in ["n't", "'s", "'re", "'ve"]
        ):
            s = s + w
        else:
            s = s + " " + w
    return s



# Sentence Generator


def nodes(t):
    result = []

    def traverse(t):
        result.append([tag(t), t])
        for b in branches(t):
            traverse(b)

    traverse(t)
    return result

def index_trees(trees):
    """Return a dictionary from tags to lists of trees."""
    index = {}
    for t in trees:
        for tag, node in nodes(t):
            if tag not in index:
                index[tag] = []
            index[tag].append(node)
    return index


import random


def coin(prob):
    def flip():
        """Return True if a coin filp comes up heads."""
        return random.random() < prob

    return flip


def gen_tree(t, tree_index, flip):
    """Return a version of t in which consitituents are randomly replaced."""
    new_branches = []
    if is_leaf(t):
        return t
    for b in branches(t):
        if flip():
            # original = b
            b = random.choice(tree_index[tag(b)])
            # print('Replacing', print_parse_tree(original), 'with', print_parse_tree(b))
        new_branches.append(gen_tree(b, tree_index, flip))
    return phrase(tag(t), new_branches)


def generate(gen=gen_tree):
    trees = [tokens_to_parse_tree(s) for s in all_sentences() if len(s) > 100] 
    tree_index = index_trees(trees)
    while True:
        original = random.choice(trees)
        print("Original: ", words(original).lower())
        edited = gen(original, tree_index, coin(0.3))
        input()
        print("Generated: ", words(edited).lower())
        input()
