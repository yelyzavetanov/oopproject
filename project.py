import flet as ft
import sqlite3


class BusinessDiaryApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Business Diary"
        self.page.theme_mode = "light"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.current_user = "unknown user"
        self.current_image_url = "./home01.gif"

        self.user_panel = UserPanel(self.page, self.update_navigation)
        self.navigation_panel = NavigationPanel(self.page, self.navigate, self.change_image)
        self.todo_list = ToDoList(self.page)
        self.notes = Notes(self.page)

        self.page.add(self.navigation_panel.panel_home)
        self.page.update()

    def change_image(self, e):
        self.navigation_panel.image.src = "./home02.gif" if self.navigation_panel.image.src == "./home01.gif" else "./home01.gif"
        self.page.update()

    def update_navigation(self):
        if len(self.page.navigation_bar.destinations) < 5:
            self.page.navigation_bar.destinations.append(
                ft.NavigationDestination(icon=ft.icons.NOTE, label="Notes")
            )
            self.page.update()

    def navigate(self, e):
        index = self.page.navigation_bar.selected_index
        self.page.clean()

        if index == 0:
            self.page.add(self.navigation_panel.panel_home)
        elif index == 1:
            self.page.add(self.user_panel.panel_auth)
        elif index == 2:
            self.page.add(self.user_panel.panel_register)
        elif index == 3:
            self.page.add(self.user_panel.panel_cabinet)
        elif index == 4:
            self.page.add(self.notes.panel_notes)
        self.page.update()


class Notes:
    def __init__(self, page):
        self.page = page
        self.notes = []
        self.notes_list = ft.Column()
        self.note_input = ft.TextField(hint_text="Enter your note", width=300, on_submit=self.add_note)
        self.add_button = ft.IconButton(icon=ft.icons.ADD_CIRCLE, on_click=self.add_note)

        self.panel_notes = ft.Column(
            [ft.Text("Notes"), ft.Row([self.note_input, self.add_button]), self.notes_list],
            alignment=ft.MainAxisAlignment.CENTER
        )

    def add_note(self, e):
        if self.note_input.value:
            self.notes.append(self.note_input.value)
            self.note_input.value = ""
            self.update_notes_list()

    def update_notes_list(self):
        self.notes_list.controls.clear()
        for note in self.notes:
            note_row = ft.Row(
                [
                    ft.Text(note),
                    ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, n=note: self.edit_note(n)),
                    ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, n=note: self.delete_note(n)),
                ]
            )
            self.notes_list.controls.append(note_row)
        self.page.update()

    def edit_note(self, note):
        self.note_input.value = note
        self.notes.remove(note)
        self.update_notes_list()

    def delete_note(self, note):
        self.notes.remove(note)
        self.update_notes_list()


class UserPanel:
    def __init__(self, page, update_navigation_callback):
        self.page = page
        self.update_navigation_callback = update_navigation_callback

        self.user_login = ft.TextField(label='Login', width=200, on_change=self.validate)
        self.user_pass = ft.TextField(label='Password', password=True, width=200, on_change=self.validate)
        self.btn_reg = ft.OutlinedButton(text="Register", width=200, on_click=self.register, disabled=True)
        self.btn_auth = ft.OutlinedButton(text="Login", width=200, on_click=self.auth_user, disabled=True)

        self.panel_register = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text('Registration'),
                        self.user_login,
                        self.user_pass,
                        self.btn_reg
                    ]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.panel_auth = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text('Login'),
                        self.user_login,
                        self.user_pass,
                        self.btn_auth
                    ]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.panel_cabinet = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Welcome to your personal account"),
                    ]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

    def register(self, e):
        try:
            db = sqlite3.connect('testdb.db')
            cur = db.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, login TEXT, password TEXT)""")
            cur.execute("INSERT INTO users (login, password) VALUES(?, ?)", (self.user_login.value, self.user_pass.value))
            db.commit()
            db.close()
            self.user_login.value = ''
            self.user_pass.value = ''
            self.btn_reg.disabled = True
            self.btn_reg.text = "Registered!"
            self.page.update()
        except sqlite3.Error as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Database error: {e}"))
            self.page.snack_bar.open = True
            self.page.update()

    def validate(self, e):
        self.btn_reg.disabled = not (self.user_login.value and self.user_pass.value)
        self.btn_auth.disabled = not (self.user_login.value and self.user_pass.value)
        self.page.update()

    def auth_user(self, e):
        try:
            db = sqlite3.connect('testdb.db')
            cur = db.cursor()
            cur.execute("SELECT * FROM users WHERE login = ? AND password = ?",
                        (self.user_login.value, self.user_pass.value))
            current_user_data = cur.fetchone()
            db.close()
            if current_user_data:
                self.update_navigation_callback()
                self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("User not found"))
                self.page.snack_bar.open = True
                self.page.update()
        except sqlite3.Error as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Database error: {e}"))
            self.page.snack_bar.open = True
            self.page.update()


class NavigationPanel:
    def __init__(self, page, navigate_callback, change_image_callback):
        self.page = page
        self.navigate_callback = navigate_callback
        self.page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.icons.HOME, label="Home"),
                ft.NavigationDestination(icon=ft.icons.VERIFIED_USER_OUTLINED, label="Login"),
                ft.NavigationDestination(icon=ft.icons.VERIFIED_USER, label="Registration"),
            ],
            on_change=navigate_callback
        )

        self.image = ft.Image(src="./home01.gif", width=80, height=80)
        self.image_container = ft.GestureDetector(content=self.image, on_tap=change_image_callback)

        self.panel_home = ft.Row(
            [ft.Column([ft.Text('Business diary'), self.image_container], alignment=ft.MainAxisAlignment.CENTER)],
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.panel_cabinet = ft.Row(
            [ft.Column([ft.Text("Personal account")], alignment=ft.MainAxisAlignment.CENTER)],
            alignment=ft.MainAxisAlignment.CENTER
        )


class ToDoList:
    def __init__(self, page):
        self.page = page
        self.todos = []
        self.todo_list = ft.Column()
        self.todo_input = ft.TextField(hint_text="What needs to be done?", width=300, on_submit=self.add_todo_item)
        self.add_button = ft.IconButton(icon=ft.icons.ADD_CIRCLE, on_click=self.add_todo_item)
        self.filter_tabs = ft.Tabs(
            selected_index=0,
            tabs=[ft.Tab(text="All"), ft.Tab(text="Active"), ft.Tab(text="Completed")],
            on_change=lambda e: self.filter_tasks(e.control.selected_index)
        )

        self.panel_todo = ft.Column(
            [ft.Text("To-Do List"), ft.Row([self.todo_input, self.add_button]), self.filter_tabs, self.todo_list],
            alignment=ft.MainAxisAlignment.CENTER
        )

    def add_todo_item(self, e):
        if self.todo_input.value:
            self.todos.append({"task": self.todo_input.value, "completed": False})
            self.todo_input.value = ""
            self.update_todo_list()

    def update_todo_list(self):
        self.todo_list.controls.clear()
        for todo in self.todos:
            task_row = ft.Row(
                [
                    ft.Checkbox(value=todo["completed"],
                                on_change=lambda e, t=todo: self.update_task_status(t, e.control.value)),
                    ft.Text(todo["task"]),
                    ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, t=todo: self.edit_task(t)),
                    ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, t=todo: self.delete_task(t)),
                ]
            )
            self.todo_list.controls.append(task_row)
        self.page.update()

    def update_task_status(self, task, status):
        task["completed"] = status
        self.update_todo_list()

    def edit_task(self, task):
        self.todo_input.value = task["task"]
        self.todos.remove(task)
        self.update_todo_list()

    def delete_task(self, task):
        self.todos.remove(task)
        self.update_todo_list()

    def filter_tasks(self, index):
        filtered_todos = self.todos
        if index == 1:
            filtered_todos = [todo for todo in self.todos if not todo["completed"]]
        elif index == 2:
            filtered_todos = [todo for todo in self.todos if todo["completed"]]

        self.todo_list.controls.clear()
        for todo in filtered_todos:
            task_row = ft.Row(
                [
                    ft.Checkbox(value=todo["completed"], on_change=lambda e, t=todo: self.update_task_status(t, e.control.value)),
                    ft.Text(todo["task"]),
                    ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, t=todo: self.edit_task(t)),
                    ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, t=todo: self.delete_task(t)),
                ]
            )
            self.todo_list.controls.append(task_row)
        self.page.update()


def main(page: ft.Page):
    app = BusinessDiaryApp(page)


ft.app(target=main)
