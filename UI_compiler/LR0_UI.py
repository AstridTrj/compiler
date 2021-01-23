import sys
from PyQt5 import sip
import pandas as pd
import numpy as np

from PyQt5.QtCore import Qt, QFile
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor
from compiler_principle import LR0_ana
from PyQt5.QtWidgets import (QFrame, QWidget, QGridLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QApplication, QTextEdit, QTableWidget,
                             QAbstractItemView, QFileDialog, QTableWidgetItem, QHeaderView)


class LR0UI(QFrame):

    def __init__(self):
        super(LR0UI, self).__init__()
        self.lr_analysis = None
        # 总窗口布局
        self.frame_grid = QGridLayout()
        self.result_show = QWidget()
        self.result_grid = QGridLayout()
        # LR输入区域
        self.input_btn_widget = QWidget()
        self.input_grid = QGridLayout()
        self.open_file = QPushButton(self.input_btn_widget, text="Open_Gra")
        self.input_text = QLineEdit("Input Statement")
        self.ok_btn = QPushButton(text="Start")
        # 文法和步骤显示区域
        self.gra_table = QWidget()
        self.gra_grid = QGridLayout()
        self.grammar_show = QTextEdit()
        self.grammar_show.setFontFamily('STFangsong')
        self.grammar_show.setFontPointSize(12)
        # 步骤显示窗口
        self.step_show = QTableWidget()
        self.step_show.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.step_show.verticalHeader().setVisible(False)  # 不显示行号
        self.step_show.setColumnCount(4)  # 设置列数
        self.step_show.setShowGrid(True)  # 设置显示网格线
        # 头部样式设置
        self.step_show.horizontalHeader().setStyleSheet("QHeaderView::section{border:1px groove gray;"
                                                        "border-radius:3px;padding:1px 1px;"
                                                        "background-color:rgb(210,210,210);"
                                                        "color:black;}")
        # 自适应列宽
        self.step_show.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置列头标号
        self.step_show.setHorizontalHeaderLabels(['sign_stack', 'status_stack', 'input_seq', 'op_explain'])
        # DFA展示
        self.dfa_table = QWidget()
        self.dfa_grid = QGridLayout()
        # DFA和分析表转换查看的按钮
        self.change_btn = QPushButton(self.dfa_table, text="See Analysis-Table")
        # 分析表定义
        self.ana_table = QTableWidget()
        self.ana_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ana_table.verticalHeader().setVisible(False)
        self.ana_table.setShowGrid(True)
        # 提示信息标签和dfa显示窗口定义
        font = QFont("STFangsong")
        font.setPointSizeF(15)
        font.setBold(True)
        self.dfa_label = QLabel("Automaton of The Grammar")
        self.dfa_label.setAlignment(Qt.AlignCenter)
        self.dfa_label.setFont(font)
        self.dfa_show = QLabel(self.dfa_table)
        self.dfa_show.setAlignment(Qt.AlignCenter)

        # 布局并添加按钮响应动作
        self.set_layout()
        self.set_action()

    def set_layout(self):
        # 主窗口布局设置
        self.frame_grid.addWidget(self.input_btn_widget, 0, 0)
        self.frame_grid.addWidget(self.result_show, 1, 0)
        self.setLayout(self.frame_grid)
        # 输入窗口布局
        self.input_grid.addWidget(self.open_file, 0, 0)
        self.input_grid.addWidget(self.input_text, 0, 1)
        self.input_grid.addWidget(self.ok_btn, 0, 2)
        self.input_btn_widget.setLayout(self.input_grid)
        # 结果展示窗口布局
        self.result_grid.addWidget(self.gra_table, 0, 0)
        self.result_grid.addWidget(self.dfa_table, 0, 1)
        self.result_grid.setColumnStretch(0, 1)  # 设置拉伸因子
        self.result_grid.setColumnStretch(1, 1)
        self.result_show.setLayout(self.result_grid)
        # 文法和步骤展示窗口布局
        self.gra_grid.addWidget(self.grammar_show, 0, 0)
        self.gra_grid.addWidget(self.step_show, 1, 0)
        self.gra_table.setLayout(self.gra_grid)
        # DFA展示窗口布局
        self.dfa_grid.addWidget(self.change_btn, 0, 0)
        self.dfa_grid.addWidget(self.dfa_label, 1, 0)
        self.dfa_grid.addWidget(self.dfa_show, 2, 0)
        self.dfa_grid.setRowStretch(1, 1)
        self.dfa_grid.setRowStretch(2, 3)
        self.dfa_table.setLayout(self.dfa_grid)

    def set_action(self):
        # 设置各按钮响应事件
        self.open_file.clicked.connect(self.open_grammar_file)
        self.ok_btn.clicked.connect(self.begin_lr0)
        self.change_btn.clicked.connect(self.table_change)

    def table_change(self):
        # 判断按钮text信息执行对应的布局更新
        if self.change_btn.text() == "See Analysis-Table":
            # 更新按钮和提示标签的信息
            self.change_btn.setText("See The DFA")
            self.dfa_label.setText("The Analysis Table")
            # 此处重新创建一个窗口对象，不然不能显示
            self.ana_table = QTableWidget()
            self.ana_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.ana_table.verticalHeader().setVisible(False)
            self.ana_table.setShowGrid(True)
            self.ana_table.horizontalHeader().setStyleSheet("QHeaderView::section{border:1px groove gray;"
                                                        "border-radius:3px;padding:1px 1px;"
                                                        "background-color:rgb(210,210,210);"
                                                        "color:black;}")
            # 自适应列宽可行高
            self.ana_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # self.ana_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.dfa_grid.addWidget(self.ana_table, 2, 0)

            self.dfa_grid.setRowStretch(2, 4)
            self.dfa_table.setLayout(self.dfa_grid)
            # 转换为分析表之后，显示分析表中的信息
            try:
                # 设置分析表和表头信息
                self.ana_table.setColumnCount(len(self.lr_analysis.action_table.columns) +
                                              len(self.lr_analysis.go_table.columns) + 1)
                self.ana_table.setHorizontalHeaderLabels(['Status'] + list(self.lr_analysis.action_table.columns) +
                                                         list(self.lr_analysis.go_table.columns))
                meg = pd.concat([self.lr_analysis.action_table, self.lr_analysis.go_table], axis=1)
                # 显示分析表内容
                for index, row in meg.iterrows():
                    self.ana_table.insertRow(index)
                    self.ana_table.setItem(index, 0, QTableWidgetItem(str(index)))
                    for i in range(len(row)):
                        if row[i] is not np.nan:
                            self.ana_table.setItem(index, i+1, QTableWidgetItem(str(row[i])))
            except Exception as e:
                print(e)
                QMessageBox.information(self, 'ERROR', 'Error, please input grammar.')

        elif self.change_btn.text() == "See The DFA":
            # 切换到DFA显示窗口
            self.change_btn.setText("See Analysis-Table")
            self.dfa_label.setText("Automaton of The Grammar")
            # 重新创建DFA显示标签
            self.dfa_show = QLabel(self.dfa_table)
            self.dfa_show.setAlignment(Qt.AlignCenter)

            self.dfa_grid.addWidget(self.dfa_show, 2, 0)

            self.dfa_grid.setRowStretch(2, 4)
            self.dfa_table.setLayout(self.dfa_grid)
            # 显示图片
            try:
                if len(self.lr_analysis.result) > 0:
                    image = QImage("img/LR_Item_DFA.png").scaled(460, 380, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                    self.dfa_show.setPixmap(QPixmap.fromImage(image))
            except Exception as e:
                print(e)
                QMessageBox.information(self, 'ERROR', 'Error, please input right grammar.')

    def open_grammar_file(self):
        # 打开文件
        filename, _s = QFileDialog.getOpenFileName(self, "Open File", '', "All Files (*);;"
                                                  "C++ Files (*.cpp *.h *.py);;"
                                                  "Txt files (*.txt);;"
                                                  "Python files (*.py);;"
                                                  "HTML-Files (*.htm *.html)")
        if filename:  # 文件名有效时才进行打开
            try:
                # 读取文件内容并设置显示到文法的显示窗口
                inFile = QFile(filename)
                if inFile.open(QFile.ReadOnly | QFile.Text):
                    text = inFile.readAll()
                    text = str(text, encoding='utf-8')
                    # 设置内容显示
                    self.grammar_show.setPlainText(text)
                    inFile.close()
                    return True
            except Exception as e:
                print(e)
                QMessageBox.information(self, 'ERROR', 'Error, please open file again.')
        return False

    def begin_lr0(self):
        # 获取文法
        grammar = self.grammar_show.toPlainText()
        if grammar:
            # 重新选择后首先进行步骤表和分析表的清空
            row_cnt = self.step_show.rowCount()
            for i in range(row_cnt):
                self.step_show.removeRow(0)
            row_cnt = self.ana_table.rowCount()
            for i in range(row_cnt):
                self.ana_table.removeRow(0)
            # 创建LR分析器
            self.lr_analysis = LR0_ana.LR0Analysis()
            # 获取输入串
            seq = self.input_text.text()
            try:
                self.lr_analysis.run(text=grammar, seq=seq)
                self.show_dfa_step()
                if self.change_btn.text() == "See Analysis-Table":
                    self.change_btn.setText("See The DFA")
                else:
                    self.change_btn.setText("See Analysis-Table")
                self.table_change()
            except Exception as e:
                print(e)
                QMessageBox.information(self, 'ERROR', 'Running error, do it again.')
        else:
            QMessageBox.information(self, 'ERROR', 'Error, please input the grammar.')

    def show_dfa_step(self):
        # 显示DFA
        image = QImage("img/LR_Item_DFA.png").scaled(460, 380, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.dfa_show.setPixmap(QPixmap.fromImage(image))
        index = 0
        # 显示输入串的分析步骤
        while index < len(self.lr_analysis.result):
            self.step_show.insertRow(index)  # 首先需要插入一行
            self.step_show.setItem(index, 0, QTableWidgetItem(self.lr_analysis.result[index][0]))
            self.step_show.setItem(index, 1, QTableWidgetItem(str(self.lr_analysis.result[index][1])))
            self.step_show.setItem(index, 2, QTableWidgetItem(self.lr_analysis.result[index][2]))
            self.step_show.setItem(index, 3, QTableWidgetItem(self.lr_analysis.result[index][3]))
            index += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("LR0_Analysis")
    frame = LR0UI()
    frame.resize(1000, 600)
    frame.show()
    app.exec_()