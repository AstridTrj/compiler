from PyQt5.QtCore import QThread, pyqtSignal


class Token(list):
    """
    (line_num, word, code)
    """
    def __init__(self, seq=()):
        super(Token, self).__init__(seq)
        pass


class Error(list):
    def __init__(self, seq=()):
        super(Error, self).__init__(seq)


class SignTable(list):
    """
    1.符号名
    2.符号的类型
    3.符号的作用域
    4.符号的存储类别
    5.符号变量其他信息
    (word, type_p, scope, type, others)
    """
    def __init__(self, seq=()):
        super(SignTable, self).__init__(seq)

    def append(self, object_p):
        item = list(object_p)

        t = 5 - len(item)
        for i in range(0, t):
            item += ['']
        try:
            self.remove(item)
        except ValueError:
            pass
        super(SignTable, self).append(item)


class CompilerBase(QThread):
    code = {
        'char': 101,
        'double': 102,
        'enum': 103,
        'float':104,
        'int': 105,
        'long': 106,
        'short': 107,
        'signed': 108,
        'struct': 109,
        'union': 110,
        'unsigned': 111,
        'void': 112,
        'for': 113,
        'do': 114,
        'while': 115,
        'break': 116,
        'continue': 117,
        'if': 118,
        'else': 119,
        'goto': 120,
        'switch': 121,
        'case': 122,
        'default': 123,
        'return': 124,
        'auto': 125,
        'extern': 126,
        'register': 127,
        'static': 128,
        'const': 129,
        'sizeof': 130,
        'typedef': 131,
        'volatile': 132,
        '+': 201,
        '-': 202,
        '*': 203,
        '/': 204,
        '%': 205,
        '++': 206,
        '--': 207,
        '==': 208,
        '!=': 209,
        '>': 210,
        '<': 211,
        '>=': 212,
        '<=': 213,
        '&': 214,
        '|': 215,
        '^': 216,
        '&&': 217,
        '||': 218,
        '!': 219,
        '~': 220,
        '<<': 221,
        '>>': 222,
        '=': 223,
        '+=': 224,
        '-=': 225,
        '*=': 226,
        '/=': 227,
        '%=': 228,
        '<<=': 229,
        '>>=': 230,
        '&=': 231,
        '^=': 232,
        '|=': 233,
        '->': 234,
        '.': 235,
        '(': 236,
        ')': 237,
        '[': 238,
        ']': 239,
        ',': 301,
        '{': 302,
        '}': 303,
        '//': 304,
        '/*': 305,
        '*/': 306,
        ';': 307,
        ':': 308,
        '?': 309,
        '\\': 310,
        'CONSTANT': 400,
        'INT_NUM': 500,
        'CHAR_NUM': 600,
        'REAL_NUM': 700,
        'STRING_LITERAL': 800,
        'TYPE_NAME': 900,
        'IDENTIFIER': 900
    }
    basic_operator = {
        '+', '-', '*', '=', '|', '&', '~', '^', '!', '>', '<', '%'
    }
    delimiter = {
        ';', ',', '{', '}', '(', ')', '[', ']', '.', ':', '\\', '?'
    }
    error_type = ['miss', 'more', 'no_code', 'no_type', 'unknown', 'success', 'fail', 'se']
    error_info = {
        error_type[0]: "词法错误 %d: 第 %d 行缺少 %s ;",
        error_type[1]: "词法错误 %d: 第 %d 行多余 %s ;",
        error_type[2]: "词法错误 %d: 第 %d 行不能识别的字符 %s ;",
        error_type[3]: "词法错误 %d: 第 %d 行没有 %s 的类型;",
        error_type[4]: "%s error: 第 %d 行%s附近错误",
        error_type[5]: "%s %d errors %s",
        error_type[6]: "%s %d %s",
        error_type[7]: "line %d 语义错误: %s %s"
    }

    # 自定义信号发射器，定义之后便可通过连接到槽，再启动信号发射器
    sinOut = pyqtSignal(Token, Error, SignTable)

    # 信息初始化，包括文件信息，token串，错误信息，符号表
    def __init__(self, filename='', text=''):
        super(CompilerBase, self).__init__()
        if filename:
            self.file_name = filename
            self.__load_file()
        elif text:
            self.file_con = text.strip()
        else:
            raise Exception("No file or text to compiler.")
        self.file_con_len = len(self.file_con)
        self.token = Token()
        self.error = Error()
        # 符号表，后续使用
        self.sign_table = SignTable()

    def __load_file(self):
        with open(self.file_name, "r", encoding='utf-8') as f:
            self.file_con = f.read()

    def run(self):
        pass

    def _exit_message(self):
        try:
            # 发射信号，
            self.sinOut.emit(self.token, self.error, self.sign_table)
        except Exception as e:
            raise e
