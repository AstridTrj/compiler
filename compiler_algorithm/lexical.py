"""
关键字：
    char double enum float int long short signed struct union unsigned void
    for do while continue break
    if else goto
    switch case default
    return
    auto extern register static
    const sizeof typdef volatile

标识符：
    由字母或下划线开头 后面有若干字母、数字或下划线组成

运算符：
    +  -  *  /  %  ++  --
    ==  !=  >  <  >=  <=
    &  |  ^  &&  ||  !  ~ 按位非  <<  >>
    =  +=  -=  /=  %=  <<=  >>=  &=  ^=  |=
    sizeof   ?:   ,   .(成员访问 )  ->(成员访问 )  (cast)强制转换   &引用   *指针
    (   )   [   ]

常数：
    整数  字符  字符串  标识符  实数

界符
    ,  '  "  {  }  ;  /*  */  // \  :  ?
"""
from compiler_principle.compile_base import CompilerBase


class Lexical(CompilerBase):
    def __init__(self, filename='', text=''):
        super(Lexical, self).__init__(filename, text)
        self.__current_line = 1
        self.__current_row = 0

    # 标识符/关键字
    def __start_with_alpha(self):
        index = self.__current_row
        while self.__current_row < self.file_con_len:
            ch = self.file_con[self.__current_row]
            if not (ch.isalpha() or ch.isalnum() or ch == '_'):
                break
            self.__current_row += 1
        word = self.file_con[index: self.__current_row]
        try:
            code = self.code[word]
        except KeyError:
            code = self.code['IDENTIFIER']
            self.sign_table.append((word, 'IDENTIFIER'))
        self.token.append((self.__current_line, word, code))

        self.__current_row -= 1

    # 数
    def __start_with_number(self):
        index = self.__current_row

        # 获取下一字符
        def get_next_char():
            if (self.__current_row + 1) < self.file_con_len:
                self.__current_row += 1
                return self.file_con[self.__current_row]
            return ""

        def isnum(_state):
            if _state == 1:
                while _state == 1:
                    c = get_next_char()
                    if c:
                        if c.isdigit():
                            continue
                        elif c == '.':
                            _state = 2
                        elif c == 'e' or c == 'E':
                            _state = 4
                        # 整数
                        else:
                            _state = 15
                    # 若c为None,表示文本已经编译完
                    else:
                        self.__current_row += 1
                        _state = 15
            if _state == 2:
                c = get_next_char()
                if c.isdigit():
                    _state = 3
                # 多余的小数点
                else:
                    _state = 11
            if _state == 3:
                while _state == 3:
                    c = get_next_char()
                    if c.isdigit():
                        continue
                    elif c == 'e' or c == 'E':
                        _state = 4
                    # 小数
                    else:
                        _state = 7
            if _state == 4:
                c = get_next_char()
                if c == '+' or c == '-':
                    _state = 5
                elif c.isdigit():
                    _state = 6
                # 多的e或者E
                else:
                    _state = 12
            if _state == 5:
                c = get_next_char()
                if c.isdigit():
                    _state = 6
                # 多的正负号
                else:
                    _state = 13
            if _state == 6:
                while _state == 6:
                    c = get_next_char()
                    # （实）指数
                    if not c.isdigit():
                        _state = 7
            if _state == 8:
                while _state == 8:
                    c = get_next_char()
                    # 八进制数
                    if not c.isdigit():
                        _state = 15
            if _state == 9:
                c = get_next_char()
                if c.isdigit() or ('A' <= c <= 'F') or ('a' <= c <= 'f'):
                    _state = 10
                # 字母x或X是多的，不代表是16进制
                else:
                    _state = 14
            if _state == 10:
                while _state == 10:
                    c = get_next_char()
                    if not (c.isdigit() or ('A' <= c <= 'F') or ('a' <= c <= 'f')):
                        _state = 15
            # 错误判断
            if _state == 7 or _state == 15:
                return _state
            elif _state == 11: # 多余的小数点
                self.error.append((1, self.__current_line, '.'))
                self.__current_row -= 1
            elif _state == 12:
                self.error.append((1, self.__current_line, 'e/E'))
                self.__current_row -= 1
            elif _state == 13:
                self.error.append((1, self.__current_line, '+/-'))
                self.__current_row -= 1
            elif _state == 14:
                self.error.append((1, self.__current_line, 'x/X'))
                self.__current_row -= 1
            return _state

        if self.file_con[self.__current_row] == '0':
            ch = get_next_char()
            # 16进制
            if ch == 'x' or ch == 'X':
                state = 9
            # 7进制
            elif '0' <= ch <= '7':
                state = 8
            elif ch == '.':
                state = 2
            # 其它即输入的是0（不允许输入带前导0的十进制数，因此此处无十进制的判断）
            else:
                state = 7
        else:
            state = 1
        state = isnum(state)
        word = self.file_con[index: self.__current_row]
        if state == 15:
            self.token.append((self.__current_line, word, self.code['INT_NUM']))
            self.sign_table.append((word, 'INT_NUM'))
        else:
            self.token.append((self.__current_line, word, self.code['REAL_NUM']))
            self.sign_table.append((word, 'REAL_NUM'))
        self.__current_row -= 1

    # 除法，除法赋值或者注释
    def __start_with_anno_multi(self):
        self.__current_row += 1
        ch = self.file_con[self.__current_row]
        if ch == '*':
            self.__current_row += 1
            while self.__current_row < self.file_con_len - 1:
                if self.file_con[self.__current_row] == '\n':
                    self.__current_line += 1
                # 超前搜索
                if not (self.file_con[self.__current_row] == '*' and self.file_con[self.__current_row+1] == '/'):
                    self.__current_row += 1
                else:
                    self.__current_row += 1
                    break
        elif ch == '/':  # //为单行注释
            while self.__current_row < self.file_con_len - 1:
                if self.file_con[self.__current_row+1] is not '\n':
                    self.__current_row += 1
                else:
                    break
        elif ch == '=':  # /=
            word = self.file_con[self.__current_row-1: self.__current_row+1]
            self.token.append((self.__current_line, word, self.code['/=']))
        else:  # /除
            self.__current_row -= 1
            word = self.file_con[self.__current_row]
            self.token.append((self.__current_line, word, self.code['/']))

    # 字符
    def __start_with_char(self):
        if (self.__current_row+1) < self.file_con_len:
            # 超前搜索
            word = self.file_con[self.__current_row+1]
            if word is not '\n' and self.__current_row < self.file_con_len - 2:
                if self.file_con[self.__current_row+2] == '\'':
                    self.token.append((self.__current_line, word, self.code['CHAR_NUM']))
                    self.sign_table.append((word, 'CHAR_NUM'))
                    self.__current_row += 2
                else:
                    # 缺少后一个‘
                    self.error.append((0, self.__current_line, '\''))
            else:  # 第一个’多余
                self.error.append((1, self.__current_line, '\''))
        else:  # 在最后多出一个‘
            self.error.append((1, self.__current_line, '\''))

    # 字符串
    def __start_with_string(self):
        self.__current_row += 1
        index = self.__current_row
        flag = 0
        while self.__current_row < self.file_con_len:
            if self.file_con[self.__current_row] == '\"':
                word = self.file_con[index: self.__current_row]
                self.token.append((self.__current_line, word, self.code['STRING_LITERAL']))
                self.sign_table.append((word, 'STRING_LITERAL'))
                break
            elif self.file_con[self.__current_row] == '\n':
                flag = 1
                break
            else:
                self.__current_row += 1
        if flag == 1:
            # 多余的第一个双引号
            self.error.append((1, self.__current_line, '\"'))
            # 退回初始位置
            self.__current_row = index

    # 运算符
    def __start_with_operator(self):
        ch = self.file_con[self.__current_row]
        index = self.__current_row

        def next_is_param(c):
            if self.__current_row + 1 < self.file_con_len:
                if self.file_con[self.__current_row+1] == c:
                    self.__current_row += 1
                    return True
            return False
        flag = 0
        if ch == '%':
            next_is_param('=')
        elif ch == '=':
            next_is_param('=')
        elif ch == '!':
            next_is_param('=')
        elif ch == '^':
            next_is_param('=')
        elif ch == '~' or ch == '.':
            pass
        elif ch == '+':
            if next_is_param('=') or next_is_param(ch):
                pass
        elif ch == '-':
            if next_is_param('=') or next_is_param(ch) or next_is_param('>'):
                pass
        elif ch == '*':
            next_is_param('=')
        elif ch == '&':
            if next_is_param('=') or next_is_param('&'):
                pass
        elif ch == '|':
            if next_is_param('=') or next_is_param('|'):
                pass
        elif ch == '>':
            if next_is_param('='):
                pass
            elif next_is_param('>'):
                next_is_param('=')
        elif ch == '<':
            if next_is_param('='):
                pass
            elif next_is_param('<'):
                next_is_param('=')
        else:
            return
        word = self.file_con[index: self.__current_row+1]
        self.token.append((self.__current_line, word, self.code[word]))

    # 界符
    def __start_with_delimiter(self):
        word = self.file_con[self.__current_row]
        self.token.append((self.__current_line, word, self.code[word]))

    # 扫描器
    def __scanner(self):
        self.__current_row = 0
        while self.__current_row < len(self.file_con):
            ch = self.file_con[self.__current_row]
            if not (ch == ' ' or ch == '\t'):
                if ch == '\n' or ch == '\r\n':  # 换行
                    self.__current_line += 1
                elif ch.isalpha() or ch == '_':  # 关键字 or 标识符
                    self.__start_with_alpha()
                elif ch.isdigit():  # 数字
                    self.__start_with_number()
                elif ch == '/':  # 除法，除法赋值或者注释
                    self.__start_with_anno_multi()
                elif ch == '#':
                    pass
                elif ch == '\'':  # 单引号，字符常量
                    self.__start_with_char()
                elif ch == '\"':  # 双引号，字符串
                    self.__start_with_string()
                elif ch in self.basic_operator:  # 含有运算符
                    self.__start_with_operator()
                elif ch in self.delimiter:  # 界符
                    self.__start_with_delimiter()
                else:
                    # 无法识别的字符
                    self.error.append((2, self.__current_line, ch))
            self.__current_row += 1

    def run(self):
        self.__scanner()
        self._exit_message()
        self.quit()


if __name__ == '__main__':
    lexer = Lexical(filename='E:\\homework\\compiler\\Compiler-Editer-C-master\\ui_pyqt5\\edit\\textedit.py')
    lexer.run()
    for i in lexer.token:
        print(i)
    print(lexer.error)