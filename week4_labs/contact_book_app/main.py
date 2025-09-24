import flet as ft
from database import init_db, toggle_favorite_db
from app_logic import display_contacts, add_contact, show_contact_details

def main(page: ft.Page):
    page.title = "📱 Enhanced Contact Book"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 900
    page.window_height = 700
    page.padding = 20
    page.bgcolor = ft.colors.GREY_50

    db_conn = init_db()
    
    # Theme toggle state
    is_dark_mode = False
    
    def toggle_theme(e):
        nonlocal is_dark_mode
        is_dark_mode = not is_dark_mode
        if is_dark_mode:
            page.theme_mode = ft.ThemeMode.DARK
            page.bgcolor = ft.colors.GREY_900
            theme_icon.icon = ft.icons.LIGHT_MODE
            theme_icon.tooltip = "Switch to Light Mode"
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            page.bgcolor = ft.colors.GREY_50
            theme_icon.icon = ft.icons.DARK_MODE
            theme_icon.tooltip = "Switch to Dark Mode"
        page.update()
    
    # Header with title and theme toggle
    theme_icon = ft.IconButton(
        icon=ft.icons.DARK_MODE,
        tooltip="Switch to Dark Mode",
        on_click=toggle_theme,
        icon_size=24
    )
    
    header = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Icon(ft.icons.CONTACTS, size=32, color=ft.colors.BLUE_700),
                ft.Text(
                    "Enhanced Contact Book",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_700
                )
            ]),
            ft.Row([
                theme_icon,
                ft.Container(
                    content=ft.Text("0 contacts", size=14, color=ft.colors.GREY_600),
                    id="contact_count"
                )
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.only(bottom=20)
    )
    
    # Search and filter section
    search_field = ft.TextField(
        label="🔍 Search contacts...",
        width=300,
        border_radius=10,
        filled=True,
        bgcolor=ft.colors.WHITE,
        on_change=lambda e: filter_contacts()
    )
    
    category_dropdown = ft.Dropdown(
        label="Filter by Category",
        width=200,
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Family"),
            ft.dropdown.Option("Friends"),
            ft.dropdown.Option("Work"),
            ft.dropdown.Option("Other")
        ],
        value="All",
        border_radius=10,
        filled=True,
        bgcolor=ft.colors.WHITE,
        on_change=lambda e: filter_contacts()
    )
    
    def filter_contacts():
        display_contacts(
            page, 
            contacts_list_view, 
            db_conn,
            search_field.value or '',
            category_dropdown.value or 'All',
            update_contact_count
        )
    
    # Contact list view
    contacts_list_view = ft.ListView(
        expand=1,
        spacing=10,
        auto_scroll=True,
        padding=ft.padding.all(10)
    )
    
    # Input fields for new contact
    name_input = ft.TextField(
        label="Full Name *",
        width=280,
        border_radius=10,
        filled=True,
        bgcolor=ft.colors.WHITE,
        prefix_icon=ft.icons.PERSON
    )
    
    phone_input = ft.TextField(
        label="Phone Number *",
        width=280,
        border_radius=10,
        filled=True,
        bgcolor=ft.colors.WHITE,
        prefix_icon=ft.icons.PHONE
    )
    
    email_input = ft.TextField(
        label="Email Address",
        width=280,
        border_radius=10,
        filled=True,
        bgcolor=ft.colors.WHITE,
        prefix_icon=ft.icons.EMAIL
    )
    
    address_input = ft.TextField(
        label="Address",
        width=280,
        border_radius=10,
        filled=True,
        bgcolor=ft.colors.WHITE,
        prefix_icon=ft.icons.HOME,
        multiline=True,
        max_lines=2
    )
    
    category_input = ft.Dropdown(
        label="Category",
        width=280,
        options=[
            ft.dropdown.Option("Family"),
            ft.dropdown.Option("Friends"),
            ft.dropdown.Option("Work"),
            ft.dropdown.Option("Other")
        ],
        value="Other",
        border_radius=10,
        filled=True,
        bgcolor=ft.colors.WHITE
    )
    
    notes_input = ft.TextField(
        label="Notes",
        width=280,
        border_radius=10,
        filled=True,
        bgcolor=ft.colors.WHITE,
        prefix_icon=ft.icons.NOTES,
        multiline=True,
        max_lines=2
    )
    
    inputs = (name_input, phone_input, email_input, address_input, category_input, notes_input)
    
    # Add contact button
    add_button = ft.ElevatedButton(
        text="Add Contact",
        icon=ft.icons.PERSON_ADD,
        width=200,
        height=50,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.BLUE_700,
            color=ft.colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn, update_contact_count, filter_contacts)
    )
    
    clear_button = ft.OutlinedButton(
        text="Clear Form",
        icon=ft.icons.CLEAR,
        width=150,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=lambda e: clear_form()
    )
    
    def clear_form():
        for field in inputs:
            if hasattr(field, 'value'):
                field.value = ""
            elif hasattr(field, 'value') and isinstance(field, ft.Dropdown):
                field.value = "Other" if field == category_input else ""
        category_input.value = "Other"
        page.update()
    
    def update_contact_count():
        # This will be called from app_logic to update the count
        pass
    
    # Create tabs for better organization
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="📋 View Contacts",
                icon=ft.icons.CONTACTS,
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            search_field,
                            category_dropdown
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Container(height=10),
                        ft.Container(
                            content=contacts_list_view,
                            bgcolor=ft.colors.WHITE if not is_dark_mode else ft.colors.GREY_800,
                            border_radius=15,
                            padding=10,
                            expand=True
                        )
                    ], expand=True),
                    padding=20
                )
            ),
            ft.Tab(
                text="➕ Add Contact",
                icon=ft.icons.PERSON_ADD,
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Add New Contact",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLUE_700
                        ),
                        ft.Container(height=20),
                        ft.Row([
                            ft.Column([
                                name_input,
                                ft.Container(height=10),
                                phone_input,
                                ft.Container(height=10),
                                email_input
                            ]),
                            ft.Container(width=20),
                            ft.Column([
                                address_input,
                                ft.Container(height=10),
                                category_input,
                                ft.Container(height=10),
                                notes_input
                            ])
                        ]),
                        ft.Container(height=30),
                        ft.Row([
                            add_button,
                            ft.Container(width=20),
                            clear_button
                        ])
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=20
                )
            )
        ]
    )
    
    # Main layout
    page.add(
        ft.Column([
            header,
            ft.Container(
                content=tabs,
                expand=True,
                bgcolor=ft.colors.WHITE if not is_dark_mode else ft.colors.GREY_800,
                border_radius=15,
                padding=10
            )
        ], expand=True)
    )
    
    # Initial load
    filter_contacts()

if __name__ == "__main__":
    ft.app(target=main)