import copy


# 文法读取
class Grammar():

    def __init__(self, filename=''):
        if filename:
            self.text = self.read_grammar_file(filename)
        else:
            self.text = ''
        self.non_term = []
        self.term = []
        self.grammar = {}
        self.per_grammar = []
        self.parse(self.text.strip())
        self.del_left_recur()
        self.extract_factor()

    # 文法整理
    def parse(self, grammar_str):
        all_term = set()
        # 分解为单条文法
        gra_list = [i for i in grammar_str.split('\n') if i]
        for per in gra_list:
            # 获取文法的左边和右边
            gra_one = [i.strip() for i in per.split('-->') if i]
            left, right = gra_one[0], gra_one[1]
            # 非终结符
            self.non_term.append(left)
            p = [i.strip() for i in right.split('|||')]
            self.grammar[left] = p
            for each in p:
                [all_term.add(k.strip()) for k in each.split(' ') if k]
        all_term = all_term | set(self.non_term)
        # 终结符
        self.term = list(all_term - set(self.non_term))

    # 提取左公因子
    def extract_factor(self):
        grammar = copy.deepcopy(self.grammar)
        for key in grammar:
            right = grammar[key]
            common = []
            # 针对同一左部找出两个推导式的相同部分
            for i in range(len(right)):
                for j in range(i+1, len(right)):
                    first, second = right[i].split(' '), right[j].split(' ')
                    prefix, index = '', 0
                    while index < len(first) and index < len(second) and first[index] == second[index]:
                        prefix = prefix + first[index] + ' '
                        index = index + 1
                    common.append(prefix.strip())
            common = [i for i in set(common) if i]
            # 提取左因子
            for com in common:
                not_com = []
                for per in grammar[key]:
                    if per[:len(com)] == com:
                        not_com.append(per[len(com)+1: ])
                        if per in self.grammar[key]:
                            self.grammar[key].remove(per)
                name = com + '\''
                while name in self.non_term:
                    name = name + '\''
                self.grammar[key].append(com + ' ' + name)
                self.grammar[name] = [i if i else '$' for i in not_com]
                self.non_term.append(name)
        self.non_term = list(set(self.non_term))
        for key in self.grammar:
            for per in self.grammar[key]:
                self.per_grammar.append(key + '-->' + per)
        if '$' in self.term:
            self.term.remove('$')

    # 消除直接左递归
    def del_left_recur(self):
        grammar = copy.deepcopy(self.grammar)
        for index in grammar:
            left, right = index, grammar[index]
            have_cur, no_cur = [], []
            for i in range(len(right)):
                if right[i].split(' ')[0] == left:
                    have_cur.append(right[i][len(left)+1:])
                else:
                    no_cur.append(right[i])
            # 若存在左递归则进行消除
            if len(have_cur) > 0:
                name = left + '\''
                while name in self.non_term:
                    name = name + '\''
                self.grammar[left] = [i + ' ' + name for i in no_cur]
                self.grammar[name] = [i + ' ' + name for i in have_cur]
                self.grammar[name].append('$')
                self.non_term.append(name)

    @staticmethod
    def read_grammar_file(filename):
        with open(filename, 'r', encoding='utf-8-sig') as f:
            text = f.read().strip()
        return text

    def write_to_file(self):
        pass


if __name__ == '__main__':
    # syner = Grammar('leftcur.txt')
    syner = Grammar('CGrammar.txt')
    print(len(syner.non_term))