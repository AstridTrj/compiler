from compiler_principle.grammar import Grammar
import copy
import pandas as pd
import numpy as np
from treelib import Tree, Node
from compiler_principle import lexical
from graphviz import Digraph
from compiler_principle import semantic


class PreParse():
    def __init__(self, gra_file, test_file):
        gra_file = 'E:\\PythonWork\\PythonWorking\\compiler\\compiler_principle\\' + gra_file
        self.lex = lexical.Lexical(filename=test_file)
        self.lex.run()
        self.seq = Grammar(gra_file)
        self.nullable = []
        self.first = {}
        self.follow = {}
        self.analysis_table = None
        self.token = self.lex.token
        self.sign_stack = ['#']
        self.token_index = 0
        self.error_ = []
        self.semantic = semantic.Semantic(test_file)
        self.run()

    # NULLABLE集合求解，装入能推出空的非终结符，能推出空包含两种情况
    # 1、S -> $
    # 2、S -> MNP......，其中M, N, P, ...都为非终结符且都属于NULLABLE
    def calculate_nullable(self):
        print('nullabling...')
        flag = True
        # 只要NULLABLE集合在变化则一直进行搜索
        while flag:
            flag = False
            # flag = copy.deepcopy(self.nullable)
            for production in self.seq.per_grammar:
                left, right = production.split('-->')
                pro_list = right.split(' ')
                if len(pro_list) == 1 and pro_list[0] == '$':
                    if left not in self.nullable:
                        self.nullable.append(left)
                        flag = False
                else:
                    if_null = [i for i in pro_list if i in self.nullable]
                    if if_null == pro_list:
                        if left not in self.nullable:
                            self.nullable.append(left)
                            flag = False
                        # self.nullable = list(set(self.nullable))

    # # FIRST集合计算
    def calculate_first(self):
        print('firsting...')
        # 各非终结符FIRST集合初始化
        for non in self.seq.non_term:
            self.first[non] = []
        flag = [0]
        # 只要各FIRST集合有变化则继续搜索
        while flag != self.first:
            # 记录变化前的FIRST
            flag = copy.deepcopy(self.first)
            # 对每个产生式进行遍历判断
            for production in self.seq.per_grammar:
                # 获得产生式左部和右部
                left, _right = production.split('-->')[0].strip(), production.split('-->')[1].strip()
                right = _right.split(' ')
                # 对于S -> ABC，即右部都是非终结符的情况，a_flag记录右部的非终结符是否都能推出$
                a_flag = False
                for beta in right:
                    # S -> $的情况
                    if beta == '$' and ('$' not in self.first[left]):
                        self.first[left].append('$')
                        break
                    # 第一个遇到终结符
                    if beta in self.seq.term:
                        a_flag = True
                        if beta not in self.first[left]:
                            self.first[left].append(beta)
                            break
                        else: break
                    # 第一个遇到非终结符
                    if beta in self.seq.non_term:
                        for k in self.first[beta]:
                            # 将beta的FIRSt中的非空终结符加入left的FIRST中
                            if k != '$' and (k not in self.first[left]):
                                self.first[left].append(k)
                        if beta not in self.nullable:
                            a_flag = True
                            break
                # 如果右部都能推出空，则left的FIRST也需加入$
                if (not a_flag) and ('$' not in self.first[left]):
                    self.first[left].append('$')

    # FOLLOW集合计算
    def calculate_follow(self, start=''):
        print('following')
        # FOLLOW集合初始化
        for non in self.seq.non_term:
            self.follow[non] = []
        # start为文法开始符号
        if start:
            self.follow[start] = ['#']
        # flag = [0]
        f = True
        while f:
            f = False
            # flag = copy.deepcopy(self.follow)
            for production in self.seq.per_grammar:
                left, right = production.split('-->')[0], production.split('-->')[1].split(' ')
                temp = copy.deepcopy(self.follow[left])
                for beta in right[::-1]:
                    if beta in self.seq.term:
                        temp = [beta]
                    if beta in self.seq.non_term:
                        # self.follow[beta].extend([i for i in temp if i != '$'])
                        # self.follow[beta] = list(set(self.follow[beta]))
                        for tp in temp:
                            if tp != '$' and (tp not in self.follow[beta]):
                                f = True
                                self.follow[beta].append(tp)

                        if beta not in self.nullable:
                            temp = copy.deepcopy(self.first[beta])
                        else:
                            temp.extend([i for i in self.first[beta] if i != '$'])
                            temp = list(set(temp))

    # 计算某个产生式右部的first集
    def cal_produ_first(self, production):
        first = []
        right = production.split('-->')[1].strip().split(' ')
        for v in right:
            if v in self.seq.term:
                first.append(v)
                return first
            if v == '$':
                first.append('$')
                return first
            if v in self.seq.non_term:
                for t in self.first[v]:
                    if t != '$':
                        first.append(t)
                if v not in self.nullable:
                    return first
        if '$' not in first:
            first.append('$')
        return first

    # 构造预测分析表
    def create_pre_analysis_table(self):
        print('table creating...')
        self.seq.term.append('#')
        self.analysis_table = pd.DataFrame(index=self.seq.non_term, columns=self.seq.term)
        for production in self.seq.per_grammar:
            left = production.split('-->')[0].strip()
            right_first = self.cal_produ_first(production)
            for a in right_first:
                if a != '$':
                    if self.analysis_table[a][left] is not np.nan:
                        print('anew')
                    self.analysis_table.loc[left, a] = production
            if '$' in right_first:
                for b in self.follow[left]:
                    if self.analysis_table[b][left] is not np.nan:
                        print('anew')
                    self.analysis_table.loc[left, b] = production
        self.seq.term.remove('#')

    def error(self):
        print('Error')

    def change_code(self):
        words = list(self.token[self.token_index])
        if words[0] == '#':
            return words
        if words[1] not in self.seq.term:
            for key, value in self.lex.code.items():
                if value == words[2]:
                    words[1] = key
        return words

    # 预测分析总控程序
    def pre_analysis(self, start=''):
        # 未设置开始符号直接退出
        if not start:
            return
        # 加入#号和文法开始符号
        self.token.append('#')
        self.sign_stack.append(start)
        # 语法分析树结构的记录
        gra_tree = Tree()
        root = gra_tree.create_node(start, str(0))
        node_stack = ['#', root]

        flag = True
        receive = True
        depth = 1
        while flag:
            if len(self.sign_stack) == 0:
                self.error_.append((6, 0, 'failed'))
                break
            # 分析栈
            top_x = self.sign_stack.pop()
            node_top = node_stack.pop()

            # 记录原始符号
            if len(self.token[self.token_index]) > 1:
                org_word = self.token[self.token_index][1]
            else:
                org_word = ' '
            # 对不在终结符的token进行转变
            self.token[self.token_index] = self.change_code()

            if len(self.token[self.token_index]) == 1:
                word, line = self.token[self.token_index][0], 0
            else:
                line, word, code = self.token[self.token_index][0], self.token[self.token_index][1], self.token[self.token_index][2]
            # 终结符
            if top_x in self.seq.term:
                # 终结符与输入符号匹配
                if self.lex.code[top_x] == code:
                    # print('匹配 ', top_x)
                    self.token_index += 1
                else:
                    if (4, line, org_word) not in self.error_:
                        self.error_.append((4, line, org_word))
                    self.error()
                    receive = False
            # 结束符号
            elif top_x == '#':
                if top_x == word:
                    flag = False
                    if receive:
                        self.error_.append((5, 0, 'success'))
                else:
                    if (4, line, org_word) not in self.error_:
                        self.error_.append((4, line, org_word))
                    self.error()
                    receive = False
            # 非终结符
            elif self.analysis_table[word][top_x] is not np.nan:
                production = self.analysis_table[word][top_x]
                right = production.split('-->')[1].strip().split(' ')

                # 记录语法树结构
                temp = []
                for per in right:
                    node = gra_tree.create_node(per, str(depth), node_top)
                    temp.append(node)
                    depth += 1

                if right[0] != '$':
                    self.sign_stack.extend(reversed(right))
                    node_stack.extend(reversed(temp))
            else:
                if (4, line, org_word) not in self.error_:
                    self.error_.append((4, line, org_word))
                self.error()
                receive = False
        temp = copy.deepcopy(self.error_)
        for e in range(len(temp)):
            if temp[e][2] in ['IDENTIFIER', 'CONSTANT']:
                self.error_.remove(temp[e])
        print(self.error_)
        # 生成语法树
        # if len(self.error_) == 1:
        #     if self.error_[0][2] == '成功':
        #         self.draw_tree(gra_tree)
        # 语义检查
        if len(self.error_) == 1:
            if self.error_[0][2] == '语法分析成功':
                self.semantic.run()

    def draw_tree(self, grammar_tree):
        graph = Digraph(name="Tree_depict", format="pdf")
        # 根节点
        root_node = grammar_tree.all_nodes()[0]
        queue_node = [root_node]

        # 利用广度优先遍历语法分析树进行绘制
        while len(queue_node) != 0:
            head_node = queue_node.pop(0)
            color = 'black'
            # 终结符
            if head_node.tag in self.seq.term:
                color = 'red'
            graph.node(name=head_node.identifier, label=head_node.tag, color=color)
            for node in grammar_tree.children(head_node.identifier):
                graph.edge(head_node.identifier, node.identifier)
                queue_node.append(node)
        graph.view(filename="Grammar_tree")

    def run(self, start='translation_unit'):
        self.calculate_nullable()
        self.calculate_first()
        self.calculate_follow(start)
        self.create_pre_analysis_table()
        self.pre_analysis(start)


if __name__ == '__main__':
    path = 'test\\testR.txt'   # test1   simple
    pa = PreParse('CEVStand.txt', path)  # leftcur    CGrammar   gra_test  notLL1   CEVStand   CGrammarNotDe

