from GUI import mainWindow, enter_window, dialog, about
from PyQt5 import QtWidgets
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
import sys
import json
import functions


class DialogWindow(QtWidgets.QDialog, dialog.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.close)

class AboutDialog(QtWidgets.QDialog, about.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class AuthDialog(QtWidgets.QDialog, enter_window.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.close)
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
    
        
class MainWindow(QtWidgets.QMainWindow, mainWindow.Ui_MainWindow):
    login = ''
    password = ''
    router_ip = ''
    session = ''
    token = None
    data = dict()
    with open("C:/Users/Ruslan/Documents/DP/programm/data.json", "r") as read_file:
        data = json.load(read_file)
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.action_3.triggered.connect(self.show_dialog)
        self.action_4.triggered.connect(self.show_about)

        self.pushButton.clicked.connect(self.wpa)        
        self.pushButton_2.clicked.connect(self.aes)
        self.pushButton_3.clicked.connect(self.brd_ssid)
        self.pushButton_5.clicked.connect(self.wifi_password)
        self.pushButton_6.clicked.connect(self.router_login)
        self.pushButton_7.clicked.connect(self.router_password)
        self.pushButton_8.clicked.connect(self.mac_filter)
        self.pushButton_10.clicked.connect(self.antenna)
        self.pushButton_11.clicked.connect(self.wps)
        self.pushButton_13.clicked.connect(self.remote_control)
        self.pushButton_14.clicked.connect(self.upnp)
        self.pushButton_15.clicked.connect(self.software)
        self.pushButton_33.clicked.connect(self.guest_network)

        self.label.setToolTip(self.data['wpa'])
        self.label_4.setToolTip(self.data['aes'])
        self.label_5.setToolTip(self.data['ssid'])
        self.label_12.setToolTip(self.data['wifi_pass'])
        self.label_9.setToolTip(self.data['r_login'])
        self.label_13.setToolTip(self.data['r_pass'])
        self.label_15.setToolTip(self.data['mac'])
        self.label_19.setToolTip(self.data['antenna'])
        self.label_21.setToolTip(self.data['wps'])
        self.label_25.setToolTip(self.data['remote_control'])
        self.label_27.setToolTip(self.data['upnp'])
        self.label_28.setToolTip(self.data['soft'])
        self.label_33.setToolTip(self.data['guest'])
        
    
    def closeEvent(self, event):
        if self.token != None:
            functions.logout(self.router_ip, self.session, self.token)
        event.accept()
    
    def show_about(self):
        dialog = AboutDialog()
        dialog.exec()

    def show_dialog(self):
        dialog = AuthDialog()
        self.token = None
        while self.token == None:
            dialog.lineEdit.setText('')
            dialog.lineEdit_2.setText('')
            dialog.exec()
            self.login = dialog.lineEdit.text()
            self.password = dialog.lineEdit_2.text()
            self.router_ip, self.token, self.session = functions.login(self.login, self.password)
            
        wpa2, aes = functions.get_wifi_sec(self.router_ip, self.token, self.session)
        settings = functions.get_config(self.router_ip, self.token, self.session)
        version = functions.soft(self.router_ip, self.token, self.session)
        wifi_password = functions.get_wifi_pass(functions.get_ssid(self.router_ip, self.token, self.session))
        wifi_password = functions.pass_checker(wifi_password)
        router_password = functions.pass_checker(self.password)
        router_login = functions.login_checker(self.login)

        labels = (self.label_2, self.label_3, self.label_6, self.label_34,
                self.label_22, self.label_20, self.label_26, self.label_30,
                self.label_17, self.label_31, self.label_10, self.label_14, self.label_11)
        buttonts = (self.pushButton, self.pushButton_2, self.pushButton_3, self.pushButton_33,
                    self.pushButton_11, self.pushButton_10, self.pushButton_13, self.pushButton_14, 
                    self.pushButton_8, self.pushButton_15, self.pushButton_5, self.pushButton_7, 
                    self.pushButton_6)

        args = (wpa2, aes, *settings, version, wifi_password,router_password, router_login)
        for i in range(len(labels)):
            if args[i] == True:
                labels[i].setStyleSheet('color: green; font: bold')
                labels[i].setText('OK')
            else:
                labels[i].setStyleSheet('color: red; font: bold')
                labels[i].setText('Проблема')
                buttonts[i].setEnabled(True)
    
    def wpa(self):
        functions.wifi_sec_on(self.router_ip, self.token, self.session)
        self.show_dialog()
    
    def aes(self):
        functions.wifi_sec_on(self.router_ip, self.token, self.session)
        self.show_dialog()

    def brd_ssid(self):
        functions.ssid(self.router_ip, self.token, self.session)
        self.show_dialog()
    
    def wifi_password(self):
        #закрыть программу
        pas = ''
        dialog = DialogWindow()
        dialog.label.setText('Пароль')
        dialog.textBrowser.setText('Длина пароля: 8-63 символа(ов) \nРазрешенные \
символы: 0123456789ABCDEFabcdefGHIJKLMNOPQRSTUVWXYZghijklmnopqrstuvwxyz`~!@#$^&*()\
-=_+[]{};:\'\"\\|/?.,<>/% ')
        dialog.lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        while pas == '':
            dialog.lineEdit.setText('')
            dialog.exec()
            data = dialog.lineEdit.text()
            if functions.pass_checker(data) == True and functions.data_checker(data, 0) == True:
                pas = data
        functions.wifi_sec_on(self.router_ip, self.token, self.session, pas)
        self.show_dialog()
    
    def router_login(self):
        #показать окно авторизации
        log = ''
        dialog = DialogWindow()
        dialog.label.setText('Логин')
        dialog.textBrowser.setText('Длина логина: 1-14 символа(ов) \nРазрешенные \
символы: 0123456789ABCDEFabcdefGHIJKLMNOPQRSTUVWXYZghijklmnopqrstuvwxyz`~!@#$^&*()\
-=_+[]{};:\'\"\\|/?.,<>/%')
        dialog.lineEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
        while log == '':
            dialog.lineEdit.setText('')
            dialog.exec()
            data = dialog.lineEdit.text()
            if functions.login_checker(data) == True and functions.data_checker(data, 1) == True:
                log = data
        functions.router_login_pass_changer(self.router_ip, self.token, self.session, self.login, self.password, log, self.password)
        self.show_dialog()

    def router_password(self):
        #показать окно авторизации
        pas = ''
        dialog = DialogWindow()
        dialog.label.setText('Пароль')
        dialog.textBrowser.setText('Длина пароля: 1-14 символа(ов) \nРазрешенные \
символы: 0123456789ABCDEFabcdefGHIJKLMNOPQRSTUVWXYZghijklmnopqrstuvwxyz`~!@#$^&*()\
-=_+[]{};:\'\"\\|/?.,<>/%')
        dialog.lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        while pas == '':
            dialog.lineEdit.setText('')
            dialog.exec()
            data = dialog.lineEdit.text()
            if functions.pass_checker(data) == True and functions.data_checker(data, 1) == True:
                pas = data
        functions.router_login_pass_changer(self.router_ip, self.token, self.session, self.login, self.password, self.login, pas)
        self.show_dialog()

    def mac_filter(self):
        #хз
        mac = ''
        dialog = DialogWindow()
        dialog.label.setText('MAC-адрес')
        dialog.textBrowser.setText('Пример разрешенной формы записи: \n\
08-72-F4-GG-7H-40 \n Разрешенные символы: \n0123456789ABCDEFabcdefGHIJK\
LMNOPQRSTUVWXYZghijklmnopqrstuvwxyz')
        dialog.lineEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
        while mac == '':
            dialog.lineEdit.setText('')
            dialog.exec()
            data = dialog.lineEdit.text()
            if functions.data_checker(data, 2) == True:
                mac = data
        functions.mac_filter_en(self.router_ip, self.token, self.session, mac)
        self.show_dialog()

    def antenna(self):
        #хз
        mode = ''
        dialog = DialogWindow()
        dialog.label.setText('Мощность')
        dialog.textBrowser.setText('1 - Минимальное значение мощности \n\
2 - Среднее значение мощности \nВведите число 1 или 2')
        dialog.lineEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
        while mode == '':
            dialog.lineEdit.setText('')
            dialog.exec()
            data = dialog.lineEdit.text()
            if data == '1' or data == '2':
                mode = data
        functions.antenna_changer(self.router_ip, self.token, self.session, mode)
        self.show_dialog()
        
    def wps(self):
        functions.wps_off(self.router_ip, self.token, self.session)
        self.pushButton_11.setEnabled(False)
        self.label_22.setStyleSheet('color: green; font: bold')
        self.label_22.setText('OK')

    def remote_control(self):
        functions.remote_off(self.router_ip, self.token, self.session)
        self.pushButton_13.setEnabled(False)
        self.label_26.setStyleSheet('color: green; font: bold')
        self.label_26.setText('OK')
    
    def upnp(self):
        functions.upnp_off(self.router_ip, self.token, self.session)
        self.pushButton_14.setEnabled(False)
        self.label_30.setStyleSheet('color: green; font: bold')
        self.label_30.setText('OK')

    def software(self):
        link = 'https://www.tp-link.com/ru/support/download/tl-wr740n/v6/#Firmware'
        QDesktopServices.openUrl(QUrl(link))
        

    def guest_network(self):
        #окно 1
        name = ''
        pas = ''
        dialog = DialogWindow()
        dialog.label.setText('Имя сети')
        dialog.textBrowser.setText('Длина имени: 1-32 символа(ов) \n\
Разрешено использование любых символов, входящих в UTF-8')
        dialog.lineEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
        while name == '':
            dialog.lineEdit.setText('')
            dialog.exec()
            data = dialog.lineEdit.text()
            if len(data) < 33:
                name = data
        
        #окно 2
        dialog.label.setText('Пароль')
        dialog.textBrowser.setText('Длина пароля: 8-63 символа(ов) \nРазрешенные \
символы: 0123456789ABCDEFabcdefGHIJKLMNOPQRSTUVWXYZghijklmnopqrstuvwxyz`~!@#$^&*()\
-=_+[]{};:\'\"\\|/?.,<>/% ')
        dialog.lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        while pas == '':
            dialog.lineEdit.setText('')
            dialog.exec()
            data = dialog.lineEdit.text()
            if functions.pass_checker(data) == True and functions.data_checker(data, 0) == True:
                pas = data
        
        functions.guest_on(self.router_ip, self.token, self.session, name, pas)

        self.pushButton_33.setEnabled(False)
        self.label_34.setStyleSheet('color: green; font: bold')
        self.label_34.setText('OK')


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()
    if window.token != None:
        functions.logout(window.router_ip, window.session, window.token)

main()
