# developing only

import threading
from overrides import overrides
import functools
import sys
from PyQt5.uic import loadUi
import PyQt5
from PyQt5.QtGui import QPixmap
import PyQt5.QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow, QListWidget, QListWidgetItem, QMessageBox, \
    QDialogButtonBox, QInputDialog, QLineEdit
import PyQt5.QtCore
from PyQt5.QtCore import QThread
from config import config_handler
import client
from plyer import notification
import plyer.platforms.macosx.notification
#import plyer.platforms.win.notification
#import plyer.platforms.linux.notification
#notification.notify(title="tytul", message="tresc")




# user_id of currently logged user
# will change value on sucessful login 
myself = ''
# user_id of user that client want to chat
selected_contact_user_id = ''
# uis data
chat_data = config_handler.get_ui_data('chat')
add_new_user_form_data = config_handler.get_ui_data('add_new_user_form')
login_form_data = config_handler.get_ui_data('login_form')
menu_data = config_handler.get_ui_data('menu')
profile_data = config_handler.get_ui_data('profile')
# indexes of hidden data in contacts list of each contact
user_data_indexes = config_handler.get_user_data_indexes()
#
_ASL = config_handler.get_active_statuses_list('statuses')
_ASI = config_handler.get_active_statuses_list('icons')
# when handling an pn message data is packed into list 
# aliases are used in order to increase readability
_MFI_CD = config_handler.get_queries_list('message_fetch_indexes')['chat_data']
_MFI_GCD = config_handler.get_queries_list('message_fetch_indexes')['general_chat_data']
_MFI_CCD = config_handler.get_queries_list('message_fetch_indexes')['conference_chat_data']
_PNSL = config_handler.get_pending_notifications_list()
_CT = config_handler.get_contact_types()
# for all the while loops 
# swtiches to false on app quit
client._ACTIVE





# ----------------------------------------------------
# PN HANDLING ON THE CLIENT SIDE
# Producer thread - _listen_to_any_responses (client module)
# acquires the lock on the pn response and then notifies 
# consumer thread after appending pn to the storage.
# Consumer thread - _listen_to_any_pns (this module)
# waits and after being notified calls 'handle_pn'
# ----------------------------------------------------

def notify_user(ntitle, nmessage):
    notification.notify(title=ntitle, message=nmessage)


def handle_pns():
    for pn in client.pns_storage:
        # todo add helper function to extract name and surname
        global pages_manager
        if pn.data_id == _PNSL['add_message_pn']:
            user_id = pn.data[_MFI_CD['sender']]
            # notification
            user_contact_item = pages_manager.get_widget("menu").get_contact_item(user_id)
            name = user_contact_item.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['name'])
            surname = user_contact_item.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['surname'])
            notify_user(f"{name} {surname}", pn.data[_MFI_CD['content']])
            # append to chat page if its opened
            global chat_pages
            widget = chat_pages.get_chat_page(user_id)
            if widget:
                # both users at the same time opened chat
                # (when chat files are created yet)
                if not widget.get_chat_id():
                    widget.reset_chat_data()
                widget.append_single_message(message_content=pn.data)
        elif pn.data_id == _PNSL['change_status_pn']:
            user_id = pn.data['user_id']
            status = pn.data['status']
            # send notify message
            # if status of some user changed to inactive - do nothing
            notify_message = ''
            if status == _ASL['active']:
                notify_message = "is now active"
            elif status == _ASL['break']:
                notify_message = "is now taking break"
            if len(notify_message):
                user_contact_item = pages_manager.get_widget("menu").get_contact_item(user_id)
                name = user_contact_item.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['name'])
                surname = user_contact_item.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['surname'])
                notify_user(f"{name} {surname}", notify_message)    
            # update status in menu page
            pages_manager.get_widget("menu").set_other_status(user_id, status)
        elif pn.data_id == _PNSL['add_general_message_pn']:
            user_id = pn.data[_MFI_GCD['sender']]
            # notify user
            user_contact_item = pages_manager.get_widget("menu").get_contact_item(user_id)
            name = user_contact_item.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['name'])
            surname = user_contact_item.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['surname'])
            notify_user(f"{name} {surname} to General Chat", pn.data[_MFI_GCD['content']])
            # append to general chat page if its opened
            widget = pages_manager.get_widget("general")
            if widget is not None:
                widget.append_single_message(message_content=pn.data)
        elif pn.data_id == _PNSL['add_conference_message_pn']:
            user_id = pn.data[_MFI_CCD['sender']]
            conference_name = pn.data[_MFI_CCD['conference_name']]
            # notify user
            user_contact_item = pages_manager.get_widget("menu").get_contact_item(user_id)
            name = user_contact_item.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['name'])
            surname = user_contact_item.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['surname'])
            notify_user(f"{name} {surname} to {conference_name}", pn.data[_MFI_CCD['content']])
            # append to general chat page if its opened
            widget = pages_manager.get_widget(conference_name)
            if widget is not None:
                widget.append_single_message(message_content=pn.data)
    
    client.pns_storage.clear()





def _listen_to_any_pns(cv):
    while client._ACTIVE:
        cv.acquire()
        with cv:
            cv.wait()
            handle_pns()
    condition_var.release()
    return




# preparing socket            
# setting up the threads for listening to the repsonses
client.client
condition_var = threading.Condition()
client.start(condition_var)
pns_thread = threading.Thread(target=_listen_to_any_pns, args=[condition_var])
pns_thread.start()



# called on app quit
def stop():
    global condition_var, pns_thread
    condition_var.acquire()
    client._ACTIVE = False
    condition_var.notify_all()
    condition_var.release()
    



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
        # 
        if type(widget_data) is dict:
            alias, widget, config = widget_data['alias'], widget_data['widget'], widget_data['config']
        else:
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


    def remove_widget(self, widget_name):
        # find the widget index at the lists
        widget_index = 0
        for index, widget_alias in enumerate(self.widgets_stack_aliases):
            if widget_alias == widget_name:
                widget_index = index
                break
        # delete widget and its data
        self.widgets_stack.removeWidget(self.get_widget(widget_name))
        del self.widgets_stack_aliases[widget_index]
        del self.widgets_stack_configs[widget_index]

        


    def switch_to_widget(self, widget_name: str):
        new_page_index = self.widgets_stack_aliases.index(widget_name)
        self.widgets_stack.setCurrentIndex(new_page_index)
        self.widgets_stack.resize(\
            self.widgets_stack_configs[new_page_index]['widget_width'], \
            self.widgets_stack_configs[new_page_index]['widget_height'])
        self.widgets_stack.currentWidget().on_switch()


    def get_widget(self, alias):
        for index, widget_alias in enumerate(self.widgets_stack_aliases):
            if widget_alias == alias:
                return self.widgets_stack.widget(index)
        return None


    def if_widget_exists(self, alias):
        for widget_alias in self.widgets_stack_aliases:
            if widget_alias == alias:
                return True
        return False


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
app.aboutToQuit.connect(client.stop)
app.aboutToQuit.connect(stop)
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

        self.button_back.clicked.connect(functools.partial(pages_manager.switch_to_widget, 'profile'))
        self.button_back.clicked.connect(self.reset_form)
        self.button_add_user.clicked.connect(self.validate_form)
        # passwords input 
        self.le_password.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        self.le_retype_password.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        #
        self.hide_issue_messages()
        

    def hide_issue_messages(self):
        self.issue_bad_id.setText("")
        self.issue_bad_login.setText("")
        self.issue_bad_password_length.setText("")
        self.issue_bad_password_differ.setText("")
        self.issue_bad_name.setText("")
        self.issue_bad_surname.setText("")
        self.issue_bad_position.setText("")


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
        issue_msgs = add_new_user_form_data['issue_messages']
        # same order as they appear in the window
        # id
        if len(self.le_id.text()) == 0:
            issue = True
            self.issue_bad_id.setText(issue_msgs['id_issue'])
        elif self.issue_bad_id.isVisible():
            self.issue_bad_id.setText("")
        
        # login
        if len(self.le_login.text()) >= 4:
            self.issue_bad_login.setText("")
            if client.send_check_if_login_is_in_use(self.le_login.text()):
                issue = True
                self.issue_bad_login.setText(issue_msgs['login_issue_in_use'])
        elif len(self.le_login.text()) == 0:
            issue = True
            self.issue_bad_login.setText(issue_msgs['login_issue_incorrect'])
            
        # password
            # length
        if len(self.le_password.text()) <= 7:
            issue = True
            self.issue_bad_password_length.setText(issue_msgs['password_issue_length'])
        elif len(self.issue_bad_password_length.text()) != 0:
            self.issue_bad_password_length.setText("")
            # match
        if self.le_password.text() != self.le_retype_password.text():
            issue = True
            self.issue_bad_password_differ.setText(issue_msgs['password_issue_match'])
        elif self.issue_bad_password_differ.isVisible():
            self.issue_bad_password_differ.setText("")
             
        # name 
        if len(self.le_name.text()) <= 1:
            issue = True
            self.issue_bad_name.setText(issue_msgs['name_issue'])
        elif self.issue_bad_name.isVisible():
            self.issue_bad_name.setText("")

        # surname
        if len(self.le_surname.text()) <= 1:
            issue = True
            self.issue_bad_surname.setText(issue_msgs['surname_issue'])
        elif self.issue_bad_surname.isVisible():
            self.issue_bad_surname.setText("")
            
        # position
        if len(self.le_position.text()) <= 2:
            issue = True
            self.issue_bad_position.setText(issue_msgs['position_issue'])
        elif self.issue_bad_position.isVisible():
            self.issue_bad_position.setText("")
        
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

        self.label_issue.setText(' ')
        

    def login_request(self):
        if len(self.le_login.text()) == 0 or len(self.le_password.text()) == 0:
            self.label_issue.setText(login_form_data['issue_messages']['missing_data_issue'])
            return

        data = {
            'login':    self.le_login.text(),
            'password': self.le_password.text()
        }
        login_status = client.send_login_request(data)
        if login_status is None:
            self.label_issue.setText(login_form_data['issue_messages']['not_found_issue'])
            return

        global myself 
        myself = login_status
        client.client_user_id = login_status
        pages_manager.add_widget(
            {
                'alias':    'menu',
                'widget':   Menu(),
                'config':   menu_data
            }
        )
        pages_manager.switch_to_widget('menu')
        pages_manager.remove_widget('login_form')
        
            




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
        self.setAttribute(PyQt5.QtCore.Qt.WA_DeleteOnClose)
        self.button_exit_chat.clicked.connect(self.exit_chat)
        self.button_send_message.clicked.connect(self.send_message)
        self.le_input_message.returnPressed.connect(self.send_message)
        self.lw_messages.setWordWrap(True)
        self.init_chat_data_loaded = False
        self.users_have_chated = False
        global myself, selected_contact_user_id
        self.myself_user_id = myself
        self.other_user_id = selected_contact_user_id
        self.other_user_full_name = ''
        self.chat_id = None


    @overrides
    def on_switch(self):
        self.init_chat_data_load()


    #
    def reset_chat_data(self):
        chat_id = client.send_check_if_chat_exists(self.myself_user_id, self.other_user_id)
        self.chat_id = chat_id
        self.button_send_message.clicked.disconnect(self.send_first_message)
        self.le_input_message.returnPressed.disconnect(self.send_first_message)
        self.button_send_message.clicked.connect(self.send_message)
        self.le_input_message.returnPressed.connect(self.send_message)
        self.users_have_chated = True


    def get_chat_id(self):
        return self.chat_id


    def init_chat_data_load(self):
        if self.init_chat_data_loaded:
            return

        # loading data that will be always displayed
        # name, surname, and address to image
        self.init_chat_data_loaded = True
        selected_user_data = client.send_chat_init_data_load(self.myself_user_id, self.other_user_id)[0]
        name, surname, image = selected_user_data
        full_name = name + ' ' + surname
        self.other_user_full_name = full_name
        self.label_chats_name.setText(full_name)

        # checking if chat file exists (if users have chated)
        # if none - chat file will be created on first message,
        # if id is correct load up to n last messages
        chat_id = client.send_check_if_chat_exists(self.myself_user_id, self.other_user_id)
        if chat_id is None:
            self.button_send_message.clicked.disconnect(self.send_message)
            self.le_input_message.returnPressed.disconnect(self.send_message)
            self.button_send_message.clicked.connect(self.send_first_message)
            self.le_input_message.returnPressed.connect(self.send_first_message)
            return

        self.chat_id = chat_id
        self.users_have_chated = True
        last_messages = client.send_get_last_messages(self.chat_id)
        for message in reversed(last_messages):
            self.append_single_message(self, message_content=message)


    def append_single_message(self, who=None, message_content=None):
        # check if last message's sender is the same 
        # if so prefix with the name wont be added
        if_prefix = True
        if self.lw_messages.count() > 0:
            last_message = self.lw_messages.item(self.lw_messages.count() - 1)
            last_message_user = last_message.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'])
            if who and who == last_message_user \
            or message_content is not None and message_content[_MFI_CD['sender']] == last_message_user:
                if_prefix = False
        
        prefix = ''
        if who == self.myself_user_id:
            message_text = self.le_input_message.text()
            if if_prefix:
                prefix = 'me\n'
            message_item = QListWidgetItem(prefix + message_text)
            message_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'], self.myself_user_id)
            message_item.setBackground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(213, 221, 222)))
            self.lw_messages.addItem(message_item)
        else:
            message_text = message_content[_MFI_CD['content']]
            # name preceding message content
            if if_prefix:
                # may seem redudant but in case of loading messages on first init 
                # messages are packed into message_content after getting them from 
                # seperate query
                if message_content[_MFI_CD['sender']] == self.myself_user_id:
                    prefix = 'me\n'
                else:
                    prefix = self.other_user_full_name + '\n'
            message_item = QListWidgetItem(prefix + message_text)
            message_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'], message_content[_MFI_CD['sender']])
            # if myself change background color
            if message_content[_MFI_CD['sender']] == self.myself_user_id:
                message_item.setBackground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(213, 221, 222)))
            self.lw_messages.addItem(message_item)
        self.lw_messages.scrollToBottom()


    def append_my_message(self):
        self.append_single_message(myself)



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
        self.le_input_message.returnPressed.disconnect(self.send_first_message)
        self.button_send_message.clicked.connect(self.send_message)
        self.le_input_message.returnPressed.connect(self.send_message)

        self.send_message()


    def send_message(self):
        if len(self.le_input_message.text()) == 0:
            return

        self.append_my_message()
        message = self.le_input_message.text()
        client.send_add_message(self.myself_user_id, self.other_user_id, self.chat_id, message)
        
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
# notes -
# self.opened_chat_pages contains users_id not chat_id,
# chat_id is obtained after creating chat page.
# in case of looking after chat page - search using
# user_id (selected_user_id)
# ----------------------------------------------------

class Chat_Pages_Manger():
    def __init__(self) -> None:
        self.opened_chat_pages = []


    def check_if_exists(self, user_id):
        if user_id in self.opened_chat_pages:
            return True
        else:
            return False


    def get_chat_page(self, user_id):
        if self.check_if_exists(user_id):
            return pages_manager.get_widget(user_id)
        else:
            return None


    def create_new_page(self, selected_user_id):
        self.opened_chat_pages.append(selected_user_id)
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

class General_Chat(Chat, QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.granted_to_type = False
    

    @overrides
    def on_switch(self):
        self.init_chat_data_load()


    @overrides
    def init_chat_data_load(self):
        if self.init_chat_data_loaded:
            return

        self.init_chat_data_loaded = True
        # chat title (label)
        general_chat_data = client.send_init_general_chat()
        self.label_chats_name.setText(general_chat_data['chat_name'])
        # check if user is granted to type in general chat
        granted = client.send_check_if_user_general_granted(self.myself_user_id) 
        self.granted_to_type = granted
        # grant user to send message
        self.le_input_message.setEnabled(granted)
        self.button_send_message.setEnabled(granted)
        if not granted:
            # disallow selection
            self.lw_messages.setSelectionMode(0)

        # append last messages
        last_messages = client.send_get_last_general_messages()
        for message in reversed(last_messages):
            self.append_single_message(message_content=message)
        

    def append_single_message(self, who=None, message_content=None):
        # check if last message's sender is the same 
        # if so prefix with the name wont be added
        if_prefix = True
        if self.lw_messages.count() > 0:
            last_message = self.lw_messages.item(self.lw_messages.count() - 1)
            last_message_user = last_message.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'])
            if who and who == last_message_user \
            or message_content is not None and message_content[_MFI_CD['sender']] == last_message_user:
                if_prefix = False

        # message sent by user himself
        if who == self.myself_user_id:
            if if_prefix:
                prefix = 'me'
                prefix_item = QListWidgetItem(prefix)
                prefix_item.setBackground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(213, 221, 222)))
                self.lw_messages.addItem(prefix_item)
            message_text = self.le_input_message.text()
            message_item = QListWidgetItem(message_text)
            message_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'], self.myself_user_id)
            message_item.setBackground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(213, 221, 222)))
            self.lw_messages.addItem(message_item)
            return

        # message received on the first init, on in pn
        # set up prefix
        if if_prefix:
            # may seem redudant but in case of loading messages on first init 
            # messages are packed into message_content after getting them from 
            # seperate query
            if message_content[_MFI_GCD['sender']] == self.myself_user_id:
                prefix = 'me'
            else:
                # based on user_if find contact in contact list and get data from contact item
                user_contact_item = pages_manager.get_widget("menu").get_contact_item(message_content[_MFI_GCD['sender']])
                name = user_contact_item.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['name'])
                surname = user_contact_item.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['surname'])
                prefix = f'{name} {surname}'
            prefix_item = QListWidgetItem(prefix)
            if message_content[_MFI_GCD['sender']] == self.myself_user_id:
                prefix_item.setBackground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(213, 221, 222)))
            self.lw_messages.addItem(prefix_item)

        message_text = message_content[_MFI_GCD['content']]
        message_item = QListWidgetItem(message_text)
        message_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'], message_content[_MFI_GCD['sender']])
        if message_content[_MFI_GCD['sender']] == self.myself_user_id:
            message_item.setBackground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(213, 221, 222)))
        self.lw_messages.addItem(message_item)


    def append_my_message(self):
        self.append_single_message(who=self.myself_user_id)


    def send_message(self):
        if len(self.le_input_message.text()) == 0:
            return

        self.append_my_message()
        message = self.le_input_message.text()
        client.send_add_general_message(self.myself_user_id, message)
        self.le_input_message.clear()


    def exit_chat(self):
        global selected_contact_user_id
        selected_contact_user_id = None
        pages_manager.switch_to_widget("menu")




# ----------------------------------------------------
#
#
#
#
#
#
#
# ----------------------------------------------------

class Conference(General_Chat, QWidget):
    def __init__(self) -> None:
        super().__init__()

    
    @overrides
    def on_switch(self):
        self.init_chat_data_load()


    @overrides
    def init_chat_data_load(self):
        if self.init_chat_data_loaded:
            return

        global selected_contact_user_id
        self.other_user_id = selected_contact_user_id
        self.init_chat_data_loaded = True
        self.label_chats_name.setText(self.other_user_id)
        last_messages = client.send_get_last_conference_messages(self.other_user_id)
        for message in reversed(last_messages):
            self.append_single_message(message_content=message)

    
    def send_message(self):
        if len(self.le_input_message.text()) == 0:
            return

        self.append_my_message()
        message = self.le_input_message.text()
        client.send_add_conference_message(self.myself_user_id, self.other_user_id, message)
        self.le_input_message.clear()




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
        self.lw_contacts.itemClicked.connect(self.open_chat)
        self.button_profile.clicked.connect(functools.partial(self.open_profile))
        self.le_search_bar.textChanged.connect(self.filtr_contacts)
        self.button_status_active.clicked.connect(functools.partial(self.change_my_status, _ASL['active']))
        self.button_status_break.clicked.connect(functools.partial(self.change_my_status, _ASL['break']))
        self.button_status_inactive.clicked.connect(functools.partial(self.change_my_status, _ASL['inactive']))
        # related to creating a conference
        self.create_conference_mode_enabled = False
        self.button_cancel_conference_create.setVisible(False)
        self.selected_items_set = set()


    @overrides
    def on_switch(self):
        self.clear_contacts_selection()
        self.check_for_conferences_button()
        self.load_contacts()


    def find_contact_by_text(self, text):
        for row_num in range(self.lw_contacts.count()):
            if text == self.lw_contacts.item(row_num).text():
                return self.lw_contacts.item(row_num)
        return None


    def validate_type_of_contact(self):
        # first item is being selected
        if not len(self.selected_items_set):
            selected_item = self.lw_contacts.currentItem()
            contact_type = selected_item.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['contact_type'])
            if contact_type == _CT['user']:
                self.selected_items_set.add(selected_item.text())
            else:
                selected_item.setSelected(False)
            return
        # more then 1 elements are selected.
        # get names of items
        currently_selected = set([item.text() for item in self.lw_contacts.selectedItems()])
        just_selected_text = list(self.selected_items_set.symmetric_difference(currently_selected)).pop()
        just_selected_item = self.find_contact_by_text(just_selected_text)
        contact_type = just_selected_item.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['contact_type'])
        if contact_type != _CT['user']:
            currently_selected.remove(just_selected_text)
            just_selected_item.setSelected(False)
        self.selected_items_set = currently_selected


    def clear_contacts_selection(self):
        for contact in self.lw_contacts.selectedItems():
            contact.setSelected(False)
        

    def check_for_conferences_button(self):
        # after first load theres no need for doing that anymore
        if self.lw_contacts.count() != 0:
            return

        global myself
        role = client.load_init_profile_data(myself)['role']
        if role == 'admin' or role == 'mod':
            self.button_create_conference.setVisible(True)
            self.button_create_conference.clicked.connect(self.switch_create_conference_mode)
            self.button_cancel_conference_create.clicked.connect(self.switch_create_conference_mode)
        else:
            self.button_create_conference.setVisible(False)

    
    def switch_create_conference_mode(self):
        if self.create_conference_mode_enabled:
            self.create_conference_mode_enabled = False
            self.button_cancel_conference_create.setVisible(False)
            self.button_create_conference.setText("Create conference")
            self.button_create_conference.clicked.disconnect(self.make_conference)
            self.button_create_conference.clicked.connect(self.switch_create_conference_mode)
            # one item possible to select at the time
            self.lw_contacts.setSelectionMode(1)
            self.lw_contacts.itemClicked.disconnect(self.validate_type_of_contact)
            self.lw_contacts.itemClicked.connect(self.open_chat)
            self.clear_contacts_selection()
            self.selected_items_set = set()
        else: 
            self.create_conference_mode_enabled = True
            self.button_cancel_conference_create.setVisible(True)
            self.button_create_conference.setText("Select users and create")
            self.button_create_conference.clicked.disconnect(self.switch_create_conference_mode)
            self.button_create_conference.clicked.connect(self.make_conference)
            # select multiple items - allows selecting multiple contacts
            self.lw_contacts.setSelectionMode(2)
            self.lw_contacts.itemClicked.disconnect(self.open_chat)
            self.lw_contacts.itemClicked.connect(self.validate_type_of_contact)


    def make_conference(self):
        # select at least one item
        if not len(self.lw_contacts.selectedItems()):
            return
        
        # gather users ids that has been selected,
        # add user_id of user creating that conference
        global myself
        selected_user_ids = [myself]
        for contact in self.lw_contacts.selectedItems():
            user_id = contact.data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'])
            selected_user_ids.append(user_id)
        # display message box to approve conference creation
        conference_name, status = QInputDialog().getText(
            self, "Create conference", "Conference name:", QLineEdit.Normal
        )
        if conference_name and status:
            qmb_inform_user = QMessageBox()
            qmb_inform_user.setWindowTitle("Conference create")
            qmb_inform_user.setText(f"Do you want to create a conference named {conference_name}?")
            qmb_inform_user.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            decision = qmb_inform_user.exec_()
            if decision != QMessageBox.Yes:
                return
        else:
            return
        # user decided to create a conference 
        # and provied proper name for it
        status = client.send_create_conference(conference_name, myself, selected_user_ids)
        if status:
            qmb_inform_user = QMessageBox()
            qmb_inform_user.setWindowTitle("Conference create")
            qmb_inform_user.setText(f"Conference {conference_name} successfully created.")
            qmb_inform_user.setStandardButtons(QMessageBox.Ok)
            qmb_inform_user.exec_()
            self.switch_create_conference_mode()
        

    def filtr_contacts(self, text):
        for row_num in range(self.lw_contacts.count()):
            user_name = self.lw_contacts.item(row_num).text()
            if user_name.lower().find(text.lower()) > -1:
                self.lw_contacts.item(row_num).setHidden(False)
            else:
                self.lw_contacts.item(row_num).setHidden(True)


    # onclick function for the client himself
    def change_my_status(self, status):
        client.send_change_status(myself, status)


    # creates appropiate icon for the users active status
    def get_status_icon(self, status):
        pixmap = QPixmap(menu_data['icon_size'], menu_data['icon_size'])
        status_icon_color = ''
        if status == _ASL['active']:
            status_icon_color = _ASI['active']
        elif status == _ASL['break']:
            status_icon_color = _ASI['break']
        elif status == _ASL['inactive']:
            status_icon_color = _ASI['inactive']
        pixmap.fill(PyQt5.QtGui.QColor(status_icon_color))
        return PyQt5.QtGui.QIcon(pixmap)


    # updating other users statuses (including icons)
    def set_other_status(self, who, status):
        # find item (user, based on his user_id)
        for row_num in range(self.lw_contacts.count()):
            some_user_id = self.lw_contacts.item(row_num).data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'])
            if who == some_user_id:
                status_icon = self.get_status_icon(status)
                self.lw_contacts.item(row_num).setIcon(status_icon)
                return


    def add_contact(self):
        pass


    def load_contacts(self):
        if self.lw_contacts.count() != 0:
            return

        # general chat
        icon = self.get_status_icon(_ASL['active'])
        general_chat_item = QListWidgetItem(menu_data['general_chat_name'])
        general_chat_item.setIcon(icon)
        general_chat_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'], "General")
        general_chat_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['contact_type'], _CT['general'])
        self.lw_contacts.addItem(general_chat_item)

        # conferences
        conferences = client.send_load_all_conferences()
        for conference in conferences:
            icon = self.get_status_icon(_ASL['active'])
            contact_item = QListWidgetItem(f"Conference {conference}")
            contact_item.setIcon(icon)
            contact_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'], conference)
            contact_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['contact_type'], _CT["conference"])
            self.lw_contacts.addItem(contact_item)

        # get regular contacts - other users 
        contacts = client.send_load_contacts(myself)
        statuses = client.send_get_other_statuses(myself)
        for single_user_data  in contacts:
            # fetching data and creating an item
            user_id, name, surname = single_user_data
            user_name = name + ' ' + surname
            list_item = QListWidgetItem(user_name)
            # fetching status and seting up the icon for the item
            pixmap = QPixmap(menu_data['icon_size'], menu_data['icon_size'])
            status_color = ''
            # users that are active/break
            if user_id in statuses:
                status = statuses[user_id]    
                if status == _ASL['active']:
                    status_color = _ASI['active']
                elif status == _ASL['break']:
                    status_color = _ASI['break']
            else:
                status_color = _ASI['inactive']
            pixmap.fill(PyQt5.QtGui.QColor(status_color))
            status_icon = PyQt5.QtGui.QIcon(pixmap)
            list_item.setIcon(status_icon)
            #data
            list_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'], user_id)
            list_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['name'], name)
            list_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['surname'], surname)
            list_item.setData(PyQt5.QtCore.Qt.UserRole + user_data_indexes['contact_type'], _CT["user"])
            self.lw_contacts.addItem(list_item)


    # for other classes or places where data hidden in contact is needed
    # (data is accessed through that item)    
    def get_contact_item(self, user_id):
        for row_num in range(self.lw_contacts.count()):
            some_user_id = self.lw_contacts.item(row_num).data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'])
            if user_id == some_user_id:
                return self.lw_contacts.item(row_num)


    def open_profile(self):
        if not pages_manager.if_widget_exists(pages_manager):
            pages_manager.add_widget(
                {
                    'alias':    'profile',
                    'widget':   Profile(),
                    'config':   profile_data
                }
            )
        pages_manager.switch_to_widget('profile')


    # onclick for contact on the users list
    def open_chat(self):
        selected_chat = self.lw_contacts.currentItem().data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['user_id'])
        selected_contact_type = self.lw_contacts.currentItem().data(PyQt5.QtCore.Qt.UserRole + user_data_indexes['contact_type'])
        if selected_contact_type == _CT['user']:
            global myself, selected_contact_user_id
            # chat pages are named after user_id
            # of a user that client is chatting with
            selected_contact_user_id = selected_chat
            if not chat_pages.check_if_exists(selected_contact_user_id):
                chat_pages.create_new_page(selected_contact_user_id)
            chat_pages.switch_to_page(selected_contact_user_id)    
        elif selected_contact_type == _CT['general']:
            if not pages_manager.if_widget_exists("general"):
                pages_manager.add_widget(
                    {
                        'alias':    'general',
                        'widget':   General_Chat(),
                        'config':   chat_data
                    }
                )
            pages_manager.switch_to_widget("general")
        elif selected_contact_type == _CT['conference']:
            selected_contact_user_id = selected_chat
            # check if user can enter conference
            status = client.send_check_if_user_in_conference(selected_contact_user_id, myself)
            if not status:
                qmb_inform_user = QMessageBox()
                qmb_inform_user.setWindowTitle("Conference")
                qmb_inform_user.setText(f"Conference {selected_contact_user_id} is not available for you.")
                qmb_inform_user.setStandardButtons(QMessageBox.Ok)
                qmb_inform_user.exec_()
                return
            if not pages_manager.if_widget_exists(selected_chat):
                pages_manager.add_widget(
                    {
                        'alias':    selected_contact_user_id,
                        'widget':   Conference(),
                        'config':   chat_data   
                    }
                )
            pages_manager.switch_to_widget(selected_contact_user_id)
            



# ----------------------------------------------------
#
#
#
#
#
#
#
# ----------------------------------------------------

class Profile(QWidget, Page):
    def __init__(self) -> None:
        super(Profile, self).__init__()
        loadUi(profile_data['path'], self)
        self.button_exit_profile.clicked.connect(functools.partial(self.switch_to, 'menu'))
        self.button_add_new_user_menu.clicked.connect(functools.partial(self.switch_to, 'add_new_user_form'))
        self.button_change_password.clicked.connect(self.change_password)
        self.button_change_personal_color.clicked.connect(self.change_personal_color)
        self.button_change_description.clicked.connect(self.change_description)
        self.le_password.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        self.le_retype_password.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)


    @overrides
    def on_switch(self):
        self.init_user_data()
        if pages_manager.if_widget_exists("add_new_user_form"):
            pages_manager.remove_widget("add_new_user_form")
            pages_manager.switch_to_widget("menu")
        


    def switch_to(self, page_alias):
        if page_alias == "add_new_user_form":
            pages_manager.add_widget(
                { 
                    "alias": "add_new_user_form",
                    "widget": Add_New_User_Form(),
                    "config": add_new_user_form_data
                }
            )
            pages_manager.switch_to_widget("add_new_user_form")
        elif page_alias == "menu":
            pages_manager.switch_to_widget("menu")


    def init_user_data(self):
        # admin prefix starts with 0000
        if myself[:4] != '0000':
            self.button_add_new_user_menu.setVisible(False)

        data = client.load_init_profile_data(myself)
        if not data:
            print('[CLIENT] Failed to load profile data.')

        self.te_description.setText(data['description'])
        temp_index = self.combo_personal_color.findText(data['color'])
        self.combo_personal_color.setCurrentIndex(temp_index)


    def change_password(self):
        if len(self.le_password.text()) <= 7:
            self.label_password_change_issue.setText('your new passwords lenght is to small')
            self.label_password_change_issue.setVisible(True)
            return
        
        self.label_password_change_issue.setText('')

        if self.le_password.text() != self.le_retype_password.text():
            self.label_password_change_issue.setText('password dont match')
            self.label_password_change_issue.setVisible(True)
            return

        self.send_any_change_request('password')
        self.le_password.clear()
        self.le_retype_password.clear()


    def change_personal_color(self):
        self.send_any_change_request('personal_color')
    

    def change_description(self):
        self.send_any_change_request('description')
        
    
    def send_any_change_request(self, which):
        if which == 'password':
            result = client.send_profile_change('password', myself, self.le_password.text())
        elif which == 'description':
            result = client.send_profile_change('description', myself, self.te_description.toPlainText())
        elif which == 'personal_color':
            result = client.send_profile_change('personal_color', myself, str(self.combo_personal_color.currentText()))

        if result:
            qmb_inform_user = QMessageBox()
            qmb_inform_user.setWindowTitle("Profile")
            qmb_inform_user.setText("Profile updated.")
            qmb_inform_user.setStandardButtons(QMessageBox.Ok)
            qmb_inform_user.exec_()
        



# ----------------------------------------------------
#
#
#
#
#
#
#
# ----------------------------------------------------




pages_manager.add_widgets(
    {
        "alias": "login_form",
        "widget": Login_Form(),
        "config": login_form_data
    }
)
pages_manager.show()

try:
    sys.exit(app.exec_())
except:
    print("App exits")



