from graphviz import Digraph

class FourTermVector:
    def __init__(self, first, second, third, fourth):
        self.first = first
        self.second = second
        self.third = third
        self.fourth = fourth

    def __repr__(self):
        return '(%-3s,%-3s,%-3s,%-3s)' % (self.first, self.second, self.third, self.fourth)


class DAG_Node:
    def __init__(self, no, val, left=None, right=None):
        self.no = no  # 编号
        self.val = val  # 值
        self.variable_ls = []  # 定值变量表
        self.left = left  # 左下的DAG_Node类
        self.right = right  # 右下的DAG_Node类
        self.isActive = False

    def __repr__(self):
        left_no = None
        if self.left is not None:
            left_no = self.left.no
        right_no = None
        if self.right is not None:
            right_no = self.right.no

        return 'No:%-4s val:%-5s val_ls:%-30s left:%-4s right:%-4s isActive:%-6s' % \
               (self.no, str(self.val), self.variable_ls, left_no, right_no, self.isActive)


class DAG:
    def __init__(self):
        self.node_ls = []
        self.node_dict = {}

    def create_node(self, val, left=None, right=None):
        global n
        if is_number(val):
            val = float(val)
        node = DAG_Node(n, val, left, right)
        self.node_ls.append(node)
        self.node_dict[val] = node
        n += 1
        return node

    def del_node(self, node):
        global n
        self.node_ls.remove(node)
        self.node_dict.pop(node.val)
        n -= 1

    def find_node(self, name, left=None, right=None):
        """ 在dag中寻找存放name的节点 """
        if is_number(name):
            name = float(name)
        if left is None and right is None:
            if name in self.node_dict :
                return self.node_dict[name]
            else:
                return None
        else:
            for node in self.node_ls:
                if (node.val == name or name in node.variable_ls) and node.left == left and node.right == right:
                    return node
            return None

    def add_variable_to_node(self, node, variable):
        if variable not in node.variable_ls:
            node.variable_ls.append(variable)
            self.node_dict[variable] = node

    def remove_variable_to_node(self, node, variable):
        if variable in node.variable_ls:
            node.variable_ls.remove(variable)
            self.node_dict.pop(variable)

    def out_put(self):
        for node in self.node_ls:
            print(node)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def read_four_term_vector(filedir):
    """ 读取文件中的四元式 """
    ftv_ls = []
    with open(filedir, 'r', encoding='utf-8') as f:
        all = f.readlines()
    for line in all:
        if line[0] in ['#', '\n']:
            continue
        a_ftv_ls = line.strip()[1:-1].split(',')
        a_ftv = FourTermVector(a_ftv_ls[0].strip(), a_ftv_ls[1].strip(), a_ftv_ls[2].strip(), a_ftv_ls[3].strip())
        ftv_ls.append(a_ftv)
    if len(ftv_ls) == 0:
        raise Exception('中间代码为空，请输出中间代码四元式！')
    return ftv_ls


dag = DAG()
n = 1  # 树中节点编号


def get_four_term_type(ftv):
    """ 获得四元式类型 (0/1/2型) """
    if '=' in ftv.first and ftv.third == '_':
        return 0
    elif ftv.first == '-' and ftv.third == '_':
        return 1
    elif ftv.first in ['+', '-', '*', '/', '%'] and ftv.second != '_' and ftv.third != '_':
        return 2
    else:
        raise Exception('四元式类型获取有误！')


def first_second_prepare_node(ftv):
    """ 步骤1、2 准备操作数节点和合并已知量 """
    global dag, n
    cur_n = n     # 记录当前的n 以来核对是否是新创建的结点

    first_node = dag.find_node(ftv.second)  # 该name的结点 或 None
    if first_node is None:
        first_node = dag.create_node(ftv.second)
    ftv_type = get_four_term_type(ftv)  # 获得四元式类型
    if ftv_type == 0:
        # 转步骤4
        forth_del_useless_assign(ftv, first_node)
        pass
    elif ftv_type == 1:
        # 判断结点是否标记为常数
        if is_number(first_node.val):
            # 执行 op B = P
            p = int(ftv.first+'1') * float(first_node.val)
            # 如果 first_node 是新构造的 则删除
            if first_node.no >= cur_n:
                dag.del_node(first_node)
            # 如果Node（P）无定义 则构造
            node_p = dag.find_node(p)
            if node_p is None:
                node_p = dag.create_node(p)
            # 转步骤4
            forth_del_useless_assign(ftv, node_p)
            pass
        else:
            # 转步骤3（1）
            third_delete_common_expression(ftv, first_node)
            pass
        pass
    elif ftv_type == 2:
        second_node = dag.find_node(ftv.third)
        if second_node is None:
            second_node = dag.create_node(ftv.third)
        # 判断Node(first_node)和Node(second_node) 是否都是标记为常数的结点
        if is_number(first_node.val) and is_number(second_node.val):
            # 执行 B op C = P
            p = eval(str(first_node.val) + ftv.first + str(second_node.val))
            # 如果node(first_node) 或 node(second_node)是创建当前四元式时新构造的结点 则删除
            if first_node.no >= cur_n:
                dag.del_node(first_node)
            if second_node.no >= cur_n:
                dag.del_node(second_node)
            # 如果Node（P） 无定义 则构造
            node_p = dag.find_node(p)
            if node_p is None:
                node_p = dag.create_node(p)
            # 转步骤4
            forth_del_useless_assign(ftv, node_p)
            pass
        else:
            # 转步骤3（2）
            third_delete_common_expression(ftv, first_node, second_node)


def third_delete_common_expression(ftv, first_node, second_node=None):
    global dag
    # 步骤(1)
    if second_node is None:
        # 检查DAG 是否已经有一结点 其唯一后继为first_node 且标记为op 如果没有则构造 否则  设该结点为temp
        temp = dag.find_node(ftv.first, first_node)
        if temp is not None:
            # 设该结点为temp 因为已经设了 所以此处pass
            pass
        else:
            # 构造该节点
            temp = dag.create_node(ftv.first, first_node)
        # 转步骤4
        forth_del_useless_assign(ftv, temp)
    # 步骤（2）
    else:
        # 检查DAG 是否已经有一结点 其左后为first_node 右后为second_node 且标记为op 如果没有则构造 否则  设该结点为temp
        temp = dag.find_node(ftv.first, first_node, second_node)
        if temp is not None:
            # 设该结点为temp 因为已经设了 所以此处pass
            pass
        else:
            # 构造该节点
            temp = dag.create_node(ftv.first, first_node, second_node)
        # 转步骤4
        forth_del_useless_assign(ftv, temp)


def forth_del_useless_assign(ftv, node):
    global dag
    node_a = dag.find_node(ftv.fourth)
    if node_a is None:
        # 如果node_a无定义 则直接把A附加在node上
        dag.add_variable_to_node(node, ftv.fourth)
    else:
        # 自己添加的：如果该节点附加标识符只有一个 那么就不删除他了
        if len(node_a.variable_ls) == 1:
            pass
        # 否则 先把A从Node_a结点的附加标识符中删除 若果node_a是叶结点 则其A标记不删除
        else:
            dag.remove_variable_to_node(node_a, ftv.fourth)
        # 把A附加到node上
        dag.add_variable_to_node(node, ftv.fourth)


def draw_pic(filename):
    global dag
    dot = Digraph(format='png')
    dot.attr(rankdir='TB')
    for node in dag.node_ls:
        dot.node(name=str(node.no), label='n'+str(node.no)+'\n'+str(node.val)+'\n'+str(node.variable_ls), shape='box', style='rounded')
        if node.left:
            dot.edge(str(node.no), str(node.left.no), arrowhead='vee', dir='none')
        if node.right:
            dot.edge(str(node.no), str(node.right.no), arrowhead='vee', dir='none')
    dot.render(filename='img/' + filename, view=False)
    return 'img/' + filename+'.png'


def dag_to_ftv():
    global dag
    new_ftv_ls = []
    for node in dag.node_ls:
        if node.variable_ls:
            for i in range(len(node.variable_ls)):
                if i == 0:
                    if node.left is None and node.right is None:  # 当前节点是叶结点 直接赋值
                        new_ftv_ls.append(FourTermVector('=', str(node.val), '_', node.variable_ls[i]))
                    else:  # 当前节点不是常数 则需要计算
                        left = '_'
                        right = '_'
                        if node.left is not None:
                            if node.left.left is None and node.left.right is None:
                                left = str(node.left.val)
                            else:
                                left = node.left.variable_ls[0]
                        if node.right is not None:
                            if node.right.left is None and node.right.right is None:
                                right = str(node.right.val)
                            else:
                                right = node.right.variable_ls[0]
                        new_ftv_ls.append(FourTermVector(node.val, left, right, node.variable_ls[i]))
                else:
                    if node.left is None and node.right is None:
                        new_ftv_ls.append(FourTermVector('=', str(node.val), '_', node.variable_ls[i]))
                    else:
                        new_ftv_ls.append(FourTermVector('=', node.variable_ls[0], '_', node.variable_ls[i]))
    print('优化后的四元式：')
    for f in new_ftv_ls:
        print(f)
    return new_ftv_ls


def delete_surplus_operation(active_variable_ls):
    """ 根据活跃变量删除dag中多余的操作 """
    for active_variable in active_variable_ls:
        node = dag.find_node(active_variable)
        if node:
            queen = [node]  # 广度优先遍历来记录需要的节点
            while queen:
                queen_head = queen.pop(0)
                # 去除无用的定值
                if queen_head.left is None and queen_head.right is None:  # 叶节点 无用的定值都可删去
                    for variable in queen_head.variable_ls:
                        if variable not in active_variable_ls:
                            queen_head.variable_ls.remove(variable)
                else:  # 不是叶结点 要保留有用节点的第一个定值
                    for variable in queen_head.variable_ls:
                        if variable not in active_variable_ls and variable != queen_head.variable_ls[0]:  # 排除第一个
                            queen_head.variable_ls.remove(variable)
                    if len(queen_head.variable_ls) == 2:
                        queen_head.variable_ls.pop(0)  # 去除掉第一个
                # 设置该节点活跃
                queen_head.isActive = True
                if queen_head.left:
                    queen.append(queen_head.left)
                if queen_head.right:
                    queen.append(queen_head.right)
    # 去除掉不活跃节点
    for node in reversed(dag.node_ls):
        if not node.isActive:
            dag.node_ls.remove(node)


def start_no_active(file_dir):
    # file_dir = '代码优化输入.txt'
    ftv_ls = read_four_term_vector(file_dir)
    # 生成dag
    for ftv in ftv_ls:
        first_second_prepare_node(ftv)
    # dag输出
    dag.out_put()
    # dag转四元式
    no_active_new_ftv_ls = dag_to_ftv()  # 没有删除活跃变量的新四元式
    # 画dag
    no_active_pic_dir = draw_pic('DAG-without-act-var')  # 没有删除活跃变量的DAG图路径（相对路径）
    return no_active_new_ftv_ls, no_active_pic_dir


def start_has_active(active_variable_ls):
    """
    :param active_variable_ls: 活跃变量列表（需要提前处理成列表）
    :return: 没删除活跃变量的四元式列表，没删除活跃变量的DAG图路径（相对路径），删除活跃变量的四元式列表，删除活跃变量的DAG图路径（相对）
    """
    if dag.node_ls == []:
        raise Exception('请先生成无指定活跃变量的DAG！')
    # 指定活跃变量
    # active_variable_ls = ['A']
    # 删除多余操作
    delete_surplus_operation(active_variable_ls)

    # dag输出
    dag.out_put()
    # dag转四元式
    active_new_ftv_ls = dag_to_ftv()  # 删除了活跃变量的新四元式
    # 画dag
    active_pic_dir = draw_pic('DAG-with-act-var')  # 删除了活跃变量的DAG图路径（相对路径）
    return active_new_ftv_ls, active_pic_dir


if __name__ == '__main__':
    file_dir = '代码优化输入.txt'
    active_variable_ls = ['A', 'B']
    start_no_active(file_dir)
    start_has_active(active_variable_ls)
