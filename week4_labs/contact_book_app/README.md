# 📱 Enhanced Contact Book Application

A modern, feature-rich contact management application built with Flet (Python) featuring advanced UI/UX and comprehensive functionality.

## ✨ New Features & Enhancements

### 🎨 **Modern UI/UX Design**
- **Beautiful Card-Based Layout** - Each contact displayed in elegant cards with category icons
- **Dark Mode Toggle** - Switch between light and dark themes seamlessly
- **Responsive Design** - Optimized for different screen sizes
- **Tabbed Interface** - Organized navigation between viewing and adding contacts
- **Material Design** - Following Google's Material Design principles

### 🔍 **Advanced Search & Filtering**
- **Real-time Search** - Search across names, phones, emails, and notes as you type
- **Category Filtering** - Filter contacts by Family, Friends, Work, or Other
- **Smart Sorting** - Favorites appear first, then alphabetical ordering
- **Empty State Handling** - Helpful messages when no contacts match filters

### 💾 **Enhanced Data Management**
- **Extended Contact Fields** - Name, phone, email, address, category, notes
- **Favorite System** - Mark important contacts as favorites with star indicators
- **Data Persistence** - All data stored in SQLite database
- **Automatic Timestamps** - Track when contacts were created

### 🛡️ **Improved User Experience**
- **Confirmation Dialogs** - Safe deletion with "Are you sure?" prompts
- **Form Validation** - Required field checking with helpful error messages
- **Success Notifications** - Visual feedback for all operations
- **Contact Details View** - Detailed popup view for each contact
- **Inline Editing** - Quick edit functionality with pre-filled forms

### 🎯 **Smart Features**
- **Contact Counter** - Real-time count of total contacts
- **Category Icons** - Visual indicators for different contact types
- **Favorite Stars** - Quick visual identification of important contacts
- **Clear Form** - One-click form clearing functionality

## 📋 **All Features**

### Core Functionality
- ✅ **Full CRUD Operations** - Create, Read, Update, Delete contacts
- ✅ **SQLite Database** - Reliable local data storage
- ✅ **Data Validation** - Ensure data integrity with required field validation
- ✅ **Real-time Updates** - Instant UI updates after operations

### Advanced Features
- ✅ **Search & Filter** - Find contacts quickly with multiple filter options
- ✅ **Favorites System** - Star important contacts for quick access
- ✅ **Category Management** - Organize contacts by relationship type
- ✅ **Dark Mode** - Eye-friendly dark theme option
- ✅ **Confirmation Dialogs** - Prevent accidental deletions
- ✅ **Detailed View** - Comprehensive contact information display
- ✅ **Modern UI** - Card-based layout with Material Design

### Data Fields
- **Name** (Required) - Full contact name
- **Phone** (Required) - Primary phone number  
- **Email** (Optional) - Email address
- **Address** (Optional) - Physical address
- **Category** - Family, Friends, Work, or Other
- **Notes** (Optional) - Additional information
- **Favorite** - Toggle for important contacts
- **Created Date** - Automatic timestamp

## 🚀 **How to Run**

### Prerequisites
- Python 3.7+
- Flet library

### Quick Start
```bash
# Navigate to the app directory
cd cccs106-projects/week4_labs/contact_book_app

# Method 1: Using virtual environment (Recommended)
../../../cccs106_env_villaruel/Scripts/python.exe main.py

# Method 2: Using batch file
run_app.bat

# Method 3: If Python is in PATH
python main.py
```

## 📁 **Project Structure**

```
contact_book_app/
├── main.py              # Main application with enhanced UI
├── database.py          # SQLite operations with extended schema
├── app_logic.py         # Business logic and UI components
├── requirements.txt     # Python dependencies
├── README.md           # This documentation
├── contacts.db         # SQLite database (auto-created)
└── run_app.bat         # Windows launcher script
```

## 🎨 **UI/UX Highlights**

### **View Contacts Tab**
- **Search Bar** - Real-time contact filtering
- **Category Dropdown** - Filter by contact type
- **Contact Cards** - Rich display with avatars, icons, and actions
- **Action Buttons** - Favorite, View, Edit, Delete for each contact
- **Empty States** - Helpful messages when no contacts found

### **Add Contact Tab**
- **Two-Column Layout** - Organized form fields
- **Input Validation** - Real-time feedback
- **Category Selection** - Dropdown with predefined options
- **Action Buttons** - Add and Clear functionality

### **Interactive Elements**
- **Confirmation Dialogs** - Modal dialogs for destructive actions
- **Detail Views** - Comprehensive contact information popups
- **Edit Dialogs** - In-place editing with form validation
- **Theme Toggle** - Smooth transition between light/dark modes

## 🔧 **Technical Details**

- **Framework**: Flet (Flutter for Python)
- **Database**: SQLite with extended schema
- **UI Pattern**: Material Design with card-based layout
- **Architecture**: Modular design with separation of concerns
- **Responsive**: Adapts to different screen sizes
- **Theming**: Light/Dark mode support

## 📱 **Usage Guide**

### **Adding Contacts**
1. Click the "➕ Add Contact" tab
2. Fill in required fields (Name and Phone)
3. Optionally add email, address, category, and notes
4. Click "Add Contact" to save

### **Managing Contacts**
1. Use the search bar to find specific contacts
2. Filter by category using the dropdown
3. Click the star icon to mark/unmark favorites
4. Use the eye icon to view full contact details
5. Use the edit icon to modify contact information
6. Use the delete icon to remove contacts (with confirmation)

### **Theme Switching**
- Click the moon/sun icon in the header to toggle between light and dark modes

## 🔮 **Future Enhancements**

Potential features for future versions:
- Import/Export functionality (CSV, VCF)
- Contact photos and avatars
- Multiple phone numbers per contact
- Birthday reminders and notifications
- Contact groups and tags
- Backup and sync capabilities
- Advanced search with multiple criteria

## 🐛 **Troubleshooting**

### Common Issues

1. **Application won't start**
   - Ensure Flet is installed: `pip install flet`
   - Check Python version (3.7+ required)

2. **Database errors**
   - Delete `contacts.db` file to reset database
   - Check file permissions in application directory

3. **UI not updating**
   - Restart the application
   - Check for any console error messages

## 📄 **License**

This project is open source and available under the MIT License.

## 🙏 **Acknowledgments**

- Built with [Flet](https://flet.dev/) - Flutter apps in Python
- Icons from Material Design Icons
- UI inspiration from modern mobile applications

---

**Enjoy your enhanced contact management experience! 🎉**