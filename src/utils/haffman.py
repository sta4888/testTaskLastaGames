from collections import Counter


class Node:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None


def build_huffman_tree(text):
    frequency = Counter(text)
    nodes = [Node(char, freq) for char, freq in frequency.items()]

    while len(nodes) > 1:
        nodes.sort(key=lambda n: n.freq)

        node1 = nodes.pop(0)
        node2 = nodes.pop(0)

        merged = Node(freq=node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2

        nodes.append(merged)

    return nodes[0]


def get_codes(node, prefix="", code_map={}):
    if node:
        if node.char is not None:
            code_map[node.char] = prefix
        get_codes(node.left, prefix + "0", code_map)
        get_codes(node.right, prefix + "1", code_map)
    return code_map


def encode(text, code_map):
    return ''.join(code_map[char] for char in text)


def decode(encoded_text, tree):
    decoded = ""
    node = tree
    for bit in encoded_text:
        node = node.left if bit == "0" else node.right
        if node.char:
            decoded += node.char
            node = tree
    return decoded


if __name__ == '__main__':
    text = "мама мыла раму"
    tree = build_huffman_tree(text)
    codes = get_codes(tree)
    encoded = encode(text, codes)
    decoded = decode(encoded, tree)
