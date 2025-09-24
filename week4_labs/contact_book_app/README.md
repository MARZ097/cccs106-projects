# Enhanced Contact Book Application

A comprehensive contact management application built with Flet (Python) featuring advanced functionality and a modern user interface.

## 🌟 Features

### Core Functionality
- ✅ **Add/Edit/Delete Contacts** - Complete CRUD operations
- ✅ **Data Persistence** - Automatic saving to JSON file
- ✅ **Search & Filter** - Find contacts by name, phone, email, or notes
- ✅ **Category Management** - Organize contacts (Family, Friends, Work, Other)
- ✅ **Favorites System** - Mark important contacts as favorites

### Enhanced Features
- ✅ **Rich Contact Information** - Name, phone, email, address, notes, and category
- ✅ **Tabbed Interface** - Separate tabs for viewing and adding contacts
- ✅ **Visual Indicators** - Category icons and favorite stars
- ✅ **Confirmation Dialogs** - Safe deletion with confirmation
- ✅ **Export Functionality** - Export contacts to JSON
- ✅ **Smart Sorting** - Favorites appear first, then alphabetical
- ✅ **Responsive Design** - Modern Material Design UI
- ✅ **Form Validation** - Required field validation
- ✅ **Status Messages** - User feedback for all operations

### Data Fields
- **Name** (Required) - Full contact name
- **Phone** (Required) - Primary phone number
- **Email** (Optional) - Email address
- **Address** (Optional) - Physical address
- **Category** - Family, Friends, Work, or Other
- **Notes** (Optional) - Additional information
- **Favorite** - Toggle for important contacts
- **Created Date** - Automatic timestamp

## 🚀 How to Run

### Prerequisites
- Python 3.7+
- Flet library

### Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Method 1: Direct execution
python main.py

# Method 2: Using flet module (if available)
python -m flet run main.py

# Method 3: Using full path to python (if virtual env issues)
path\to\your\python.exe main.py
```

## 📁 Project Structure

```
contact_book_app/
├── main.py              # Main application file
├── database.py          # Database operations (SQLite)
├── app_logic.py         # Application logic and UI functions
├── requirements.txt     # Python dependencies
├── README.md           # This documentation
├── contacts.db         # Auto-generated SQLite database
└── run_app.bat         # Windows batch file to run the app
```

## 💾 Data Storage

- Contacts are automatically saved to SQLite database (`contacts.db`)
- Data persists between application sessions
- Relational database structure ensures data integrity
- SQLite format provides efficient storage and querying

## 🎨 User Interface

### View Contacts Tab
- **Search Bar** - Real-time contact filtering
- **Category Filter** - Filter by contact category
- **Export Button** - Export all contacts
- **Contact Cards** - Rich display with all information
- **Action Buttons** - Favorite, Edit, Delete for each contact

### Add/Edit Contact Tab
- **Form Fields** - All contact information fields
- **Add/Update Button** - Context-sensitive button
- **Clear Form** - Reset all fields
- **Validation** - Required field checking

## 🔧 Features in Detail

### Search Functionality
- Search across name, phone, email, and notes
- Real-time filtering as you type
- Case-insensitive matching

### Category System
- Four predefined categories with unique icons
- Visual category indicators
- Filter contacts by category

### Favorites System
- Star/unstar contacts
- Favorites appear at the top of the list
- Visual star indicator

### Data Export
- Export all contacts to timestamped JSON file
- Preserves all contact information
- Useful for backups and data migration

## 🛠️ Technical Details

- **Framework**: Flet (Flutter for Python)
- **Data Format**: JSON
- **UI Pattern**: Material Design
- **Architecture**: Single-page application with tabs
- **Storage**: Local file system

## 📱 Usage Tips

1. **Quick Add**: Use Tab 2 to quickly add new contacts
2. **Bulk Edit**: Use search to find contacts quickly for editing
3. **Organization**: Use categories to organize your contacts
4. **Favorites**: Star important contacts for quick access
5. **Backup**: Regularly export your contacts for safety

## 🔮 Future Enhancements

Potential features for future versions:
- Import from CSV/VCF files
- Contact photos
- Multiple phone numbers per contact
- Birthday reminders
- Contact groups/tags
- Dark mode support
- Cloud synchronization

## 🐛 Troubleshooting

### Common Issues

1. **Flet command not found**
   - Use `python -m flet run main.py` instead
   - Or run directly with `python main.py`

2. **Permission errors**
   - Ensure write permissions in the application directory
   - Check if antivirus is blocking file creation

3. **Data not saving**
   - Check if `contacts.json` file is created
   - Verify file permissions

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to contribute by:
- Reporting bugs
- Suggesting new features
- Submitting pull requests
- Improving documentation