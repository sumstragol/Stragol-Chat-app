# developing only

from json import load
from overrides import overrides
import functools
import sys
from PyQt5.uic import loadUi
import PyQt5
import PyQt5.QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow, QListWidget, QListWidgetItem, QMessageBox, \
    QDialogButtonBox
from config import config_handler
import client

# user_id of currently logged user
# will change value on sucessful login 
myself = None
# user_id of user that client want to chat
selected_contact_user_id = None
# uis data
chat_data = config_handler.get_ui_data('chat')
add_new_user_form_data = config_handler.get_ui_data('add_new_user_form')
login_form_data = config_handler.get_ui_data('login_form')
menu_data = config_handler.get_ui_data('menu')
# indexes of hidden data in contacts list of each contact
user_data_indexes = config_handler.get_user_data_indexes()


# preparing socket
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
        self.widgets_stack_aliases = []
        self.widgets_stack_configs = []
        self.widgets_stack.resize(login_form_data['widget_width'], login_form_data['widget_height'])
        

    def add_widget(self, widget_data):
        alias, widget, config = widget_data
        self.widgets_stack.addWidget(widget)
        self.widgets_stack_aliases.append(alias)
        self.widgets_stack_configs.append(config)


    def add_widgets(self, *widgets):
        for record in widgets:
            alias, widget, config = record['alias'], record['widget'], record['config']
            self.widgets_stack.addWidget(widget)
            self.widgets_stack_aliases.append(alias)
            self.widgets_stack_configs.append(config)


    def switch_to_widget(self, widget_name: str):
        new_page_index = self.widgets_stack_aliases.index(widget_name)
        self.widgets_stack.setCurrentIndex(new_page_index)
        self.widgets_stack.resize(\
            self.widgets_stack_configs[new_page_index]['widget_width'], \
            self.widgets_stack_configs[new_page_index]['widget_height'])
        self.widgets_stack.currentWidget().on_switch()


    def show(self):
        self.widgets_stack.show()




# ----------------------------------------------------
# Page
# base class for all pages.
# has method that is called each time user
# switches to that page
# ----------------------------------------------------

class Page():
    def on_switch(self):
        return None




app = QApplication(sys.argv)
pages_manager = Pages()




# ----------------------------------------------------
#
#
#
#
#
#
#
# ----------------------------------------------------

class Add_New_User_Form(QWidget, Page):
    def __init__(self) -> None:
        super(Add_New_User_Form, self).__init__()
        loadUi(add_new_user_form_data['path'], self)

        # button for switching back to recent place
        # in final version - to settings 
        self.button_back.clicked.connect(functools.partial(pages_manager.switch_to_widget, 'menu'))
        self.button_back.clicked.connect(self.reset_form)
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

        status = client.send_add_new_user_query(data)
        
        if status:
            self.reset_form()
            qmb_inform_user = QMessageBox()
            qmb_inform_user.setWindowTitle("User added")
            qmb_inform_user.setText("User sucessfully added.")
            qmb_inform_user.setStandardButtons(QMessageBox.Ok)
            qmb_inform_user.exec_()
            return
        else:
            pass




# ----------------------------------------------------
#
#
#
#
#
#
#
# ----------------------------------------------------

class Login_Form(QWidget, Page):
    def __init__(self) -> None:
        super(Login_Form, self).__init__()
        loadUi(login_form_data['path'], self)

        self.button_log_in.clicked.connect(self.login_request)
        self.le_password.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        self.le_password.returnPressed.connect(self.login_request)

        self.issue_data_missing.setVisible(False)
        self.issue_data_incorrect.setVisible(False)


    def login_request(self):
        if len(self.le_login.text()) == 0 or len(self.le_password.text()) == 0:
            self.issue_data_missing.setVisible(True)
            self.issue_data_incorrect.setVisible(False)
            return

        data = {
            'login':    self.le_login.text(),
            'password': self.le_password.text()
        }
        login_status = client.send_login_request(data)
        if login_status:
            global myself 
            myself = login_status
            pages_manager.switch_to_widget('menu')
        else:
            self.issue_data_missing.setVisible(False)
            self.issue_data_incorrect.setVisible(True)
            return




# ----------------------------------------------------
#
#
#
#
#
#
#
# ----------------------------------------------------

class Chat(QWidget, Page):
    def __init__(self) -> None:
        super(Chat, self).__init__()
        loadUi(chat_data['path'], self)
        self.button_exit_chat.clicked.connect(self.exit_chat)
        self.button_send_message.clicked.connect(self.send_message)
        self.init_chat_data_loaded = False
        self.users_have_chated = False
        global myself, selected_contact_user_id
        self.myself_user_id = myself
        self.other_user_id = selected_contact_user_id
        self.chat_id = None

    @overrides
    def on_switch(self):
        self.init_chat_data_load()


    def init_chat_data_load(self):
        if self.init_chat_data_loaded:
            return

        # loading data that will be always displayed
        # name, surname, and address to image
        self.init_chat_data_loaded = True
        selected_user_data = client.send_chat_init_data_load(self.myself_user_id, self.other_user_id)[0]
        name, surname, image = selected_user_data
        full_name = name + ' ' + surname
        self.label_chats_name.setText(full_name)

        # checking if chat file exists (if users have chated)
        # if none - chat file will be created on first message,
        # if id is correct load up to n last messages
        chat_id = client.send_check_if_chat_exists(self.myself_user_id, self.other_user_id)
        if chat_id is None:
            self.button_send_message.clicked.disconnect(self.send_message)
            self.button_send_message.clicked.connect(self.send_first_message)
            return
        self.chat_id = chat_id
        self.users_have_chated = True
        #chat_last_messages = client.send_load_messages(self.chat_id)
        #print(chat_last_messages)


    def append_my_message(self):
        my_last_sent_message = self.le_input_message.text()

    # method for first message, creating chat file etc
    # after getting things ready, reassigning onclick method
    # for button_send_message to regular send_message()
    def send_first_message(self):
        status = client.send_create_new_chat(self.myself_user_id, self.other_user_id)
        if not status:
            print('[MAIN WINDOW] Failed to create new chat.')
            return
        chat_id = client.send_check_if_chat_exists(self.myself_user_id, self.other_user_id)
        if not chat_id:
            print('[MAIN WINDOW] Failed to retrive chat_id')
            return
        self.chat_id = chat_id

        self.button_send_message.clicked.disconnect(self.send_first_message)
        self.button_send_message.clicked.connect(self.send_message)
        
        self.send_message()


    def send_message(self):
        self.append_my_message()
        message = self.le_input_message.text()
        client.send_add_message(self.myself_user_id, self.chat_id, message)
        
        self.le_input_message.clear()


    def exit_chat(self):
        global selected_contact_user_id
        selected_contact_user_id = None
        pages_manager.switch_to_widget('menu')




# ----------------------------------------------------
# CHAT PAGES MANAGER
#
# to make life easier - interface over page_manager,
# to help switching to chat page more easily, plus
# some additional functionality that may help in 
# case of CHAT pages(widgets)
#
# ----------------------------------------------------

class Chat_Pages_Manger():
    def __init__(self) -> None:
        self.opened_chat_pages = {}


    def check_if_exists(self, user_id):
        if user_id in self.opened_chat_pages:
            return True
        else:
            return False


    def create_new_page(self, selected_user_id):
        pages_manager.add_widget(
            [
                selected_user_id,
                Chat(),
                chat_data
            ]
        )


    def switch_to_page(self, selected_user_id):
        pages_manager.switch_to_widget(selected_user_id)




chat_pages = Chat_Pages_Manger()


# ----------------------------------------------------
#
#
#
#
#
#
#
# ----------------------------------------------------

class Menu(QWidget, Page):
    def __init__(self) -> None:
        super(Menu, self).__init__()
        loadUi(menu_data['path'], self)
        self.button_status_inactive.clicked.connect(functools.partial(pages_manager.switch_to_widget, 'add_new_user_form'))
        self.lw_contacts.itemClicked.connect(self.open_chat)


    @overrides
    def on_switch(self):
        self.load_contacts()
        

    def load_contacts(self):
        if self.lw_contacts.count() != 0:
            return 


        contacts = client.send_load_contacts(myself)
        for single_user_data  in contacts:
            user_id, name, surname = single_user_data
            user_name = name + ' ' + surname
            list_item = QListWidgetItem(user_name)
            list_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'], user_id)
            self.lw_contacts.addItem(list_item)


    def open_chat(self):
        global myself, selected_contact_user_id
        selected_contact_user_id = self.lw_contacts.currentItem().data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'])
        if not chat_pages.check_if_exists(selected_contact_user_id):
            chat_pages.create_new_page(selected_contact_user_id)

        chat_pages.switch_to_page(selected_contact_user_id)
        



pages_manager.add_widgets(
    {
        "alias": "login_form",
        "widget": Login_Form(),
        "config": login_form_data
    },
    {
        "alias": "menu",
        "widget": Menu(),
        "config": menu_data
    },
    { 
        "alias": "add_new_user_form",
        "widget": Add_New_User_Form(),
        "config": add_new_user_form_data
    }
)
pages_manager.show()

try:
    sys.exit(app.exec_())
except:
    pass
