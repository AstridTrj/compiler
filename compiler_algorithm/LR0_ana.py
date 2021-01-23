import copy
import operator
import numpy as np
import pandas as pd
from graphviz import Digraph


class ItemSet(object):
    def __init__(self):
        self.no = -1
        self.items = []


class LR0Analysis(object):

    def __init__(self, grammar_file="lr_grammar.txt"):
        self.filename = grammar_file
        self.grammar = []
        self.grammar_dict = {}
        self.all_term = []
        self.non_term = []
        self.term = []
        self.item_dfa = []
        self.dfa_start = []
        self.items = []
        self.start = ''
        self.num = 0
        self.action_table = None
        self.go_table = None
        self.result = []

    # 构造LR0自动机，生成项目集的DFA
    def create_item_dfa(self):
        # 确定初始的项目集，即由增广文法添加的一句确定
        first = ItemSet()
        first.items = [["S'", ['.', self.start]]]
        first.no = self.get_num()
        first.items = self.item_closure(first)
        self.items.append(first)
        self.dfa_start.append(first)
        stack = [first]
        # 广度优先生成所有项目集
        while len(stack) > 0:
            item = stack.pop(0)
            # 对每一个项目都遍历所有的符号，包括终结符和非终结符
            for sign in self.all_term:
                # 得到当前项目集通过当前符号能到达的下一个项目集，若没有则会返回None
                next_i = self.go_to(item, sign)
                # 判断是否有下一个项目集，有才进行对应的操作
                if next_i:
                    # 涉及类判断，不能判断编号no，只能判断items属性是否相等
                    not_exist, ext_id = self.item_exist(next_i)
                    # 如果通过判断生成的下一个项目集不在已经存在的项目集中则将其添加到已有集合，并加入栈中
                    if not_exist:
                        stack.append(next_i)
                        self.items.append(next_i)
                    else:  # 如果已经存在，则将全局num减1，保证有序
                        self.num -= 1
                        next_i.no = ext_id
                    # 添加一个关系，即dfa的边
                    self.item_dfa.append([item, sign, next_i])
        # for i in self.items:
        #     print(i.no, end=': ')
        #     for j in i.items:
        #         print(j[0], ' -> ', ' '.join(j[1]), end='     ')
        #     print()
        # print(len(self.item_dfa))
        # for link in self.item_dfa:
        #     print('( ', link[0].no, ': ', link[1], '->', link[2].no, ' )')
        # self.draw_item_dfa()

    def create_analysis_table(self):
        item_num = []
        for item in self.items:
            item_num.append(item.no)
        self.action_table = pd.DataFrame(index=item_num, columns=self.term + ['$'])
        self.go_table = pd.DataFrame(index=item_num, columns=self.non_term)
        for item in self.items:  # 遍历所有的项目集
            for per in item.items:  # 遍历每个项目集里面的所有项目
                left, right = per[0], per[1]  # 每个项目的左部和右部
                if right.index('.') == len(right) - 1:  # 点的位置在最后，即接收或者规约状态
                    if left == "S'":  # 接收状态
                        self.action_table.loc[item.no, '$'] = 'acc'
                    else:  # 规约动作
                        produce = copy.deepcopy(right)
                        produce.remove('.')
                        produce.insert(0, '->')
                        produce.insert(0, left)
                        for a in self.term + ['$']:   # 对每个终结符都设置规约时所选择的表达式
                            if self.action_table.loc[item.no, a] is np.nan:
                                self.action_table.loc[item.no, a] = 'r' + str(self.grammar.index(' '.join(produce).strip())+1)
                else:  # 点不在产生式末尾
                    a = right[right.index('.') + 1]  # 点后的符号
                    e_, id_no = self.item_exist(self.go_to(item, a))  # 当前项目通过当前符号所到达的下一个项目集的编号
                    if a in self.term:  # 遇到终结符，进行规约的动作填写action表
                        if not e_:
                            self.action_table.loc[item.no, a] = 's' + str(id_no)
                    elif a in self.non_term:  # 遇到非终结符，填写goto表
                        if not e_:
                            self.go_table.loc[item.no, a] = id_no
        # print(self.action_table)
        # print(self.go_table)

    def lr0_analysis(self, sequence: str):
        sequence = sequence.split(' ')
        sequence.append('$')
        status_stack = [0]  # 状态栈
        sign_stack = ['$']  # 符号栈
        while True:
            t = [str(i) for i in status_stack]
            cur_res = [' '.join(sign_stack), ' '.join(t), ' '.join(sequence)]
            cur_status = status_stack[-1]
            sign = sequence[0]
            cur_act = self.action_table[sign][cur_status]
            if cur_act[0] == 's':  # 移进
                cur_res.append('移入')
                sequence = sequence[1:]
                sign_stack.append(sign)
                status_stack.append(int(cur_act[1]))
            elif cur_act[0] == 'r':  # 规约
                produce = self.grammar[int(cur_act[1])-1]
                cur_res.append('根据' + produce + '规约')
                left, right = produce.split('->')[0].strip(), produce.split('->')[1].strip().split(' ')
                for i in range(len(right)):
                    sign_stack.pop()
                    status_stack.pop()
                sign_stack.append(left)
                status_stack.append(int(self.go_table[left][status_stack[-1]]))
            elif cur_act == 'acc':
                cur_res.append('接受')
                print('成功，接受')
                self.result.append(cur_res)
                break
            else:
                print('error')
            self.result.append(cur_res)
        for i in self.result:
            print(i)

    def item_closure(self, item: ItemSet):
        last_item = ''
        now_item = copy.deepcopy(item.items)
        while not operator.eq(now_item, last_item):
            last_item = copy.deepcopy(now_item)
            for j in last_item:
                left, right = j[0], j[1]
                if right.index('.') != len(right) - 1:
                    dot_next = right[right.index('.') + 1]
                    if dot_next in self.non_term:
                        for per in self.grammar_dict[dot_next]:
                            add_dot = copy.deepcopy(per)
                            add_dot.insert(0, '.')
                            if [dot_next, add_dot] not in now_item:
                                now_item.append([dot_next, add_dot])
        return last_item

    def go_to(self, item: ItemSet, x):
        new_item = []
        for per_item in item.items:
            left, right = per_item[0], per_item[1]
            if right.index('.') != len(right) - 1:
                dot_next = right[right.index('.') + 1]
                if dot_next == x:
                    new_one = copy.deepcopy(right)
                    new_one.remove('.')
                    new_one.insert(right.index('.')+1, '.')
                    new_item.append([left, new_one])
        if len(new_item) > 0:
            add_item = ItemSet()
            add_item.no = self.get_num()
            add_item.items = new_item
            add_item.items = self.item_closure(add_item)
            return add_item
        return None

    def parse_grammar(self, text, start=''):
        if not start:
            self.start = text[0]
        else:
            self.start = start
        all_term = set()
        self.grammar.extend([i for i in text.split('\n') if i])
        for per in self.grammar:
            left, right = per.split('->')[0].strip(), per.split('->')[1].strip()
            self.non_term.append(left)
            right_list = []
            for i in right.split(' '):
                if i:
                    all_term.add(i.strip())
                    right_list.append(i)
            if left not in self.grammar_dict.keys():
                self.grammar_dict[left] = []
            self.grammar_dict[left].append(right_list)
        all_term = all_term | set(self.non_term)
        self.non_term = list(set(self.non_term))
        self.term = list(all_term - set(self.non_term))
        self.all_term = list(all_term)

    def draw_item_dfa(self):
        graph = Digraph(name="LR_Item_DFA", format="png")
        graph.attr(rankdir='LR', nodesep='.25')
        graph.attr(kw='node', _attributes={'shape': 'rectangle', 'color': 'red'})
        for point in self.dfa_start:
            label = 'I' + str(point.no) + '\n'
            for per in point.items:
                label += per[0] + '→' + ' '.join(per[1]) + '\n'
            graph.node(name=str(point.no), label=label)
        graph.attr(kw='node', _attributes={'shape': 'rectangle', 'color': 'black'})
        graph.attr(kw='graph', _attributes={'splines': 'compound'})
        for link in self.item_dfa:
            first, sign, second = link[0], link[1], link[2]
            # 左部项目集
            label = 'I' + str(first.no) + '\n'
            for per in first.items:
                label += per[0] + '→' + ' '.join(per[1]) + '\n'
            graph.node(name=str(first.no), label=label)
            # 右部项目集
            label = 'I' + str(second.no) + '\n'
            for per in second.items:
                label += per[0] + '→' + ' '.join(per[1]) + '\n'
            graph.node(name=str(second.no), label=label)
            # 建立连接关系
            graph.edge(tail_name=str(first.no), head_name=str(second.no), label=sign)
        graph.render("img/LR_Item_DFA")

    def item_exist(self, item: ItemSet):
        for each_i in self.items:
            flag = True
            id_no = each_i.no
            for element in each_i.items:
                if element not in item.items:
                    flag = False
                    break
            if flag:
                return False, id_no
        return True, -1

    @staticmethod
    def read_grammar(filename=""):
        with open(filename, 'r', encoding='utf-8-sig') as f:
            text = f.read().strip()
        return text

    def get_num(self):
        self.num += 1
        return self.num - 1

    def run(self, text="", seq=""):
        if not text:
            text = self.read_grammar(self.filename)
        self.parse_grammar(text)
        print('grammar: ', self.grammar)
        self.create_item_dfa()
        self.create_analysis_table()
        self.lr0_analysis(sequence=seq)
        self.draw_item_dfa()


if __name__ == '__main__':
    lr0 = LR0Analysis(grammar_file="lr_grammar.txt")  # lr_grammar    simple_gra
    lr0.run()