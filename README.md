# Library Management System

## Overview
The Library Management System is a Python-based application designed to manage the operations of a library. This system allows for the addition, viewing, and management of authors, books, genres, and users. It also supports borrowing and returning books. The backend is powered by a MySQL database.

## Features
- **Book Operations**: Add new books, borrow books, return books, search for books by title, author, ISBN, or genre.
- **User Operations**: Add new users, view user details, display all users.
- **Author Operations**: Add new authors, view author details, display all authors.
- **Genre Operations**: Add new genres, view genre details, display all genres.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/SylverVB/BE-HW-W3D5-Database-Library-Management-System-Application.git
    cd BE-HW-W3D5-Database-Library-Management-System-Application
    ```

2. Set up the MySQL database:
    - Ensure MySQL is installed and running.
    - Update the database connection details in `connect_lms.py`.
    - Create the database and tables by running the SQL commands in `library.sql`:
      ```bash
      mysql -u root -p < library.sql
      ```

## Usage

### Running the Main Program
1. **Execute the Script**: Run `Library Management System.py` to start the Library Management System.
2. **Navigate the Menu**: Use the console-based menu to perform various operations related to books, users, authors, and genres.

### Example Operations

#### Adding a New Book
1. Select "Book Operations" from the main menu.
2. Choose "Add a new book".
3. Enter the required book details, such as title, author, ISBN, and genre.

#### Borrowing a Book
1. Select "Book Operations" from the main menu.
2. Choose "Borrow a book".
3. Enter the book's ISBN and user details to borrow the book.

#### Returning a Book
1. Select "Book Operations" from the main menu.
2. Choose "Return a book".
3. Enter the required details to return the book.

#### Adding a New User
1. Select "User Operations" from the main menu.
2. Choose "Add a new user".
3. Enter the required user details, such as name and library ID.

#### Viewing Author Details
1. Select "Author Operations" from the main menu.
2. Choose "View author details".
3. Enter the author's name to view their details.

## Files and Classes

### 1. `Library Management System_DB_Integration.py`
This is the main file that runs the Library Management System. It includes the main function that handles user interactions and menu options.

### 2. `book.py`
Defines the `Book` class, representing a book in the library. It includes methods for getting book details, borrowing, and returning books.

### 3. `author.py`
Defines the `Author` class, representing an author. It includes methods for getting author details and managing the books written by the author.

### 4. `fiction.py`
Defines the `FictionBook` class, inheriting from `Book`. It includes additional attributes and methods specific to fiction books.

### 5. `genre.py`
Defines the `Genre` class, representing a genre in the library. It includes methods for managing categories and books within the genre.

### 6. `nonfiction.py`
Defines the `NonFictionBook` class, inheriting from `Book`. It includes additional attributes and methods specific to nonfiction books.

### 7. `user.py`
Defines the `User` class, representing a user of the library. It includes methods for getting user details and managing the books borrowed by the user.

### 8. `library.py`
Contains the `Library` class with methods to manage authors, books, and genres. a user of the library. It includes methods for getting user details and managing the books borrowed by the user.

### 9. `connect_lms.py`
Contains the function to connect to the MySQL database.

### 10. `library.sql`
Contains SQL commands to set up the database schema.

## Database Schema

The database consists of the following tables:

1. `authors`: Stores author information.
2. `genres`: Stores genre information.
3. `genre_categories`: Stores genre categories.
4. `users`: Stores user information.
5. `books`: Stores book information.
6. `borrowed_books`: Stores information about borrowed books.

Refer to `library.sql` for the detailed schema and table creation commands.

## Conclusion
The Library Management System offers a comprehensive solution for managing library operations efficiently. With seamless integration with a MySQL database, the system ensures data integrity and reliability. This integration allows for the storage and retrieval of essential information such as books, authors, genres, and user details. By leveraging database capabilities, the system enhances the organization and accessibility of library resources, facilitating tasks such as adding, viewing, and managing library items. With its user-friendly interface and robust database integration, the Library Management System presents a promising tool for streamlining library operations and improving user experience.

## Dependencies:
- The program requires MySQL Connector/Python for database connectivity.
- Python 2.x or Python 3.x can be used to run the program.

## Contributing:
Contributions to the Library Management System app are welcome! Feel free to submit bug fixes, feature enhancements, or suggestions via pull requests.

## License:
This application is the property of Victor Bondaruk. However, it is unlicensed, which means that no specific license has been applied to it. As the owner, Victor Bondaruk retains all rights to the application.

## Contact:
For any inquiries or support, please contact Victor Bondaruk at user@example.com.