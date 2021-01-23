import pandas as pd
import numpy as np
import operator


def main():
    t = pd.DataFrame(index=['a', 'b', 'c'], columns=['m', 'p', 'l'])

    t = [1, 5, 6, 5, 6]

    t = t[1:]
    print(t)


if __name__ == '__main__':
    main()