"""
Test the update dialog layout to ensure buttons are visible
"""
from update_dialog import UpdateDialog

# Create mock update info
mock_update_info = {
    'update_available': True,
    'client_version': '2.0.3',
    'server_version': '2.0.4',
    'changelog': [
        {'version': '2.0.4', 'changes': ['Enhanced GUI dialogs', 'Better button layout']},
        {'version': '2.0.3', 'changes': ['Initial release with core gameplay']}
    ]
}

print("🧪 Testing Update Dialog Layout")
print("This will show the dialog with visible buttons")
print("Check that Yes/No buttons are clearly visible")

# Create and show dialog
dialog = UpdateDialog()
dialog.show_update_prompt(mock_update_info)

print("Dialog should be showing with buttons visible...")