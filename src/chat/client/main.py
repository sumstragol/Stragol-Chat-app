# developing only

from json import load
import functools
import sys
from PyQt5.uic import loadUi
import PyQt5.QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow
from config import config_handler
import client

test = config_handler.get_ui_data('test')
add_new_user_form_data = config_handler.get_ui_data('add_new_user_form')
name = sys.argv[1]
client.client

# ----------------------------------------------------
# Pages 
# to help switching between all widgets,
# to avoiding confusions from traversing chat windows,
# it allows for quickly changing currently displayed
# widget by calling its alias
# ----------------------------------------------------
class Pages():
    def __init__(self) -> None:
        self.widgets_stack = PyQt5.QtWidgets.QStackedWidget()
        self.widgets_stack.setFixedHeight(761)
        self.widgets_stack.setFixedWidth(675)
        self.widgets_stack_aliases = []
        

    def add_widgets(self, *widgets):
        for record in widgets:
            alias, widget = record['alias'], record['widget']
            self.widgets_stack.addWidget(widget)
            self.widgets_stack_aliases.append(alias)


    def switch_to_widget(self, widget_name: str):
        new_page_index = self.widgets_stack_aliases.index(widget_name)
        self.widgets_stack.setCurrentIndex(new_page_index)


    def show(self):
        self.widgets_stack.show()


app = QApplication(sys.argv)
pages_manager = Pages()


class Add_New_User_Form(QWidget):
    def __init__(self) -> None:
        super(Add_New_User_Form, self).__init__()
        loadUi(add_new_user_form_data['path'], self)

        # button for switching back to recent place
        # in final version - to settings 
        self.chat_page.clicked.connect(functools.partial(pages_manager.switch_to_widget, 'login_form'))
        self.chat_page.clicked.connect(self.reset_form)
        self.button_add_user.clicked.connect(self.validate_form)
        # passwords input 
        self.le_password.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        self.le_retype_password.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        #
        self.hide_issue_messages()
        

    def hide_issue_messages(self):
        self.issue_bad_id.setVisible(False)
        self.issue_bad_login_length.setVisible(False)
        self.issue_bad_login_in_use.setVisible(False)
        self.issue_bad_password_length.setVisible(False)
        self.issue_bad_password_differ.setVisible(False)
        self.issue_bad_name.setVisible(False)
        self.issue_bad_surname.setVisible(False)
        self.issue_bad_position.setVisible(False)


    def reset_form(self):
        self.hide_issue_messages()
        self.le_id.clear()
        self.role_box.setCurrentIndex(0)
        self.le_login.clear()
        self.le_password.clear()
        self.le_retype_password.clear()
        self.le_name.clear()
        self.le_surname.clear()
        self.le_position.clear()
        self.le_description.clear()
        self.le_image_link.clear()


    def validate_form(self):   
        issue = False
        # same order as they appear in the window
        # id
        if len(self.le_id.text()) == 0:
            issue = True
            self.issue_bad_id.setVisible(True)
        elif self.issue_bad_id.isVisible():
            self.issue_bad_id.setVisible(False)
        
        # login
        if len(self.le_login.text()) != 0:
            self.issue_bad_login_length.setVisible(False)


            if client.send_check_if_login_is_in_use(self.le_login.text()):
                issue = True
                self.issue_bad_login_in_use.setVisible(True)
            else:
                self.issue_bad_login_in_use.setVisible(False)
        elif len(self.le_login.text()) == 0:
            issue = True
            # if user didnt provide the login,
            # firstly display the length requirement
            self.issue_bad_login_in_use.setVisible(False)
            self.issue_bad_login_length.setVisible(True)
            

        # password
            # length
        if len(self.le_password.text()) <= 7:
            issue = True
            self.issue_bad_password_length.setVisible(True)
        elif self.issue_bad_password_length.isVisible():
            self.issue_bad_password_length.setVisible(False)
            # match
        if self.le_password.text() != self.le_retype_password.text():
            issue = True
            self.issue_bad_password_differ.setVisible(True)
        elif self.issue_bad_password_differ.isVisible():
            self.issue_bad_password_differ.setVisible(False)
        
        
        # name 
        if len(self.le_name.text()) <= 1:
            issue = True
            self.issue_bad_name.setVisible(True)
        elif self.issue_bad_name.isVisible():
            self.issue_bad_name.setVisible(False)

        # surname
        if len(self.le_surname.text()) <= 1:
            issue = True
            self.issue_bad_surname.setVisible(True)
        elif self.issue_bad_surname.isVisible():
            self.issue_bad_surname.setVisible(False)
        
            
        # position
        if len(self.le_position.text()) <= 2:
            issue = True
            self.issue_bad_position.setVisible(True)
        elif self.issue_bad_position.isVisible():
            self.issue_bad_position.setVisible(False)
        

        if issue: return

        self.send_form()


    def send_form(self):
        # package forms data into single dict
        data = {
            'id':           self.le_id.text(), 
            'role':         str(self.role_box.currentText()),
            'login':        self.le_login.text(),
            'password':     self.le_password.text(),
            'name':         self.le_name.text(),
            'surname':      self.le_surname.text(),
            'position':     self.le_position.text(),
            'description':  self.le_description.text(),
            'image':        self.le_image_link.text()
        }

        client.send_add_new_user_query(data)

        self.reset_form()




class Login_Form(QWidget):
    def __init__(self) -> None:
        super(Login_Form, self).__init__()
        loadUi(test['path'], self)
        #
        self.tinput.returnPressed.connect(self.send_message)
        #
        self.add_user_page.clicked.connect(functools.partial(pages_manager.switch_to_widget, 'add_new_user_form'))


    def send_message(self):
        message = self.tinput.text()
        self.tinput.clear()
        client.send_add_message_query(message, name, '1234')







pages_manager.add_widgets(
    { 
        "alias": "login_form",
        "widget": Login_Form()
    },
    { 
        "alias": "add_new_user_form",
        "widget": Add_New_User_Form()
    }
)
pages_manager.show()

try:
    sys.exit(app.exec_())
except:
    pass
