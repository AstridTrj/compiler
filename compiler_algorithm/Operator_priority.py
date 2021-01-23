

def read_grammar(filedir):
    """
    根据路径读文法
    要求：1、文法中不得出现空
         2、
    """
    grammar_dict = {}
    all_word_set = set()
    f = open(filedir, 'r', encoding='utf-8-sig')  # utf-8-sig 可以解决第一行第一个字符是无关字符的问题
    for line in f.readlines():
        left = line.split('->')[0].strip()  # 左部
        all_right = line.split('->')[1].strip()  # 一个左部的右部
        # all_right_ls = all_right.split('或')  # 一个左部的右部列表分为每一个推导式
        all_right_ls = all_right.split('|')  # 一个左部的右部列表分为每一个推导式
        right_ls = []  # 一个左部对应的多个右部的二维列表 # 第一层：该左部推导出的右部列表  第二层：一个句子划分的终结符、非终结符
        for each_right in all_right_ls:
            each_right_ls = each_right.strip().split(' ')  # 对每个推导式划分 终结符、非终结符
            right_ls.append(each_right_ls)
            all_word_set.update(each_right_ls)  # 全部单词集合
        grammar_dict[left] = right_ls
    f.close()
    if len(grammar_dict) == 0:
        raise Exception('文法为空，请重新输入文法！')
    return grammar_dict, all_word_set, all_word_set - set(grammar_dict.keys())


def cal_first_vt(grammar_dict, terminal_word_set):
    # 建立first_vt二维字典
    first_vt_dict = {}
    # 1.对每个非终结符P和终结符a 设置 first_vt_dict[P][a] = 0
    for nt in grammar_dict:  # 非终结符
        temp_dict = {}  # 内层字典
        for t in terminal_word_set:  # 终结符
            temp_dict[t] = 0
        first_vt_dict[nt] = temp_dict
    # 2.对每个形如P->a 或 P->Qa... 的产生式 应用规则1
    for nt in grammar_dict:
        for each_right_ls in grammar_dict[nt]:
            t = ''  # 第一或第二个的终结符
            if each_right_ls[0] in terminal_word_set:
                t = each_right_ls[0]
            elif len(each_right_ls) > 1 and each_right_ls[1] in terminal_word_set:
                t = each_right_ls[1]
            if t != '':
                first_vt_dict[nt][t] = 1
    # 3.当堆栈非空 应用规则2
    isChange = True
    while isChange:
        isChange = False
        for nt in grammar_dict:
            for each_right_ls in grammar_dict[nt]:
                if each_right_ls[0] in grammar_dict:  # 第一个是非终结符
                    for t in first_vt_dict[each_right_ls[0]]:
                        if first_vt_dict[each_right_ls[0]][t] == 1 and first_vt_dict[nt][t] == 0:
                            first_vt_dict[nt][t] = 1
                            isChange = True

    print('First_Vt:')
    for first_vt in first_vt_dict:
        print(first_vt, end='')
        print(first_vt_dict[first_vt])
    return first_vt_dict


def cal_last_vt(grammar_dict, terminal_word_set):
    # 建立last_vt_dict二维字典
    last_vt_dict = {}
    # 1.对每个非终结符P和终结符a 设置 last_vt_dict[P][a] = 0
    for nt in grammar_dict:  # 非终结符
        temp_dict = {}  # 内层字典
        for t in terminal_word_set:  # 终结符
            temp_dict[t] = 0
        last_vt_dict[nt] = temp_dict
    # 2.对每个形如P->..a 或 P->..aQ 的产生式 应用规则1
    for nt in grammar_dict:
        for each_right_ls in grammar_dict[nt]:
            t = ''  # 倒数第一或第二个的终结符
            if each_right_ls[-1] in terminal_word_set:
                t = each_right_ls[-1]
            elif len(each_right_ls) > 1 and each_right_ls[-2] in terminal_word_set:
                t = each_right_ls[-2]
            if t != '':
                last_vt_dict[nt][t] = 1
    # 3.当堆栈非空 应用规则2
    isChange = True
    while isChange:
        isChange = False
        for nt in grammar_dict:
            for each_right_ls in grammar_dict[nt]:
                if each_right_ls[-1] in grammar_dict:  # 最后一个是非终结符
                    for t in last_vt_dict[each_right_ls[-1]]:
                        if last_vt_dict[each_right_ls[-1]][t] == 1 and last_vt_dict[nt][t] == 0:
                            last_vt_dict[nt][t] = 1
                            isChange = True
    print('last_vt_dict:')
    for last_vt in last_vt_dict:
        print(last_vt, end='')
        print(last_vt_dict[last_vt])
    return last_vt_dict

def alter_table(priority_dict, a, b, op):
    if priority_dict[a][b] == '':
        priority_dict[a][b] = op
    elif priority_dict[a][b] != op:
        raise Exception("请确保该文法是算符优先文法：算符优先关系表(%s,%s)处原来是%s，现在是%s" % (a, b, priority_dict[a][b], op))
    # priority_dict[a][b] = op0

def get_priority_table(grammar_dict, terminal_word_set, first_vt_dict, last_vt_dict):
    priority_table_dict = {}
    # 初始化 priority_dict
    for t1 in terminal_word_set:
        temp_dict = {}
        for t2 in terminal_word_set:
            temp_dict[t2] = ''
        priority_table_dict[t1] = temp_dict
    # 逐个检查
    for nt in grammar_dict:
        for each_right_ls in grammar_dict[nt]:
            for i in range(len(each_right_ls)-1):  # 0~n-2
                # 1. P->..ab..
                if each_right_ls[i] in terminal_word_set and each_right_ls[i+1] in terminal_word_set:
                    alter_table(priority_table_dict, each_right_ls[i], each_right_ls[i+1], '=')
                # 2. P->..aQb..
                if i<=len(each_right_ls)-3  and each_right_ls[i] in terminal_word_set and each_right_ls[i+2] in \
                        terminal_word_set and each_right_ls[i+1] in grammar_dict:
                    alter_table(priority_table_dict, each_right_ls[i], each_right_ls[i+2], '=')
                # 3. P->..aR..
                if each_right_ls[i] in terminal_word_set and each_right_ls[i+1] in grammar_dict:
                    for a in first_vt_dict[each_right_ls[i+1]]:
                        if first_vt_dict[each_right_ls[i+1]][a] == 1:  # 遍历FirstVt集合

                            alter_table(priority_table_dict, each_right_ls[i], a, '<')
                # 4. P->..Rb..
                if each_right_ls[i] in grammar_dict and each_right_ls[i+1] in terminal_word_set:
                    for a in last_vt_dict[each_right_ls[i]]:
                        if last_vt_dict[each_right_ls[i]][a] == 1:
                            alter_table(priority_table_dict, a, each_right_ls[i+1], '>')
                # 5. P-> ..RR..
                if each_right_ls[i] in grammar_dict and each_right_ls[i+1] in grammar_dict:
                    raise Exception('该文法不是算符优先文法，存在非终结符相连！')
    print('算符优先关系表：')
    for temp in priority_table_dict:
        print(temp, end='')
        print(priority_table_dict[temp])
    return priority_table_dict


def reduced(grammar_dict, terminal_word_set, leftest_prime_phrase):
    """
    根据最左素短语 返回归约成的非终结符
    """
    # shortest_prime_phrase 最短素短语
    print('对%s进行归约中' % (''.join(leftest_prime_phrase)))
    for nt in grammar_dict:
        for each_right_ls in grammar_dict[nt]:
            if len(leftest_prime_phrase) == len(each_right_ls):
                for i in range(len(leftest_prime_phrase)):
                    if leftest_prime_phrase[i] in terminal_word_set and leftest_prime_phrase[i] != each_right_ls[i]:
                        break

                    if i == len(leftest_prime_phrase)-1:
                        # print(''.join(leftest_prime_phrase) + '进行归约：')
                        # print(nt + ' -> '+ ''.join(each_right_ls))
                        return nt, each_right_ls
    raise Exception('没有成功归约，请确保你的输入符合文法。')


def analyse(grammar_dict, terminal_word_set, priority_table_dict, sentence):
    if len(sentence) == 0:
        raise Exception('sentence为空，请输入要规约的字符串！')
    # 可视化的需要的列表
    watch_stack = ['#']
    watch_sentence = [sentence]
    leftest_prime_phrase = ['']
    notes = ['初始状态']
    # 1.初始化
    stack = ["#"]
    top = 0
    sentence_i = 0
    # 2.
    while not (len(stack) == 2 and stack[1] in grammar_dict and sentence[sentence_i] == '#'):
        # print("stack : %s" % ('|'.join(stack)))
        if stack[top] in terminal_word_set:
            j = top
        else:
            j = top-1
        # print('j : %d , sentence_i : %d' % (j, sentence_i))
        if priority_table_dict[stack[j]][sentence[sentence_i]] in ['<', '=']:
            stack.append(sentence[sentence_i])
            top += 1
            sentence_i += 1
            # 修改用于可视化的列表
            leftest_prime_phrase.append('')
            notes.append('%s移进' % stack[-1])
        elif priority_table_dict[stack[j]][sentence[sentence_i]] == '>':
            q = stack[j]
            if stack[j-1] in terminal_word_set:
                j -= 1
            else:
                j -= 2
            while priority_table_dict[stack[j]][q] != '<':
                q = stack[j]
                if stack[j - 1] in terminal_word_set:
                    j -= 1
                else:
                    j -= 2
            # 把stack[j+1] stack[top]归约
            shortest_prime_phrase = stack[j+1:top+1]
            stack = stack[:j+1]
            nt, right_ls = reduced(grammar_dict, terminal_word_set, shortest_prime_phrase)
            stack.append(nt)
            top = j+1
            # 修改可视化的列表
            leftest_prime_phrase.append(''.join(shortest_prime_phrase))
            notes.append('用%s归约' % (nt + '->' + ''.join(right_ls)))

        watch_stack.append(''.join(stack))
        watch_sentence.append(''.join(sentence[sentence_i:]))

    for i in range(len(watch_stack)):
        print('%-15s %-15s %-10s %-20s' % (watch_stack[i], watch_sentence[i], leftest_prime_phrase[i], notes[i]))
    return watch_stack, watch_sentence, leftest_prime_phrase, notes   # 对应输出就好


def start(filedir: str, sentence: str):
    """
    :param filedir:文法的路径
    :param sentence: 要规约的字符串
    :return:
    """
    grammar_dict, all_word_set, terminal_word_set = read_grammar(filedir)
    print('读取文法完毕')
    # print(grammar_dict)
    # print(all_word_set)
    # print(terminal_word_set)
    first_vt_dict = cal_first_vt(grammar_dict, terminal_word_set)
    last_vt_dict = cal_last_vt(grammar_dict, terminal_word_set)
    priority_table_dict = get_priority_table(grammar_dict, terminal_word_set, first_vt_dict, last_vt_dict)

    # sentence = '(i+i)*(i+i)*i'
    watch_stack, watch_sentence, leftest_prime_phrase, notes = analyse(grammar_dict, terminal_word_set, priority_table_dict, sentence + '#')
    return [first_vt_dict, last_vt_dict, priority_table_dict], [watch_stack, watch_sentence, leftest_prime_phrase, notes]


if __name__ == '__main__':
    start('算符优先文法.txt', '(i+i)*(i+i)*i')
