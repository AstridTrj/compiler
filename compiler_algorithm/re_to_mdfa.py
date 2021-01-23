import copy
from graphviz import Digraph
import operator


class RetoMFA(object):

    def __init__(self, file='E:\PythonWork\PythonWorking\compiler\compiler_principle/test/reExp.txt', text=''):
        self.exp = text.strip()
        if not text:
            self.read_re_exp(file)
        self.input_sign = []
        self.nfa = []  # nfa边集合
        self.index = -1  # nfa求解计数
        self.num = 0  # nfa状态编号
        self.dfa_status = {}  # nfa转化为dfa时得到的所有状态即其编号
        self.dfa = []  # dfa边集合
        self.dfa_start = []  # dfa初态
        self.dfa_end = []  # dfa的终态集合
        self.mdfa = []  # 最小化的dfa
        self.mdfa_start = []
        self.mdfa_end = []

    # 给读入的正则表达式加乘法点，如ab -> a . b,方便后续转化为后缀式(逆波兰式)
    def add_dot(self):
        re_exp = list(self.exp) + ['#']
        index = 0
        while re_exp[index] != '#':
            if re_exp[index].isalnum() and re_exp[index+1].isalnum():
                re_exp.insert(index+1, '.')
                index += 1
            if re_exp[index].isalnum() and re_exp[index+1] == '(':
                re_exp.insert(index+1, '.')
                index += 1
            if re_exp[index] in ['*', ')'] and (re_exp[index+1].isalnum() or re_exp[index+1] == '('):
                re_exp.insert(index+1, '.')
                index += 1
            index += 1
        re_exp.pop()
        self.exp = ''.join(re_exp)
        print('添加乘法连接符：', self.exp)
        self.infix_to_postfix()

    # 将添加了乘法连接符的正则式转化为后缀式
    def infix_to_postfix(self):
        priority = ['(', ')', '|', '.', '*']  # 各符号优先级
        op_stack = []
        postfix = []
        for alpha in self.exp:
            if alpha.isalnum():
                postfix.append(alpha)
                if alpha not in self.input_sign:
                    self.input_sign.append(alpha)
            elif alpha == '(':
                    op_stack.append(alpha)
            elif alpha == ')':
                while op_stack[-1] != '(':
                    postfix.append(op_stack.pop())
                op_stack.pop()
            else:
                while len(op_stack) > 0 and priority.index(op_stack[-1]) >= priority.index(alpha):
                    postfix.append(op_stack.pop())
                op_stack.append(alpha)
        while len(op_stack) > 0:
            postfix.append(op_stack.pop())
        print('后缀式：', postfix)
        postfix.reverse()
        self.exp = copy.deepcopy(postfix)
        print('反转后的后缀式: ', self.exp)

    # 与连接
    def and_link(self):
        # 获取左右两部分的起点和终点
        n1, n2 = self.create_status()
        n3, n4 = self.create_status()
        # 两者之间添加一条空弧
        self.nfa.append([n4, 'ε', n1])
        # 返回起点和终点，由于是逆波兰式且对逆波兰式进行了反转故n3是起点,n2是终点
        return [n3, n2]

    # 或连接
    def or_link(self):
        # 获取相或的两项的起点和终点
        n1, n2 = self.create_status()
        n3, n4 = self.create_status()
        # 新建两个状态，分别用于左右连接
        n5 = self.get_num()
        n6 = self.get_num()
        # 建立空弧连接
        self.nfa.append([n5, 'ε', n1])
        self.nfa.append([n5, 'ε', n3])
        self.nfa.append([n2, 'ε', n6])
        self.nfa.append([n4, 'ε', n6])
        return [n5, n6]

    # 闭包运算
    def closure_link(self):
        # 闭包运算只涉及一项，故只获取一项的起点和终点
        n1, n2 = self.create_status()
        self.nfa.append([n2, 'ε', n1])
        # 新建用于左右连接的两个状态
        n4 = self.get_num()
        n3 = self.get_num()
        # 建立对应的空弧
        self.nfa.append([n4, 'ε', n1])
        self.nfa.append([n2, 'ε', n3])
        self.nfa.append([n4, 'ε', n3])
        return [n4, n3]

    # 当前字符的判断以及状态的新建
    def create_status(self):
        self.index += 1
        next_ch = self.exp[self.index]
        # res存储对应项的起点和终点
        res = []
        # 依次判断各操作，执行对应的边的创建
        if next_ch == '.':
            res = self.and_link()
        elif next_ch == '|':
            res = self.or_link()
        elif next_ch == '*':
            res = self.closure_link()
        else:  # 为运算对象，则新建两个状态一条边，作为该运算对象的转换
            n1 = self.get_num()
            n2 = self.get_num()
            self.nfa.append([n2, next_ch, n1])
            res = [n2, n1]
        return res

    def get_nfa(self):
        # 递归执行nfa的创建，获得最终整体的起点和终点
        start, end = self.create_status()
        # 绘制nfa
        self.draw_nfa([start], [end])
        self.nfa2dfa(start, end)

    # nfa转化为dfa
    def nfa2dfa(self, start, end):
        num = 0  # dfa状态编号
        first = self.closure_op(start)  # dfa的初始状态，即为nfa起点状态通过空弧所能到达的所有状态
        print("first: ", first)
        stack = [first]  # 存储未访问的dfa的状态
        self.dfa_start.append(0)
        while len(stack) > 0:  # 当所有的dfa的状态都处理则结束循环
            top = stack.pop()
            print("top: ", top)
            if top:
                if str(top) not in self.dfa_status.keys():  # 记录当前的状态并编号
                    self.dfa_status[str(top)] = num
                    num += 1
            for sign in self.input_sign:  # 对每个输入符号，判断top状态所能到达的其他状态
                # 新的状态应为所能到达的且到达状态能通过空弧转换到达的所有状态的集合
                new_sta = self.closure_op(self.nfa_move(top, sign))
                print('new sta: ', new_sta)
                if len(new_sta) > 0:
                    # 记录新的状态并编号
                    if str(new_sta) not in self.dfa_status.keys():
                        self.dfa_status[str(new_sta)] = num
                        num += 1
                        stack.append(new_sta)
                    # 判断结束状态
                    if end in new_sta and (self.dfa_status[str(new_sta)] not in self.dfa_end):
                        self.dfa_end.append(self.dfa_status[str(new_sta)])
                    if start in new_sta and (self.dfa_status[str(new_sta)] not in self.dfa_start):
                        self.dfa_start.append(self.dfa_status[str(new_sta)])
                    # 记录转换边，最终则可构成转换后的dfa
                    self.dfa.append([self.dfa_status[str(top)], sign, self.dfa_status[str(new_sta)]])
        print('dfa sta: ', self.dfa_status)
        self.draw_dfa()  # 绘制dfa
        self.dfa2mdfa()

    # dfa的最小化
    def dfa2mdfa(self):
        original = [self.dfa_end]
        print(self.dfa, 'dfa')
        n_acc = []
        for key, value in self.dfa_status.items():
            if value not in self.dfa_end:
                n_acc.append(value)
        # original装入初始的终态节点集合和非终态节点集合
        original.append(n_acc)
        new_ = copy.deepcopy(original)
        original = []
        # 一直划分直到没有任何集合被划分为止
        while not operator.eq(original, new_):
            original = copy.deepcopy(new_)
            for group in new_:
                for sign in self.input_sign:
                    new_group = {}
                    for status in group:
                        next_s = self.divert_to(status, sign, self.dfa)
                        print('next s: ', next_s)
                        if next_s:
                            t = new_.index([i for i in new_ if next_s in i][0])
                            if t in new_group.keys():
                                new_group[t].add(status)
                            else:
                                new_group[t] = set()
                                new_group[t].add(status)
                        else:
                            s_key = str(len(new_group))
                            while s_key in new_group.keys():
                                s_key += '0'
                            new_group[s_key] = set()
                            new_group[s_key].add(status)
                    if len(new_group.keys()) > 1:
                        new_.remove(group)
                        for _k, value in new_group.items():
                            new_.append(list(value))
                        break
        print('dfa: ', self.dfa)
        self.get_min_dfa(new_)

    def get_min_dfa(self, partition):
        start, end = [], []
        # partition接收得到的mdfa的所有状态
        for index, status in enumerate(partition):
            for point in status:
                if (point in self.dfa_start) and (index not in start):
                    start.append(index)
                if (point in self.dfa_end) and (index not in end):
                    end.append(index)
                for sign in self.input_sign:
                    ori_s = self.divert_to(point, sign, self.dfa)
                    if ori_s:
                        next_s = partition.index([i for i in partition if ori_s in i][0])
                        if [index, sign, next_s] not in self.mdfa:
                            self.mdfa.append([index, sign, next_s])
        self.mdfa_start = start
        self.mdfa_end = end
        print('mdfa: ', self.mdfa)
        print(start, '左起点右终点', end)
        self.draw_mdfa()  # 绘制mdfa

    @staticmethod
    def divert_to(s, sign, table):
        for i in table:
            if i[0] == s and i[1] == sign:
                return i[2]
        return None

    def closure_op(self, start):
        if isinstance(start, (set, list)):
            stack = list(start)
            reach_set = set(copy.deepcopy(start))
        else:
            stack = [start]
            reach_set = {start}
        while len(stack) > 0:
            top = stack.pop()
            for edge in self.nfa:
                if edge[0] == top and edge[1] == 'ε':
                    reach_set.add(edge[2])
                    stack.append(edge[2])
        return list(reach_set)

    def nfa_move(self, sou, sign):
        stack = list(sou)
        reach_set = set()
        while len(stack) > 0:
            top = stack.pop()
            for edge in self.nfa:
                if edge[0] == top and edge[1] == sign:
                    reach_set.add(edge[2])
                    stack.append(edge[2])
        return list(reach_set)

    # nfa图形绘制
    def draw_nfa(self, start, end):
        graph = Digraph(name="NFA", format="png")
        graph.attr(rankdir='LR', nodesep='.25', size="20,5")
        graph.attr(kw='node', _attributes={'shape': 'doublecircle'})
        for point in end:
            graph.node(name=str(point), label=str(point))
        graph.attr(kw='node', _attributes={'shape': 'circle', 'color': 'red'})
        for point in start:
            graph.node(name=str(point), label=str(point))

        graph.attr(kw='node', _attributes={'shape': 'circle', 'color': 'black'})
        for edge in self.nfa:
            graph.node(name=str(edge[0]), label=str(edge[0]))
            graph.node(name=str(edge[2]), label=str(edge[2]))
            graph.edge(tail_name=str(edge[0]), head_name=str(edge[2]), label=str(edge[1]))
        graph.render("img/NFA")

    def draw_dfa(self):
        graph = Digraph(name="DFA", format="png")
        graph.attr(rankdir='LR', nodesep='.25', size="20,5")
        graph.attr(kw='node', _attributes={'shape': 'doublecircle'})
        for point in self.dfa_end:
            graph.node(name=str(point), label=str(point))
        graph.attr(kw='node', _attributes={'shape': 'circle', 'color': 'red'})
        for point in self.dfa_start:
            graph.node(name=str(point), label=str(point))

        graph.attr(kw='node', _attributes={'shape': 'circle', 'color': 'black'})
        for edge in self.dfa:
            graph.node(name=str(edge[0]), label=str(edge[0]))
            graph.node(name=str(edge[2]), label=str(edge[2]))
            graph.edge(tail_name=str(edge[0]), head_name=str(edge[2]), label=str(edge[1]))
        graph.render("img/DFA")

    def draw_mdfa(self):
        graph = Digraph(name="MDFA", format="png")
        graph.attr(rankdir='LR', nodesep='.25', size="20,5")
        graph.attr(kw='node', _attributes={'shape': 'doublecircle'})
        for point in self.mdfa_end:
            graph.node(name=str(point), label=str(point))
        graph.attr(kw='node', _attributes={'shape': 'circle', 'color': 'red'})
        for point in self.mdfa_start:
            graph.node(name=str(point), label=str(point))

        graph.attr(kw='node', _attributes={'shape': 'circle', 'color': 'black'})
        for edge in self.mdfa:
            graph.node(name=str(edge[0]), label=str(edge[0]))
            graph.node(name=str(edge[2]), label=str(edge[2]))
            graph.edge(tail_name=str(edge[0]), head_name=str(edge[2]), label=str(edge[1]))
        graph.render("img/MDFA")

    def read_re_exp(self, path):
        with open(path, "r", encoding='utf-8') as f:
            self.exp = f.read()

    def get_num(self):
        self.num += 1
        return self.num - 1

    def run(self):
        self.add_dot()
        self.get_nfa()


if __name__ == '__main__':
    filename = "test/reExp.txt"
    nfa = RetoMFA(text='a(a|b)*|b')  # (a|(a)*b|c)*(c|df)b*     (a|b)*abb  (a|b)*a(a|b)(a|b)
    nfa.run()