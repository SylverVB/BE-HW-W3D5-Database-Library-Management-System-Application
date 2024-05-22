# Module 5: Mini-project | Library Management System with Database Integration

# Project Requirements
# In this project, you will integrate a MySQL database with Python to develop an advanced Library Management System. This command-line-based application is designed to streamline 
# the management of books and resources within a library. Your mission is to create a robust system that allows users to browse, borrow, return, and explore a collection of books 
# while demonstrating your proficiency in database integration, SQL, and Python.

# Integration with the "Library Management System" Project from Module 4 (OOP):

# For this project, you will build upon the foundation laid in "Module 4: Python Object-Oriented Programming (OOP)." The object-oriented structure and classes you developed in that 
# module will serve as the core framework for the Library Management System. You will leverage the classes such as Book, User, Author, and Genre that you previously designed, extending 
# their capabilities to integrate seamlessly with the MySQL database.

# Enhanced User Interface (UI) and Menu:

# Create an improved, user-friendly command-line interface (CLI) for the Library Management System with separate menus for each class of the system. <div class="oc-markdown-custom-container 
# oc-markdown-activatable" contenteditable="false" data-value="``` Welcome to the Library Management System with Database Integration!
# Main Menu:
# Book Operations
# User Operations
# Author Operations
# Genre Operations
# Quit "> Welcome to the Library Management System with Database Integration!"

# Database Integration with MySQL:

# 1. Integrate a MySQL database into the Library Management System to store and retrieve data related to books, users, authors, and genres.
# 2. Design and create the necessary database tables to represent these entities. You will align these tables with the object-oriented structure from the previous project.
# 3. Establish connections between Python and the MySQL database for data manipulation, enhancing the persistence and scalability of your Library Management System.

# Data Definition Language Scripts:

# 1. Create the necessary database tables for the Library Management System. For instance: Books Table:
# Welcome to the Library Management System with Database Integration! **** Main Menu: 1. Book Operations 2. User Operations 3. Author Operations 4. Genre Operations 5. Quit

# Database Connection:

# 1. Establish a connection to the MySQL database using the mysql-connector-python library.
# 2. Create a database cursor to execute SQL queries. Functions for Data Manipulation:
# 3. Create functions for adding new books, users, authors, and genres to the database.
# 4. Implement functions for updating book availability, marking books as borrowed or returned.
# 5. Develop functions for searching books by ISBN, title, author, or genre.
# 6. Define functions for displaying lists of books, users, authors, and genres.
# 7. Implement functions for user registration and viewing user details. User Interface Functions:
# 8. Create a user-friendly command-line interface (CLI) with clear menu options.
# 9. Implement functions to handle user interactions using the input() function.
# 10. Validate user input using regular expressions (regex) to ensure proper formatting. Error Handling:
# 11. Use try, except, else, and finally blocks to manage errors gracefully.
# 12. Handle exceptions related to database operations, input validation, and other potential issues.
# 13. Use meaningful variable and function names that convey their purpose.
# 14. Write clear comments and docstrings to explain the functionality of functions and classes.
# 15. Follow PEP 8 style guidelines for code formatting and structure.
# 16. Ensure proper indentation and spacing for readability. Modular Design:
# 17. Organize code into separate modules to promote modularity and maintainability.
# 18. Create distinct modules for database operations, user interactions, error handling, and core functionalities. GitHub Repository:
# 19. Create a GitHub repository for your project and commit code regularly.
# 20. Maintain a clean and interactive README.md file in your GitHub repository, providing clear instructions on how to run the application and explanations of its features.
# 21. Include a link to your GitHub repository in your project documentation. Optional Bonus Points:
# 22. User Authentication (Bonus): Implement a user authentication system that requires users to create accounts and log in before accessing the library. This enhances security and allows for personalized features.
# 23. Due Dates for Borrowed Books (Bonus): Enhance the system by assigning due dates to borrowed books. When users borrow a book, the system should calculate and display the due date.
# 24. Fine Calculation (Bonus): Implement a fine calculation system for overdue books. Users who exceed the due date should be charged fines based on predefined rules. Users should have the option to pay fines, and their accounts should be updated accordingly. Effective Project Communication:
# 25. Create a video presentation or explanation of the Library Management System project.
# 26. Demonstrate the ability to explain technical concepts and project details in a concise and understandable manner.


from library import Library

def main():
    
    library = Library()

    while True:
        print("\nWelcome to the Library Management System!")
        print("\nMenu:\n")
        print("1. Book Operations")
        print("2. User Operations")
        print("3. Author Operations")
        print("4. Genre Operations")
        print("5. Quit")

        choice = input("\nPlease make your choice (enter from 1 to 5): \n")
        try:
            if choice == "1".strip():
                try:
                    choice = input("\nWhat would you like to do?\n"
                            "\n1. Add a new book"
                            "\n2. Borrow a book"
                            "\n3. Return a book"
                            "\n4. Search for a book"
                            "\n5. Display books\n"
                        "\nEnter your choice from 1 to 4:\n").lower().strip()
                    if choice == "1".strip():
                        library.add_book()
                    elif choice == "2".strip():
                        library.check_out_book()
                    elif choice == "3".strip():
                        library.check_in_book()
                    elif choice == "4".strip():
                        try: 
                            choice = input("\nHow would you like to search for a book\n"
                                            "\n1. By title"
                                            "\n2. By author"
                                            "\n3. By ISBN\n"
                                            "\nEnter your choice from 1 to 3:\n").lower().strip()
                            if choice == "1".strip():
                                library.search_book_title()
                            elif choice == "2".strip():
                                library.search_book_author()
                            elif choice == "3".strip():
                                library.search_book_isbn()
                            else:
                                print("\nPlease enter a valid response!\n")
                        except Exception as e:
                            print(f"An error occurred: {e}")
                    elif choice == "5".strip():
                        try: 
                            choice = input("\nWhich books would you like to display?\n"
                                            "\n1. All books in the library"
                                            "\n2. All currently loaned books\n"
                                            "\nEnter your choice from 1 to 2:\n").lower().strip()
                            if choice == "1".strip():
                                library.display_all_books()
                            elif choice == "2".strip():
                                library.display_all_loaned_books()
                            else:
                                print("\nPlease enter a valid response!")
                        except Exception as e:
                            print(f"An error occurred: {e}")
                    else:
                        print("\nPlease enter a valid response!\n")
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif choice == "2".strip():
                try:
                    choice = input("\nWhat would you like to do?\n"
                            "\n1. Add a new user"
                            "\n2. View user details"
                            "\n3. Display all users\n"
                        "\nEnter your choice from 1 to 3:\n").lower().strip()
                    if choice == "1".strip():
                        library.add_user()
                    elif choice == "2".strip():
                        library.view_user_info()
                    elif choice == "3".strip():
                        library.display_all_users()
                    else:
                        print("\nPlease enter a valid response!")
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif choice == "3".strip():
                try:
                    choice = input("\nWhat would you like to do?\n"
                            "\n1. Add a new author"
                            "\n2. View author details"
                            "\n3. Display all authors\n"
                        "\nEnter your choice from 1 to 3:\n").lower().strip()
                    if choice == "1".strip():
                        library.add_author()
                    elif choice == "2".strip():
                        library.view_author_details()
                    elif choice == "3".strip():
                        library.display_all_authors()
                    else:
                        print("\nPlease enter a valid response!")
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif choice == "4".strip():
                try:
                    choice = input("\nWhat would you like to do?\n"
                            "\n1. Add a new genre"
                            "\n2. View genre details"
                            "\n3. Display all genres\n"
                        "\nEnter your choice from 1 to 3:\n").lower().strip()
                    if choice == "1".strip():
                        library.add_genre()
                    elif choice == "2".strip():
                        library.view_genre_details()
                    elif choice == "3".strip():
                        library.view_all_genres()
                    else:
                        print("\nPlease enter a valid response!")
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif choice == "5".strip():
                print("\nThank you for using our program!\n")
                break
            else:
                print("\nPlease enter a valid response!")
        except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()