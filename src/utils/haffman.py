from collections import Counter


class Node:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None


def sort_nodes_by_freq(nodes):
    n = len(nodes)
    for i in range(n):
        for j in range(0, n - i - 1):
            if nodes[j].freq > nodes[j + 1].freq:
                nodes[j], nodes[j + 1] = nodes[j + 1], nodes[j]


def build_huffman_tree(text):
    frequency = Counter(text)  # подсчет частот
    nodes = []
    for char, freq in frequency.items():
        nodes.append(Node(char, freq))

    print(f"nodes {nodes}")
    for node in nodes:
        print(node.char, node.freq)

    while len(nodes) > 1:
        sort_nodes_by_freq(nodes)

        print(nodes[-1].char, nodes[-1].freq)
        print(nodes)

        node1 = nodes[0]
        node2 = nodes[1]
        print(node1.char, node1.freq)
        print(node2.char, node2.freq)

        merged = Node(freq=node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2

        # Удаляем первые два узла
        new_nodes = []
        for i in range(2, len(nodes)):
            new_nodes.append(nodes[i])
        new_nodes.append(merged)
        nodes = new_nodes

    return nodes[0]


def get_codes(node, prefix="", code_map=None):
    if code_map is None:
        code_map = {}

    if node is not None:
        if node.char is not None:
            code_map[node.char] = prefix
        get_codes(node.left, prefix + "0", code_map)
        get_codes(node.right, prefix + "1", code_map)

    return code_map


def encode(text, code_map):
    result = ""
    for char in text:
        result += code_map[char]
    return result


def decode(encoded_text, tree):
    decoded = ""
    node = tree
    for bit in encoded_text:
        if bit == "0":
            node = node.left
        else:
            node = node.right

        if node.char is not None:
            decoded += node.char
            node = tree

    return decoded


if __name__ == '__main__':
    text = "мама мыла раму"
    tree = build_huffman_tree(text)
    codes = get_codes(tree)
    encoded = encode(text, codes)
    decoded = decode(encoded, tree)
