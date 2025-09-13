import flet as ft
import mysql.connector
from db_connection import connect_db

def main(page: ft.Page):
    # Page settings
    page.title = "User Login"
    page.window_width = 400
    page.window_height = 350
    page.window_center()
    page.window_frameless = True
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.AMBER_ACCENT

    # Title
    title = ft.Text(
        "User Login",
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial",
        text_align=ft.TextAlign.CENTER
    )

    # Username field
    username = ft.TextField(
        label="User name",
        hint_text="Enter your user name",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        icon=ft.Icons.PERSON,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
    )

    # Password field
    password = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your secret key",
        width=300,
        password=True,
        can_reveal_password=True,
        icon=ft.Icons.LOCK,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
    )

    # Async login handler
    async def login_click(e):
        uname = username.value.strip()
        pwd = password.value.strip()

        if not uname or not pwd:
            await page.dialog_async(
                ft.AlertDialog(
                    title=ft.Text("Input Error"),
                    content=ft.Text("Please enter username and password"),
                    icon=ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE)
                )
            )
            return

        try:
            conn = connect_db()
            if conn is None:
                raise mysql.connector.Error("DB connection failed")

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (uname, pwd))
            result = cursor.fetchone()
            conn.close()

            if result:
                await page.dialog_async(
                    ft.AlertDialog(
                        title=ft.Text("Login Successful"),
                        content=ft.Text(f"Welcome, {uname}!"),
                        icon=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN)
                    )
                )
            else:
                await page.dialog_async(
                    ft.AlertDialog(
                        title=ft.Text("Login Failed"),
                        content=ft.Text("Invalid username or password"),
                        icon=ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED)
                    )
                )
        except mysql.connector.Error:
            await page.dialog_async(
                ft.AlertDialog(
                    title=ft.Text("Database Error"),
                    content=ft.Text("An error occurred while connecting to the database"),
                    icon=ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE)
                )
            )

    # Login button
    login_btn = ft.ElevatedButton(
        text="Login",
        icon=ft.Icons.LOGIN,
        width=100,
        on_click=login_click
    )

    # Layout
    page.add(
        title,
        ft.Container(content=ft.Column([username, password], spacing=20)),
        ft.Container(
            content=login_btn,
            alignment=ft.alignment.top_right,
            margin=ft.Margin(0, 20, 40, 0)
        )
    )

ft.app(target=main)
