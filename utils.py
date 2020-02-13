


def get_ord_list(word):
    l = []
    for c in word:
        l.append(ord(c))
    return l



if __name__ == '__main__':
    print(get_ord_list("drago sciancato"))