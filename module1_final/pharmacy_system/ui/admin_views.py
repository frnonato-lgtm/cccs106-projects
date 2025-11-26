import flet as ft
from database import get_db_connection

# Just a simple dashboard for the admin
def AdminDashboard():
    return ft.Column([
        ft.Text("Admin Dashboard", size=25, weight="bold"),
        ft.Text("System Overview and User Management.")
    ])

# Shows a list of all users in the database
def UserManagement():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()

    return ft.ListView(
        expand=True,
        controls=[
            ft.ListTile(
                leading=ft.Icon(ft.Icons.SUPERVISED_USER_CIRCLE),
                title=ft.Text(u['full_name']),
                subtitle=ft.Text(f"Role: {u['role']}")
            ) for u in users
        ]
    )