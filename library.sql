-- CREATING AND USING OUR LIBRARY DATA BASE

CREATE DATABASE library_management_system;

USE library_management_system;

CREATE TABLE authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    biography TEXT
);

SELECT *
FROM authors;

DROP TABLE authors;

CREATE TABLE genres (
	id INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(50),
    genre_description VARCHAR(200)
);

DROP TABLE genres;

-- ALTER TABLE genres
-- DROP COLUMN genre_details;

-- ALTER TABLE genres
-- ADD genre_description VARCHAR(200);

SELECT *
FROM genres;

CREATE TABLE genre_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    genre_id INT,
    category_subject VARCHAR(50),
    FOREIGN KEY (genre_id) REFERENCES genres(id)
);

SELECT *
FROM genre_categories;

DROP TABLE genre_categories;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    library_id VARCHAR(10) NOT NULL UNIQUE
);

SELECT *
FROM users;

DROP TABLE users;

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT,
    isbn VARCHAR(17) NOT NULL,
    genre_id INT,
    category_subject VARCHAR(255),
    availability BOOLEAN DEFAULT 1,
    FOREIGN KEY (author_id) REFERENCES authors(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id)
);

SELECT *
FROM books;

DROP TABLE books;

CREATE TABLE borrowed_books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    book_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

SELECT *
FROM borrowed_books;

DROP TABLE borrowed_books;
