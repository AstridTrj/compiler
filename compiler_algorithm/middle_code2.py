from compiler_principle import lexical


class MiddleCodePlus(object):

    def __init__(self, file):
        lex = lexical.Lexical(file)
        lex.run()
        self.tokens = lex.token
        self.length = len(self.tokens)
        self.index = 0
        self.four = [('begin', '_', '_', '_')]
        self.var = 'T'
        self.n = 0

    def judge_execute(self):
        while self.index < len(self.tokens):
            if self.tokens[self.index][1] in ['if', 'for', 'while', 'do']:
                port, _t = self.compound_statement()
            elif self.tokens[self.index][2] == 900 and self.tokens[self.index+1][1] in ['=', '+=', '-=', '*=', '/=', '%=']:
                self.assignment()
            elif self.tokens[self.index][2] == 900 and self.tokens[self.index+1][1] == '(':
                self.fun_call()
            else:
                pass
            self.index += 1

    # 简单赋值语句处理
    def assignment(self):
        # 等号左边标识符
        left = self.tokens[self.index][1]
        self.index += 2
        op = self.tokens[self.index - 1][1]
        infix = []

        # 若为字符串则单独处理
        if self.tokens[self.index][2] == 800:
            self.four.append((op, self.tokens[self.index][1], '_', left))
            self.index += 1
        else:
            while self.tokens[self.index][1] != ';':
                infix.append(self.tokens[self.index])
                self.index += 1
            if len(infix) == 1:
                self.four.append((op, infix[0][1], '_', left))
            else:
                var = self.infix_to_postfix(infix)
                self.four.append((op, var, '_', left))
            self.index += 1

    # if语句的四元式处理
    def if_statement(self):
        self.index += 1  # 跳到if后的布尔表达式
        true, false = self.boolean_exp()  # 执行布尔表达式，得到其真假出口
        self.back_fill(true, len(self.four))  # 回填真出口
        if self.tokens[self.index][1] == ')':
            self.index += 1
        s1_chain, res = self.compound_statement()  # 执行if后复合语句,若有退出链，放入s1_chain

        q, t_chain, s_chain = len(self.four), 0, 0
        self.four.append(('j', '_', '_', '0'))  # 跳过S2
        if s1_chain and not res:
            t_chain = self.merge(s1_chain, q)
        else:
            t_chain = q

        # 处理else语句
        if self.index < len(self.tokens) and self.tokens[self.index][1] == 'else':
            self.back_fill(false, len(self.four))  # 回填if假出口
            self.index += 1
            s2_chain, _s = self.compound_statement()  # 执行else后的复合语句
            if s2_chain and not _s:
                s_chain = self.merge(s2_chain, t_chain)
            else:
                s_chain = t_chain
        return s_chain

    # 复合语句处理
    def compound_statement(self):
        port = 0
        not_return = True
        while self.index < len(self.tokens):
            if self.tokens[self.index][1] == '{':
                self.index += 1
                continue
            elif self.tokens[self.index][1] == '}':
                self.index += 1
                break
            elif self.tokens[self.index][1] == 'if':
                port = self.if_statement()
                if port:
                    self.back_fill(port, len(self.four))
            elif self.tokens[self.index][1] == 'for':
                self.for_statement()
            elif self.tokens[self.index][1] == 'while':
                self.while_statement()
            elif self.tokens[self.index][1] == 'do':
                self.do_statement()
            elif self.tokens[self.index][2] == 900 and self.tokens[self.index+1][1] in ['=', '+=', '-=', '*=', '/=', '%=']:
                self.assignment()
            elif self.tokens[self.index][2] == 900 and self.tokens[self.index+1][1] == '(':
                self.fun_call()
            else:
                # print('error', self.tokens[self.index])
                self.index += 1
        return port, not_return

    def for_e3(self):
        e3_list = []
        while self.tokens[self.index][1] != ')':
            e3_list.append(self.tokens[self.index])
            self.index += 1
        if len(e3_list) == 2:
            self.four.append((e3_list[1][1][0], e3_list[0][1], '1', self.var+str(self.n)))
            self.four.append(('=', self.var + str(self.n), '_', e3_list[0][1]))
            self.n += 1
        else:
            left = e3_list[0][1]
            e3_list.pop(0)
            e3_list.pop(0)
            right = self.infix_to_postfix(e3_list)
            self.four.append(('=', right, '_', left))

    def for_statement(self):
        self.index += 2
        self.assignment()  # E1 部分
        self.index -= 1
        test = len(self.four)  # 记录E2部分的起点
        true, false = self.boolean_exp()  # 得到E2部分的真假出口
        e3_inc = len(self.four)  # E3部分入口
        self.index += 1  # 跳过E2与E3之间的分号
        self.for_e3()
        self.index += 1  # 跳过右括号
        self.four.append(('j', '_', '_', str(test)))  # E3执行完跳转到E2进行判断
        # S部分执行
        self.back_fill(true, len(self.four))  # 回填E2的真出口
        port, not_return = self.compound_statement()  # not_return指示port是否是S部分中间跳出
        b_chain = false
        if not not_return:  # 如果S部分中间有跳出，则将E2假出口false与port合并
            b_chain = self.merge(false, port)
        self.four.append(('j', '_', '_', str(e3_inc)))  # E3执行完后跳转到E3继续循环
        self.back_fill(b_chain, len(self.four))

    def while_statement(self):
        # while E S
        self.index += 1
        head = len(self.four)
        true, false = self.boolean_exp()
        self.back_fill(true, len(self.four))  # 立刻回填真出口
        self.index += 1  # 跳过右括号
        port, not_return = self.compound_statement()
        if not not_return:  # 若有中途退出的，则回填为退出后的四元式编号
            self.back_fill(port, len(self.four))
        else:
            self.four.append(('j', '_', '_', str(head)))
        self.back_fill(false, len(self.four))

    def do_statement(self):
        # do S while E;
        self.index += 1  # 跳过关键字do
        do_head = len(self.four)  # 记录S部分的开头，以回填E的真出口
        port, not_return = self.compound_statement()  # S部分四元式生成
        if not not_return:
            self.back_fill(port, len(self.four))
        self.index += 1  # 跳过关键字while
        true, false = self.boolean_exp()  # E的真假出口
        self.back_fill(true, do_head)  # 回填E的真出口为do_head
        self.back_fill(false, len(self.four))
        self.index += 2

    def fun_call(self):
        if self.tokens[self.index-1][1] not in ['void', 'int', 'float', 'double']:
            func_name = self.tokens[self.index][1]
            self.index += 2
            while self.index < len(self.tokens) and self.tokens[self.index][1] not in [';', ')']:
                name_list = []
                while self.index < len(self.tokens) and self.tokens[self.index][1] not in [',', ')']:
                    name_list.append(self.tokens[self.index])
                    self.index += 1
                var = self.infix_to_postfix(name_list)
                self.four.append(('para', var, '_', '_'))
                self.index += 1
            self.four.append(('call', func_name, '_', '_'))

    # 布尔表达式处理
    def boolean_exp(self):
        right_true, right_false = '', ''
        # 根据优先级处理,先处理逻辑或左右的式子，即逻辑与非和关系表达式
        left_true, left_false = self.logical_or_exp()
        if self.tokens[self.index][1] == '||':
            # 回填左部的假出口
            if left_false and left_false != '0':
                need_fill = self.four[left_false]
                self.four[left_false] = (need_fill[0], need_fill[1], need_fill[2], len(self.four))
            # 继续执行||后面的表达式
            right_true, right_false = self.boolean_exp()
        if right_true:
            true = self.merge(left_true, right_true)
            return true, right_false
        else:
            return left_true, left_false

    # 逻辑或表达式
    def logical_or_exp(self):
        # 处理逻辑与左右的式子,即逻辑非和关系表达式
        left_true, left_false = self.relation_exp()
        right_true, right_false = '', ''
        if self.tokens[self.index][1] == '&&':
            # 回填左部的真出口
            if left_true and left_true != '0':
                need_fill = self.four[left_true]
                self.four[left_true] = (need_fill[0], need_fill[1], need_fill[2], len(self.four))
            # 继续执行&&后面的表达式
            right_true, right_false = self.logical_or_exp()
        if right_false:
            # 合并前后的假出口并返回，该假出口即整个表达式的假出口
            false = self.merge(left_false, right_false)
            return right_true, false
        else:
            return left_true, left_false

    # 关系表达式处理
    def relation_exp(self):
        self.index += 1
        # 逻辑非后仍为一个关系表达式
        if self.tokens[self.index][1] == '!':
            return self.relation_exp()
        else:
            # 若为左括号其后则为一表达式
            if self.tokens[self.index][1] == '(':
                true, false = self.boolean_exp()
                if self.tokens[self.index][1] == ')':
                    self.index += 1
                return true, false
            else:
                infix = []
                while self.tokens[self.index][1] not in ['>', '<', '>=', '<=', '!=', '==', '&&', '||', ';']:
                    infix.append(self.tokens[self.index])
                    self.index += 1
                # 获取左部存储最后结果的变量
                left = self.infix_to_postfix(infix)
                # 若下一个字符是关系运算符则获取其右部，否则进行回填
                if self.tokens[self.index][1] in ['>', '<', '>=', '<=', '!=', '==']:
                    # 记录当前的关系运算符号
                    relation_op = self.tokens[self.index][1]
                    self.index += 1
                    infix.clear()
                    # 计算关系运算符的右部的表达式
                    while self.tokens[self.index][1] not in ['>', '<', '>=', '<=', '!=', '==', '&&', '||', ';', ')']:
                        infix.append(self.tokens[self.index])
                        self.index += 1
                    # 获取右部最后计算出来的变量
                    right = self.infix_to_postfix(infix)
                    relation_op = 'j' + relation_op  # 跳转符号
                    # 产生一条真出口和一条假出口的四元式
                    true_port = len(self.four)
                    self.four.append((relation_op, left, right, '0'))
                    false_port = len(self.four)
                    self.four.append(('j', '_', '_', '0'))
                    return true_port, false_port
                else:  # 此时无关系运算符，只有一个表达式
                    true_port = len(self.four)
                    self.four.append(('jnz', left, '_', '0'))
                    false_port = len(self.four)
                    self.four.append(('j', '_', '_', '0'))
                    return true_port, false_port

    def print_four(self):
        for i, meta in enumerate(self.four):
            print(i, meta)

    # 合并两个四元式链，返回合并后的链首
    def merge(self, first, second):
        p_i = int(second)
        if p_i == 0:
            return first
        while int(self.four[p_i][3]) != 0:
            p_i = int(self.four[p_i][3])
        now_ = self.four[p_i]
        self.four[p_i] = (now_[0], now_[1], now_[2], first)
        return second

    # 回填出口
    def back_fill(self, port, now_port):
        # print('*'*100)
        # self.print_four()
        # print('*'*100)

        p_i, pre = int(port), 0
        while p_i != 0:
            last = self.four[p_i]
            self.four[p_i] = (last[0], last[1], last[2], now_port)
            p_i = int(last[3])

    # 简单赋值表达式转化为逆波兰式(中缀转后缀)
    def infix_to_postfix(self, infix):
        # print(infix, 'infix')
        # :param infix: 包含各
        # 表达式组成部分的token
        # :return postfix: 逆波兰式
        op_stack = []  # 操作符栈
        postfix = []  # 逆波兰式(后缀表达式)
        op_priority = {'*': 2, '/': 2, '%': 2, '+': 1, '-': 1, '(': 0, ')': 0}  # 优先级
        # op_priority = {'(': -1, ')': -1, '||': 0, '&&': 1, '|': 2, '^': 3, '&': 4, '==': 5, '!=': 5, '<': 6, '>': 6,
        #                '<=': 6, '>=': 6, '+': 7, '-': 7, '*': 8, '/': 8, '%': 8, '!': 9}
        for meta in infix:
            if meta[2] == 900 or meta[1].isdigit():  # 数字或变量
                postfix.append(meta)
            elif meta[1] == '(':
                op_stack.append(meta)
            elif meta[1] == ')':
                while op_stack[-1][1] != '(':
                    postfix.append(op_stack.pop())
                op_stack.pop()
            else:  # 操作符 判断优先级
                while len(op_stack) > 0 and op_priority[op_stack[-1][1]] >= op_priority[meta[1]]:
                    postfix.append(op_stack.pop())
                op_stack.append(meta)
        # 剩余符号直接入后缀栈
        while len(op_stack) > 0:
            postfix.append(op_stack.pop())
        return self.gen_quaternary_assign(postfix)

    # 赋值表达式后缀式生成四元式，相当于表达式计算的过程
    def gen_quaternary_assign(self, post_exp):
        num_stack = []
        res = ""
        if len(post_exp) == 1:
            return post_exp[0][1]
        for meta in post_exp:
            if meta[2] == 900 or meta[1].isdigit():
                num_stack.append(meta[1])
            else:
                right = num_stack.pop()
                left = num_stack.pop()
                self.four.append((meta[1], left, right, self.var + str(self.n)))
                num_stack.append(self.var + str(self.n))
                res = self.var + str(self.n)
                self.n += 1
        return res

    def run(self):
        self.judge_execute()


if __name__ == '__main__':
    file_path = "test/testfan.txt"
    middle = MiddleCodePlus(file_path)
    middle.judge_execute()
    middle.print_four()