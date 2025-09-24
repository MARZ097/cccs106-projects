import flet as ft
from database import (
    update_contact_db, delete_contact_db, add_contact_db, 
    get_all_contacts_db, toggle_favorite_db
)

def display_contacts(page, contacts_list_view, db_conn, search_term='', category_filter='All', update_count_callback=None):
    """Display contacts with enhanced UI using cards"""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search_term, category_filter)
    
    # Update contact count
    if update_count_callback:
        count_text = f"{len(contacts)} contact{'s' if len(contacts) != 1 else ''}"
        # Find and update the contact count display
        for control in page.controls:
            if hasattr(control, 'content') and hasattr(control.content, 'controls'):
                for row in control.content.controls:
                    if hasattr(row, 'controls'):
                        for item in row.controls:
                            if hasattr(item, 'controls'):
                                for subitem in item.controls:
                                    if hasattr(subitem, 'content') and hasattr(subitem.content, 'value'):
                                        if 'contact' in str(subitem.content.value):
                                            subitem.content.value = count_text
                                            page.update()
                                            break

    if not contacts:
        empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.icons.PEOPLE_OUTLINE,
                    size=80,
                    color=ft.colors.GREY_400
                ),
                ft.Text(
                    "No contacts found" if search_term or category_filter != 'All' else "No contacts yet",
                    size=18,
                    color=ft.colors.GREY_600,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Add your first contact to get started!" if not search_term and category_filter == 'All' else "Try adjusting your search or filter",
                    size=14,
                    color=ft.colors.GREY_500,
                    text_align=ft.TextAlign.CENTER
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            padding=40
        )
        contacts_list_view.controls.append(empty_state)
    else:
        for contact in contacts:
            contact_id, name, phone, email, address, category, notes, favorite = contact
            
            # Category icons and colors
            category_config = {
                'Family': {'icon': ft.icons.FAMILY_RESTROOM, 'color': ft.colors.PINK_400},
                'Friends': {'icon': ft.icons.PEOPLE, 'color': ft.colors.GREEN_400},
                'Work': {'icon': ft.icons.WORK, 'color': ft.colors.BLUE_400},
                'Other': {'icon': ft.icons.PERSON, 'color': ft.colors.GREY_400}
            }
            
            config = category_config.get(category, category_config['Other'])
            
            # Create contact card
            contact_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        # Header row with avatar and favorite
                        ft.Row([
                            ft.Container(
                                content=ft.Stack([
                                    ft.CircleAvatar(
                                        content=ft.Icon(
                                            config['icon'],
                                            size=24,
                                            color=ft.colors.WHITE
                                        ),
                                        bgcolor=config['color'],
                                        radius=25
                                    ),
                                    ft.Container(
                                        content=ft.Icon(
                                            ft.icons.STAR,
                                            size=16,
                                            color=ft.colors.ORANGE
                                        ),
                                        visible=bool(favorite),
                                        top=-5,
                                        right=-5,
                                        bgcolor=ft.colors.WHITE,
                                        border_radius=10,
                                        padding=2
                                    )
                                ]),
                                width=60,
                                height=60
                            ),
                            ft.Expanded(
                                child=ft.Column([
                                    ft.Text(
                                        name,
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.GREY_800
                                    ),
                                    ft.Text(
                                        f"📱 {phone}",
                                        size=14,
                                        color=ft.colors.GREY_600
                                    ),
                                    ft.Text(
                                        f"📧 {email}" if email else "📧 No email",
                                        size=12,
                                        color=ft.colors.GREY_500
                                    ) if email else ft.Container()
                                ], spacing=2)
                            ),
                            ft.Container(
                                content=ft.Chip(
                                    label=ft.Text(category, size=12),
                                    bgcolor=config['color'],
                                    color=ft.colors.WHITE
                                ),
                                alignment=ft.alignment.top_right
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        
                        # Additional info (if available)
                        ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.HOME, size=16, color=ft.colors.GREY_500),
                                ft.Text(address, size=12, color=ft.colors.GREY_600)
                            ]) if address else ft.Container(),
                            ft.Row([
                                ft.Icon(ft.icons.NOTES, size=16, color=ft.colors.GREY_500),
                                ft.Text(notes, size=12, color=ft.colors.GREY_600, italic=True)
                            ]) if notes else ft.Container()
                        ], spacing=5),
                        
                        # Action buttons
                        ft.Row([
                            ft.IconButton(
                                icon=ft.icons.STAR if favorite else ft.icons.STAR_BORDER,
                                icon_color=ft.colors.ORANGE if favorite else ft.colors.GREY_400,
                                tooltip="Toggle Favorite",
                                on_click=lambda e, cid=contact_id: toggle_favorite(page, cid, db_conn, contacts_list_view, search_term, category_filter, update_count_callback)
                            ),
                            ft.IconButton(
                                icon=ft.icons.VISIBILITY,
                                icon_color=ft.colors.BLUE_600,
                                tooltip="View Details",
                                on_click=lambda e, c=contact: show_contact_details(page, c, db_conn, contacts_list_view, search_term, category_filter, update_count_callback)
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                icon_color=ft.colors.GREEN_600,
                                tooltip="Edit Contact",
                                on_click=lambda e, c=contact: open_edit_dialog(page, c, db_conn, contacts_list_view, search_term, category_filter, update_count_callback)
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                icon_color=ft.colors.RED_600,
                                tooltip="Delete Contact",
                                on_click=lambda e, cid=contact_id, cname=name: confirm_delete_contact(page, cid, cname, db_conn, contacts_list_view, search_term, category_filter, update_count_callback)
                            ),
                        ], alignment=ft.MainAxisAlignment.END)
                    ], spacing=10),
                    padding=15
                ),
                elevation=3,
                margin=ft.margin.only(bottom=10)
            )
            
            contacts_list_view.controls.append(contact_card)
    
    page.update()

def add_contact(page, inputs, contacts_list_view, db_conn, update_count_callback=None, refresh_callback=None):
    """Add a new contact with validation"""
    name_input, phone_input, email_input, address_input, category_input, notes_input = inputs
    
    # Validation
    if not name_input.value or not name_input.value.strip():
        show_snack_bar(page, "Name is required!", ft.colors.RED)
        return
    
    if not phone_input.value or not phone_input.value.strip():
        show_snack_bar(page, "Phone number is required!", ft.colors.RED)
        return
    
    # Add contact to database
    add_contact_db(
        db_conn,
        name_input.value.strip(),
        phone_input.value.strip(),
        email_input.value.strip() if email_input.value else '',
        address_input.value.strip() if address_input.value else '',
        category_input.value if category_input.value else 'Other',
        notes_input.value.strip() if notes_input.value else '',
        0  # favorite
    )
    
    # Clear form
    for field in inputs:
        if hasattr(field, 'value'):
            field.value = ""
    category_input.value = "Other"
    
    # Refresh display
    if refresh_callback:
        refresh_callback()
    
    show_snack_bar(page, f"Contact '{name_input.value}' added successfully!", ft.colors.GREEN)
    page.update()

def toggle_favorite(page, contact_id, db_conn, contacts_list_view, search_term='', category_filter='All', update_count_callback=None):
    """Toggle favorite status of a contact"""
    toggle_favorite_db(db_conn, contact_id)
    display_contacts(page, contacts_list_view, db_conn, search_term, category_filter, update_count_callback)

def confirm_delete_contact(page, contact_id, contact_name, db_conn, contacts_list_view, search_term='', category_filter='All', update_count_callback=None):
    """Show confirmation dialog before deleting contact"""
    def delete_confirmed(e):
        delete_contact_db(db_conn, contact_id)
        display_contacts(page, contacts_list_view, db_conn, search_term, category_filter, update_count_callback)
        dialog.open = False
        page.update()
        show_snack_bar(page, f"Contact '{contact_name}' deleted successfully!", ft.colors.ORANGE)
    
    def delete_cancelled(e):
        dialog.open = False
        page.update()
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.icons.WARNING, color=ft.colors.RED, size=28),
            ft.Text("Confirm Delete", size=20, weight=ft.FontWeight.BOLD)
        ]),
        content=ft.Container(
            content=ft.Column([
                ft.Text(
                    f"Are you sure you want to delete '{contact_name}'?",
                    size=16
                ),
                ft.Text(
                    "This action cannot be undone.",
                    size=14,
                    color=ft.colors.GREY_600,
                    italic=True
                )
            ], spacing=10),
            padding=10
        ),
        actions=[
            ft.TextButton(
                "Cancel",
                on_click=delete_cancelled,
                style=ft.ButtonStyle(color=ft.colors.GREY_600)
            ),
            ft.ElevatedButton(
                "Delete",
                on_click=delete_confirmed,
                style=ft.ButtonStyle(
                    bgcolor=ft.colors.RED_600,
                    color=ft.colors.WHITE
                ),
                icon=ft.icons.DELETE
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    page.dialog = dialog
    dialog.open = True
    page.update()

def open_edit_dialog(page, contact, db_conn, contacts_list_view, search_term='', category_filter='All', update_count_callback=None):
    """Open edit dialog for contact"""
    contact_id, name, phone, email, address, category, notes, favorite = contact
    
    # Create edit fields
    edit_name = ft.TextField(label="Full Name *", value=name, width=300)
    edit_phone = ft.TextField(label="Phone Number *", value=phone, width=300)
    edit_email = ft.TextField(label="Email Address", value=email or '', width=300)
    edit_address = ft.TextField(label="Address", value=address or '', width=300, multiline=True, max_lines=2)
    edit_category = ft.Dropdown(
        label="Category",
        value=category or 'Other',
        width=300,
        options=[
            ft.dropdown.Option("Family"),
            ft.dropdown.Option("Friends"),
            ft.dropdown.Option("Work"),
            ft.dropdown.Option("Other")
        ]
    )
    edit_notes = ft.TextField(label="Notes", value=notes or '', width=300, multiline=True, max_lines=2)
    edit_favorite = ft.Checkbox(label="Favorite Contact", value=bool(favorite))

    def save_changes(e):
        if not edit_name.value or not edit_name.value.strip():
            show_snack_bar(page, "Name is required!", ft.colors.RED)
            return
        
        if not edit_phone.value or not edit_phone.value.strip():
            show_snack_bar(page, "Phone number is required!", ft.colors.RED)
            return
        
        update_contact_db(
            db_conn,
            contact_id,
            edit_name.value.strip(),
            edit_phone.value.strip(),
            edit_email.value.strip() if edit_email.value else '',
            edit_address.value.strip() if edit_address.value else '',
            edit_category.value if edit_category.value else 'Other',
            edit_notes.value.strip() if edit_notes.value else '',
            1 if edit_favorite.value else 0
        )
        
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn, search_term, category_filter, update_count_callback)
        show_snack_bar(page, f"Contact '{edit_name.value}' updated successfully!", ft.colors.GREEN)

    def cancel_edit(e):
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.icons.EDIT, color=ft.colors.BLUE, size=28),
            ft.Text("Edit Contact", size=20, weight=ft.FontWeight.BOLD)
        ]),
        content=ft.Container(
            content=ft.Column([
                ft.Row([edit_name, edit_phone]),
                ft.Row([edit_email, edit_category]),
                edit_address,
                edit_notes,
                edit_favorite
            ], spacing=15),
            width=650,
            height=400
        ),
        actions=[
            ft.TextButton(
                "Cancel",
                on_click=cancel_edit,
                style=ft.ButtonStyle(color=ft.colors.GREY_600)
            ),
            ft.ElevatedButton(
                "Save Changes",
                on_click=save_changes,
                style=ft.ButtonStyle(
                    bgcolor=ft.colors.BLUE_600,
                    color=ft.colors.WHITE
                ),
                icon=ft.icons.SAVE
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    page.dialog = dialog
    dialog.open = True
    page.update()

def show_contact_details(page, contact, db_conn, contacts_list_view, search_term='', category_filter='All', update_count_callback=None):
    """Show detailed view of contact"""
    contact_id, name, phone, email, address, category, notes, favorite = contact
    
    # Category icons and colors
    category_config = {
        'Family': {'icon': ft.icons.FAMILY_RESTROOM, 'color': ft.colors.PINK_400},
        'Friends': {'icon': ft.icons.PEOPLE, 'color': ft.colors.GREEN_400},
        'Work': {'icon': ft.icons.WORK, 'color': ft.colors.BLUE_400},
        'Other': {'icon': ft.icons.PERSON, 'color': ft.colors.GREY_400}
    }
    
    config = category_config.get(category, category_config['Other'])
    
    def close_details(e):
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.CircleAvatar(
                content=ft.Icon(config['icon'], size=24, color=ft.colors.WHITE),
                bgcolor=config['color'],
                radius=20
            ),
            ft.Column([
                ft.Text(name, size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Icon(ft.icons.STAR, size=16, color=ft.colors.ORANGE) if favorite else ft.Container(),
                    ft.Text(category, size=14, color=ft.colors.GREY_600)
                ])
            ], spacing=2)
        ], spacing=15),
        content=ft.Container(
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.icons.PHONE, color=ft.colors.BLUE),
                    title=ft.Text("Phone"),
                    subtitle=ft.Text(phone, selectable=True)
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.EMAIL, color=ft.colors.GREEN),
                    title=ft.Text("Email"),
                    subtitle=ft.Text(email if email else "No email provided", selectable=True)
                ) if email else ft.Container(),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.HOME, color=ft.colors.ORANGE),
                    title=ft.Text("Address"),
                    subtitle=ft.Text(address if address else "No address provided", selectable=True)
                ) if address else ft.Container(),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.NOTES, color=ft.colors.PURPLE),
                    title=ft.Text("Notes"),
                    subtitle=ft.Text(notes if notes else "No notes", selectable=True)
                ) if notes else ft.Container(),
            ], spacing=10),
            width=400,
            height=300
        ),
        actions=[
            ft.ElevatedButton(
                "Close",
                on_click=close_details,
                style=ft.ButtonStyle(
                    bgcolor=ft.colors.BLUE_600,
                    color=ft.colors.WHITE
                )
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    
    page.dialog = dialog
    dialog.open = True
    page.update()

def show_snack_bar(page, message, color):
    """Show a snack bar with message"""
    page.show_snack_bar(
        ft.SnackBar(
            content=ft.Text(message, color=ft.colors.WHITE),
            bgcolor=color,
            duration=3000
        )
    )