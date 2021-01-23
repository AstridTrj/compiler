import sys

from compiler_principle import Operator_priority
from PyQt5.QtCore import Qt, QFile
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QTextDocumentWriter
from PyQt5.QtWidgets import (QFrame, QWidget, QGridLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QApplication, QTextEdit, QTableWidget,
                             QAbstractItemView, QFileDialog, QTableWidgetItem, QHeaderView)


class OpPreUI(QFrame):
    
    def __init__(self):
        super(OpPreUI, self).__init__()
        self.op_pre = None
        self.filename = ""
        self.first_part = None
        self.second_part = None
        self.frame_grid = QGridLayout()  # 总布局

        self.input_widget = QWidget()  # 输入窗口
        self.input_grid = QGridLayout()  # 输入窗口布局
        self.open_file_btn = QPushButton(text="读取文法")  # 读取文法按钮
        self.string_input = QLineEdit()  # 输入串框
        self.string_input.setPlaceholderText("输入分析串")
        self.start_btn = QPushButton(text="start")  # 开始按钮

        self.result_widget = QWidget()  # 结果展示窗口
        self.result_grid = QGridLayout()  # 结果展示布局

        self.left_widget = QWidget()  # 左部窗口
        self.left_grid = QGridLayout()  # 左部布局
        self.grammar = QTextEdit()  # 文法显示窗口
        self.grammar.setFontFamily('STFangsong')
        self.grammar.setFontPointSize(12)

        self.change_btn = QPushButton(text="查看FirstVT(以下为LastVT)")  # FirstVt和LastVT查看切换按钮

        self.vt_show = QTableWidget()  # VT显示窗口
        self.vt_show.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.vt_show.setShowGrid(True)  # 设置显示网格线
        self.vt_show.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应列宽

        self.right_widget = QWidget()  # 右部窗口
        self.right_grid = QGridLayout() # 右部布局
        self.priority_table = QTableWidget()  # 优先关系表
        self.priority_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.priority_table.setShowGrid(True)  # 设置显示网格线
        self.priority_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应列宽

        self.step_show = QTableWidget()  # 步骤展示窗口
        self.step_show.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.step_show.verticalHeader().setVisible(False)  # 不显示行号
        self.step_show.setShowGrid(True)  # 设置显示网格线
        self.step_show.setColumnCount(4)  # 设置列数
        # 头部样式设置
        self.step_show.horizontalHeader().setStyleSheet("QHeaderView::section{border:1px groove gray;"
                                                        "border-radius:3px;padding:1px 1px;"
                                                        "background-color:rgb(210,210,210);"
                                                        "color:black;}")
        # 自适应列宽
        self.step_show.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置列头标号
        self.step_show.setHorizontalHeaderLabels(['符号栈', '输入串', '最左素短语', '动作'])

        # 调用布局设置对各部件进行组织
        self.layout_setting()
        self.button_action_setting()

    def layout_setting(self):
        # 总布局设置
        self.frame_grid.addWidget(self.input_widget, 0, 0)
        self.frame_grid.addWidget(self.result_widget, 1, 0)
        self.setLayout(self.frame_grid)

        # 输入窗口布局
        self.input_grid.addWidget(self.open_file_btn, 0, 0)
        self.input_grid.addWidget(self.string_input, 0, 1)
        self.input_grid.addWidget(self.start_btn, 0, 2)
        self.input_widget.setLayout(self.input_grid)

        # 结果显示布局
        self.result_grid.addWidget(self.left_widget, 0, 0)
        self.result_grid.addWidget(self.right_widget, 0, 1)
        # # 设置拉伸因子
        self.result_grid.setColumnStretch(0, 1)
        self.result_grid.setColumnStretch(1, 1)
        self.result_widget.setLayout(self.result_grid)

        # 左部显示窗口布局
        self.left_grid.addWidget(QLabel("输入/导入文法如下"), 0, 0)
        self.left_grid.addWidget(self.grammar, 1, 0)
        self.left_grid.addWidget(self.change_btn, 2, 0)
        self.left_grid.addWidget(self.vt_show, 3, 0)
        self.left_widget.setLayout(self.left_grid)

        # 右部显示窗口布局
        self.right_grid.addWidget(QLabel("优先关系表"), 0, 0)
        self.right_grid.addWidget(self.priority_table, 1, 0)
        self.right_grid.addWidget(self.step_show, 2, 0)
        self.right_widget.setLayout(self.right_grid)

    # 按钮响应事件设置
    def button_action_setting(self):
        self.open_file_btn.clicked.connect(self.open_grammar_file)
        self.start_btn.clicked.connect(self.start_op_pre)
        self.change_btn.clicked.connect(self.vt_show_change)

    # 读取文法文件并显示到文法窗口
    def open_grammar_file(self):
        # 打开文法文件
        filename, _s = QFileDialog.getOpenFileName(self, "Open File", '', "All Files (*);;"
                                                                          "C++ Files (*.cpp *.h *.py);;"
                                                                          "Txt files (*.txt);;"
                                                                          "Python files (*.py);;"
                                                                          "HTML-Files (*.htm *.html)")
        if filename:  # 文件名有效时才进行打开
            self.filename = filename
            try:
                # 读取文件内容并设置显示到文法的显示窗口
                file = QFile(filename)
                if file.open(QFile.ReadOnly | QFile.Text):
                    text = file.readAll()
                    text = str(text, encoding='utf-8')
                    # 设置内容显示
                    self.grammar.setPlainText(text)
                    file.close()
                    return True
            except Exception as e:
                print(e)
                QMessageBox.information(self, 'ERROR', 'Error, please open file again.')
        return False

    def start_op_pre(self):
        # 获取文法
        grammar = self.grammar.toPlainText()
        if grammar:
            # 每次运行先清空各表已有内容
            # 清空步骤显示表
            row_cnt = self.step_show.rowCount()
            for i in range(row_cnt):
                self.step_show.removeRow(0)

            # 创建算符优先分析器
            self.op_pre = None  # 导入算法                待完成..........
            # 获取输入串
            seq = self.string_input.text()
            if seq:
                if self.grammar.document().isModified():
                    self.write_to_file()
                try:
                    # 执行算法
                    self.first_part, self.second_part = Operator_priority.start(self.filename, seq)
                    # 显示优先表和步骤表，VT表由按钮点击完成显示，此处不显示
                    self.show_prior_step()
                except Exception as e:
                    print(e)
                    QMessageBox.information(self, 'ERROR', 'Running error, do it again.')
            else:
                QMessageBox.information(self, 'ERROR', 'Error, please input a string.')
        else:
            QMessageBox.information(self, 'ERROR', 'Error, please input the grammar.')

    # FirstVT和LastVT的切换显示
    def vt_show_change(self):
        if self.change_btn.text() == "查看FirstVT(以下为LastVT)":
            self.change_btn.setText("查看LastVT(以下为FirstVT)")
            first_vt = self.first_part[0]
            header_label = list(first_vt.keys())
            col_label = list(first_vt[header_label[0]].keys())
            self.vt_show.horizontalHeader().setStyleSheet("QHeaderView::section{border:1px groove gray;"
                                                                 "border-radius:3px;padding:1px 1px;"
                                                                 "background-color:rgb(210,210,210);"
                                                                 "color:black;}")
            self.vt_show.verticalHeader().setStyleSheet("QHeaderView::section{border:1px groove gray;"
                                                               "border-radius:3px;padding:1px 1px;"
                                                               "background-color:rgb(210,210,210);"
                                                               "color:black;}")
            self.vt_show.setColumnCount(len(col_label))
            self.vt_show.setHorizontalHeaderLabels(col_label)
            self.vt_show.setRowCount(len(header_label))
            self.vt_show.setVerticalHeaderLabels(header_label)
            for i, row_v in enumerate(col_label):
                for j, col_v in enumerate(header_label):
                    self.vt_show.setItem(j, i, QTableWidgetItem(str(first_vt[col_v][row_v])))
        elif self.change_btn.text() == "查看LastVT(以下为FirstVT)":
            self.change_btn.setText("查看FirstVT(以下为LastVT)")
            last_vt = self.first_part[1]
            header_label = list(last_vt.keys())
            col_label = list(last_vt[header_label[0]].keys())
            self.vt_show.horizontalHeader().setStyleSheet("QHeaderView::section{border:1px groove gray;"
                                                          "border-radius:3px;padding:1px 1px;"
                                                          "background-color:rgb(210,210,210);"
                                                          "color:black;}")
            self.vt_show.verticalHeader().setStyleSheet("QHeaderView::section{border:1px groove gray;"
                                                        "border-radius:3px;padding:1px 1px;"
                                                        "background-color:rgb(210,210,210);"
                                                        "color:black;}")
            self.vt_show.setColumnCount(len(col_label))
            self.vt_show.setHorizontalHeaderLabels(col_label)
            self.vt_show.setRowCount(len(header_label))
            self.vt_show.setVerticalHeaderLabels(header_label)
            for i, row_v in enumerate(col_label):
                for j, col_v in enumerate(header_label):
                    self.vt_show.setItem(j, i, QTableWidgetItem(str(last_vt[col_v][row_v])))

    # 显示优先关系表和步骤表
    def show_prior_step(self):
        # 显示优先关系表
        prior = self.first_part[2]
        self.priority_table.horizontalHeader().setStyleSheet("QHeaderView::section{border:1px groove gray;"
                                                        "border-radius:3px;padding:1px 1px;"
                                                        "background-color:rgb(210,210,210);"
                                                        "color:black;}")
        self.priority_table.verticalHeader().setStyleSheet("QHeaderView::section{border:1px groove gray;"
                                                             "border-radius:3px;padding:1px 1px;"
                                                             "background-color:rgb(210,210,210);"
                                                             "color:black;}")
        header_label = list(prior.keys())
        self.priority_table.setColumnCount(len(header_label))
        self.priority_table.setHorizontalHeaderLabels(header_label)
        self.priority_table.setRowCount(len(header_label))
        self.priority_table.setVerticalHeaderLabels(header_label)
        for i, row_v in enumerate(header_label):
            for j, column_v in enumerate(header_label):
                self.priority_table.setItem(i, j, QTableWidgetItem(str(prior[row_v][column_v])))

        # 显示分析步骤
        sign, seq, left, action = self.second_part[0], self.second_part[1], self.second_part[2], self.second_part[3]
        for i in range(len(sign)):
            self.step_show.insertRow(i)
            self.step_show.setItem(i, 0, QTableWidgetItem(str(sign[i])))
            self.step_show.setItem(i, 1, QTableWidgetItem(str(seq[i])))
            self.step_show.setItem(i, 2, QTableWidgetItem(str(left[i])))
            self.step_show.setItem(i, 3, QTableWidgetItem(str(action[i])))

    def write_to_file(self):
        writer = QTextDocumentWriter(self.filename)
        writer.write(self.grammar.document())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Op_Pre_Analysis")
    frame = OpPreUI()
    frame.resize(1000, 600)
    frame.show()
    app.exec_()