import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap, QKeyEvent

from PyQt5.QtWidgets import QMessageBox
from uerlogin import Ui_Ui_login as Ui_login
from hello import Ui_Ui_hello as Ui_hello
from order import Ui_Ui_order as Ui_order
from user_register import Ui_Register
from admin_login import Ui_Admin
from manage import Ui_Manage
from admin_register import Ui_admin_register
from company_register import Ui_company_register
from company_manage import Ui_company
import random

from db_config import connect_db

# 定义全局变量message
user_message = []
company_message = []


# 主窗口
class HelloWindow(QtWidgets.QMainWindow, Ui_hello):
    switch_window1 = QtCore.pyqtSignal()  # 跳转信号
    switch_window2 = QtCore.pyqtSignal()  # 跳转信号

    def __init__(self):
        super(HelloWindow, self).__init__()
        self.setupUi(self)
        self.userButton.clicked.connect(self.userLogin)
        self.pushButton_2.clicked.connect(self.adminLogin)

    def userLogin(self):
        self.switch_window1.emit()

    def adminLogin(self):
        self.switch_window2.emit()


# 登录窗口
class LoginWindow(QtWidgets.QMainWindow, Ui_login):
    switch_window1 = QtCore.pyqtSignal()  # 跳转信号
    switch_window2 = QtCore.pyqtSignal()  # 跳转信号

    def __init__(self):
        super(LoginWindow, self).__init__()
        self.setupUi(self)
        self.login.clicked.connect(self.Login)
        self.register_.clicked.connect(self.Register)

    def Login(self):
        # 连接数据库
        conn_user = connect_db("passenger")
        cur_user = conn_user.cursor()
        cur_user.execute("select account,password from passenger;")
        rows = cur_user.fetchall()
        # 关闭连接
        conn_user.close()
        username = self.username.text()
        password = self.password.text()
        global user_message
        user_message = [username, password]
        if password == "":
            QMessageBox.warning(self, '警告', '密码不能为空，请输入!')
            return None
        if (username, password) in rows:
            self.switch_window1.emit()
            self.username.clear()
            self.password.clear()
        else:
            if password != "":
                QMessageBox.critical(self, '错误', '账号或密码错误！')
                self.username.clear()
                self.password.clear()
                return None

    def Register(self):
        self.switch_window2.emit()


#  订票窗口
class OrderWindow(QtWidgets.QMainWindow, Ui_order):
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        super(OrderWindow, self).__init__()
        self.setupUi(self)
        self.pushButton_29.clicked.connect(self.back)
        self.modify.clicked.connect(self.user_message_modify)
        self.select.clicked.connect(self.order_select)
        self.cancel.clicked.connect(self.order_cancel)
        self.select_2.clicked.connect(self.flight_inquiry)
        self.order.clicked.connect(self.flight_order)
        self.modify_2.clicked.connect(self.display_message)
        self.display()

    def display(self):
        # 连接数据库
        conn_user = connect_db("passenger")
        cur_user = conn_user.cursor()
        # 完整航班展示
        # global user_message
        if user_message:
            cur_user.execute("select name,gender from passenger where account='%s';") % user_message[0]
            result = cur_user.fetchall()
            if result[1] == '男':
                self.widget.setWindowIconText("你好，%s先生") % result[0]
            else:
                self.widget.setWindowIconText("你好，%s女士") % result[0]
        cur_user.execute("select count(*) from flight;")
        num = cur_user.fetchall()
        self.tableWidget_2.setRowCount(num[0][0])
        cur_user.execute("select flight_id,company.company_name,departure_city,departure_airport,arrival_city,"
                         "arrival_airport"
                         ",departure_time,model from flight,company where flight.company_id=company.company_id;")
        rows = cur_user.fetchall()
        conn_user.close()
        count = 0
        for row in rows:
            item1 = QTableWidgetItem(row[0])
            self.tableWidget_2.setItem(count, 0, item1)
            item2 = QTableWidgetItem(row[1])
            self.tableWidget_2.setItem(count, 1, item2)
            item3 = QTableWidgetItem(row[2])
            self.tableWidget_2.setItem(count, 2, item3)
            item4 = QTableWidgetItem(row[3])
            self.tableWidget_2.setItem(count, 3, item4)
            item5 = QTableWidgetItem(row[4])
            self.tableWidget_2.setItem(count, 4, item5)
            item6 = QTableWidgetItem(row[5])
            self.tableWidget_2.setItem(count, 5, item6)
            item7 = QTableWidgetItem(str(row[6]))
            self.tableWidget_2.setItem(count, 6, item7)
            item8 = QTableWidgetItem(row[7])
            self.tableWidget_2.setItem(count, 7, item8)
            count += 1

    def back(self):
        self.switch_window.emit()

    # 航班查询
    def flight_inquiry(self):
        # 连接数据库
        conn_user = connect_db("passenger")
        cur_user = conn_user.cursor()
        # 读入text框输入的数据
        depart = self.departure.text()
        arrive = self.arrival.text()
        start_date = self.lineEdit_startday_2.text()
        sql_connect = "select count(*) from flight,cabin where " \
                       "flight.flight_id=cabin.flight_id and flight.departure_city='%s' and flight.arrival_city='%s' and " \
                       "cabin.flight_date='%s';" % (depart, arrive, start_date)
        try:
            cur_user.execute(sql_connect)
        except Exception as e:
            print(e)
            depart = ""
            arrive = ""
            start_date = ""
            QMessageBox.warning(self, '提示', '日期格式输入错误')
        if depart != "" and arrive != "" and start_date != "":
            num = cur_user.fetchall()
            self.tableWidget_3.setRowCount(num[0][0])
            sql_connect_ = "select flight.flight_id,cabin.cabin_id,cabin.flight_date,flight.departure_time,cabin.seats," \
                           "cabin.available_seat,cabin.price from flight,cabin where flight.flight_id=cabin.flight_id " \
                           "and flight.departure_city='%s' and flight.arrival_city='%s' and cabin.flight_date='%s';" \
                           % (depart, arrive, start_date)
            cur_user.execute(sql_connect_)
            rows = cur_user.fetchall()
            conn_user.close()
            count = 0
            for row in rows:
                item1 = QTableWidgetItem(row[0])
                self.tableWidget_3.setItem(count, 0, item1)
                item2 = QTableWidgetItem(row[1])
                self.tableWidget_3.setItem(count, 1, item2)
                item3 = QTableWidgetItem(str(row[2])[0:10])
                self.tableWidget_3.setItem(count, 2, item3)
                item4 = QTableWidgetItem(str(row[3]))
                self.tableWidget_3.setItem(count, 3, item4)
                item5 = QTableWidgetItem(str(row[4]))
                self.tableWidget_3.setItem(count, 4, item5)
                item6 = QTableWidgetItem(str(row[5]))
                self.tableWidget_3.setItem(count, 5, item6)
                item7 = QTableWidgetItem(str(row[6]))
                self.tableWidget_3.setItem(count, 6, item7)
                count += 1
        else:
            self.lineEdit_startday_2.clear()
            self.lineEdit_startday_2.setPlaceholderText("示例格式：2022-12-05")
            conn_user.close()
            pass

    # 机票订购
    def flight_order(self):
        # 连接数据库
        conn_user = connect_db("passenger")
        cur_user = conn_user.cursor()
        flight_id = self.lineEdit_flightid.text()
        start_date = self.lineEdit_startday1_2.text()
        cabin_level = self.lineEdit_cabin_level.text()
        if flight_id == '' or start_date == '' or cabin_level == '':
            QMessageBox.information(self, '提示', '未获取到完整信息，无法进行订票，请补充信息！')
        else:
            sql_connect = "select flight_id,cabin_id from cabin"
            cur_user.execute(sql_connect)
            rows = cur_user.fetchall()
            if (flight_id, cabin_level) not in rows:
                QMessageBox.information(self, '提示', '并没有您所选择的对应航班，请重新选择')
            else:
                # 查询余票数量的语句
                sql_connect = "select cabin.available_seat from cabin where flight_id='%s' and flight_date='%s' " \
                              "and cabin_id='%s'" % (flight_id, start_date, cabin_level)
                try:
                    cur_user.execute(sql_connect)
                except Exception as e:
                    print(e)
                    flight_id = ""
                    start_date = ""
                    cabin_level = ""
                    QMessageBox.warning(self, '提示', '日期格式输入错误')
                    return None
                if flight_id != "" and start_date != "" and cabin_level != "":
                    num = cur_user.fetchall()
                    if num[0][0] == 0:
                        QMessageBox.information(self, '提示', '抱歉，您选择%s航班（%s）余票不足' % (flight_id, cabin_level))
                    else:
                        # 获取当前订单数量
                        sql_connect = "select count(*) from ticket"
                        cur_user.execute(sql_connect)
                        num = cur_user.fetchall()
                        sql_connect = "select orders_id from Refund"
                        cur_user.execute(sql_connect)
                        orders = cur_user.fetchall()
                        if orders:
                            order_id = orders[0][0]
                            sql_connect = "delete from Refund where orders_id='%s'" % order_id
                            cur_user.execute(sql_connect)
                            conn_user.commit()
                        else:
                            count_str = str(num[0][0]+1).zfill(6)
                            order_id = "order" + count_str
                        # 获取乘客基本信息
                        sql_connect = "select identity_id,name from passenger where account='%s'" % user_message[0]
                        cur_user.execute(sql_connect)
                        passenger_ = cur_user.fetchall()
                        # 获取航班基本信息
                        sql_connect = "select seats,available_seat,price from cabin where " \
                                      "cabin_id='%s' and flight_id='%s' and flight_date='%s'" \
                                      % (cabin_level, flight_id, start_date)
                        cur_user.execute(sql_connect)
                        cabin_ = cur_user.fetchall()
                        # 登机口
                        gate = random.randint(1, 16)
                        # 计算获得座位号
                        seat_num = 1
                        seat_num_ = cabin_[0][0] - cabin_[0][1] + 1
                        sql_connect = "select seat_num from ticket where cabin_level='%s' and flight_id='%s' and " \
                                      "flight_date='%s'" % (cabin_level, flight_id, start_date)
                        cur_user.execute(sql_connect)
                        option_seat_num = cur_user.fetchall()
                        for i in range(1, seat_num_+1):
                            if cabin_level == 'F-头等舱':
                                seat_num = 'F_' + str(i)
                            elif cabin_level == 'C-商务舱':
                                seat_num = 'C_' + str(i)
                            else:
                                seat_num = 'Y_' + str(i)
                            if (seat_num,) not in option_seat_num:
                                break
                        sql_connect = "insert into ticket (orders_id,name,identity_id,flight_id,flight_date,gate," \
                                      "cabin_level,seat_num) values ('%s','%s','%s','%s','%s','%s','%s','%s')" \
                                      % (order_id, passenger_[0][1], passenger_[0][0], flight_id, start_date, gate,
                                         cabin_level, seat_num)
                        cur_user.execute(sql_connect)
                        conn_user.commit()
                        # 修改余票数量
                        available_seat = cabin_[0][1] - 1
                        sql_connect = "update cabin set available_seat='%s' where flight_id='%s' and cabin_id='%s' and " \
                                      "flight_date='%s'" % (available_seat, flight_id, cabin_level, start_date)
                        cur_user.execute(sql_connect)
                        conn_user.commit()
                        conn_user.close()
                        QMessageBox.information(self, '通知', '订票成功！')
                else:
                    self.lineEdit_startday1_2.clear()
                    self.lineEdit_startday1_2.setPlaceholderText("示例格式：2022-12-05")
                    pass
            self.lineEdit_flightid.clear()
            self.lineEdit_startday1_2.clear()
            self.lineEdit_cabin_level.clear()

    # 票务查询
    def order_select(self):
        # 连接数据库
        conn_user = connect_db("passenger")
        cur_user = conn_user.cursor()
        passenger_name = self.lineEdit_passangername.text()
        start_date = self.lineEdit_startday.text()
        identity_id = self.lineEdit_identity_3.text()
        """需要补充功能，不允许查询非本人的机票"""
        sql_connect = "select name, identity_id from passenger where account='%s'" % user_message[0]
        cur_user.execute(sql_connect)
        result = cur_user.fetchall()
        if identity_id != result[0][1] and passenger_name != result[0][0]:
            QMessageBox.information(self, '提示', '请输入正确的个人信息来查询票务')
        else:
            sql_connect = "select count(*) from ticket where identity_id='%s'and flight_date='%s'" % \
                          (identity_id, start_date)
            cur_user.execute(sql_connect)
            num = cur_user.fetchall()
            self.tableWidget.setRowCount(num[0][0])
            sql_connect = "select ticket.flight_id,departure_airport,arrival_airport,departure_time,terminal," \
                          "gate,cabin_level,seat_num,cabin.price from ticket " \
                          "inner join flight on flight.flight_id=ticket.flight_id " \
                          "inner join cabin on cabin.flight_id=ticket.flight_id and cabin.cabin_id=ticket.cabin_level "\
                          "and cabin.flight_date=ticket.flight_date "\
                          "where identity_id='%s' and ticket.flight_date='%s'" % \
                          (identity_id, start_date)
            cur_user.execute(sql_connect)
            rows = cur_user.fetchall()
            count = 0
            for row in rows:
                item1 = QTableWidgetItem(row[0])
                self.tableWidget.setItem(count, 0, item1)
                item2 = QTableWidgetItem(row[1])
                self.tableWidget.setItem(count, 1, item2)
                item3 = QTableWidgetItem(row[2])
                self.tableWidget.setItem(count, 2, item3)
                item4 = QTableWidgetItem(str(row[3]))
                self.tableWidget.setItem(count, 3, item4)
                item5 = QTableWidgetItem(row[4])
                self.tableWidget.setItem(count, 4, item5)
                item6 = QTableWidgetItem(row[5])
                self.tableWidget.setItem(count, 5, item6)
                item7 = QTableWidgetItem(row[6])
                self.tableWidget.setItem(count, 6, item7)
                item8 = QTableWidgetItem(str(row[7]))
                self.tableWidget.setItem(count, 7, item8)
                item9 = QTableWidgetItem(str(row[8]))
                self.tableWidget.setItem(count, 8, item9)
                count += 1

    # 机票退订
    def order_cancel(self):
        # 连接数据库
        conn_user = connect_db("passenger")
        cur_user = conn_user.cursor()
        flight_id = self.lineEdit_flight.text()
        start_date = self.lineEdit_startday1.text()
        cabin_level = self.lineEdit_passanger1.text()
        sql_connect = "select identity_id from passenger where account='%s'" % user_message[0]
        cur_user.execute(sql_connect)
        identity_id = cur_user.fetchall()[0][0]
        if flight_id == '' or start_date == '' or cabin_level == '':
            QMessageBox.information(self, '提示', '未获取到完整信息，无法进行退票，请补充信息！')
        else:
            sql_connect = "select count(*) from ticket where identity_id='%s' and flight_id='%s' and cabin_level='%s' " \
                          "and flight_date='%s'" % (identity_id, flight_id, cabin_level, start_date)
            cur_user.execute(sql_connect)
            num = cur_user.fetchall()[0][0]
            if num == 0:
                QMessageBox.information(self, '提示', '没有该票务信息')
            else:
                sql_connect = "delete from ticket where identity_id='%s' and flight_id='%s' and cabin_level='%s' and " \
                              "flight_date='%s'" % (identity_id, flight_id, cabin_level, start_date)
                cur_user.execute(sql_connect)
                conn_user.commit()
                sql_connect = "select available_seat from cabin where flight_id='%s' and cabin_id='%s' and " \
                              "flight_date='%s'" % (flight_id, cabin_level, start_date)
                cur_user.execute(sql_connect)
                available_seat = cur_user.fetchall()[0][0] + num
                sql_connect = "update cabin set available_seat='%s' where flight_id='%s' and " \
                              "cabin_id='%s' and flight_date='%s'" % (available_seat, flight_id, cabin_level, start_date)
                cur_user.execute(sql_connect)
                conn_user.commit()
                conn_user.close()
                QMessageBox.information(self, '通知', '退票成功！')
            self.lineEdit_flight.clear()
            self.lineEdit_startday1.clear()
            self.lineEdit_passanger1.clear()

    # 显示用户原始信息
    def display_message(self):
        # 连接数据库
        conn_user = connect_db("passenger")
        cur_user = conn_user.cursor()
        sql_connect = "select * from passenger where account='%s'" % user_message[0]
        cur_user.execute(sql_connect)
        result = cur_user.fetchall()
        conn_user.close()
        self.lineEdit_identity.setPlaceholderText(result[0][0])
        self.lineEdit_name.setPlaceholderText(result[0][1])
        self.lineEdit_birth.setPlaceholderText(str(result[0][3])[0:10])
        self.lineEdit_phone.setPlaceholderText(result[0][4])
        self.lineEdit_sex.setPlaceholderText(result[0][2])

    # 用户信息修改
    def user_message_modify(self):
        # 连接数据库
        conn_user = connect_db("passenger")
        cur_user = conn_user.cursor()
        sql_connect = "select * from passenger where account='%s'" % user_message[0]
        cur_user.execute(sql_connect)
        result = cur_user.fetchall()
        orig_identity = result[0][0]
        orig_name = result[0][1]
        # 用户修改信息获取
        name = self.lineEdit_name.text()
        sex = self.lineEdit_sex.text()
        birth = self.lineEdit_birth.text()
        phonenum = self.lineEdit_phone.text()
        identity = self.lineEdit_identity.text()
        if name != '':
            sql_connect = "update passenger set name='%s' where account='%s'" % (name, user_message[0])
            cur_user.execute(sql_connect)
            conn_user.commit()
            sql_connect = "update ticket set name='%s' where name='%s'" % (name, orig_name)
            cur_user.execute(sql_connect)
            conn_user.commit()
        if sex != '':
            sql_connect = "update passenger set gender='%s' where account='%s'" % (sex, user_message[0])
            cur_user.execute(sql_connect)
            conn_user.commit()
        if birth != '':
            sql_connect = "update passenger set birthday='%s' where account='%s'" % (birth, user_message[0])
            cur_user.execute(sql_connect)
            conn_user.commit()
        if phonenum != '':
            sql_connect = "select tel_num from passenger where account!='%s'" % user_message[0]
            cur_user.execute(sql_connect)
            rows = cur_user.fetchall()
            if (phonenum) in rows:
                QMessageBox.warning(self, '警告', '该电话号码已存在，请正确输入电话号码')
            else:
                sql_connect = "update passenger set tel_num='%s' where account='%s'" % (phonenum, user_message[0])
                cur_user.execute(sql_connect)
                conn_user.commit()
        if identity != '':
            sql_connect = "select identity_id from passenger where account!='%s'" % user_message[0]
            cur_user.execute(sql_connect)
            rows = cur_user.fetchall()
            if (identity) in rows:
                QMessageBox.warning(self, '警告', '该身份证号已存在，请正确输入身份证号')
            else:
                sql_connect = "update passenger set identity_id='%s' where account='%s'" % (identity, user_message[0])
                cur_user.execute(sql_connect)
                conn_user.commit()
                sql_connect = "update ticket set identity_id='%s' where identity_id='%s'" % (identity, orig_identity)
                cur_user.execute(sql_connect)
                conn_user.commit()
        if self.lineEdit_password.text() != '' or self.lineEdit_password1.text() != '':
            if self.lineEdit_password.text() != self.lineEdit_password1.text() and \
                    (self.lineEdit_password1.text() != "" and self.lineEdit_password.text() != ""):
                QMessageBox.warning(self, '提醒', '两次密码输入不一致，请重新输入')
                self.lineEdit_password.clear()
                self.lineEdit_password1.clear()
            elif self.lineEdit_password.text() == self.lineEdit_password1.text() != "":
                password = self.lineEdit_password.text()
                sql_connect = "update passenger set password='%s' where account='%s'" % (password, user_message[0])
                cur_user.execute(sql_connect)
                conn_user.commit()
                conn_user.close()
                QMessageBox.information(self, '通知', '用户信息已修改！')
                self.lineEdit_name.clear()
                self.lineEdit_sex.clear()
                self.lineEdit_birth.clear()
                self.lineEdit_phone.clear()
                self.lineEdit_identity.clear()
                self.lineEdit_password.clear()
                self.lineEdit_password1.clear()
        else:
            conn_user.close()
            QMessageBox.information(self, '通知', '用户信息已修改！')
            self.lineEdit_name.clear()
            self.lineEdit_sex.clear()
            self.lineEdit_birth.clear()
            self.lineEdit_phone.clear()
            self.lineEdit_identity.clear()
            self.lineEdit_password.clear()
            self.lineEdit_password1.clear()


# 注册窗口
class RegisterWindow(QtWidgets.QMainWindow, Ui_Register):
    switch_window1 = QtCore.pyqtSignal()  # 跳转信号
    switch_window2 = QtCore.pyqtSignal()  # 跳转信号

    def __init__(self):
        super(RegisterWindow, self).__init__()
        self.setupUi(self)
        self.cancel.clicked.connect(self.Cancel)
        self.register_2.clicked.connect(self.Complete)

    def Cancel(self):
        self.switch_window1.emit()
        self.lineEdit_name.clear()
        self.lineEdit_sex.clear()
        self.lineEdit_birth.clear()
        self.lineEdit_phone.clear()
        self.lineEdit_identity.clear()
        self.lineEdit_username.clear()
        self.lineEdit_password.clear()
        self.lineEdit_password1.clear()

    def Complete(self):
        # 连接数据库
        conn_user = connect_db("passenger")
        cur_user = conn_user.cursor()
        # 读取写入的信息
        name = self.lineEdit_name.text()
        sex = self.lineEdit_sex.text()
        birth = self.lineEdit_birth.text()
        phonenum = self.lineEdit_phone.text()
        identity = self.lineEdit_identity.text()
        username = self.lineEdit_username.text()
        if name == "" or sex == "" or birth == "" or phonenum == "" or identity == "" or \
                username == "" or self.lineEdit_password.text() == "" or self.lineEdit_password1.text() == "":
            QMessageBox.warning(self, '提醒', '请完善您所填写的信息！')
        if self.lineEdit_password.text() != self.lineEdit_password1.text() and \
                (self.lineEdit_password1.text() != "" and self.lineEdit_password.text() != ""):
            QMessageBox.warning(self, '提醒', '两次密码输入不一致，请重新输入')
        elif self.lineEdit_password.text() == self.lineEdit_password1.text() != "":
            password = self.lineEdit_password.text()
            sql_connect = "insert into passenger(identity_id,name,gender,birthday,tel_num,account,password) values " \
                          "('%s','%s','%s','%s','%s','%s','%s')" % (identity, name, sex, birth, phonenum, username, password)
            cur_user.execute(sql_connect)
            conn_user.commit()
            conn_user.close()

            self.switch_window2.emit()
            self.lineEdit_name.clear()
            self.lineEdit_sex.clear()
            self.lineEdit_birth.clear()
            self.lineEdit_phone.clear()
            self.lineEdit_identity.clear()
            self.lineEdit_username.clear()
            self.lineEdit_password.clear()
            self.lineEdit_password1.clear()


# 管理员登录窗口
class AdminLoginWindow(QtWidgets.QMainWindow, Ui_Admin):
    switch_window1 = QtCore.pyqtSignal()  # 跳转信号
    switch_window2 = QtCore.pyqtSignal()  # 跳转信号
    switch_window3 = QtCore.pyqtSignal()  # 跳转信号
    switch_window4 = QtCore.pyqtSignal()  # 跳转信号

    def __init__(self):
        super(AdminLoginWindow, self).__init__()
        self.setupUi(self)
        self.login.clicked.connect(self.adminLogin)
        self.register_.clicked.connect(self.adminRegister)
        self.login_2.clicked.connect(self.companyLogin)
        self.register_1.clicked.connect(self.companyRegister)

    def adminLogin(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        cur_admin.execute("select * from administrator;")
        rows1 = cur_admin.fetchall()
        conn_admin.close()
        username = self.username.text()
        password = self.password.text()
        if password == "":
            QMessageBox.warning(self, '警告', '密码不能为空，请输入！')
            return None
        if (username, password) in rows1:
            self.switch_window1.emit()
            self.username.clear()
            self.password.clear()
        else:
            if password != "":
                QMessageBox.critical(self, '错误', '账号或密码错误！')
                self.password.clear()
                self.username.clear()
                return None

    def adminRegister(self):
        self.switch_window2.emit()

    def companyLogin(self):
        # 连接数据库
        conn_company = connect_db("company")
        cur_company = conn_company.cursor()
        cur_company.execute("select company_id,c_password from company;")
        rows2 = cur_company.fetchall()
        cur_company.close()
        username = self.username_2.text()
        password = self.password_2.text()
        if password == "":
            QMessageBox.warning(self, '警告', '密码不能为空，请输入！')
            return None
        if (username, password) in rows2:
            global company_message
            company_message = [username, password]
            self.switch_window3.emit()
            self.username_2.clear()
            self.password_2.clear()
        else:
            if password != "":
                QMessageBox.critical(self, '错误', '账号或密码错误！')
                self.password_2.clear()
                self.username_2.clear()
                return None

    def companyRegister(self):
        self.switch_window4.emit()


# 管理员控制界面
class AdminManageWindow(QtWidgets.QMainWindow, Ui_Manage):
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        super(AdminManageWindow, self).__init__()
        self.setupUi(self)
        self.display()
        # 设置按键与槽函数连接
        self.pushButton_29.clicked.connect(self.back)
        self.pushButton.clicked.connect(self.flight_message_by_id)
        self.pushButton_2.clicked.connect(self.flight_message_by_company)
        self.flight_modify.clicked.connect(self.flight_modify_)
        self.message_input.clicked.connect(self.add_flight)
        self.insert.clicked.connect(self.add_cabin_F)
        self.insert1.clicked.connect(self.add_cabin_C)
        self.insert2.clicked.connect(self.add_cabin_Y)
        self.delete_flight.clicked.connect(self.flight_cancel1)
        self.delete_banci.clicked.connect(self.flight_cancel2)
        self.pushButton_46.clicked.connect(self.cabin_inquery)
        self.cabin_modify.clicked.connect(self.cabin_modify_)
        self.inquery1.clicked.connect(self.order_by_date)
        self.inquery2.clicked.connect(self.order_by_place)
        self.inquery3.clicked.connect(self.order_by_name)
        self.modify.clicked.connect(self.order_modify)
        self.flight_modify_2.clicked.connect(self.flight_modify_select)

    def display(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        # 初始航班查询界面显示
        cur_admin.execute("select count(*) from flight;")
        num = cur_admin.fetchall()
        self.tableWidget.setRowCount(num[0][0])
        self.tableWidget_3.setRowCount(num[0][0])
        self.tableWidget_4.setRowCount(num[0][0])
        cur_admin.execute(
            "select flight_id,company.company_name,departure_time,departure_city,departure_airport,arrival_city,"
            "arrival_airport,model,terminal from flight,company where flight.company_id=company.company_id;")
        rows = cur_admin.fetchall()
        count = 0
        for row in rows:
            item1 = QTableWidgetItem(row[0])
            item1_ = QTableWidgetItem(row[0])
            item1_1 = QTableWidgetItem(row[0])
            self.tableWidget.setItem(count, 0, item1)
            self.tableWidget_3.setItem(count, 0, item1_)
            self.tableWidget_4.setItem(count, 0, item1_1)
            item2 = QTableWidgetItem(row[1])
            item2_ = QTableWidgetItem(row[1])
            item2_1 = QTableWidgetItem(row[1])
            self.tableWidget.setItem(count, 1, item2)
            self.tableWidget_3.setItem(count, 1, item2_)
            self.tableWidget_4.setItem(count, 1, item2_1)
            item3 = QTableWidgetItem(str(row[2]))
            item3_ = QTableWidgetItem(str(row[2]))
            item3_1 = QTableWidgetItem(str(row[2]))
            self.tableWidget.setItem(count, 2, item3)
            self.tableWidget_3.setItem(count, 2, item3_)
            self.tableWidget_4.setItem(count, 2, item3_1)
            item4 = QTableWidgetItem(row[3])
            item4_ = QTableWidgetItem(row[3])
            item4_1 = QTableWidgetItem(row[3])
            self.tableWidget.setItem(count, 3, item4)
            self.tableWidget_3.setItem(count, 3, item4_)
            self.tableWidget_4.setItem(count, 3, item4_1)
            item5 = QTableWidgetItem(row[4])
            item5_ = QTableWidgetItem(row[4])
            item5_1 = QTableWidgetItem(row[4])
            self.tableWidget.setItem(count, 4, item5)
            self.tableWidget_3.setItem(count, 4, item5_)
            self.tableWidget_4.setItem(count, 4, item5_1)
            item6 = QTableWidgetItem(row[5])
            item6_ = QTableWidgetItem(row[5])
            item6_1 = QTableWidgetItem(row[5])
            self.tableWidget.setItem(count, 5, item6)
            self.tableWidget_3.setItem(count, 5, item6_)
            self.tableWidget_4.setItem(count, 5, item6_1)
            item7 = QTableWidgetItem(row[6])
            item7_ = QTableWidgetItem(row[6])
            item7_1 = QTableWidgetItem(row[6])
            self.tableWidget.setItem(count, 6, item7)
            self.tableWidget_3.setItem(count, 6, item7_)
            self.tableWidget_4.setItem(count, 6, item7_1)
            item8 = QTableWidgetItem(row[7])
            item8_ = QTableWidgetItem(row[7])
            item8_1 = QTableWidgetItem(row[7])
            self.tableWidget.setItem(count, 7, item8)
            self.tableWidget_3.setItem(count, 7, item8_)
            self.tableWidget_4.setItem(count, 7, item8_1)
            item9 = QTableWidgetItem(row[8])
            item9_ = QTableWidgetItem(row[8])
            item9_1 = QTableWidgetItem(row[8])
            self.tableWidget.setItem(count, 8, item9)
            self.tableWidget_3.setItem(count, 8, item9_)
            self.tableWidget_4.setItem(count, 8, item9_1)
            count += 1
        # 订单初始展示
        sql_connect = "select count(*) from ticket;"
        cur_admin.execute(sql_connect)
        num = cur_admin.fetchall()
        self.tableWidget_2.setRowCount(num[0][0])
        sql_connect = "select orders_id,name,ticket.flight_id,departure_airport,arrival_airport,departure_time," \
                      "cabin_level,seat_num,cabin.price from ticket " \
                      "inner join flight on flight.flight_id=ticket.flight_id " \
                      "inner join cabin on cabin.flight_id=ticket.flight_id and cabin.cabin_id=ticket.cabin_level"
        cur_admin.execute(sql_connect)
        rows = cur_admin.fetchall()
        conn_admin.close()
        count = 0
        for row in rows:
            item1 = QTableWidgetItem(row[0])
            self.tableWidget_2.setItem(count, 0, item1)
            item2 = QTableWidgetItem(row[1])
            self.tableWidget_2.setItem(count, 1, item2)
            item3 = QTableWidgetItem(str(row[2]))
            self.tableWidget_2.setItem(count, 2, item3)
            item4 = QTableWidgetItem(row[3])
            self.tableWidget_2.setItem(count, 3, item4)
            item5 = QTableWidgetItem(row[4])
            self.tableWidget_2.setItem(count, 4, item5)
            item6 = QTableWidgetItem(str(row[5]))
            self.tableWidget_2.setItem(count, 5, item6)
            item7 = QTableWidgetItem(row[6])
            self.tableWidget_2.setItem(count, 6, item7)
            item8 = QTableWidgetItem(str(row[7]))
            self.tableWidget_2.setItem(count, 7, item8)
            item9 = QTableWidgetItem(str(row[8]))
            self.tableWidget_2.setItem(count, 8, item9)
            count += 1

    def back(self):
        self.switch_window.emit()

    # 航班信息查看_根据航班编号
    def flight_message_by_id(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        flight_id = self.lineEdit_flightid.text()
        if flight_id != '':
            sql_connect = "select count(*) from flight where flight_id like '%s%%';" % flight_id
            cur_admin.execute(sql_connect)
            num = cur_admin.fetchall()
            self.tableWidget.setRowCount(num[0][0])
            sql_connect = "select flight_id,company.company_name,departure_time,departure_city,departure_airport," \
                          "arrival_city,arrival_airport,model,terminal from flight,company where " \
                          "flight.company_id=company.company_id and flight_id like '%s%%'" % flight_id
        else:
            sql_connect = "select count(*) from flight;"
            cur_admin.execute(sql_connect)
            num = cur_admin.fetchall()
            self.tableWidget.setRowCount(num[0][0])
            sql_connect = "select flight_id,company.company_name,departure_time,departure_city,departure_airport," \
                          "arrival_city,arrival_airport,model,terminal from flight,company " \
                          "where flight.company_id=company.company_id;"
        cur_admin.execute(sql_connect)
        rows = cur_admin.fetchall()
        conn_admin.close()
        count = 0
        for row in rows:
            item1 = QTableWidgetItem(row[0])
            self.tableWidget.setItem(count, 0, item1)
            item2 = QTableWidgetItem(row[1])
            self.tableWidget.setItem(count, 1, item2)
            item3 = QTableWidgetItem(str(row[2]))
            self.tableWidget.setItem(count, 2, item3)
            item4 = QTableWidgetItem(row[3])
            self.tableWidget.setItem(count, 3, item4)
            item5 = QTableWidgetItem(row[4])
            self.tableWidget.setItem(count, 4, item5)
            item6 = QTableWidgetItem(row[5])
            self.tableWidget.setItem(count, 5, item6)
            item7 = QTableWidgetItem(row[6])
            self.tableWidget.setItem(count, 6, item7)
            item8 = QTableWidgetItem(row[7])
            self.tableWidget.setItem(count, 7, item8)
            item9 = QTableWidgetItem(row[8])
            self.tableWidget.setItem(count, 8, item9)
            count += 1

    # 航班信息查看_根据航空公司
    def flight_message_by_company(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        air_company = self.lineEdit_aircompany.text()
        if air_company != '':
            sql_connect = "select count(*) from flight,company where flight.company_id=company.company_id and " \
                          "company.company_name='%s';" % air_company
            cur_admin.execute(sql_connect)
            num = cur_admin.fetchall()
            self.tableWidget.setRowCount(num[0][0])
            sql_connect = "select flight_id,company.company_name,departure_time,departure_city,departure_airport," \
                          "arrival_city,arrival_airport,model,terminal from flight,company where " \
                          "flight.company_id=company.company_id and company.company_name='%s';" % air_company
        else:
            sql_connect = "select count(*) from flight,company where flight.company_id=company.company_id;"
            cur_admin.execute(sql_connect)
            num = cur_admin.fetchall()
            self.tableWidget.setRowCount(num[0][0])
            sql_connect = "select flight_id,company.company_name,departure_time,departure_city,departure_airport," \
                          "arrival_city,arrival_airport,model,terminal from flight,company " \
                          "where flight.company_id=company.company_id;"
        cur_admin.execute(sql_connect)
        rows = cur_admin.fetchall()
        conn_admin.close()
        count = 0
        for row in rows:
            item1 = QTableWidgetItem(row[0])
            self.tableWidget.setItem(count, 0, item1)
            item2 = QTableWidgetItem(row[1])
            self.tableWidget.setItem(count, 1, item2)
            item3 = QTableWidgetItem(str(row[2]))
            self.tableWidget.setItem(count, 2, item3)
            item4 = QTableWidgetItem(row[3])
            self.tableWidget.setItem(count, 3, item4)
            item5 = QTableWidgetItem(row[4])
            self.tableWidget.setItem(count, 4, item5)
            item6 = QTableWidgetItem(row[5])
            self.tableWidget.setItem(count, 5, item6)
            item7 = QTableWidgetItem(row[6])
            self.tableWidget.setItem(count, 6, item7)
            item8 = QTableWidgetItem(row[7])
            self.tableWidget.setItem(count, 7, item8)
            item9 = QTableWidgetItem(row[8])
            self.tableWidget.setItem(count, 8, item9)
            count += 1

    def flight_modify_select(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        flight_id = self.lineEdit_flightid_2.text()
        sql_connect = "select count(*) from flight where flight_id='%s';" % flight_id
        cur_admin.execute(sql_connect)
        num = cur_admin.fetchall()
        self.tableWidget_3.setRowCount(num[0][0])
        if flight_id != '':
            sql_connect = "select count(*) from flight where flight_id like '%s%%';" % flight_id
            cur_admin.execute(sql_connect)
            num = cur_admin.fetchall()
            self.tableWidget_3.setRowCount(num[0][0])
            sql_connect = "select flight_id,company.company_name,departure_time,departure_city,departure_airport," \
                          "arrival_city,arrival_airport,model,terminal from flight,company " \
                          "where flight.company_id=company.company_id and flight_id like '%s%%';" % flight_id
        else:
            sql_connect = "select count(*) from flight"
            cur_admin.execute(sql_connect)
            num = cur_admin.fetchall()
            self.tableWidget_3.setRowCount(num[0][0])
            sql_connect = "select flight_id,company.company_name,departure_time,departure_city,departure_airport," \
                          "arrival_city,arrival_airport,model,terminal from flight,company " \
                          "where flight.company_id=company.company_id;"
        cur_admin.execute(sql_connect)
        rows = cur_admin.fetchall()
        conn_admin.close()
        count = 0
        for row in rows:
            item1 = QTableWidgetItem(row[0])
            self.tableWidget_3.setItem(count, 0, item1)
            item2 = QTableWidgetItem(row[1])
            self.tableWidget_3.setItem(count, 1, item2)
            item3 = QTableWidgetItem(str(row[2]))
            self.tableWidget_3.setItem(count, 2, item3)
            item4 = QTableWidgetItem(row[3])
            self.tableWidget_3.setItem(count, 3, item4)
            item5 = QTableWidgetItem(row[4])
            self.tableWidget_3.setItem(count, 4, item5)
            item6 = QTableWidgetItem(row[5])
            self.tableWidget_3.setItem(count, 5, item6)
            item7 = QTableWidgetItem(row[6])
            self.tableWidget_3.setItem(count, 6, item7)
            item8 = QTableWidgetItem(row[7])
            self.tableWidget_3.setItem(count, 7, item8)
            item9 = QTableWidgetItem(row[8])
            self.tableWidget_3.setItem(count, 8, item9)
            count += 1

    # 航班信息修改
    def flight_modify_(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        flight_id = self.lineEdit_flightid_2.text()
        air_company = self.lineEdit_aircompany1.text()
        depart_time = self.lineEdit_departtime.text()
        depart_city = self.lineEdit_departcity.text()
        depart_airport = self.lineEdit_departairport.text()
        arrive_city = self.lineEdit_arrivecity.text()
        arrive_airport = self.lineEdit_arriveairport.text()
        model = self.lineEdit_planemodel.text()
        terminal = self.lineEdit_terminal.text()
        if air_company != '':
            sql_connect = "select count(*) from company where company_name='%s'" % air_company
            cur_admin.execute(sql_connect)
            num = cur_admin.fetchall()[0][0]
            if num == 0:
                QMessageBox.warning(self, '警告', '系统中不存在该航空公司')
                self.lineEdit_aircompany1.clear()
                return None
            else:
                sql_connect = "select company_id from company where company_name='%s'" % air_company
                cur_admin.execute(sql_connect)
                company_id = cur_admin.fetchall()[0][0]
                sql_connect = "update flight set company_id='%s' where flight_id='%s'" % (company_id, flight_id)
                cur_admin.execute(sql_connect)
                conn_admin.commit()
        if depart_time != '':
            sql_connect = "update flight set departure_time='%s' where flight_id='%s'" % (depart_time, flight_id)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
        if depart_city != '':
            sql_connect = "update flight set departure_city='%s' where flight_id='%s'" % (depart_city, flight_id)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
        if depart_airport != '':
            sql_connect = "update flight set departure_airport='%s' where flight_id='%s'" % (depart_airport, flight_id)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
        if arrive_city != '':
            sql_connect = "update flight set arrival_city='%s' where flight_id='%s'" % (arrive_city, flight_id)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
        if arrive_airport != '':
            sql_connect = "update flight set arrival_airport='%s' where flight_id='%s'" % (arrive_airport, flight_id)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
        if model != '':
            sql_connect = "update flight set model='%s' where flight_id='%s'" % (model, flight_id)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
        if terminal != '':
            sql_connect = "update flight set terminal='%s' where flight_id='%s'" % (terminal, flight_id)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
        if air_company or depart_time or depart_city or depart_airport or arrive_city or arrive_airport or model or terminal:
            QMessageBox.information(self, '通知', '航班信息已修改！')
        conn_admin.close()

    # 增加航班
    def add_flight(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        flight_id = self.lineEdit_flightid2.text()
        air_company = self.lineEdit_aircompany2.text()
        depart_time = self.lineEdit_departtime1.text()
        depart_city = self.lineEdit_departcity_2.text()
        depart_airport = self.lineEdit_departairport_2.text()
        arrive_city = self.lineEdit_arrivecity1.text()
        arrive_airport = self.lineEdit_arriveairport1.text()
        model = self.lineEdit_planemodel1.text()
        terminal = self.lineEdit_terminal1.text()
        if flight_id == '' or air_company == '' or depart_time == '' or depart_city == '' or depart_airport == '' or \
                arrive_city == '' or arrive_airport == '' or model == '':
            QMessageBox.information(self, '提示', '除航站楼信息外，其余为必填项')
        else:
            sql_connect = "select flight_id from flight"
            cur_admin.execute(sql_connect)
            flight_ids = cur_admin.fetchall()
            if (flight_id) in flight_ids:
                QMessageBox.information(self, '提示', '该航班已存在')
            else:
                sql_connect = "select company_id from company where company_name='%s'" % air_company
                cur_admin.execute(sql_connect)
                company_id = cur_admin.fetchall()[0][0]
                if company_id == None:
                    QMessageBox.information(self, '提示', '系统中没有注册该航空公司')
                    return None
                else:
                    sql_connect = "insert into flight (flight_id,company_id,departure_time,departure_city," \
                                  "departure_airport,arrival_city,arrival_airport,model,terminal) values " \
                                  "('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (flight_id, company_id,
                                                                                      depart_time, depart_city,
                                                                                      depart_airport, arrive_city,
                                                                                      arrive_airport, model,
                                                                                      terminal)
                    cur_admin.execute(sql_connect)
                    conn_admin.commit()
                    conn_admin.close()
                    QMessageBox.information(self, '通知', '航班添加成功')
            self.lineEdit_flightid2.clear()
            self.lineEdit_aircompany2.clear()
            self.lineEdit_departtime1.clear()
            self.lineEdit_departcity_2.clear()
            self.lineEdit_departairport_2.clear()
            self.lineEdit_arrivecity1.clear()
            self.lineEdit_arriveairport1.clear()
            self.lineEdit_planemodel1.clear()
            self.lineEdit_terminal1.clear()

    # 增加舱位_F舱
    def add_cabin_F(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        flight_id = self.lineEdit_flightid3.text()
        F_seats = self.lineEdit_seats.text()
        F_date = self.lineEdit_departdate.text()
        F_price = self.lineEdit_price.text()
        cabin_id = 'F-头等舱'
        sql_connect = "select count(*) from cabin where flight_id='%s' and cabin_id='%s' and flight_date='%s'" % \
                      (flight_id, cabin_id, F_date)
        cur_admin.execute(sql_connect)
        num = cur_admin.fetchall()[0][0]
        if num != 0:
            QMessageBox.information(self, '提示', '该班次对应的舱位已经存在，如需修改请使用修改功能')
        else:
            sql_connect = "insert into cabin (cabin_id,flight_id,seats,available_seat,price,flight_date) values " \
                          "('%s','%s','%s','%s','%s','%s')" % (cabin_id, flight_id, F_seats, F_seats, F_price, F_date)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
            conn_admin.close()
            QMessageBox.information(self, '通知', '添加成功')

    # 增加舱位_C舱
    def add_cabin_C(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        flight_id = self.lineEdit_flightid3.text()
        C_seats = self.lineEdit_seat1.text()
        C_date = self.lineEdit_departdate1.text()
        C_price = self.lineEdit_price1.text()
        cabin_id = 'C-商务舱'
        sql_connect = "select count(*) from cabin where flight_id='%s' and cabin_id='%s' and flight_date='%s'" % \
                      (flight_id, cabin_id, C_date)
        cur_admin.execute(sql_connect)
        num = cur_admin.fetchall()[0][0]
        if num != 0:
            QMessageBox.information(self, '提示', '该班次对应的舱位已经存在，如需修改请使用修改功能')
        else:
            sql_connect = "insert into cabin (cabin_id,flight_id,seats,available_seat,price,flight_date) values " \
                          "('%s','%s','%s','%s','%s','%s')" % (cabin_id, flight_id, C_seats, C_seats, C_price, C_date)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
            conn_admin.close()
            QMessageBox.information(self, '通知', '添加成功')

    # 增加舱位_Y舱
    def add_cabin_Y(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        flight_id = self.lineEdit_flightid3.text()
        Y_seats = self.lineEdit_seat2.text()
        Y_date = self.lineEdit_departdate2.text()
        Y_price = self.lineEdit_price2.text()
        cabin_id = 'Y-经济舱'
        sql_connect = "select count(*) from cabin where flight_id='%s' and cabin_id='%s' and flight_date='%s'" % \
                      (flight_id, cabin_id, Y_date)
        cur_admin.execute(sql_connect)
        num = cur_admin.fetchall()[0][0]
        if num != 0:
            QMessageBox.information(self, '提示', '该班次对应的舱位已经存在，如需修改请使用修改功能')
        else:
            sql_connect = "insert into cabin (cabin_id,flight_id,seats,available_seat,price,flight_date) values " \
                          "('%s','%s','%s','%s','%s','%s')" % (cabin_id, flight_id, Y_seats, Y_seats, Y_price, Y_date)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
            conn_admin.close()
            QMessageBox.information(self, '通知', '添加成功')

    # 航班管理（取消航班）
    """注意！航班取消后对应的舱位也要取消"""
    def flight_cancel1(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        flight_id_1 = self.lineEdit_flightid4.text()
        sql_connect = "select count(*) from flight where flight_id='%s'" % flight_id_1
        cur_admin.execute(sql_connect)
        num = cur_admin.fetchall()[0][0]
        if num == 0:
            QMessageBox.information(self, '提示', '不存在该航班信息')
        else:
            sql_connect = "delete from cabin where flight_id='%s'" % flight_id_1
            cur_admin.execute(sql_connect)
            conn_admin.commit()
            sql_connect = "delete from flight where flight_id='%s'" % flight_id_1
            cur_admin.execute(sql_connect)
            conn_admin.commit()
            conn_admin.close()
            QMessageBox.information(self, '提示', '航班信息已删除')
            self.display()

    # 航班管理（取消班次）
    """注意！班次取消后对应的日期的舱位也要取消"""
    def flight_cancel2(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        flight_id_2 = self.lineEdit_flightid5.text()
        depart_date = self.lineEdit_departdate3.text()
        sql_connect = "select count(*) from cabin where flight_id='%s' and flight_date='%s'" % (flight_id_2, depart_date)
        cur_admin.execute(sql_connect)
        num = cur_admin.fetchall()[0][0]
        if num == 0:
            QMessageBox.information(self, '提示', '不存在该班次信息')
        else:
            sql_connect = "delete from cabin where flight_id='%s' and flight_date='%s'" % (flight_id_2, depart_date)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
            conn_admin.close()
            QMessageBox.information(self, '提示', '班次信息已删除')

    # 航班舱位查询
    def cabin_inquery(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        flight_id = self.lineEdit_flightid6.text()
        depart_date = self.lineEdit_departdate5.text()
        sql_connect = "select cabin_id,seats,available_seat,price from cabin where flight_id='%s' and flight_date='%s'" \
                      % (flight_id, depart_date)
        cur_admin.execute(sql_connect)
        rows = cur_admin.fetchall()
        conn_admin.close()
        for row in rows:
            if row[0] == 'F-头等舱':
                item1 = QTableWidgetItem(str(row[1]))
                self.tableWidget_10.setItem(0, 0, item1)
                item2 = QTableWidgetItem(str(row[2]))
                self.tableWidget_10.setItem(0, 1, item2)
                item3 = QTableWidgetItem(str(row[3]))
                self.tableWidget_10.setItem(0, 2, item3)
            elif row[0] == 'C-商务舱':
                item1 = QTableWidgetItem(str(row[1]))
                self.tableWidget_10.setItem(1, 0, item1)
                item2 = QTableWidgetItem(str(row[2]))
                self.tableWidget_10.setItem(1, 1, item2)
                item3 = QTableWidgetItem(str(row[3]))
                self.tableWidget_10.setItem(1, 2, item3)
            else:
                item1 = QTableWidgetItem(str(row[1]))
                self.tableWidget_10.setItem(2, 0, item1)
                item2 = QTableWidgetItem(str(row[2]))
                self.tableWidget_10.setItem(2, 1, item2)
                item3 = QTableWidgetItem(str(row[3]))
                self.tableWidget_10.setItem(2, 2, item3)

    # 舱位修改
    def cabin_modify_(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        flight_id = self.lineEdit_departdate4_2.text()
        orig_depart = self.lineEdit_departdate4_3.text()
        cabin_num = self.lineEdit_cabinid.text()
        seats = self.lineEdit_seats3.text()
        price = self.lineEdit_price3.text()
        sql_connect = "select count(*) from cabin where flight_id='%s' and cabin_id='%s' and flight_date='%s'" % \
                      (flight_id, cabin_num, orig_depart)
        cur_admin.execute(sql_connect)
        num = cur_admin.fetchall()[0][0]
        if num == 0:
            QMessageBox.information(self, '提示', '不存在对应班次的该舱位')
        else:
            if seats != '':
                sql_connect = "select seats,available_seat from cabin where flight_id='%s' and cabin_id='%s' and " \
                              "flight_date='%s'" % (flight_id, cabin_num, orig_depart)
                cur_admin.execute(sql_connect)
                result = cur_admin.fetchall()
                orig_seats, available_seat = result[0][0], result[0][1]
                new_available_seat = int(seats) - orig_seats + available_seat
                if new_available_seat < 0:
                    new_available_seat = 0
                sql_connect = "update cabin set seats='%s',available_seat='%s' where flight_id='%s' and cabin_id='%s' "\
                              "and flight_date='%s'" % (seats, new_available_seat, flight_id, cabin_num, orig_depart)
                cur_admin.execute(sql_connect)
                conn_admin.commit()
                self.lineEdit_seats3.clear()
            if price != '':
                sql_connect = "update cabin set price='%s' where flight_id='%s' and cabin_id='%s' and flight_date='%s'"\
                              % (price, flight_id, cabin_num, orig_depart)
                cur_admin.execute(sql_connect)
                conn_admin.commit()
                self.lineEdit_price3.clear()
            QMessageBox.information(self, '通知', '舱位信息修改成功！')
            conn_admin.close()

    # 订单管理-根据出发日期查询
    def order_by_date(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        depart_date = self.lineEdit_date.text()
        if depart_date == '':
            self.display()
        else:
            sql_connect = "select count(*) from ticket where flight_date='%s';" % depart_date
            cur_admin.execute(sql_connect)
            num = cur_admin.fetchall()
            self.tableWidget_2.setRowCount(num[0][0])
            sql_connect = "select orders_id,name,ticket.flight_id,departure_airport,arrival_airport,departure_time," \
                          "cabin_level,seat_num,cabin.price from ticket " \
                          "inner join flight on flight.flight_id=ticket.flight_id " \
                          "inner join cabin on cabin.flight_id=ticket.flight_id and cabin.cabin_id=ticket.cabin_level " \
                          "where ticket.flight_date='%s'" % depart_date
            cur_admin.execute(sql_connect)
            rows = cur_admin.fetchall()
            conn_admin.close()
            count = 0
            for row in rows:
                item1 = QTableWidgetItem(row[0])
                self.tableWidget_2.setItem(count, 0, item1)
                item2 = QTableWidgetItem(row[1])
                self.tableWidget_2.setItem(count, 1, item2)
                item3 = QTableWidgetItem(str(row[2]))
                self.tableWidget_2.setItem(count, 2, item3)
                item4 = QTableWidgetItem(row[3])
                self.tableWidget_2.setItem(count, 3, item4)
                item5 = QTableWidgetItem(row[4])
                self.tableWidget_2.setItem(count, 4, item5)
                item6 = QTableWidgetItem(str(row[5]))
                self.tableWidget_2.setItem(count, 5, item6)
                item7 = QTableWidgetItem(row[6])
                self.tableWidget_2.setItem(count, 6, item7)
                item8 = QTableWidgetItem(str(row[7]))
                self.tableWidget_2.setItem(count, 7, item8)
                item9 = QTableWidgetItem(str(row[8]))
                self.tableWidget_2.setItem(count, 8, item9)
                count += 1

    # 订单管理-根据始发地查询
    def order_by_place(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        depart_place = self.lineEdit_depart.text()
        if depart_place == '':
            self.display()
        else:
            sql_connect = "select count(*) from flight,ticket where flight.flight_id=ticket.flight_id and " \
                          "departure_city='%s';" % depart_place
            cur_admin.execute(sql_connect)
            num = cur_admin.fetchall()
            self.tableWidget_2.setRowCount(num[0][0])
            sql_connect = "select orders_id,name,ticket.flight_id,departure_airport,arrival_airport,departure_time," \
                          "cabin_level,seat_num,cabin.price from ticket " \
                          "inner join flight on flight.flight_id=ticket.flight_id " \
                          "inner join cabin on cabin.flight_id=ticket.flight_id and cabin.cabin_id=ticket.cabin_level " \
                          "where departure_city='%s'" % depart_place
            cur_admin.execute(sql_connect)
            rows = cur_admin.fetchall()
            conn_admin.close()
            count = 0
            for row in rows:
                item1 = QTableWidgetItem(row[0])
                self.tableWidget_2.setItem(count, 0, item1)
                item2 = QTableWidgetItem(row[1])
                self.tableWidget_2.setItem(count, 1, item2)
                item3 = QTableWidgetItem(str(row[2]))
                self.tableWidget_2.setItem(count, 2, item3)
                item4 = QTableWidgetItem(row[3])
                self.tableWidget_2.setItem(count, 3, item4)
                item5 = QTableWidgetItem(row[4])
                self.tableWidget_2.setItem(count, 4, item5)
                item6 = QTableWidgetItem(str(row[5]))
                self.tableWidget_2.setItem(count, 5, item6)
                item7 = QTableWidgetItem(row[6])
                self.tableWidget_2.setItem(count, 6, item7)
                item8 = QTableWidgetItem(str(row[7]))
                self.tableWidget_2.setItem(count, 7, item8)
                item9 = QTableWidgetItem(str(row[8]))
                self.tableWidget_2.setItem(count, 8, item9)
                count += 1

    # 订单管理-根据乘客姓名查询
    def order_by_name(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        passenger_name = self.lineEdit_passengername.text()
        if passenger_name == '':
            self.display()
        else:
            sql_connect = "select count(*) from ticket where name='%s';" % passenger_name
            cur_admin.execute(sql_connect)
            num = cur_admin.fetchall()
            self.tableWidget_2.setRowCount(num[0][0])
            sql_connect = "select orders_id,name,ticket.flight_id,departure_airport,arrival_airport,departure_time," \
                          "cabin_level,seat_num,cabin.price from ticket " \
                          "inner join flight on flight.flight_id=ticket.flight_id " \
                          "inner join cabin on cabin.flight_id=ticket.flight_id and cabin.cabin_id=ticket.cabin_level " \
                          "where name='%s'" % passenger_name
            cur_admin.execute(sql_connect)
            rows = cur_admin.fetchall()
            conn_admin.close()
            count = 0
            for row in rows:
                item1 = QTableWidgetItem(row[0])
                self.tableWidget_2.setItem(count, 0, item1)
                item2 = QTableWidgetItem(row[1])
                self.tableWidget_2.setItem(count, 1, item2)
                item3 = QTableWidgetItem(str(row[2]))
                self.tableWidget_2.setItem(count, 2, item3)
                item4 = QTableWidgetItem(row[3])
                self.tableWidget_2.setItem(count, 3, item4)
                item5 = QTableWidgetItem(row[4])
                self.tableWidget_2.setItem(count, 4, item5)
                item6 = QTableWidgetItem(str(row[5]))
                self.tableWidget_2.setItem(count, 5, item6)
                item7 = QTableWidgetItem(row[6])
                self.tableWidget_2.setItem(count, 6, item7)
                item8 = QTableWidgetItem(str(row[7]))
                self.tableWidget_2.setItem(count, 7, item8)
                item9 = QTableWidgetItem(str(row[8]))
                self.tableWidget_2.setItem(count, 8, item9)
                count += 1

    # 订单管理-升舱
    def order_modify(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        order_id = self.lineEdit_flight.text()
        cabin_level = self.lineEdit_cabin_level.text()
        if order_id == '' or cabin_level == '':
            QMessageBox.information(self, '提示', '请输入完整信息，否则无法准确定位修改！')
        else:
            sql_connect = "select cabin_level,flight_id,flight_date from ticket where orders_id='%s'" % order_id
            cur_admin.execute(sql_connect)
            result = cur_admin.fetchall()
            # 修改班次对应原舱位的余票数量
            sql_connect = "select available_seat from cabin where cabin_id='%s' and flight_id='%s' " \
                          "and flight_date='%s'" % (result[0][0], result[0][1], result[0][2])
            cur_admin.execute(sql_connect)
            available_seat = cur_admin.fetchall()[0][0] + 1
            sql_connect = "update cabin set available_seat='%s' where cabin_id='%s' and flight_id='%s' and " \
                          "flight_date='%s'" % (available_seat, result[0][0], result[0][1], result[0][2])
            cur_admin.execute(sql_connect)
            conn_admin.commit()
            # 修改现舱位对应余票数量
            sql_connect = "select seats, available_seat from cabin where cabin_id='%s' and flight_id='%s' " \
                          "and flight_date='%s'" % (cabin_level, result[0][1], result[0][2])
            cur_admin.execute(sql_connect)
            seat = cur_admin.fetchall()
            seats, available_seat = seat[0][0], seat[0][1]
            # 计算获得座位号
            seat_num = 1
            seat_num_ = seats - available_seat + 1
            sql_connect = "select seat_num from ticket where cabin_level='%s' and flight_id='%s' and " \
                          "flight_date='%s'" % (cabin_level, result[0][1], result[0][2])
            cur_admin.execute(sql_connect)
            option_seat_num = cur_admin.fetchall()
            for i in range(1, seat_num_ + 1):
                if cabin_level == 'F-头等舱':
                    seat_num = 'F_' + str(i)
                elif cabin_level == 'C-商务舱':
                    seat_num = 'C_' + str(i)
                else:
                    seat_num = 'Y_' + str(i)
                if (seat_num,) not in option_seat_num:
                    break
            available_seat -= 1
            sql_connect = "update cabin set available_seat='%s' where cabin_id='%s' and flight_id='%s' and " \
                          "flight_date='%s'" % (available_seat, cabin_level, result[0][1], result[0][2])
            cur_admin.execute(sql_connect)
            conn_admin.commit()
            # 修改订单信息
            sql_connect = "update ticket set cabin_level='%s',seat_num='%s' where orders_id='%s'" % \
                          (cabin_level, seat_num, order_id)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
            conn_admin.close()
            QMessageBox.information(self, '通知', '修改成功')
            self.lineEdit_passengername.clear()
            self.lineEdit_flight.clear()
            self.lineEdit_cabin_level.clear()


# 管理员注册界面
class AdminRegisterWindow(QtWidgets.QMainWindow, Ui_admin_register):
    switch_window1 = QtCore.pyqtSignal()  # 跳转信号
    switch_window2 = QtCore.pyqtSignal()  # 跳转信号

    def __init__(self):
        super(AdminRegisterWindow, self).__init__()
        self.setupUi(self)
        self.register_2.clicked.connect(self.Complete)
        self.cancel.clicked.connect(self.Cancel)

    def Cancel(self):
        self.switch_window1.emit()
        self.lineEdit_num.clear()
        self.lineEdit_password.clear()
        self.lineEdit_password1.clear()

    def Complete(self):
        # 连接数据库
        conn_admin = connect_db("admin")
        cur_admin = conn_admin.cursor()
        # 读取写入的信息
        worknum = self.lineEdit_num.text()
        if worknum == "" or self.lineEdit_password.text() == "" or self.lineEdit_password1.text() == "":
            QMessageBox.warning(self, '提醒', '请完善您所填写的信息！')
        if self.lineEdit_password.text() != self.lineEdit_password1.text() and \
                (self.lineEdit_password.text() != "" and self.lineEdit_password1.text() != ""):
            QMessageBox.warning(self, '提醒', '两次密码输入不一致，请重新输入')
        elif self.lineEdit_password.text() == self.lineEdit_password1.text() != "":
            password = self.lineEdit_password.text()
            # sql insert操作
            sql_connect = "insert into administrator (admin_id,admin_password) values ('%s','%');" % (worknum, password)
            cur_admin.execute(sql_connect)
            conn_admin.commit()
            conn_admin.close()

            self.switch_window2.emit()


# 公司注册界面
class CompanyRegisterWindow(QtWidgets.QMainWindow, Ui_company_register):
    switch_window1 = QtCore.pyqtSignal()  # 跳转信号
    switch_window2 = QtCore.pyqtSignal()  # 跳转信号

    def __init__(self):
        super(CompanyRegisterWindow, self).__init__()
        self.setupUi(self)
        self.register_2.clicked.connect(self.Complete)
        self.cancel.clicked.connect(self.Cancel)

    def Cancel(self):
        self.switch_window1.emit()
        self.lineEdit_name.clear()
        self.lineEdit_num.clear()
        self.lineEdit_hotline.clear()
        self.lineEdit_password.clear()
        self.lineEdit_password1.clear()

    def Complete(self):
        # 连接数据库
        conn_company = connect_db("company")
        cur_company = conn_company.cursor()
        # 读取写入的信息
        company_id = self.lineEdit_num.text()
        name = self.lineEdit_name.text()
        hotline = self.lineEdit_hotline.text()
        if company_id == "" or name == "" or hotline == "" or \
                self.lineEdit_password.text() == "" or self.lineEdit_password1.text() == "":
            QMessageBox.warning(self, '提醒', '请完善您所填写的信息！')
        if self.lineEdit_password.text() == self.lineEdit_password1.text() != "":
            password = self.lineEdit_password.text()
            # sql insert操作
            sql_connect = "insert into company (company_id,company_name,hotline,c_password) " \
                          "values ('%s','%s','%s','%s')" % (company_id, name, hotline, password)
            cur_company.execute(sql_connect)
            conn_company.commit()
            conn_company.close()
            QMessageBox.information(self, '通知', '信息录入成功')

            self.switch_window2.emit()
            self.lineEdit_name.clear()
            self.lineEdit_num.clear()
            self.lineEdit_hotline.clear()
            self.lineEdit_password.clear()
            self.lineEdit_password1.clear()
        elif self.lineEdit_password.text() != self.lineEdit_password1.text() and \
                (self.lineEdit_password.text() != "" and self.lineEdit_password1.text() != ""):
            QMessageBox.warning(self, '提醒', '两次密码输入不一致，请重新输入')


# 公司控制界面
class CompanyManageWindow(QtWidgets.QMainWindow, Ui_company):
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        super(CompanyManageWindow, self).__init__()
        self.setupUi(self)
        self.return_2.clicked.connect(self.back)
        self.display_.clicked.connect(self.display)
        self.message.clicked.connect(self.display_message)
        self.modify.clicked.connect(self.modify_)

    def display(self):
        # 连接数据库
        conn_company = connect_db("company")
        cur_company = conn_company.cursor()
        sql_connect = "select count(*) from flight where company_id='%s'" % company_message[0]
        cur_company.execute(sql_connect)
        num = cur_company.fetchall()[0][0]
        self.tableWidget.setRowCount(num)
        sql_connect = "select * from flight where company_id='%s'" % company_message[0]
        cur_company.execute(sql_connect)
        rows = cur_company.fetchall()
        conn_company.close()
        count = 0
        for row in rows:
            item1 = QTableWidgetItem(row[0])
            self.tableWidget.setItem(count, 0, item1)
            item2 = QTableWidgetItem(str(row[2]))
            self.tableWidget.setItem(count, 1, item2)
            item3 = QTableWidgetItem(row[3])
            self.tableWidget.setItem(count, 2, item3)
            item4 = QTableWidgetItem(row[4])
            self.tableWidget.setItem(count, 3, item4)
            item5 = QTableWidgetItem(row[5])
            self.tableWidget.setItem(count, 4, item5)
            item6 = QTableWidgetItem(row[6])
            self.tableWidget.setItem(count, 5, item6)
            item7 = QTableWidgetItem(row[7])
            self.tableWidget.setItem(count, 6, item7)
            item8 = QTableWidgetItem(row[8])
            self.tableWidget.setItem(count, 7, item8)
            count += 1

    def back(self):
        self.switch_window.emit()

    # 显示用户原始信息
    def display_message(self):
        # 连接数据库
        conn_company = connect_db("company")
        cur_company = conn_company.cursor()
        sql_connect = "select * from company where company_id='%s'" % company_message[0]
        cur_company.execute(sql_connect)
        result = cur_company.fetchall()
        conn_company.close()
        self.lineEdit_name.setPlaceholderText(result[0][1])
        self.lineEdit_hotline.setPlaceholderText(result[0][2])

    def modify_(self):
        # 连接数据库
        conn_company = connect_db("company")
        cur_company = conn_company.cursor()
        name = self.lineEdit_name.text()
        hotline = self.lineEdit_hotline.text()
        if name != '':
            sql_connect = "update company set company_name='%s' where company_id='%s'" % (name, company_message[0])
            cur_company.execute(sql_connect)
            conn_company.commit()
        if hotline != '':
            sql_connect = "update company set hotline='%s' where company_id='%s'" % (hotline, company_message[0])
            cur_company.execute(sql_connect)
            conn_company.commit()
        if self.lineEdit_password.text() != '' or self.lineEdit_password2.text() != '':
            if self.lineEdit_password.text() != self.lineEdit_password2.text() and \
                    (self.lineEdit_password2.text() != "" and self.lineEdit_password.text() != ""):
                QMessageBox.warning(self, '提醒', '两次密码输入不一致，请重新输入')
                self.lineEdit_password.clear()
                self.lineEdit_password2.clear()
            elif self.lineEdit_password.text() == self.lineEdit_password2.text() != "":
                password = self.lineEdit_password.text()
                sql_connect = "update company set c_password='%s' where company_id='%s'" % (password, company_message[0])
                cur_company.execute(sql_connect)
                conn_company.commit()
                conn_company.close()
                QMessageBox.information(self, '通知', '航空公司信息已修改！')
                self.lineEdit_name.clear()
                self.lineEdit_hotline.clear()
                self.lineEdit_password.clear()
                self.lineEdit_password2.clear()
        else:
            conn_company.close()
            QMessageBox.information(self, '通知', '航空公司信息已修改！')
            self.lineEdit_name.clear()
            self.lineEdit_hotline.clear()


# 利用一个控制器来控制页面的跳转
class Controller:
    def __init__(self):
        self.hello = HelloWindow()
        self.login = LoginWindow()
        self.order = OrderWindow()
        self.user_register = RegisterWindow()
        self.admin_login = AdminLoginWindow()
        self.admin_manager =AdminManageWindow()
        self.admin_register = AdminRegisterWindow()
        self.company_register = CompanyRegisterWindow()
        self.company_manager = CompanyManageWindow()

    # 跳转到 hello 窗口
    def show_hello(self):
        self.hello.switch_window1.connect(self.show_login)
        self.hello.switch_window2.connect(self.show_admin_login)
        self.hello.show()

    # 跳转到 login 窗口, 注意关闭原页面
    def show_login(self):
        self.hello.close()
        if self.user_register.isVisible():
            self.user_register.close()
        if self.order.isVisible():
            self.order.close()
        # 跳转到订票窗口的连接
        self.login.switch_window1.connect(self.show_order)
        # 跳转到注册窗口的连接
        self.login.switch_window2.connect(self.show_user_register)
        self.login.show()

    # 跳转到 order 窗口, 注意关闭原页面
    def show_order(self):
        self.login.close()
        # 界面返回管理
        self.order.switch_window.connect(self.show_login)
        self.order.show()

    # 跳转到 user_register 窗口
    def show_user_register(self):
        self.login.close()
        # 注册完跳转回登录窗口
        self.user_register.switch_window2.connect(self.show_login)
        # 取消跳转回登录窗口
        self.user_register.switch_window1.connect(self.show_login)
        self.user_register.show()

    # 跳转到 admin_login 窗口
    def show_admin_login(self):
        self.hello.close()
        if self.admin_register.isVisible():
            self.admin_register.close()
        if self.company_register.isVisible():
            self.company_register.close()
        if self.admin_manager.isVisible():
            self.admin_manager.close()
        if self.company_manager.isVisible():
            self.company_manager.close()
        # 跳转到管理窗口的连接
        self.admin_login.switch_window1.connect(self.show_admin_manager)
        self.admin_login.switch_window2.connect(self.show_admin_register)
        self.admin_login.switch_window3.connect(self.show_company_manager)
        self.admin_login.switch_window4.connect(self.show_company_register)
        self.admin_login.show()

    # 跳转到 admin_manager 窗口
    def show_admin_manager(self):
        self.admin_login.close()
        # 界面返回管理
        self.admin_manager.switch_window.connect(self.show_admin_login)
        self.admin_manager.show()

    # 跳转到 admin_register 窗口
    def show_admin_register(self):
        self.admin_login.close()
        # 注册完跳转回登录窗口
        self.admin_register.switch_window2.connect(self.show_admin_login)
        # 取消跳转回登录窗口
        self.admin_register.switch_window1.connect(self.show_admin_login)
        self.admin_register.show()

    # 跳转到 company_register 窗口
    def show_company_register(self):
        self.admin_login.close()
        # 注册完跳转回登录窗口
        self.company_register.switch_window2.connect(self.show_admin_login)
        # 取消跳转回登录窗口
        self.company_register.switch_window1.connect(self.show_admin_login)
        self.company_register.show()

    # 跳转到 company_manager 窗口
    def show_company_manager(self):
        self.admin_login.close()
        # 界面返回管理
        self.company_manager.switch_window.connect(self.show_admin_login)
        self.company_manager.show()



def main():
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()  # 控制器实例
    controller.show_hello()  # 默认展示的是 hello 页面
    sys.exit(app.exec_())


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)  # 自适应分辨率
    main()
