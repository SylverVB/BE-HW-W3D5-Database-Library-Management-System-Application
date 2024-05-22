from book import Book
from user import User
from author import Author
from genre import Genre
from fiction import FictionBook
from nonfiction import NonFictionBook
from connect_lms import connect_db
from mysql.connector import Error
import re

# ALMOST DONE WITH THE PROJECT. FIRST COMMIT

class Library:

    def __init__(self):
        self.books = {} # Dictionary to store books with ISBN as key
        self.loaned_books = {} # Dictionary to track loaned books with library ID as key
        self.users = [] # List to store User objects
        self.authors = [] # List to store Author objects
        self.genres = [] # List to store Genre objects

    def add_book(self, silent=False): # Using silent parameter to suppress certain prompts or messages when adding a book
        try:
            conn = connect_db()
            cursor = conn.cursor()
            print("\nPlease enter the following information to add a book:")
            title = input("\nBook title:\n").title().strip()
            author = input("\nBook author:\n").title().strip()
            # Checking if the author already exists in the library:
            author_obj = None # Initializing author_obj as None
            for existing_author in self.authors:
                if existing_author.get_name() == author:
                    author_obj = existing_author # Setting author_obj if a match is found
                    break
            if not author_obj:
                # If the author does not exist, call the add_author() method
                print("\nThis author has not been found in the library.")
                author_obj = self.add_author(silent=silent) # Passing the correct silent parameter
            isbn = input("\nBook ISBN (13 digits: example: 978-92-95055-02-5):\n").strip()
            while not re.match(r"^\d{3}-\d{2}-\d{5}-\d{2}-\d{1}$", isbn):
                isbn = input("\nPlease enter the ISBN in the correct format (example: 978-92-95055-02-5):\n").strip()
            if isbn in self.books:
                print("\nThis book is already in the library!")
            genre = input("\nPlease enter the type of genre (Fiction or Nonfiction):\n").title().strip()
            # Checking if the genre exists
            genre_obj = None
            for existing_genre in self.genres:
                if existing_genre.get_name() == genre:
                    genre_obj = existing_genre
                    break
            # If genre does not exist, adding the genre:
            if not genre_obj:
                # Passing silent parameter to avoid redundant prompts about subject for nonfiction genre
                genre_obj = self.add_genre(genre, silent=silent)
            # Prompting for category/subject and creating the appropriate book object
            if genre == "Fiction":
                category = input("\nFiction Genre category:\n").title().strip()
                genre_obj.add_category(category) # Adding category to genre
                new_book = FictionBook(title, author_obj, isbn, genre_obj, category)
                genre_obj.add_book_to_category(category, new_book) # Adding book to genre category

                query = "INSERT INTO book (title, author_id, isbn, genre_id, category) VALUES (%s, %s)"              # ???
                cursor.execute(query, (new_book.get_title(), new_book.get_author(), new_book.get_isbn, new_book.get_genre(), new_book.get_category()))
                conn.commit()
                print(f"\n{new_book.get_title()} by {new_book.get_author()} has also been successfully added to the database!")

            elif genre == "Nonfiction":
                subject = input("\nNonFiction Genre subject:\n").title().strip()
                genre_obj.add_category(subject)
                new_book = NonFictionBook(title, author_obj, isbn, genre_obj, subject)
                genre_obj.add_book_to_category(subject, new_book)
            else:
                print("Invalid genre type. Please specify 'Fiction' or 'Nonfiction'.")
                return
            # Assigning the newly created book object (new_book) to the books dictionary attribute of the Library class, using the ISBN as the key:
            self.books[isbn] = new_book
            print(f'\nThe book "{title}" by {author} has been added to the library.')

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
            library_id = input("\nYour library id (example: AA12345):\n").upper().strip()
            while not re.match(r"^[A-Za-z]{2}\d{5}$", library_id):
                library_id = input("\nPlease enter your library_id in the correct format (example: AA123-45678):\n").upper().strip()
            # Checking if the user already exists in the system:
            for user in self.users:
                if user.get_library_id() == library_id:
                    print("\nUser with the same library ID already exists!")
                    return user
            # If the user doesn't exist, create a new user object and add it to the list:
            new_user = User(name, library_id)
            self.users.append(new_user)
            print(f"\n{new_user.name} (Library ID: {new_user.get_library_id()}) has been added as a new user to the library.")

            query = "INSERT INTO books (title, author, isbn, genre, category) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (new_user.get_t, new_user.get_library_id()))
            conn.commit()
            print(f"\n{new_user.name} (Library ID: {new_user.get_library_id()}) has also been successfully added to the database!")
            
            return new_user

        except Error as e:
            print(f"\nError: {e}")

        finally:
            if conn and conn.is_connected():
                    cursor.close()
                    conn.close()
            

    def check_out_book(self):
        print("\nPlease enter the following information:")
        isbn = input("\nBook ISBN (13 digits: example: 978-92-95055-02-5):\n").strip()
        while not re.match(r"^\d{3}-\d{2}-\d{5}-\d{2}-\d{1}$", isbn):
            isbn = input("\nPlease enter the ISBN in the correct format (example: 978-92-95055-02-5):\n").strip()
        if isbn in self.books:
            current_user = self.add_user()  # Adding or getting the current user
            if self.books[isbn].borrow_book():
                current_user.borrowed_books.append(self.books[isbn]) # Adding the book to the current user's borrowed books
                print(f'\nThe book "{self.books[isbn].get_title()}" by {self.books[isbn].get_author()}, ISBN: {isbn}, has been loaned to {current_user.name.title()}, library ID {current_user.get_library_id()}')
                # Adding the book to the loaned_books dictionary:
                if current_user.get_library_id() not in self.loaned_books:
                    # Initializing an empty dictionary for the user's library ID. Without it, we will have a KeyError if the ID doesn't exist:
                    self.loaned_books[current_user.get_library_id()] = {} 
                self.loaned_books[current_user.get_library_id()][isbn] = self.books[isbn] # Adding the book to the user's library ID dictionary
            else:
                print("\nThe book is unavailable!")
        else:
           print(f"\nThere is no book with ISBN '{isbn}' in the library!")     

    def check_in_book(self):
        print("\nPlease enter the following information to return a book:")
        library_id = input("\nYour library ID (example: AZ12345):\n").upper().strip()
        while not re.match(r"^[A-Za-z]{2}\d{5}$", library_id):
            library_id = input("\nPlease enter your library ID in the correct format (example: AZ12345):\n").upper().strip()
        isbn = input("\nBook ISBN (example: 978-92-95055-02-5):\n").strip()
        while not re.match(r"^\d{3}-\d{2}-\d{5}-\d{2}-\d{1}$", isbn):
            isbn = input("\nPlease enter the ISBN in the correct format (example: 978-92-95055-02-5):\n").strip()
        # Looking for the user by Library ID:
        user = None # Initializing user variable
        for returning_user in self.users:
            if returning_user.get_library_id() == library_id:
                user = returning_user
                # Adding "break" here to ensure that once the matching user is found, the loop exits immediately reducing the number 
                # of unnecessary iterations. It also help us avoid potential errors if there are duplicate library IDs or other unforeseen issues:
                break
        if user is None:  # If no user is found with the given library ID
            print(f"\nNo user with Library ID: {library_id} has been found in the library!")
        else:
            if library_id in self.loaned_books and isbn in self.loaned_books[library_id]:  # Checking if the book is recorded as loaned to the user
                book = self.loaned_books[library_id].pop(isbn)  # Removing the book from loaned_books
                if book in user.borrowed_books:
                    user.borrowed_books.remove(book)  # Removing the book from the user's borrowed_books list
                    book.return_book() # Setting the book as available
                    print(f"\nThe book '{book.get_title()}', ISBN: {isbn} has been returned by {user.name}, (Library ID: {library_id})")
                else:
                    # If book was not found in the user's borrowed_books list
                    print(f"\nThe book with ISBN {isbn} has not been borrowed by {user.name.title()} (Library ID: {library_id})")
            else:
                print(f"\nNo record found for the book with ISBN {isbn} borrowed by {user.name.title()}, (Library ID: {library_id})")

    def search_book_title(self):
        title = input("\nEnter the book title:\n").lower().strip()
        search_result = {}
        # if search_result = {}
        for isbn, book in self.books.items():
            if title in book.get_title().lower(): # Checking if the title input is found in any of our books
                search_result[isbn] = book # Adding all matching books to search results
        if search_result: # Checking if any books were found
            print("\nThis is what we have found in the library:\n")
            for isbn, book in search_result.items():
                print(f"{book.get_title()} by {book.get_author()}, ISBN: {isbn}")
        else:
            print(f"\nNo book titled '{title.title()}' has been found in the library!")

        return search_result

    def search_book_author(self):
        author = input("\nEnter the book author?\n").lower().strip()
        search_result = {}
        for isbn, book in self.books.items():
            if author in book.get_author().lower(): 
                search_result[isbn] = book
        if search_result:
            print("\nThis is what we have found in the library:\n")
            for isbn, book in search_result.items():
                print(f"{book.get_title()} by {book.get_author()}, ISBN: {isbn}")
        else:
            print(f"\nNo '{author.title()}' has been found in the library!")

        return search_result

    def search_book_isbn(self):
        isbn = input("\nEnter the book ISBN (13 digits: example: 978-92-95055-02-5):\n").strip()
        while not re.match(r"^\d{3}-\d{2}-\d{5}-\d{2}-\d{1}$", isbn):
                isbn = input("\nPlease enter the ISBN in the correct format (example: 978-92-95055-02-5):\n").strip()
        search_result = {}
        for book_isbn, book in self.books.items():
            if book.get_isbn() == isbn:
                search_result[isbn] = book
        if search_result:
            print("\nThis is what we have found in the library:\n")
            for book_isbn, book in search_result.items():
                print(f"{book.get_title()} by {book.get_author()}, ISBN: {book_isbn}")
        else:
            print(f"\nNo ISBN '{isbn}' has been found in our library!")

        return search_result

    def display_all_books(self):
        print("\nHere is the list of books in the library:\n")
        for isbn, book in self.books.items():
            print(f"{book.get_title()} by {book.get_author()}, ISBN: {isbn}")
        if not self.books:
            print("Currently, there are no books in the library!")
              
    def display_all_loaned_books(self):
        print("\nHere is the list of loaned books in the library:")
        if not self.loaned_books: # First checking if there are no loaned books before iterating over each book and Library ID
            print("\nNo books are currently loaned!")
        else:
            for library_id, books in self.loaned_books.items(): # Iterating over each library_id and its associated books in loaned_books dictionary
                user = self.find_user_by_library_id(library_id) # Finding the user associated with the current library_id
                if user and user.borrowed_books: # Checking if the user exists and has borrowed books
                    print(f"\nBooks loaned to {user.name} (Library ID: {library_id}):")
                    # Iterating over each book (ISBN and Book object) loaned to the user:
                    for isbn, book in books.items():
                        print(f"\n{book.get_title()} by {book.get_author()}, ISBN: {isbn}") 
                elif not user:
                    # Although the code set up ensures that each borrowed book is linked to a valid user through their library ID, 
                    # the message will be printed in case no user is found for loaned books:
                    print(f"\nBooks loaned to unknown user (Library ID {library_id}):")
        # Checking if there are no loaned books at all or no users with borrowed books
        # If there are no users with borrowed books, it prints the message "No books are currently loaned!". Otherwise, it doesn't print anything
        if not any(user.borrowed_books for user in self.users):
            print("\nNo books are currently loaned!")   
                
    def view_user_info(self):
        print("\nPlease enter the following information:")
        library_id = input("\nLibrary ID (example: AZ12345):\n").upper().strip()
        while not re.match(r"^[A-Za-z]{2}\d{5}$", library_id):
            library_id = input("\nPlease enter the Library ID in the correct format (example: AZ12345):\n").upper().strip()
        # Finding the user with the given library ID:
        user = self.find_user_by_library_id(library_id)
        if user:
            user.show_user_info() # Displaying user's borrowed books
        else:
            print(f"\nNo user was found with Library ID {library_id}.") # Printing this message if no user is found with the given Library ID
    
    def find_user_by_library_id(self, library_id): # Searching for and returning a user by their Library ID, or None if the user is not found
        for user in self.users:
            if user.get_library_id() == library_id:
                return user
        return None
    
    def display_all_users(self):
        print("\nHere is the list of current users in the library:")
        if not self.users:
            print("\nNo users are found!")
        else:
            for user in self.users:
                print(f"\n{user.name.title()} (Library ID: {user.get_library_id()})")

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
            # Checking if an author with the same name already exists in the library
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
            print('\nThe author has been successfully added to the database!')
            
            return new_author

        except Error as e:
            print(f"\nError: {e}")

        finally:
            if conn and conn.is_connected():
                    cursor.close()
                    conn.close()
        
    def view_author_details(self):
        author_name = input("\nPlease enter the name of the author you are interested in:\n").title().strip()
        # Looking for the authors containing the entered name:
        matched_authors = [author for author in self.authors if author.get_name() == author_name]
        if matched_authors:
            if len(matched_authors) > 1:
                # If multiple authors match, listing them and letting the user choose
                print(f"\nMultiple authors found matching '{author_name}':")
                for idx, author in enumerate(matched_authors, start=1): # Enumerating over matched authors to list them with index numbers starting from 1
                    print(f"{idx}. {author.get_name()}")
                # Asking user to select an author:
                choice = input("\nEnter the number of the author you want to view:\n").strip()
                while not choice.isdigit() or int(choice) < 1 or int(choice) > len(matched_authors):
                    choice = input("\nInvalid choice. Please enter a valid number:\n").strip()
                # Display the selected author's information
                chosen_author = matched_authors[int(choice) - 1] # Getting the chosen author based on the user's selection and deduct 1 to match the index
                chosen_author.show_author_info() # Displaying the selected author's information
            else:
                # If only one author matches, show that author's information
                matched_authors[0].show_author_info()
        else:
            print(f"\n{author_name} is not in the list of authors in the library!")
    
    def display_all_authors(self):
        print("\nHere is the list of current authors in the library:")
        if not self.authors:
            print("\nNo authors have been added to the library yet!")
        else:
            for author in self.authors:
                print(f"\nAuthor: {author.get_name()}")
                print(f"Biography: {author.get_biography()}")

    def add_genre(self, genre=None):
        try:
            # Establishing a connection to the database
            conn = connect_db()
            cursor = conn.cursor()
            
            # If genre is not specified, prompting the user to input it
            if genre is None:
                genre = input("\nPlease enter the type of genre you want to add (Fiction or Nonfiction):\n").title().strip()

            # Validating the genre input
            if genre not in ["Fiction", "Nonfiction"]:
                print("Invalid genre type. Please specify 'Fiction' or 'Nonfiction'.")
                return None

            # Checking if the genre already exists in the local list
            for existing_genre in self.genres:
                if existing_genre.get_name() == genre:
                    # If the genre exists, prompting the user to add a new category/subject
                    if genre == "Fiction":
                        category = input("\nFiction Genre category:\n").title().strip()
                        existing_genre.add_category(category)
                    elif genre == "Nonfiction":
                        subject = input("\nNonfiction Genre subject:\n").title().strip()
                        existing_genre.add_category(subject)
                    
                    # Retrieving the genre ID from the database
                    category_query = "INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)"
                    genre_id_query = "SELECT id FROM genres WHERE genre_name = %s"
                    cursor.execute(genre_id_query, (genre,))
                    genre_id_result = cursor.fetchall()

                    if genre_id_result:  # Checking if any rows were returned
                        genre_id = genre_id_result[0][0]  # Accessing the first element of the first tuple

                        # Inserting the new category/subject into the genre_categories table
                        if genre == "Fiction":
                            cursor.execute(category_query, (genre_id, category))
                        elif genre == "Nonfiction":
                            cursor.execute(category_query, (genre_id, subject))
                        
                        conn.commit()
                    else:
                        print("No Genre ID Retrieved. Genre not found.")

                    # Informing the user that the genre already exists and a new category/subject has been added
                    print(f"\nGenre '{existing_genre.get_name()}' already exists in the library. Added new category/subject.")
                    return existing_genre

            # If the genre does not exist in the local list, prompting the user to add it
            description = input("\nGenre description (no more than 200 characters):\n").capitalize().strip()
            if len(description) > 200:
                description = description[:200]
            new_genre = Genre(genre, description)
            self.genres.append(new_genre)  # Adding the new genre to the list

            # Inserting the new genre into the genres table in the database
            genre_query = "INSERT INTO genres (genre_name, genre_description) VALUES (%s, %s)"
            cursor.execute(genre_query, (new_genre.get_name(), new_genre.get_description()))
            conn.commit()

            # Retrieving the ID of the newly inserted genre
            cursor.execute("SELECT LAST_INSERT_ID()")
            genre_id_result = cursor.fetchall()

            if genre_id_result:  # Checking if any rows were returned
                genre_id = genre_id_result[0][0]  # Accessing the first element of the first tuple

                # Inserting each category/subject into the genre_categories table
                category_query = "INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)"
                for category in new_genre.get_categories():
                    cursor.execute(category_query, (genre_id, category))

                conn.commit()
            else:
                print("No Newly Inserted Genre ID Retrieved.")

            # Informing the user that the genre and its categories have been successfully added to the database
            print('\nThe genre and its categories have been successfully added to the database!')

            return new_genre

        except Error as e:
            # Handling any errors that occur during the process
            print(f"\nAn error occurred: {e}")

        finally:
            # Closing the cursor and database connection
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

   



# Retrieve ID result WORK!!

    # def add_genre(self, genre=None):
    #     try:
    #         conn = connect_db()
    #         cursor = conn.cursor()
            
    #         if genre is None:
    #             genre = input("\nPlease enter the type of genre you want to add (Fiction or Nonfiction):\n").title().strip()

    #         if genre not in ["Fiction", "Nonfiction"]:
    #             print("Invalid genre type. Please specify 'Fiction' or 'Nonfiction'.")
    #             return None

    #         # Checking if the genre already exists
    #         for existing_genre in self.genres:
    #             if existing_genre.get_name() == genre:
    #                 if genre == "Fiction":
    #                     category = input("\nFiction Genre category:\n").title().strip()
    #                     existing_genre.add_category(category)
    #                 elif genre == "Nonfiction":
    #                     subject = input("\nNonFiction Genre subject:\n").title().strip()
    #                     existing_genre.add_category(subject)
                    
    #                 # Insert the new category into the genre_categories table
    #                 category_query = "INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)"
    #                 genre_id_query = "SELECT id FROM genres WHERE genre_name = %s"
    #                 cursor.execute(genre_id_query, (genre,))
    #                 genre_id_result = cursor.fetchall()

    #                 print("Genre ID Result:", genre_id_result)

    #                 if genre_id_result:  # Check if any rows were returned
    #                     genre_id = genre_id_result[0][0]  # Access the first element of the first tuple
    #                     print("Retrieved Genre ID:", genre_id)

    #                     if genre == "Fiction":
    #                         cursor.execute(category_query, (genre_id, category))
    #                     elif genre == "Nonfiction":
    #                         cursor.execute(category_query, (genre_id, subject))
                        
    #                     conn.commit()
    #                     print("Category/Subject Inserted Successfully!")
    #                 else:
    #                     print("No Genre ID Retrieved. Genre not found.")

    #                 print(f"\nGenre '{existing_genre.get_name()}' already exists in the library. Added new category/subject.")
    #                 return existing_genre

    #         # If genre does not exist, prompting for description and adding it
    #         description = input("\nGenre description (no more than 200 characters):\n").capitalize().strip()
    #         if len(description) > 200:
    #             description = description[:200]
    #         new_genre = Genre(genre, description)
    #         self.genres.append(new_genre)  # Adding the new genre to the list

    #         print(f"\nGenre '{new_genre.get_name()}' has been added to the list of genres in the library.")
        
    #         # Inserting the new genre into the genres table
    #         genre_query = "INSERT INTO genres (genre_name, genre_description) VALUES (%s, %s)"
    #         cursor.execute(genre_query, (new_genre.get_name(), new_genre.get_description()))
    #         conn.commit()

    #         # Retrieve the ID of the newly inserted genre
    #         cursor.execute("SELECT LAST_INSERT_ID()")
    #         genre_id_result = cursor.fetchall()

    #         print("Newly Inserted Genre ID Result:", genre_id_result)

    #         if genre_id_result:  # Check if any rows were returned
    #             genre_id = genre_id_result[0][0]  # Access the first element of the first tuple
    #             print("Retrieved Newly Inserted Genre ID:", genre_id)

    #             # Inserting each category/subject into the genre_categories table
    #             category_query = "INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)"
    #             for category in new_genre.get_categories():
    #                 cursor.execute(category_query, (genre_id, category))

    #             conn.commit()
    #             print("Categories Inserted Successfully!")
    #         else:
    #             print("No Newly Inserted Genre ID Retrieved.")

    #         print('\nThe genre and its categories have been successfully added to the database!')

    #         return new_genre

    #     except Error as e:
    #         print(f"\nAn error occurred: {e}")

    #     finally:
    #         if conn and conn.is_connected():
    #             cursor.close()
    #             conn.close()


    
    # def add_genre(self, genre=None):
    #     try:
    #         conn = connect_db()
    #         cursor = conn.cursor()
    #         if genre is None:
    #             genre = input("\nPlease enter the type of genre you want to add (Fiction or Nonfiction):\n").title().strip()

    #         if genre not in ["Fiction", "Nonfiction"]:
    #             print("Invalid genre type. Please specify 'Fiction' or 'Nonfiction'.")
    #             return None

    #         # Checking if the genre already exists
    #         for existing_genre in self.genres:
    #             if existing_genre.get_name() == genre:
    #                 if genre == "Fiction":
    #                     category = input("\nFiction Genre category:\n").title().strip()
    #                     existing_genre.add_category(category)
    #                 elif genre == "Nonfiction":
    #                     subject = input("\nNonFiction Genre subject:\n").title().strip()
    #                     existing_genre.add_category(subject)
                    
    #                 # Insert the new category into the genre_categories table
    #                 category_query = "INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)"
    #                 genre_id_query = "SELECT id FROM genres WHERE genre_name = %s"
    #                 cursor.execute(genre_id_query, (genre,))
    #                 genre_id = cursor.fetchall()[0][0] # Access the first element of the first tuple

    #                 if genre == "Fiction":
    #                     cursor.execute(category_query, (genre_id, category))
    #                 elif genre == "Nonfiction":
    #                     cursor.execute(category_query, (genre_id, subject))
                    
    #                 conn.commit()

    #                 print(f"\nGenre '{existing_genre.get_name()}' already exists in the library. Added new category/subject.")
    #                 return existing_genre

    #         # If genre does not exist, prompting for description and adding it
    #         description = input("\nGenre description (no more than 200 characters):\n").capitalize().strip()
    #         if len(description) > 200:
    #             description = description[:200]
    #         new_genre = Genre(genre, description)
    #         self.genres.append(new_genre)  # Adding the new genre to the list

    #         print(f"\nGenre '{new_genre.get_name()}' has been added to the list of genres in the library.")
        
    #         # Inserting the new genre into the genres table
    #         genre_query = "INSERT INTO genres (genre_name, genre_description) VALUES (%s, %s)"
    #         cursor.execute(genre_query, (new_genre.get_name(), new_genre.get_description()))
    #         conn.commit()

    #         # Retrieve the ID of the newly inserted genre
    #         cursor.execute("SELECT LAST_INSERT_ID()")
    #         genre_id = cursor.fetchall()[0][0]  # Fetch all rows and retrieve the first row

    #         # Inserting each category/subject into the genre_categories table
    #         category_query = "INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)"
    #         for category in new_genre.get_categories():
    #             cursor.execute(category_query, (genre_id, category))

    #         conn.commit()
    #         print('\nThe genre and its categories have been successfully added to the database!')

    #         return new_genre

    #     except Error as e:
    #         print(f"\nAn error occurred: {e}")

    #     finally:
    #         if conn and conn.is_connected():
    #             cursor.close()
    #             conn.close()














    # def add_genre(self, genre=None):
    #     try:
    #         conn = connect_db()
    #         cursor = conn.cursor()
    #         if genre is None:
    #             genre = input("\nPlease enter the type of genre you want to add (Fiction or Nonfiction):\n").title().strip()

    #         if genre not in ["Fiction", "Nonfiction"]:
    #             print("Invalid genre type. Please specify 'Fiction' or 'Nonfiction'.")
    #             return None

    #         # Checking if the genre already exists
    #         for existing_genre in self.genres:
    #             if existing_genre.get_name() == genre:
    #                 if genre == "Fiction":
    #                     category = input("\nFiction Genre category:\n").title().strip()
    #                     existing_genre.add_category(category)
    #                 elif genre == "Nonfiction":
    #                     subject = input("\nNonFiction Genre subject:\n").title().strip()
    #                     existing_genre.add_category(subject)
    #                 print(f"\nGenre '{existing_genre.get_name()}' already exists in the library. Added new category/subject.")
    #                 return existing_genre

    #         # If genre does not exist, prompting for description and adding it
    #         description = input("\nGenre description (no more than 200 characters):\n").capitalize().strip()
    #         if len(description) > 200:
    #             description = description[:200]
    #         new_genre = Genre(genre, description)
    #         self.genres.append(new_genre)  # Adding the new genre to the list

    #         print(f"\nGenre '{new_genre.get_name()}' has been added to the list of genres in the library.")
        
    #         # Inserting the new genre into the genres table
    #         genre_query = "INSERT INTO genres (genre_name, genre_description) VALUES (%s, %s)"
    #         cursor.execute(genre_query, (new_genre.get_name(), new_genre.get_description()))
    #         genre_id = cursor.lastrowid  # Getting the id of the newly inserted genre

    #         # Inserting each category/subject into the genre_categories table
    #         category_query = "INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)"
    #         for category in new_genre.get_categories():
    #             cursor.execute(category_query, (genre_id, category))

    #         conn.commit()
    #         print('\nThe genre and its categories have been successfully added to the database!')

    #         return new_genre

    #     except Error as e:
    #         print(f"\nAn error occurred: {e}")

    #     finally:
    #         if conn and conn.is_connected():
    #             cursor.close()
    #             conn.close()




             


       






# WORKING!!!

    # def add_genre(self, genre=None, silent=False):
    #     try:
    #         conn = connect_db()
    #         cursor = conn.cursor()

    #         if genre is None:
    #             genre = input("\nPlease enter the type of genre you want to add (Fiction or Nonfiction):\n").title().strip()

    #         if genre == "Fiction" or genre == "Nonfiction":
    #             description = input("\nGenre description (no more than 200 characters):\n").capitalize().strip()
    #             if len(description) > 200:
    #                 description = description[:200]
    #             new_genre = Genre(genre, description)
    #         else:
    #             print("Invalid genre type. Please specify 'Fiction' or 'Nonfiction'.")
    #             return None
            
    #         existing_genre = None 
    #         genre_id = None
    #         for genre_obj in self.genres: 
    #             if genre_obj.get_name() == new_genre.get_name():
    #                 existing_genre = genre_obj
    #                 if genre == "Fiction":
    #                     category = input("\nFiction Genre category:\n").title().strip()
    #                     existing_genre.add_category(category)
    #                 elif genre == "Nonfiction":
    #                     subject = input("\nNonFiction Genre subject:\n").title().strip()
    #                     existing_genre.add_category(subject)
                    
    #                 if not silent:
    #                     print(f"\nGenre '{existing_genre.get_name()}' already exists in the library.")
    #                 break

    #         if existing_genre is None: 
    #             self.genres.append(new_genre) 
    #             if not silent:
    #                 print(f"\nGenre '{new_genre.get_name()}' has been added to the list of genres in the library.")
                
    #             # After inserting the new genre into the genres table
    #             query = "INSERT INTO genres (genre_name, genre_description) VALUES (%s, %s)"
    #             cursor.execute(query, (new_genre.get_name(), new_genre.get_description()))
    #             conn.commit() 

    #             # Retrieve the genre_id of the newly inserted genre
    #             genre_id = cursor.lastrowid

    #             # Check if the genre_id is not None (indicating successful insertion)
    #             if genre_id is not None:
    #                 # Insert categories into the genre_categories table using the retrieved genre_id
    #                 category_query = "INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)"
    #                 for category in new_genre.get_categories().keys():
    #                     cursor.execute(category_query, (genre_id, category))
    #                 conn.commit()
    #             else:
    #                 print("Error: Failed to retrieve genre ID after inserting into genres table.")
    #         else: 
    #             category_query = "INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)"
    #             for category in existing_genre.get_categories().keys():
    #                 cursor.execute(category_query, (genre_id, category))
                
    #             conn.commit() 

    #         print('\nThe genre and its categories have been successfully added to the database!')

    #         return new_genre if existing_genre is None else existing_genre
        
    #     except Error as e:
    #         print(f"\nAn error occurred: {e}")

    #     finally:
    #         if conn and conn.is_connected():
    #             cursor.close()
    #             conn.close()
    
    # def get_genre_id_from_db(self, cursor, genre_name):
    #     query = "SELECT id FROM genres WHERE genre_name = %s"
    #     cursor.execute(query, (genre_name,))
    #     result = cursor.fetchone()
    #     if result:
    #         return result[0]
    #     return None










    # def add_genre(self, genre=None, silent=False): # Making the genre parameter optional. It allows us to call the method within add_book() without needing to providing a genre argument
    #                                                # Adding an optional silent parameter. When silent is True, it suppresses the messages about the genre already existing or being added
    #     try:
    #         conn = connect_db()
    #         cursor = conn.cursor()

    #         if genre is None:
    #             genre = input("\nPlease enter the type of genre you want to add (Fiction or Nonfiction):\n").title().strip()

    #         if genre == "Fiction" or genre == "Nonfiction":
    #             description = input("\nGenre description (no more than 200 characters):\n").capitalize().strip()
    #             if len(description) > 200:
    #                 description = description[:200]
    #             new_genre = Genre(genre, description)
    #         else:
    #             print("Invalid genre type. Please specify 'Fiction' or 'Nonfiction'.")
    #             return None
            
    #         existing_genre = None # Initializing existing_genre to None
    #         genre_id = None
    #         for genre_obj in self.genres: # Checking if the genre already exists:
    #             if genre_obj.get_name() == new_genre.get_name():
    #                 existing_genre = genre_obj
    #                 if genre == "Fiction":
    #                     category = input("\nFiction Genre category:\n").title().strip()
    #                     existing_genre.add_category(category)
    #                 elif genre == "Nonfiction":
    #                     subject = input("\nNonFiction Genre subject:\n").title().strip()
    #                     existing_genre.add_category(subject)

    #                 cursor.fetchall() # Clearing any unread results before executing the next query
    #                 genre_id = self.get_genre_id_from_db(cursor, existing_genre.get_name())  # Get the existing genre's ID from the database
    #                 if not silent:
    #                     print(f"\nGenre '{existing_genre.get_name()}' already exists in the library.")
    #                 break

    #         if existing_genre is None: # New genre
    #             self.genres.append(new_genre) # If it doesn't exist, adding the new genre to the list
    #             if not silent:
    #                 print(f"\nGenre '{new_genre.get_name()}' has been added to the list of genres in the library.")
            
    #             query = "INSERT INTO genres (genre_name, genre_description) VALUES (%s, %s)"
    #             cursor.execute(query, (new_genre.get_name(), new_genre.get_description()))
    #             genre_id = cursor.lastrowid  # Retrieving the ID of the last inserted row in the genres table. This ID is used to associate categories/subjects with the correct genre.

    #             category_query = "INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)"
    #             # Convert the categories dictionary to a string to avoid this Error: Failed processing format-parameters; Python 'dict' cannot be converted to a MySQL type
    #             # categories_str = ', '.join(new_genre.get_categories().keys()) 
    #             #   For example, 
    #             #   categories_dict = {
    #             #     "Science": [],
    #             #     "Mystery": [],
    #             #     "Fantasy": []
    #             #   }  is converted first to: ["Science", "Mystery", "Fantasy"] and then to a string separated by comma: "Science, Mystery, Fantasy"

    #             # Inserting each category/subject into the genre_categories table
    #             for category in new_genre.get_categories().keys():
    #                 cursor.execute(category_query, (genre_id, category))

    #         else: # Existing genre
    #             category_query = "INSERT INTO genre_categories (genre_id, category_subject) VALUES (%s, %s)"
    #             for category in existing_genre.get_categories().keys():
    #                 cursor.execute(category_query, (genre_id, category))

    #         conn.commit()
    #         print('\nThe genre and its categories have been successfully added to the database!')

    #         return new_genre if existing_genre is None else existing_genre
        
    #     except Error as e:
    #         print(f"\nError: {e}")

    #     finally:
    #         if conn and conn.is_connected():
    #                 cursor.close()
    #                 conn.close()

    # def get_genre_id_from_db(self, cursor, genre_name):
    #     query = "SELECT id FROM genres WHERE genre_name = %s"
    #     cursor.execute(query, (genre_name,))
    #     result = cursor.fetchone()
    #     if result:
    #         return result[0]
    #     return None
    
    def view_genre_details(self):
        for genre in self.genres:
            print(f"\nGenre: {genre.get_name()}, Description: {genre.get_description()}")
            for category, books in genre.get_categories().items():
                print(f"Category: {category}")
                for book in books:
                    print(f"  - {book}")
   
    def view_all_genres(self):
        print("\nHere is the list of all genres in the library:")
        if not self.genres:
            print("\nNo genres have been added to the library yet!")
        else:
            for genre in self.genres:
                print(f"\nGenre: {genre.get_name()}")
                print(f"Description: {genre.get_description()}")
                print("\nBooks in this genre:")
                # Using self.books.values() to access all the Book objects stored in the library, regardless of their ISBN keys:
                genre_books = [book for book in self.books.values() if book.get_genre() == genre]
                if genre_books:
                    for book in genre_books:
                        # Using book.get_author().get_name() call to first retrieve the Author object and then get the name of the author:
                        print(f"  - Title: {book.get_title()}, Author: {book.get_author().get_name()}")
                else:
                    print("  - No books in this genre")