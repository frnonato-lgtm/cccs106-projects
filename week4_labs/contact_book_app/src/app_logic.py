# app_logic.py
import flet as ft
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db

def display_contacts(page, contacts_list_view, db_conn, search_term=""):
    """Fetches and displays all contacts in the ListView."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search_term)
    for contact in contacts:
        contact_id, name, phone, email = contact
        contacts_list_view.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                                            ft.Row([ft.Icon(ft.Icons.PHONE), ft.Text(phone)]),
                                            ft.Row([ft.Icon(ft.Icons.EMAIL), ft.Text(email)]),
                                        ],
                                        expand=True,
                                    ),
                                    ft.PopupMenuButton(
                                        icon=ft.Icons.MORE_VERT,
                                        items=[
                                            ft.PopupMenuItem(
                                                text="Edit",
                                                icon=ft.Icons.EDIT,
                                                on_click=lambda _, c=contact: open_edit_dialog(page, c, db_conn, contacts_list_view)
                                            ),
                                            ft.PopupMenuItem(),
                                            ft.PopupMenuItem(
                                                text="Delete",
                                                icon=ft.Icons.DELETE,
                                                on_click=lambda _, cid=contact_id: confirm_delete(page, cid, db_conn, contacts_list_view)
                                            ),
                                        ],
                                    ),
                                ]
                            )
                        ]
                    ),
                    padding=10
                )
            )
        )
    page.update()

def add_contact(page, inputs, contacts_list_view, db_conn, search_field):
    """Adds a new contact and refreshes the list."""
    name_input, phone_input, email_input = inputs
    if not name_input.value.strip():
        name_input.error_text = "Name cannot be empty"
        page.update()
        return
    name_input.error_text = None
    add_contact_db(db_conn, name_input.value, phone_input.value, email_input.value)
    for field in inputs:
        field.value = ""
    display_contacts(page, contacts_list_view, db_conn, search_field.value)
    page.update()

def delete_contact(page, contact_id, db_conn, contacts_list_view, search_term=""):
    """Deletes a contact and refreshes the list."""
    delete_contact_db(conn=db_conn, contact_id=contact_id)
    display_contacts(page, contacts_list_view, db_conn, search_term)

def confirm_delete(page, contact_id, db_conn, contacts_list_view):
    """Asks for confirmation before deleting a contact."""
    def yes_action(e):
        delete_contact(page, contact_id, db_conn, contacts_list_view)
        dialog.open = False
        page.update()
    def no_action(e):
        dialog.open = False
        page.update()
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Delete"),
        content=ft.Text("Are you sure you want to delete this contact?"),
        actions=[
            ft.TextButton("No", on_click=no_action),
            ft.TextButton(
                content=ft.Text("Yes", color=ft.Colors.RED),
                on_click=yes_action
            ),
        ],
    )
    page.open(dialog)

def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    """Opens a dialog to edit a contact's details."""
    contact_id, name, phone, email = contact
    edit_name = ft.TextField(label="Name", value=name, width=350)
    edit_phone = ft.TextField(label="Phone", value=phone, width=350)
    edit_email = ft.TextField(label="Email", value=email, width=350)

    # Apply colors based on theme
    def apply_edit_colors():
        fields = [edit_name, edit_phone, edit_email]
        if page.theme_mode == ft.ThemeMode.DARK:
            for f in fields:
                f.color = ft.Colors.WHITE
                f.border_color = ft.Colors.WHITE
        else:
            for f in fields:
                f.color = ft.Colors.BLACK
                f.border_color = ft.Colors.BLACK

    apply_edit_colors()

    def save_and_close(e):
        if not edit_name.value.strip():
            edit_name.error_text = "Name cannot be empty"
            page.update()
            return
        edit_name.error_text = None
        update_contact_db(db_conn, contact_id, edit_name.value, edit_phone.value, edit_email.value)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)

    dialog_content = ft.Container(
        content=ft.Column(
            [edit_name, edit_phone, edit_email],
            tight=True
        ),
        padding=20,
        width=400
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=dialog_content,
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
            ft.TextButton("Save", on_click=save_and_close),
        ]
    )

    page.open(dialog)