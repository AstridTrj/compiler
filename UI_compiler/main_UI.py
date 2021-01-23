import sys

from PyQt5.QtCore import QFileInfo, QFile, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import re_exp_UI
from Dag_UI import DagUI
from LR0_UI import LR0UI
from OpPre_UI import OpPreUI
from compiler_principle.UI_compiler import widget_edit
from compiler_principle.fanCompiler import lexical, syner, semantic_analysis, middle_code, target_code

# 图标路径
rsrcfilename = 'logo'


class My_compilerUI(QMainWindow):
    lexer = None  # 词法分析器
    syner = None  # 语法分析器
    semantic = None  # 语义分析器
    target = None  # 目标代码生成器
    re2mdfa = None  # 正则转换程序
    op_pre_syner = None  # 算符优先分析器
    lr0_syner = None  # LR0分析器
    middle = None  # 中间代码生成器
    dag = None  # DAG优化
    docwidget = {}  # 停靠窗口
    filename = None  # 文件名
    layout = None  # 总页面布局
    tab = None  # QTabWidget设置

    def __init__(self):
        super(My_compilerUI, self).__init__()
        self.initUI()  # 界面初始化
        self.init_menu()  # 设置菜单

    def initUI(self):
        w = QWidget()  # 页面布局主要为一主窗口
        self.layout = QGridLayout()  # 窗口中的布局
        w.setLayout(self.layout)
        self.setCentralWidget(w)  # 设置为QMainWindow的中心
        self.tab = QTabWidget(w)
        qtabBar = QTabBar()
        self.tab.setTabBar(qtabBar)

        self.tab.setTabsClosable(True)
        self.tab.tabCloseRequested.connect(self.tab_close)
        self.layout.addWidget(self.tab, 0, 0)

    def tab_changed(self):
        # currentWidget可获取当前页面
        self.filename = self.tab.currentWidget().filename
        self.set_current_file_name(self.filename)

    def tab_close(self, index):
        self.tab.setCurrentIndex(index)
        self.filename = self.tab.currentWidget().filename
        if self.tab.currentWidget().e_edit.document().isModified():
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText('The file has been modified !!!')
            msgBox.setInformativeText('Do you want to save your changes?')
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)
            res = msgBox.exec_()
            if res == QMessageBox.Save:
                # save the file
                self.file_save()
                self.tab.removeTab(index)
            elif res == QMessageBox.Discard:
                self.tab.removeTab(index)
                self.layout.addWidget(self.tab)
            else:
                # 选择取消时则不做操作
                pass
        else:
            self.tab.removeTab(index)
            self.layout.addWidget(self.tab)

    # 保存当前文件
    def file_save(self):
        try:
            # 不存在当前文件
            if not self.filename:
                return self.file_save_as()
            else:
                writer = QTextDocumentWriter(self.tab.currentWidget().filename)
                print(self.tab.currentWidget().filename)
                success = writer.write(self.tab.currentWidget().e_edit.document())
                print(success)
                if success:
                    self.tab.currentWidget().e_edit.document().setModified(False)
                    return True
        except Exception as e:
            print(e)
            QMessageBox.information(self, 'ERROR', 'Save file error, new a file or do it again.')
        return False

    def file_save_as(self):
        filename, _a = QFileDialog.getSaveFileName(self, "Save as...", None,
                                            "Txt files (*.txt);;"
                                            "Python files (*.py);;"
                                            "HTML-Files (*.htm *.html);;"
                                            "C Files(*.c);;"
                                            "All Files (*)")
        if filename:
            self.filename = filename
            if self.file_save():
                self.tab.setTabText(self.tab.currentIndex(), QFileInfo(filename).fileName())
        return False

    def set_current_file_name(self, filename=''):
        self.tab.currentWidget().e_edit.document().setModified(False)
        if not filename:
            showname = 'untitled.txt'
        else:
            showname = QFileInfo(filename).fileName()
        self.setWindowTitle(self.tr("%s[*] - %s" % (showname, "Complier Editer")))
        self.setWindowModified(False)

    # 添加响应事件
    def create_action(self, text, slot=None, shortcut=None, icon=None, tip=None,
                                                                                checkable=False):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon('{0}'.format(icon)))
        # 快捷方式
        if shortcut is not None:
            action.setShortcut(shortcut)
        # 提示信息
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    @staticmethod
    def add_actions(target, actions):
        for action in actions:
            if action is None:
                # 设置分隔符
                target.addSeparator()
            else:
                target.addAction(action)

    def init_menu(self):
        file_new_action = self.create_action('&New', self.file_new,
                                             QKeySequence.New, rsrcfilename + '/filenew.jpg', "新建文件")
        file_open_action = self.create_action('&Open...', self.file_open, QKeySequence.Open,
                                              rsrcfilename + '/fileopen.jpg', "打开文件" )
        file_save_action = self.create_action('&Save', self.file_save, QKeySequence.Save,
                                              rsrcfilename + '/filesave.jpg', "保存文件")
        file_save_as_action = self.create_action('Save &As...', self.file_save_as, icon=rsrcfilename + '/filesaveas.jpg',
                                                 tip="另存为...")
        file_quit_action = self.create_action("&Quit", self.close, "Ctrl+Q", rsrcfilename + "/filequit.jpg",
                                              "退出系统")
        edit_copy_action = self.create_action("&Copy", self.edit_copy, QKeySequence.Copy,
                                              rsrcfilename + '/editcopy.jpg', "复制选中内容")
        edit_cut_action = self.create_action("Cu&t", self.edit_cut, QKeySequence.Cut,
                                             rsrcfilename + '/editcut.jpg', "剪切选中内容")
        edit_paste_action = self.create_action("&Paste", self.edit_paste, QKeySequence.Paste,
                                               rsrcfilename + '/edipaste.jpg', "粘贴内容到光标处")
        edit_redo_action = self.create_action("&Redo", self.edit_redo, QKeySequence.Redo,
                                              rsrcfilename + '/editredo.jpg', "重做动作")
        edit_undo_action = self.create_action("&Undo", self.edit_undo, QKeySequence.Undo,
                                              rsrcfilename + '/editundo.jpg', "撤销动作")
        lexical_analysis_action = self.create_action("&Start", self.start_lexer)
        syner_pre_analysis = self.create_action("&PreSyner", self.start_syner)
        semantic_analysis = self.create_action("Start Semantic", self.start_semantic)
        middle_code_action = self.create_action("&Start middle", self.start_middle)
        target_code_action = self.create_action("Start gen-TargetCode", self.start_target_code)

        re_exp_action = self.create_action("Re2MDFA", self.re_to_mdfa)
        operator_pre_action = self.create_action("OperatorPreSyner", self.start_op_pre)
        lr0_action = self.create_action("LR0_Syner", self.start_lr0)
        dag_action = self.create_action("DAG_Optimize", self.start_dag)

        # 文件操作菜单
        file_menu = self.menuBar().addMenu('&File')
        self.add_actions(file_menu, [file_new_action, file_open_action,
                                     file_save_action, file_save_as_action, None, file_quit_action])
        # 文本编辑菜单
        edit_menu = self.menuBar().addMenu('&Edit')
        self.add_actions(edit_menu, [edit_copy_action, edit_cut_action, edit_paste_action,
                                     edit_undo_action, edit_redo_action])
        # 词法分析菜单
        lexical_analysis_menu = self.menuBar().addMenu("&LexicalAnalysis")
        self.add_actions(lexical_analysis_menu, [lexical_analysis_action, re_exp_action])
        # 语法分析菜单
        syntax_analysis_menu = self.menuBar().addMenu("&SyntaxAnalysis")
        self.add_actions(syntax_analysis_menu, [syner_pre_analysis, operator_pre_action, lr0_action])
        # 语义分析菜单
        semantic_analysis_menu = self.menuBar().addMenu("SemanticAnalysis")
        self.add_actions(semantic_analysis_menu, [semantic_analysis])
        # 中间代码生成菜单选项
        middle_code_menu = self.menuBar().addMenu("&MiddleCode")
        self.add_actions(middle_code_menu, [middle_code_action, dag_action])
        # 目标代码生成菜单选项
        target_code_menu = self.menuBar().addMenu("&TargetCode")
        self.add_actions(target_code_menu, [target_code_action])
        help_menu = self.menuBar().addMenu("&Help")

        file_toolbar = self.addToolBar("File")
        file_toolbar.setObjectName("file_toolbar")
        self.add_actions(file_toolbar, [file_new_action, file_open_action, file_save_action, file_save_as_action,
                                        file_quit_action])
        edit_toolbar = self.addToolBar("Edit")
        edit_toolbar.setObjectName("edit_toolbar")
        self.add_actions(edit_toolbar, [edit_copy_action, edit_cut_action, edit_paste_action,
                          edit_undo_action, edit_redo_action])

    def file_new(self):
        try:
            filename, _a = QFileDialog.getSaveFileName(self, "Save as...", None,
                                                         "Txt files (*.txt);;"
                                                         "Python files (*.py);;"
                                                         "HTML-Files (*.htm *.html);;C Files(*.c);;"
                                                         "All Files (*)")

            if filename:
                t = widget_edit.TableEdit()
                t.filename = filename
                self.filename = filename
                self.tab.addTab(t, QFileInfo(filename).fileName())
                self.tab.setCurrentWidget(t)
                self.layout.addWidget(self.tab)
        except Exception as e:
            print(e)
            return False
        return True

    def file_open(self):
        filename, _a = QFileDialog.getOpenFileName(self, 'Open File', None,
                                                   "All Files (*);;"
                                                   "C Files(*.c);;"
                                                   "C++ Files (*.cpp *.h *.py);;"
                                                   "Txt files (*.txt);;"
                                                   "Python files (*.py);;"
                                                   "HTML-Files (*.htm *.html)")
        if filename:
            t = widget_edit.TableEdit()
            t.filename = filename
            self.filename = filename
            self.tab.addTab(t, QFileInfo(filename).fileName())
            self.tab.setCurrentWidget(t)
            self.layout.addWidget(self.tab)
            if self.load_file(filename):
                return True
            else:
                return False
        return False

    def edit_copy(self):
        try:
            cursor = self.tab.currentWidget().e_edit.textCursor()
            text = cursor.selectedText()
            if text:
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
        except Exception as e:
            pass

    def edit_cut(self):
        try:
            cursor = self.tab.currentWidget().e_edit.textCursor()
            text = cursor.selectedText()
            if text:
                cursor.removeSelectedText()
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
        except Exception as e:
            pass

    def edit_paste(self):
        try:
            text_edit = self.tab.currentWidget().e_edit
            clipboard = QApplication.clipboard()
            text_edit.insertPlainText(clipboard.text())
        except Exception as e:
            pass

    def edit_redo(self):
        try:
            self.tab.currentWidget().e_edit.redo()
        except Exception as e:
            pass

    def edit_undo(self):
        try:
            self.tab.currentWidget().e_edit.undo()
        except Exception as e:
            pass

    def start_dag(self):
        self.dag = DagUI()
        self.dag.resize(1000, 600)
        self.dag.show()

    def start_lr0(self):
        self.lr0_syner = LR0UI()
        self.lr0_syner.resize(1000, 600)
        self.lr0_syner.show()

    def start_op_pre(self):
        self.op_pre_syner = OpPreUI()
        self.op_pre_syner.resize(1000, 600)
        self.op_pre_syner.show()

    def re_to_mdfa(self):
        self.re2mdfa = re_exp_UI.ReExpUI()
        self.re2mdfa.resize(700, 600)
        self.re2mdfa.show()

    # 目标代码生成
    def start_target_code(self):
        try:
            # 获取当前页面的文件名
            dock_name = QFileInfo(self.tab.currentWidget().filename).fileName()
            # 创建目标代码生成器
            target_code.inite()
            self.target = target_code.start(self.semantic[0], self.semantic[1], self.semantic[2],
                                            self.semantic[3], self.semantic[4], self.middle[0], self.middle[1])
        except Exception as e:
            QMessageBox.information(self, 'ERROR', str(e))
            return None
        try:
            # 结果显示
            self.docwidget[dock_name]['target_code'].setPlainText(self.target[0])
        except Exception as e:
            QMessageBox.information(self, 'ERROR', str(e))

    def start_semantic(self):
        try:
            # 获取当前页面的文件名
            dock_name = QFileInfo(self.tab.currentWidget().filename).fileName()
            # 创建语义分析器
            self.semantic = semantic_analysis.symbol_table_and_static_check()
        except Exception as e:
            QMessageBox.information(self, 'ERROR', str(e))
            return None
        try:
            # 结果显示
            for i in self.semantic[4]:
                self.docwidget[dock_name]['error'].addItem(i)
            if len(self.semantic[4]) == 0:
                self.docwidget[dock_name]['error'].addItem("语义分析成功.")
        except Exception as e:
            QMessageBox.information(self, 'ERROR', str(e))

    # 中间代码生成
    def start_middle(self):
        try:
            dock_name = QFileInfo(self.tab.currentWidget().filename).fileName()
            self.middle = middle_code.create_mid_code()
        except Exception as e:
            QMessageBox.information(self, 'ERROR', str(e))
            return None
        try:
            # QListWidget类型，为其添加item，相当于列名
            self.docwidget[dock_name]['quaternary'].addItem('num（op，num1，num2，num3）')
            for i, four in enumerate(self.middle[0]):
                self.docwidget[dock_name]['quaternary'].addItem("%2s     %s" % (i, str(four)))
            self.docwidget[dock_name]['error'].addItem("中间代码生成成功.")
        except Exception as e:
            QMessageBox.information(self, 'ERROR', str(e))

    def start_lexer(self):
        try:
            dock_name = QFileInfo(self.tab.currentWidget().filename).fileName()
            token = QListWidget()
            error = QListWidget()
            quaternary = QListWidget()
            target = QTextEdit()
            target.setFontPointSize(10)
            target.setReadOnly(True)
            self.docwidget[dock_name] = {'token': token, 'error': error, 'quaternary': quaternary, 'target_code': target}
            # 注意问题源
            self.lexer = lexical.run_lexical_analysis(self.tab.currentWidget().filename)
            self.show_token_error()
        except Exception as e:
            QMessageBox.information(self, 'ERROR', str(e))
            return None
        try:
            # 停靠控件，类似小窗口,可任意拖动
            dock_token = QDockWidget('Token')
            dock_token.setWidget(self.docwidget[dock_name]['token'])
            dock_token.setObjectName(dock_name)
            # AllDockWidgetFeatures设置窗口具有所有特性
            dock_token.setFeatures(dock_token.AllDockWidgetFeatures)
            # 设置停靠区域
            self.addDockWidget(Qt.RightDockWidgetArea, dock_token)

            dock_error = QDockWidget("Error")
            dock_error.setWidget(self.docwidget[dock_name]["error"])
            dock_error.setObjectName(dock_name)
            dock_error.setFeatures(dock_error.AllDockWidgetFeatures)
            self.addDockWidget(Qt.RightDockWidgetArea, dock_error)

            dock_four = QDockWidget("Quaternary")
            dock_four.setWidget(self.docwidget[dock_name]["quaternary"])
            dock_four.setObjectName(dock_name)
            dock_four.setFeatures(dock_four.AllDockWidgetFeatures)
            self.addDockWidget(Qt.RightDockWidgetArea, dock_four)

            dock_target = QDockWidget("TargetCode")
            dock_target.setWidget(self.docwidget[dock_name]["target_code"])
            dock_target.setObjectName(dock_name)
            dock_target.setFeatures(dock_target.AllDockWidgetFeatures)
            self.addDockWidget(Qt.RightDockWidgetArea, dock_target)

            # 把多个dockwidget变成一个tab形式的窗体,类似合并
            self.tabifyDockWidget(dock_token, dock_error)
            self.tabifyDockWidget(dock_error, dock_four)
            self.tabifyDockWidget(dock_four, dock_target)
        except Exception as e:
            QMessageBox.information(self, 'ERROR', str(e))

    # 语法分析器
    def start_syner(self):
        try:
            # 获取当前页面的文件名
            dock_name = QFileInfo(self.tab.currentWidget().filename).fileName()
            # 创建语法分析器
            self.syner = syner.run_grammatical_analysis()
        except Exception as e:
            QMessageBox.information(self, 'ERROR', str(e))
            return None
        try:
            # 结果显示
            for i in self.syner[0]:
                self.docwidget[dock_name]['error'].addItem(i)
            if len(self.syner[0]) == 0:
                self.docwidget[dock_name]['error'].addItem("语法分析成功.")
        except Exception as e:
            QMessageBox.information(self, 'ERROR', str(e))

    def token_double_clicked(self, item):
        pass

    def error_double_clicked(self, item):
        pass

    def show_token_error(self):
        dock_name = QFileInfo(self.tab.currentWidget().filename).fileName()
        try:
            # QListWidget类型，为其添加item，相当于列名
            self.docwidget[dock_name]['token'].addItem('row\tcol\tword\tcode')
            for i in self.lexer[0]:
                self.docwidget[dock_name]['token'].addItem(str(i.row) + '\t' + str(i.col) + '\t' + str(i.word) + '\t' + str(i.code))
            for i in self.lexer[1]:
                self.docwidget[dock_name]['error'].addItem(i)
            if len(self.lexer[1]) == 0:
                self.docwidget[dock_name]['error'].addItem("词法分析成功.")
        except Exception as e:
            print(e)
            QMessageBox.information(self, 'ERROR', 'Show error.')

    def load_file(self, filename=''):
        # 加载文件
        if filename:
            try:
                # 打开文件读取内容写到当前页面
                inFile = QFile(filename)
                if inFile.open(QFile.ReadOnly | QFile.Text):
                    text = inFile.readAll()
                    text = str(text, encoding='utf-8')
                    self.tab.currentWidget().e_edit.setPlainText(text)
                    inFile.close()
                    return True
            except Exception as e:
                # 当打开错误时给予错误提示
                QMessageBox.warning(self, "Load Error !", "Failed to load {0}: {1}".format(filename, e))
                return False
        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Complier Editer")
    app.setWindowIcon(QIcon("{0}".format(rsrcfilename + "/compiler.jpg")))
    win = My_compilerUI()
    win.resize(1200, 600)
    win.show()
    sys.exit(app.exec_())
