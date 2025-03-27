# Library Management System

This project is a library management system that allows both librarians and users to log in. Users can borrow books, and librarians can manage users and view borrowing activities.

## Features

- Separate login for librarians and users.
- Librarians can view, add, delete, and update users.
- Users can borrow books.
- Librarians can view and manage borrowing activities.
- Users can leave comments and rate books.
- Users can see the comments and ratings of other users.
- Users can see the popular books of the week.
- Users can see all the books in the library and see the author and description of the book.

## Installation

### Requirements

- Python 3.x
- Django

### Steps

1. Navigate to the Project Directory
    Change your current directory to the project's directory:

    cd /path/to/your/project

2. Create and activate a virtual environment:

    python -m venv myvenv

    myvenv\Scripts\activate
    
3. Install the required packages:

    pip install -r requirements.txt
    
4. Create the database:
    python manage.py makemigrations

    python manage.py migrate
    
5. Start the development server:

    python manage.py runserver
    
6. Create Admin Profile

    To create a superuser for the admin panel, run:

    python manage.py createsuperuser


### Login

Login page for both librarians and users:
http://127.0.0.1:8000
