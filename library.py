from book import Book
from user import User
from author import Author
from genre import Genre
from fiction import FictionBook
from nonfiction import NonFictionBook
from connect_lms import connect_db
from mysql.connector import Error
import re


class Library:

    def __init__(self):
        self.books = {} # Dictionary to store books with ISBN as key
        self.loaned_books = {} # Dictionary to track loaned books with library ID as key
        self.users = [] # List to store User objects
        self.authors = [] # List to store Author objects
        self.genres = [] # List to store Genre objects
       

    def add_book(self, silent=False):
        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)  # Using a buffered cursor to resolve "Unread result found" error

            print("\nPlease enter the following information to add a book:")
            title = input("\nBook title:\n").title().strip()
            author_name = input("\nBook author:\n").title().strip()

            # Checking if the author already exists in the library:
            author_obj = None
            for existing_author in self.authors:
                if existing_author.get_name().lower() == author_name.lower():
                    author_obj = existing_author
                    print(f"Author {author_name} found in the library.")
                    break

            if not author_obj:
                print("\nThis author has not been found in the library.")
                author_obj = self.add_author(author=author_name, silent=silent)

            # Retrieving the author_id from the database:
            cursor.execute("SELECT id FROM authors WHERE LOWER(name) = %s", (author_name.lower(),))
            author_id_result = cursor.fetchone() # This line executes a query to select the id of an author from the authors table where the author's name matches author_name
            if author_id_result:
                author_id = author_id_result[0] # Extracting id (the first element) from the tuple author_id_result (for example (1,)) and assigning it to author_id
            else:
                print(f"Author '{author_name}' not found in the database.")
                return

            isbn = input("\nBook ISBN (13 digits: example: 978-92-95055-02-5):\n").strip()
            while not re.match(r"^\d{3}-\d{2}-\d{5}-\d{2}-\d{1}$", isbn):
                isbn = input("\nPlease enter the ISBN in the correct format (example: 978-92-95055-02-5):\n").strip()

            if isbn in self.books:
                print("\nThis book is already in the library!")
                return

            genre = input("\nPlease enter the type of genre (Fiction or Nonfiction):\n").title().strip()
            while not re.match(r"^(Fiction|Nonfiction)$", genre):
                genre = input("\nInvalid genre type. Please specify 'Fiction' or 'Nonfiction':\n").title().strip()

            # Checking if the genre exists:
            genre_obj = None
            for existing_genre in self.genres:
                if existing_genre.get_name().lower() == genre.lower():
                    genre_obj = existing_genre
                    break

            # If genre does not exist, adding the genre:
            if not genre_obj:
                genre_obj = self.add_genre(genre)
                cursor.execute("SELECT id FROM genres WHERE LOWER(genre_name) = %s", (genre.lower(),))
                genre_id_result = cursor.fetchone()
                if genre_id_result:
                    genre_id = genre_id_result[0]
                else:
                    print(f"Genre '{genre}' not found in the database.")
                    return
            else:
                cursor.execute("SELECT id FROM genres WHERE LOWER(genre_name) = %s", (genre.lower(),))
                genre_id_result = cursor.fetchone() # The line executes a query to select the id of a genre from the genres table where the genre name matches genre input
                if genre_id_result:
                    genre_id = genre_id_result[0] # Extracting the id (the first element) from the tuple genre_id_result (for example (1,)) and assigning it to genre_id
                else:
                    print(f"Genre '{genre}' not found in the database.")
                    return

            # Prompting for category/subject and creating the appropriate book object:
            category_subject = None
            availability = 1  # Default availability to True (1)

            if genre == "Fiction":
                category = input("\nFiction Genre category:\n").title().strip()
                genre_obj.add_category(category)  # Adding category to genre
                new_book = FictionBook(title, author_obj, isbn, genre_obj, category)
                genre_obj.add_book_to_category(category, new_book)  # Adding book to genre category
                category_subject = category

                # Adding the category to the database if not already present:
                cursor.execute("SELECT id FROM genre_categories WHERE genre_id = %s AND category_subject = %s", (genre_id, category))
                if cursor.fetchone() is None:
                    cursor.execute("INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)", (genre_id, category))
                    conn.commit()

            elif genre == "Nonfiction":
                subject = input("\nNonfiction Genre subject:\n").title().strip()
                genre_obj.add_category(subject)
                new_book = NonFictionBook(title, author_obj, isbn, genre_obj, subject)
                genre_obj.add_book_to_category(subject, new_book)
                category_subject = subject

                # Adding the subject to the database if not already present:
                cursor.execute("SELECT id FROM genre_categories WHERE genre_id = %s AND category_subject = %s", (genre_id, subject))
                if cursor.fetchone() is None:
                    cursor.execute("INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)", (genre_id, subject))
                    conn.commit()

            else:
                print("Invalid genre type. Please specify 'Fiction' or 'Nonfiction'.")
                return

            # Inserting the new book into the database:
            query = "INSERT INTO books (title, author_id, isbn, genre_id, category_subject, availability) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (new_book.get_title(), author_id, new_book.get_isbn(), genre_id, category_subject, availability))
            conn.commit()

            # Assigning the newly created book object (new_book) to the books dictionary attribute of the Library class:
            self.books[isbn] = new_book
            print(f'\nThe book "{title}" by {author_name} has been added to the library.')

        except Error as e:
            print(f"\nError: {e}")

        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    

    def add_user(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            name = input("\nWhat is your full name?\n").title().strip()
            library_id = input("\nYour library ID (example: AA12345):\n").upper().strip()
            while not re.match(r"^[A-Za-z]{2}\d{5}$", library_id):
                library_id = input("\nPlease enter your Library ID in the correct format (example: AA123-45678):\n").upper().strip()
            # Checking if the user already exists in the system:
            for user in self.users:
                if user.get_library_id() == library_id:
                    print("\nUser with the same library ID already exists!")
                    return user
            # If the user doesn't exist, create a new user object and add it to the list:
            new_user = User(name, library_id)
            self.users.append(new_user)
            print(f"\n{new_user.name} (Library ID: {new_user.get_library_id()}) has been added as a new user to the library.")

            query = "INSERT INTO users (name, library_id) VALUES (%s, %s)"
            cursor.execute(query, (new_user.name, new_user.get_library_id()))
            conn.commit()
            
            return new_user

        except Error as e:
            print(f"\nError: {e}")

        finally:
            if conn and conn.is_connected():
                    cursor.close()
                    conn.close()


    def check_out_book(self):
        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True) # Using a buffered cursor to resolve "Unread result found" error

            print("\nPlease enter the following information to check out the book:")
            isbn = input("\nBook ISBN (13 digits: example: 978-92-95055-02-5):\n").strip()
            while not re.match(r"^\d{3}-\d{2}-\d{5}-\d{2}-\d{1}$", isbn):
                isbn = input("\nPlease enter the ISBN in the correct format (example: 978-92-95055-02-5):\n").strip()
            
            # The query retrieves book details (ID, title, availability, and author name) by joining the books and authors tables and filtering by ISBN.
            # 'b' is used as an alias for books table; 'JOIN authors a ON b.author_id = a.id' joins the books table with the authors table on the condition 
            # that the author_id column in the books table matches the id column in the authors table. This join is necessary to retrieve the author's name.
            # 'WHERE b.isbn = %s' filters the results to include only the row where the book's ISBN matches the given value (%s is a placeholder for the actual ISBN value):
            cursor.execute("""
                SELECT b.id, b.title, b.availability, a.name 
                FROM books b
                JOIN authors a ON b.author_id = a.id 
                WHERE b.isbn = %s
            """, (isbn,))
            book_result = cursor.fetchone() # The result from the query includes the book ID, title, availability, and author name

            if book_result:
                book_id, book_title, availability, author_name = book_result # Unpacking the tuple book_result and assigning the result to book_id, book_title, availability, author_name
                if availability == 1:  # If the book is available
                    name = input("\nYour full name:\n").title().strip()
                    library_id = input("\nYour Library ID (example: AA12345):\n").upper().strip()
                    while not re.match(r"^[A-Za-z]{2}\d{5}$", library_id):
                        library_id = input("\nPlease enter your Library ID in the correct format (example: AA12345):\n").upper().strip()

                    cursor.execute("SELECT id, name FROM users WHERE library_id = %s", (library_id,))
                    user_result = cursor.fetchone() # Fetching the first row from the result of the executed SQL query and assigning it to the variable user_result

                    if user_result:
                        user_id, user_name = user_result # Unpacking the tuple user_result and assigning the result to user_id and user_name
                        current_user = User(user_name, library_id)
                        print(f"\nWelcome back, {current_user.name} (Library ID: {current_user.get_library_id()})!")
                    else:
                        cursor.execute("INSERT INTO users (name, library_id) VALUES (%s, %s)", (name, library_id))
                        conn.commit()
                        user_id = cursor.lastrowid
                        current_user = User(name, library_id)
                        print(f"\n{current_user.name} (Library ID: {current_user.get_library_id()}) has been added as a new user to the library.")

                    cursor.execute("UPDATE books SET availability = 0 WHERE id = %s", (book_id,))
                    cursor.execute("INSERT INTO borrowed_books (user_id, book_id) VALUES (%s, %s)", (user_id, book_id))
                    conn.commit()

                    print(f'\nThe book "{book_title}" by {author_name}, ISBN: {isbn}, has been loaned to {current_user.name}, Library ID {current_user.get_library_id()}')
                else:
                    print("\nThe book is currently unavailable!")
            else:
                print(f"\nThere is no book with ISBN '{isbn}' in the library!")

        except Error as e:
            print(f"\nError: {e}")

        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


    def check_in_book(self):
        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)

            # Populating self.users from the database:
            cursor.execute("SELECT id, name, library_id FROM users")
            # self.users = []
            for user_row in cursor.fetchall():
                user = User(user_row[1], user_row[2])
                user.id = user_row[0]
                self.users.append(user)

            print("\nPlease enter the following information to return a book:")
            library_id = input("\nYour library ID (example: AZ12345):\n").upper().strip()
            while not re.match(r"^[A-Za-z]{2}\d{5}$", library_id):
                library_id = input("\nPlease enter your library ID in the correct format (example: AZ12345):\n").upper().strip()
            isbn = input("\nBook ISBN (example: 978-92-95055-02-5):\n").strip()
            while not re.match(r"^\d{3}-\d{2}-\d{5}-\d{2}-\d{1}$", isbn):
                isbn = input("\nPlease enter the ISBN in the correct format (example: 978-92-95055-02-5):\n").strip()

            # Looking for the user by Library ID:
            user = None  # Initializing user variable
            for returning_user in self.users:
                if returning_user.get_library_id() == library_id:
                    user = returning_user
                    # Adding "break" here to ensure that once the matching user is found, the loop exits immediately reducing the number 
                    # of unnecessary iterations. It also help us avoid potential errors if there are duplicate library IDs or other unforeseen issues:
                    break

            if user is None:  # If no user is found with the given library ID
                print(f"\nNo user with Library ID: {library_id} has been found in the library!")
            else:
                cursor.execute("SELECT id FROM books WHERE isbn = %s", (isbn,))
                book_result = cursor.fetchone()
                if not book_result:
                    print(f"\nNo book with ISBN {isbn} has been found in the library!")
                    return

                book_id = book_result[0]

                cursor.execute("SELECT * FROM borrowed_books WHERE user_id = %s AND book_id = %s", (user.id, book_id))
                borrowed_book_result = cursor.fetchone()

                if borrowed_book_result:
                    cursor.execute("UPDATE books SET availability = 1 WHERE isbn = %s", (isbn,))
                    cursor.execute("DELETE FROM borrowed_books WHERE user_id = %s AND book_id = %s", (user.id, book_id))
                    conn.commit()
                    print(f"\nThe book with ISBN {isbn} has been returned by {user.name} (Library ID: {library_id})")
                else:
                    print(f"\nNo record found for the book with ISBN {isbn} borrowed by {user.name} (Library ID: {library_id})")

        except Error as e:
            print(f"\nError: {e}")

        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


    def search_book_title(self):
        title = input("\nEnter the book title:\n").lower().strip()
        
        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)
            
            # Searching for books with titles containing the input.
            # LOWER(b.title): Converts the 'title' column in 'books' to lowercase to ensure case-insensitive comparison.
            # Using the SQL LIKE operator to search for a pattern:
            query = """
            SELECT b.isbn, b.title, a.name 
            FROM books b 
            JOIN authors a ON b.author_id = a.id 
            WHERE LOWER(b.title) LIKE %s
            """
            cursor.execute(query, ('%' + title + '%',))
            search_result = cursor.fetchall()  # Fetching all matching records

            if search_result:
                print("\nThis is what we have found in the library:\n")
                for isbn, book_title, author in search_result:
                    print(f"{book_title} by {author}, ISBN: {isbn}")
            else:
                print(f"\nNo book titled '{title.title()}' has been found in the library!")

        except Error as e:
            print(f"\nError: {e}")
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    

    def search_book_author(self):
        author = input("\nEnter the book author:\n").lower().strip()
        
        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)
            
            # Searching for books by the given author:
            query = """
            SELECT b.isbn, b.title, a.name 
            FROM books b 
            JOIN authors a ON b.author_id = a.id 
            WHERE LOWER(a.name) LIKE %s
            """
            cursor.execute(query, ('%' + author + '%',))
            search_result = cursor.fetchall()  # Fetching all matching records

            if search_result:
                print("\nThis is what we have found in the library:\n")
                for isbn, book_title, author_name in search_result:
                    print(f"{book_title} by {author_name}, ISBN: {isbn}")
            else:
                print(f"\nNo '{author.title()}' has been found in the library!")

        except Error as e:
            print(f"\nError: {e}")
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


    def search_book_isbn(self):
        isbn = input("\nEnter the book ISBN (13 digits: example: 978-92-95055-02-5):\n").strip()
        while not re.match(r"^\d{3}-\d{2}-\d{5}-\d{2}-\d{1}$", isbn):
            isbn = input("\nPlease enter the ISBN in the correct format (example: 978-92-95055-02-5):\n").strip()

        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)
            
            # Searching for the book by ISBN:
            query = """
            SELECT b.isbn, b.title, a.name 
            FROM books b 
            JOIN authors a ON b.author_id = a.id 
            WHERE b.isbn = %s
            """
            cursor.execute(query, (isbn,))
            search_result = cursor.fetchone()  # Fetching the matching record

            if search_result:
                isbn, book_title, author = search_result
                print(f"\nThis is what we have found in the library:\n\n{book_title} by {author}, ISBN: {isbn}")
            else:
                print(f"\nNo ISBN '{isbn}' has been found in our library!")

        except Error as e:
            print(f"\nError: {e}")
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    

    def display_all_books(self):
        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)
            
            # Retrieving all books:
            query = """
            SELECT b.isbn, b.title, a.name 
            FROM books b 
            JOIN authors a ON b.author_id = a.id
            """
            cursor.execute(query)
            all_books = cursor.fetchall()  # Fetching all books

            print("\nHere is the list of books in the library:\n")
            if all_books:
                for isbn, title, author in all_books:
                    print(f"{title} by {author}, ISBN: {isbn}")
            else:
                print("Currently, there are no books in the library!")

        except Error as e:
            print(f"\nError: {e}")
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                

    def display_all_loaned_books(self):
        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)
            
            # Retrieve all loaned books along with user information
            query = """
            SELECT u.name, u.library_id, b.title, a.name, b.isbn 
            FROM borrowed_books bb
            JOIN users u ON bb.user_id = u.id
            JOIN books b ON bb.book_id = b.id
            JOIN authors a ON b.author_id = a.id
            """
            cursor.execute(query)
            loaned_books = cursor.fetchall()  # Fetch all loaned books and associated user info

            print("\nHere is the list of loaned books in the library:")
            if loaned_books:
                # Create a dictionary to group books by user
                user_books = {}
                for user_name, library_id, book_title, author_name, isbn in loaned_books:
                    if (user_name, library_id) not in user_books:
                        user_books[(user_name, library_id)] = []
                    user_books[(user_name, library_id)].append((book_title, author_name, isbn))
                
                # Print the grouped books
                for (user_name, library_id), books in user_books.items():
                    print(f"\nBooks loaned to {user_name} (Library ID: {library_id}):")
                    for book_title, author_name, isbn in books:
                        print(f"  - {book_title} by {author_name}, ISBN: {isbn}")
            else:
                print("\nNo books are currently loaned!")

        except Error as e:
            print(f"\nError: {e}")
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


    def view_user_info(self):
        print("\nPlease enter the following information:")
        library_id = input("\nLibrary ID (example: AZ12345):\n").upper().strip()
        while not re.match(r"^[A-Za-z]{2}\d{5}$", library_id):
            library_id = input("\nPlease enter the Library ID in the correct format (example: AZ12345):\n").upper().strip()

        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)
            
            # Retrieving user information and borrowed books:
            query = """
            SELECT u.id, u.name, b.title, a.name, b.isbn 
            FROM users u
            LEFT JOIN borrowed_books bb ON u.id = bb.user_id
            LEFT JOIN books b ON bb.book_id = b.id
            LEFT JOIN authors a ON b.author_id = a.id
            WHERE u.library_id = %s
            """
            cursor.execute(query, (library_id,))
            user_info = cursor.fetchall()

            if user_info:
                user_id, user_name = user_info[0][:2]
                print(f"\nUser Information:\nName: {user_name}\nLibrary ID: {library_id}")
                print("\nBorrowed Books:")
                for _, _, title, author, isbn in user_info:
                    if title:  # Only print borrowed books if there are any
                        print(f"  - {title} by {author}, ISBN: {isbn}")
            else:
                print(f"\nNo user was found with Library ID {library_id}.")

        except Error as e:
            print(f"\nError: {e}")
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    
    def display_all_users(self):
        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)
            
            # Retrieving all users:
            query = "SELECT name, library_id FROM users"
            cursor.execute(query)
            users = cursor.fetchall()  # Fetching all users

            print("\nHere is the list of current users in the library:\n")
            if users:
                for name, library_id in users:
                    print(f"{name.title()} (Library ID: {library_id})")
            else:
                print("\nNo users are found!")

        except Error as e:
            print(f"\nError: {e}")
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


    def add_author(self, author=None, silent=False): # Making the author parameter optional. It allows us to call the method within add_book() without needing to providing an author argument
                                                     # Adding an optional silent parameter. When silent is True, it suppresses the messages about the author already existing or being added
        try:
            conn = connect_db()
            cursor = conn.cursor()

            if author is None:
                print("\nPlease enter the following information to add a new author:")
                author = input("\nAuthor's full name:\n").title().strip()
            else:
                print(f"\nAdding a new author: {author}")
            biography = input("\nAuthor's biography (no more than 300 characters):\n").capitalize().strip()
            if len(biography) > 300:
                biography = biography[:300]
            new_author = Author(author, biography)
            # Checking if an author with the same name already exists in the library:
            if any(existing_author.get_name() == author for existing_author in self.authors):
                if not silent:
                    print(f"\n{new_author.get_name()} already exists in the library")
            else:
                self.authors.append(new_author)
                if not silent:
                    print(f"\n{new_author.get_name()} has been added to the list of authors in the library.")

            query = "INSERT INTO authors (name, biography) VALUES (%s, %s)"
            cursor.execute(query, (new_author.get_name(), new_author.get_biography()))
            conn.commit()
            
            return new_author

        except Error as e:
            print(f"\nError: {e}")

        finally:
            if conn and conn.is_connected():
                    cursor.close()
                    conn.close()


    def view_author_details(self):
        author_name = input("\nPlease enter the name of the author you are interested in:\n").title().strip()

        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)
            
            # Searching for books by the given author.
            # Using the SQL LIKE operator to search for a pattern:
            query = """
            SELECT b.title, b.isbn 
            FROM books b 
            JOIN authors a ON b.author_id = a.id 
            WHERE LOWER(a.name) LIKE %s
            """
            cursor.execute(query, ('%' + author_name.lower() + '%',))
            books_by_author = cursor.fetchall()  # Fetching all books by the author

            if books_by_author:
                print(f"\nBooks by authors matching '{author_name}':\n")
                for title, isbn in books_by_author:
                    print(f"{title}, ISBN: {isbn}")
            else:
                print(f"\nNo books by authors matching '{author_name}' have been found in the library!")

        except Error as e:
            print(f"\nError: {e}")
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    
    def display_all_authors(self):
        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)
            
            # Retrieving all authors:
            query = "SELECT name, biography FROM authors"
            cursor.execute(query)
            authors = cursor.fetchall() # Fetching all authors

            print("\nHere is the list of current authors in the library:\n")
            if authors:
                for name, biography in authors:
                    print(f"\nAuthor: {name}\nBiography: {biography}")
            else:
                print("\nNo authors have been added to the library yet!")

        except Error as e:
            print(f"\nError: {e}")
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


    def add_genre(self, genre=None, category_subject=None, silent=False):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # If genre is not specified, prompting the user to input it:
            if genre is None:
                genre = input("\nPlease enter the type of genre you want to add (Fiction or Nonfiction):\n").title().strip()

            # Validating the genre input:
            if genre not in ["Fiction", "Nonfiction"]:
                print("Invalid genre type. Please specify 'Fiction' or 'Nonfiction'.")
                return None

            # Checking if the genre already exists in the local list and database:
            for existing_genre in self.genres:
                if existing_genre.get_name() == genre:
                    if not silent:
                        print(f"\nGenre '{existing_genre.get_name()}' already exists in the library.")
                    if category_subject:
                        existing_genre.add_category(category_subject)
                    return existing_genre

            # If the genre doesn't exist, prompting for description and adding it:
            description = input("\nGenre description (no more than 200 characters):\n").capitalize().strip()
            if len(description) > 200:
                description = description[:200]

            new_genre = Genre(genre, description)
            self.genres.append(new_genre)

            # Inserting the new genre into the database:
            cursor.execute("INSERT INTO genres (genre_name, genre_description) VALUES (%s, %s)", (new_genre.get_name(), new_genre.get_description()))
            conn.commit()

            # Retrieving the genre ID from the database:
            cursor.execute("SELECT id FROM genres WHERE genre_name = %s", (genre,))
            genre_id_result = cursor.fetchone()
            if genre_id_result:
                genre_id = genre_id_result[0]

                # If category_subject is provided, adding it to the database:
                if category_subject:
                    cursor.execute("INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)", (genre_id, category_subject))
                    conn.commit()

            if not silent:
                print(f"\nGenre '{new_genre.get_name()}' has been added to the database.")

            return new_genre

        except Error as e:
            print(f"\nAn error occurred: {e}")

        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    
    def view_genre_details(self):
        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)
            
            # Retrieve all genres and their details
            query = "SELECT id, genre_name, genre_description FROM genres"
            cursor.execute(query)
            genres = cursor.fetchall()  # Fetch all genres

            for genre_id, genre_name, genre_description in genres:
                print(f"\nGenre: {genre_name}, Description: {genre_description}")
                
                # Retrieve categories for this genre
                query = """
                SELECT gc.category_subject 
                FROM genre_categories gc
                WHERE gc.genre_id = %s
                """
                cursor.execute(query, (genre_id,))
                categories = cursor.fetchall()  # Fetch categories for the current genre
                
                if categories:
                    for (category_subject,) in categories:
                        print(f"Category: {category_subject}")
                        
                        # Retrieve books for this category within the genre
                        query = """
                        SELECT b.title, a.name 
                        FROM books b
                        JOIN authors a ON b.author_id = a.id
                        WHERE b.genre_id = %s AND b.category_subject = %s
                        """
                        cursor.execute(query, (genre_id, category_subject))
                        books = cursor.fetchall()  # Fetch books in the current category

                        if books:
                            for title, author in books:
                                print(f"  - {title} by {author}")
                        else:
                            print("  - No books in this category")
                else:
                    print("  - No categories in this genre")

        except Error as e:
            print(f"\nError: {e}")
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

        
    def view_all_genres(self):
        try:
            conn = connect_db()
            cursor = conn.cursor(buffered=True)
            
            # Retrieve all genres
            query = "SELECT genre_name, genre_description FROM genres"
            cursor.execute(query)
            genres = cursor.fetchall()  # Fetch all genres

            print("\nHere is the list of all genres in the library:\n")
            if genres:
                for genre_name, genre_description in genres:
                    print(f"\nGenre: {genre_name}\nDescription: {genre_description}")
                    # Retrieve books in this genre
                    query = """
                    SELECT b.title, a.name 
                    FROM books b
                    JOIN authors a ON b.author_id = a.id
                    WHERE b.genre_id = (SELECT id FROM genres WHERE genre_name = %s)
                    """
                    cursor.execute(query, (genre_name,))
                    books = cursor.fetchall()  # Fetch books in the current genre

                    if books:
                        print("\nBooks in this genre:")
                        for title, author in books:
                            print(f"  - Title: {title}, Author: {author}")
                    else:
                        print("  - No books in this genre")
            else:
                print("\nNo genres have been added to the library yet!")

        except Error as e:
            print(f"\nError: {e}")
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()