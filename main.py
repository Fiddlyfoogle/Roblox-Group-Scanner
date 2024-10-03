import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import os
import threading

def get_group_info(group_id):
    try:
        # Get basic group info
        group_info_url = f"https://groups.roblox.com/v1/groups/{group_id}"
        group_info = requests.get(group_info_url).json()

        # Get group roles
        roles_url = f"https://groups.roblox.com/v1/groups/{group_id}/roles"
        roles = requests.get(roles_url).json()['roles']

        # Get members for each role
        members_by_role = {}
        for role in roles:
            role_id = role['id']
            role_name = role['name']
            members = []
            cursor = ""
            while True:
                members_url = f"https://groups.roblox.com/v1/groups/{group_id}/roles/{role_id}/users?limit=100&cursor={cursor}"
                response = requests.get(members_url).json()
                members.extend(response['data'])
                cursor = response.get('nextPageCursor')
                if not cursor:
                    break
            members_by_role[role_name] = members

        return {
            'name': group_info['name'],
            'id': group_info['id'],
            'description': group_info['description'],
            'owner': group_info['owner'],
            'memberCount': group_info['memberCount'],
            'members_by_role': members_by_role
        }
    except requests.RequestException as e:
        return f"Failed to fetch group info: {e}"

def save_group_info(group_id, folder_path):
    info = get_group_info(group_id)
    if isinstance(info, str):  # Error occurred
        return info

    file_path = os.path.join(folder_path, f"group_{group_id}_info.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"Group Name: {info['name']}\n")
        f.write(f"Group ID: {info['id']}\n")
        f.write(f"Description: {info['description']}\n")
        f.write(f"Owner: {info['owner']['username']} (ID: {info['owner']['userId']})\n")
        f.write(f"Total Members: {info['memberCount']}\n")
        f.write("\nMembers by Role:\n")
        for role, members in info['members_by_role'].items():
            f.write(f"\n{role} ({len(members)} members):\n")
            for member in members:
                f.write(f"  - {member['username']} (ID: {member['userId']})\n")

    return f"Group information saved to {file_path}"

def fetch_and_save():
    group_id = group_id_entry.get()
    folder_path = folder_path_var.get()

    if not group_id or not folder_path:
        messagebox.showerror("Error", "Please enter a group ID and select a folder.")
        return

    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Fetching and saving group info... Please wait.\n")
    fetch_button.config(state=tk.DISABLED)

    def fetch_thread():
        result = save_group_info(group_id, folder_path)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, result)
        fetch_button.config(state=tk.NORMAL)

    threading.Thread(target=fetch_thread, daemon=True).start()

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_path_var.set(folder_path)

# Create the main window
root = tk.Tk()
root.title("Roblox Group Info Saver")
root.geometry("600x400")

# Create and pack the input frame
input_frame = ttk.Frame(root, padding="10")
input_frame.pack(fill=tk.X)

group_id_label = ttk.Label(input_frame, text="Enter Group ID:")
group_id_label.grid(row=0, column=0, sticky=tk.W)

group_id_entry = ttk.Entry(input_frame, width=20)
group_id_entry.grid(row=0, column=1, padx=5)

folder_path_var = tk.StringVar()
folder_path_label = ttk.Label(input_frame, text="Select Folder:")
folder_path_label.grid(row=1, column=0, sticky=tk.W, pady=5)

folder_path_entry = ttk.Entry(input_frame, textvariable=folder_path_var, width=40)
folder_path_entry.grid(row=1, column=1, padx=5, pady=5)

folder_button = ttk.Button(input_frame, text="Browse", command=select_folder)
folder_button.grid(row=1, column=2, padx=5, pady=5)

fetch_button = ttk.Button(input_frame, text="Fetch and Save", command=fetch_and_save)
fetch_button.grid(row=2, column=1, pady=10)

# Create and pack the result text area
result_text = tk.Text(root, wrap=tk.WORD, width=70, height=15)
result_text.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

root.mainloop()
