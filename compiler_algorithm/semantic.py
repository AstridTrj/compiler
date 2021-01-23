import pandas as pd
from compiler_principle import lexical

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 500)


class Semantic(object):

    def __init__(self, test_file):
        lex = lexical.Lexical(test_file)
        lex.run()
        self.tokens =lex.token
        self.length = len(self.tokens)
        # self.string = ''
        self.label = 1
        self.constant_table = pd.DataFrame(index=['name', 'type', 'value'])
        self.variable_table = pd.DataFrame(index=['name', 'scope', 'type', 'value', 'address'])
        self.function_table = pd.DataFrame(index=['name', 'return_type', 'param_num', 'param'])
        self.error = []  # (line, name, error_message)
        # self.string_table = pd.DataFrame(index=['name', 'start', 'length'])

    # 符号表插入
    def insert_table(self, table_type, value):
        if table_type == 'constant':
            self.constant_table[value[0]] = value
        # 变量表以名字和作用域作为key
        if table_type == 'variable':
            self.variable_table[value[1]+'/'+value[0]] = value
        if table_type == 'function':
            self.function_table[value[0]] = value

    # 同名判断
    def is_same(self, v):
        if v[0] in self.constant_table.columns:
            if v[1] == 'const':
                return False
            elif v[1] == '/0':
                return False
            elif v[1] == 'func':
                return False
        if v[0] in self.function_table.columns:
            return False
        if (v[1] + '/' + v[0]) in self.variable_table.columns:
            return False
        return True

    # 检查变量是否声明及使用是否合法（当前作用域可使用外层作用域变量）
    def if_exist(self, n_type, n_value):
        if n_type == 'const':
            if n_value[0] in self.constant_table.columns:
                return True
        elif n_type == 'func':
            if n_value[0] in self.function_table.columns:
                return True
        elif n_type == 'var':
            for scope in self.variable_table.columns:
                scope_list = scope.split('/')
                n_list = n_value[1].split('/')
                if n_value[0] == scope_list[-1]:
                    flag = True
                    for i in range(1, len(scope_list)-1):
                        if scope_list[i] != n_list[i]:
                            flag = False
                            break
                    if flag:
                        return False
            return True
        return False

    def scope_find(self, value, scope):
        scope = scope.split('/')
        while len(scope) > 1:
            if ('/'.join(scope)+'/'+value) in self.variable_table.columns:
                return self.variable_table['/'.join(scope)+'/'+value]['type']
            scope.pop()
        return ''

    # 常量表添加及对应部分语义错误
    def constant_check(self):
        index = 0
        while index < self.length:
            if self.tokens[index][1] == 'const':
                _type = self.tokens[index+1][1]
                index = index + 2
                while index < self.length and self.tokens[index][1] != ';':
                    name = self.tokens[index][1]
                    value = self.tokens[index+2][1]
                    if self.is_same([name, 'const', value]):
                        self.insert_table('constant', [name, _type, value])
                    else:
                        # 同名错误处理
                        self.error.append((self.tokens[index][0], name, '常量已存在'))
                        print('error')
                    index = index + 3
                    if self.tokens[index][1] == ',':
                        index = index + 1
            index = index + 1
        # print(self.constant_table)

    # 函数，变量处理及对应部分语义错误处理
    def create_sign_table(self):
        scope_stack = ['/0']
        index = 0
        type_list = ['int', 'float', 'double', 'char', 'void']
        while index < self.length:
            # 去除常量语句
            if self.tokens[index][1] == 'const':
                while self.tokens[index][1] != ';':
                    index = index + 1
            # 作用域处理
            if self.tokens[index][1] == '{':
                scope_stack.append(str(self.label))
                self.label += 1
            elif self.tokens[index][1] == '}':
                scope_stack.pop()
            # 遇到声明或定义语句
            elif self.tokens[index][1] in type_list:
                _type = self.tokens[index][1]
                # 函数定义
                if self.tokens[index+2][1] == '(':
                    line, name = self.tokens[index+1][0], self.tokens[index+1][1]
                    index = index + 3
                    p_num = 0
                    param_list = None
                    # 统计函数形参
                    while self.tokens[index][1] != ')':
                        if self.tokens[index][1] == ',':
                            index = index + 1
                        p_type = self.tokens[index][1]
                        p_name = self.tokens[index+1][1]
                        p_scope = '/'.join(scope_stack) + '/' + str(self.label)
                        if self.is_same([p_name, p_scope, p_type, None, None]):
                            self.insert_table('variable', [p_name, p_scope, p_type, None, None])
                            p_num += 1
                            if param_list:
                                param_list += ',' + p_type
                            else:
                                param_list = p_type
                        else:
                            self.error.append((self.tokens[index+1][0], p_name, '参数变量已存在'))
                            print('error')
                        index = index + 2
                    # 将函数的声明加入函数表
                    if self.is_same([name, 'func']):
                        self.insert_table('function', [name, _type, p_num, param_list])
                    else:
                        self.error.append((line, name, '函数名已存在'))
                        print('error')
                # 变量定义或声明
                else:
                    index = index + 1
                    flag = False
                    # 保证一个定义或声明语句正常搜索完
                    while self.tokens[index][1] != ';' and self.tokens[index-1][1] != ';':
                        line, name = self.tokens[index][0], self.tokens[index][1]
                        # 判断当前标识符后面的符号，以做对应的动作
                        if self.tokens[index+1][1] == ',':
                            # 无初始化值的变量
                            if self.is_same([name, '/'.join(scope_stack)]):
                                self.insert_table('variable', [name, '/'.join(scope_stack), _type, None, None])
                            else:
                                self.error.append((line, name, '变量已存在'))
                                print('error')
                            index = index + 2
                        elif self.tokens[index+1][1] == '=':
                            # 有初始化的变量
                            value = self.tokens[index+2][1]
                            if self.is_same([name, '/'.join(scope_stack)]):
                                self.insert_table('variable', [name, '/'.join(scope_stack), _type, value, None])
                            else:
                                self.error.append((line, name, '变量已存在'))
                                print('error')
                            index = index + 4
                            flag = True
                        # 当前语句结束
                        elif self.tokens[index+1][1] == ';':
                            if self.is_same([name, '/'.join(scope_stack)]):
                                self.insert_table('variable', [name, '/'.join(scope_stack), _type, None, None])
                            else:
                                self.error.append((line, name, '变量已存在'))
                                print('error')
                            index = index + 1
                            break
                    # 标识符后面是等号比较特殊，需将token指针前移
                    if flag:
                        index = index - 1
            index = index + 1
        # print(self.variable_table)
        # print(self.function_table)
        # print(self.error)

    # 变量未声明，赋值错误及break,continue,return的使用的错误处理
    def id_use_error(self):
        scope_stack = ['/0']
        loop_stack = []
        index = 0
        level = 1
        type_list = ['int', 'float', 'double', 'char', 'void']
        while index < self.length:
            if self.tokens[index][1] == 'const':
                while self.tokens[index][1] != ';':
                    index = index + 1
            if self.tokens[index][1] == '{':
                scope_stack.append(str(level))
                level += 1
            elif self.tokens[index][1] == '}':
                scope_stack.pop()
                if len(loop_stack) > 0:
                    loop_stack.pop()
            # 遇到选择或者循环标志则入栈，用于检测break,continue
            elif self.tokens[index][1] in ['for', 'while', 'switch', 'if', 'else']:
                loop_stack.append(self.tokens[index][1])
            # 函数名入栈，用于检测return
            elif self.tokens[index][2] == 900 and self.tokens[index+1][1] == '('and (self.tokens[index-1][1] in type_list):
                loop_stack.append(self.tokens[index][1])
            # 表达式赋值错误处理
            elif self.tokens[index][1] == '=':
                # 赋值左部不为标识符
                if self.tokens[index-1][2] != 900:
                    self.error.append((self.tokens[index-1][0], self.tokens[index-1][1], '错误赋值'))
                # 赋值类型不匹配
                elif self.tokens[index+1][2] == 900:
                    left_name = self.tokens[index-1][1]
                    left_type = self.scope_find(left_name, '/'.join(scope_stack))
                    index = index + 1
                    while self.tokens[index][1] != ';' and self.tokens[index][1] != ',':
                        right_name = self.tokens[index][1]
                        right_type = self.scope_find(right_name, '/'.join(scope_stack))
                        # 赋值表达式左右类型不匹配
                        if left_type != right_type:
                            self.error.append((self.tokens[index][0], self.tokens[index][1], '赋值类型不匹配'))
                        if self.tokens[index+1][1] != ';' and self.tokens[index+1][1] != ',':
                            index = index + 2
                        else:
                            index = index + 1
            # 未定义变量判断，若是标识符且不是函数名
            elif self.tokens[index][2] == 900 and self.tokens[index+1][1] != '(' and (self.tokens[index-1][1] not in type_list):
                if self.if_exist('var', [self.tokens[index][1], '/'.join(scope_stack)]):
                    self.error.append((self.tokens[index][0], self.tokens[index][1], '变量未定义'))
            elif self.tokens[index][1] == 'break':
                if len(loop_stack) < 1 or ('for' not in loop_stack and 'while' not in loop_stack and 'switch' not in loop_stack):
                    self.error.append((self.tokens[index][0], self.tokens[index][1], '使用错误'))
            elif self.tokens[index][1] == 'continue':
                if len(loop_stack) < 1 or ('for' not in loop_stack and 'while' not in loop_stack):
                    self.error.append((self.tokens[index][0], self.tokens[index][1], '使用错误'))
            elif self.tokens[index][1] == 'return':
                fun_name = loop_stack[-1]
                index = index + 1
                while self.tokens[index][1] != ';':
                    if self.tokens[index][1].isdigit() and self.function_table[fun_name]['return_type'] != 'int':
                        self.error.append((self.tokens[index-1][0], self.tokens[index-1][1], '类型不匹配'))
                        break
                    if self.tokens[index][2] == 900:
                        re_name = self.tokens[index][1]
                        sco = '/'.join(scope_stack) + '/' + re_name
                        if self.variable_table[sco]['type'] != self.function_table[fun_name]['return_type']:
                            self.error.append((self.tokens[index-1][0], self.tokens[index-1][1], '类型不匹配'))
                            break
                    index = index + 1
            # 函数实参与形参以及函数是否定义检查
            elif self.tokens[index][2] == 900 and self.tokens[index+1][1] == '('and (self.tokens[index-1][1] not in type_list):
                p_name, line, p_num, p_type = self.tokens[index][1], self.tokens[index][0], 0, ''
                index = index + 2
                while self.tokens[index][1] != ')':
                    idt = self.tokens[index][1]
                    if p_type:
                        p_type += ',' + self.variable_table['/'.join(scope_stack)+'/'+idt]['type']
                    else:
                        p_type = self.variable_table['/'.join(scope_stack)+'/'+idt]['type']
                    p_num += 1
                    if self.tokens[index+1][1] == ',':
                        index += 2
                    else:
                        index += 1
                if self.if_exist('func', [p_name]):
                    if p_num == self.function_table[p_name]['param_num']:
                        if p_type != self.function_table[p_name]['param']:
                            self.error.append((line, p_name, '函数参数类型不匹配'))
                    else:
                        self.error.append((line, p_name, '函数参数不匹配'))
                else:
                    self.error.append((line, p_name, '函数未定义'))
            index += 1
        print(self.error)

    def run(self):
        self.constant_check()
        self.create_sign_table()
        self.id_use_error()

    def write_to_file(self):
        self.constant_table.to_csv('constant.csv')
        self.variable_table.to_csv('variable.csv')
        self.function_table.to_csv('function.csv')


if __name__ == '__main__':
    file = 'test\\testR.txt'
    # for i in lex.token:
    #     print(type(i[1]))
    ss = Semantic(file)
    ss.constant_check()
    ss.create_sign_table()
    ss.id_use_error()
    ss.write_to_file()