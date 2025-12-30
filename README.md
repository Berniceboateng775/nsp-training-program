#  SQL Practice & Learning Notes
## Introduction to SQL

### What is SQL?
**SQL (Structured Query Language)** is the standard language for interacting with relational databases. It allows you to:
- **C**reate data (INSERT)
- **R**ead data (SELECT)
- **U**pdate data (UPDATE)
- **D**elete data (DELETE)

This is known as **CRUD** operations.

### Why Learn SQL?
- Essential for data analysis and data science
- Query and analyze large datasets efficiently
- Used by almost every company with data
- High-demand skill in the job market

---

## My Dataset

I am working with a **Bookstore Database** containing the following tables:

### Books Table
| Column | Type | Description |
|--------|------|-------------|
| book_id | INTEGER | Primary Key - Unique book identifier |
| book_title | TEXT | Title of the book |
| book_author | TEXT | Author name |
| book_genre | TEXT | Genre category |
| price | REAL | Book price in dollars |
| units_sold | INTEGER | Number of units sold (has NULL) |
| quantity | INTEGER | Stock quantity |
| author_id | INTEGER | Foreign Key to Authors table |
| book_rating | REAL | Average rating (1-5) |

### Authors Table
| Column | Type | Description |
|--------|------|-------------|
| author_id | INTEGER | Primary Key - Unique author identifier |
| author_name | TEXT | Author's full name |
| country | TEXT | Author's country of origin |
| birth_year | INTEGER | Year of birth |

### Orders Table
| Column | Type | Description |
|--------|------|-------------|
| order_id | INTEGER | Primary Key |
| book_id | INTEGER | Foreign Key to Books |
| customer_name | TEXT | Customer name |
| order_date | TEXT | Date of order |
| quantity | INTEGER | Quantity ordered |

---

## Basic SQL Operations

### 1. SELECT - Retrieving Data

```sql
-- Select all columns from a table
SELECT * FROM data;

-- Select specific columns
SELECT book_title, book_author, price FROM data;

-- Using aliases for cleaner output
SELECT book_title AS "Book Name", price AS "Price ($)" FROM data;
```

### 2. WHERE - Filtering Data

```sql
-- Filter by condition
SELECT * FROM data WHERE price > 14;

-- Multiple conditions with AND
SELECT * FROM data WHERE price > 12 AND book_rating > 4.5;

-- Using OR for alternative conditions
SELECT * FROM data WHERE book_genre = 'Fantasy' OR book_genre = 'Mafia';

-- Using IN for multiple values
SELECT * FROM data WHERE book_genre IN ('Fantasy', 'Mafia', 'Dark Romace');

-- Using BETWEEN for ranges
SELECT * FROM data WHERE price BETWEEN 10 AND 15;

-- Pattern matching with LIKE
SELECT * FROM data WHERE book_title LIKE '%Wing%';  -- Contains 'Wing'
SELECT * FROM data WHERE book_author LIKE 'J%';      -- Starts with 'J'
```

### 3. ORDER BY - Sorting Results

```sql
-- Sort ascending (default)
SELECT * FROM data ORDER BY price ASC;

-- Sort descending
SELECT * FROM data ORDER BY price DESC;

-- Sort by multiple columns
SELECT * FROM data ORDER BY book_genre, book_rating DESC;
```

### 4. LIMIT - Restricting Results

```sql
-- Get only first 3 rows
SELECT * FROM data LIMIT 3;

-- Skip first 2, then get 3 rows (pagination)
SELECT * FROM data LIMIT 3 OFFSET 2;
```

### 5. INSERT - Adding New Data

```sql
-- Insert a single row
INSERT INTO data (book_title, book_author, book_genre, price, units_sold, book_id, quantity, author_id, book_rating)
VALUES ('Iron Flame', 'Rebecca Yarros', 'Fantasy', 15.99, 500, 6, 60, 3, 4.8);

-- Insert multiple rows
INSERT INTO data (book_title, book_author, price, book_id)
VALUES 
    ('Book One', 'Author A', 9.99, 7),
    ('Book Two', 'Author B', 11.99, 8);
```

### 6. UPDATE - Modifying Data

```sql
-- Update a single column
UPDATE data SET price = 11.99 WHERE book_id = 1;

-- Update multiple columns
UPDATE data SET price = 12.99, quantity = 25 WHERE book_title = 'ACOTAR';
```

### 7. DELETE - Removing Data

```sql
-- Delete specific rows
DELETE FROM data WHERE book_id = 5;

-- Delete all rows (be careful!)
DELETE FROM data;
```

---

## SQL Constraints

Constraints are rules applied to columns to ensure data integrity.

### 1. NOT NULL Constraint

Ensures a column cannot have NULL values.

```sql
-- Creating a table with NOT NULL constraint
CREATE TABLE books (
    book_id INTEGER NOT NULL,
    book_title TEXT NOT NULL,
    price REAL NOT NULL,
    units_sold INTEGER  -- This CAN be NULL
);

-- This will FAIL because book_title is NOT NULL
INSERT INTO books (book_id, price) VALUES (1, 10.99);
-- Error: NOT NULL constraint failed

-- Checking for NULL values
SELECT * FROM data WHERE units_sold IS NULL;

-- Finding rows where column is NOT NULL
SELECT * FROM data WHERE units_sold IS NOT NULL;
```

### 2. PRIMARY KEY Constraint

- Uniquely identifies each record in a table
- Cannot be NULL
- Each table should have ONE primary key

```sql
-- Creating a table with PRIMARY KEY
CREATE TABLE authors (
    author_id INTEGER PRIMARY KEY,  -- Unique identifier
    author_name TEXT NOT NULL,
    country TEXT,
    birth_year INTEGER
);

-- In SQLite, PRIMARY KEY auto-increments
INSERT INTO authors (author_name, country) VALUES ('J.J McAvoy', 'Canada');
-- author_id will be automatically assigned as 1
```

### 3. FOREIGN KEY Constraint

- Creates a link between two tables
- References a PRIMARY KEY in another table
- Ensures referential integrity

```sql
-- Creating tables with FOREIGN KEY relationship
CREATE TABLE authors (
    author_id INTEGER PRIMARY KEY,
    author_name TEXT NOT NULL,
    country TEXT
);

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY,
    book_title TEXT NOT NULL,
    author_id INTEGER,
    price REAL,
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

-- Now books.author_id MUST reference a valid authors.author_id
-- This ensures data consistency between tables
```

### 4. UNIQUE Constraint

Ensures all values in a column are different.

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    email TEXT UNIQUE,  -- No duplicate emails allowed
    username TEXT UNIQUE
);
```

### 5. DEFAULT Constraint

Sets a default value when no value is specified.

```sql
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    in_stock INTEGER DEFAULT 1,  -- Defaults to 1 if not specified
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 6. CHECK Constraint

Limits values that can be placed in a column.

```sql
CREATE TABLE books (
    book_id INTEGER PRIMARY KEY,
    book_title TEXT NOT NULL,
    price REAL CHECK(price > 0),  -- Price must be positive
    rating REAL CHECK(rating >= 1 AND rating <= 5)  -- Rating between 1-5
);
```

---

## SQL JOINs

JOINs combine rows from two or more tables based on related columns.

### Visual Representation

```
Table A (Books)          Table B (Authors)
+---------+             +-----------+
| book_id |──────────── | author_id |
| title   |   JOIN ON   | name      |
| auth_id |   auth_id = | country   |
+---------+   author_id +-----------+
```

### 1. INNER JOIN

Returns only rows that have matching values in BOTH tables.

```sql
-- Get books with their author details
SELECT 
    b.book_title,
    b.price,
    a.author_name,
    a.country
FROM books b
INNER JOIN authors a ON b.author_id = a.author_id;
```

**Result:** Only books that have a matching author are returned.

### 2. LEFT (OUTER) JOIN

Returns ALL rows from the LEFT table, and matched rows from the right table.
NULL values appear where there's no match.

```sql
-- Get all books, even those without author info
SELECT 
    b.book_title,
    b.price,
    a.author_name
FROM books b
LEFT JOIN authors a ON b.author_id = a.author_id;
```

**Result:** All books are returned. If a book has no matching author, author columns show NULL.

### 3. RIGHT (OUTER) JOIN

Returns ALL rows from the RIGHT table, and matched rows from the left table.
*(Note: SQLite doesn't support RIGHT JOIN, but you can achieve it by swapping tables in LEFT JOIN)*

```sql
-- Get all authors, even those without books
SELECT 
    b.book_title,
    a.author_name,
    a.country
FROM books b
RIGHT JOIN authors a ON b.author_id = a.author_id;

-- In SQLite, use LEFT JOIN with swapped tables:
SELECT 
    b.book_title,
    a.author_name,
    a.country
FROM authors a
LEFT JOIN books b ON a.author_id = b.author_id;
```

### 4. FULL (OUTER) JOIN

Returns ALL rows when there's a match in EITHER table.
*(SQLite doesn't directly support FULL JOIN, but you can use UNION)*

```sql
-- Full outer join using UNION (SQLite workaround)
SELECT 
    b.book_title,
    a.author_name
FROM books b
LEFT JOIN authors a ON b.author_id = a.author_id

UNION

SELECT 
    b.book_title,
    a.author_name
FROM authors a
LEFT JOIN books b ON a.author_id = b.author_id;
```

### JOIN Comparison Chart

| JOIN Type | Returns |
|-----------|---------|
| INNER JOIN | Only matching rows from both tables |
| LEFT JOIN | All rows from left + matching from right |
| RIGHT JOIN | All rows from right + matching from left |
| FULL JOIN | All rows from both tables |

---

## GROUP BY & Aggregations

GROUP BY groups rows with the same values and allows aggregate calculations.

### Aggregate Functions

| Function | Description | Example |
|----------|-------------|---------|
| COUNT() | Count rows | COUNT(*) |
| SUM() | Sum values | SUM(price) |
| AVG() | Average | AVG(book_rating) |
| MIN() | Minimum | MIN(price) |
| MAX() | Maximum | MAX(price) |
| ROUND() | Round numbers | ROUND(AVG(price), 2) |

### Basic GROUP BY

```sql
-- Count books per genre
SELECT 
    book_genre,
    COUNT(*) as book_count
FROM data
GROUP BY book_genre;

-- Total revenue by genre
SELECT 
    book_genre,
    SUM(price * units_sold) AS revenue
FROM data
GROUP BY book_genre
ORDER BY revenue DESC;

-- Average price per genre
SELECT 
    book_genre,
    ROUND(AVG(price), 2) AS avg_price
FROM data
GROUP BY book_genre;
```

### HAVING Clause

HAVING filters groups (like WHERE, but for aggregated data).

```sql
-- Genres with average price > $13
SELECT 
    book_genre,
    ROUND(AVG(price), 2) AS avg_price
FROM data
GROUP BY book_genre
HAVING AVG(price) > 13;

-- Genres with more than 1 book
SELECT 
    book_genre,
    COUNT(*) as book_count
FROM data
GROUP BY book_genre
HAVING COUNT(*) > 1;
```

### WHERE vs HAVING

| WHERE | HAVING |
|-------|--------|
| Filters individual rows | Filters groups |
| Used BEFORE GROUP BY | Used AFTER GROUP BY |
| Can't use aggregate functions | Used with aggregate functions |

```sql
-- Combined example
SELECT 
    book_genre,
    AVG(price) as avg_price,
    SUM(units_sold) as total_sold
FROM data
WHERE book_rating > 4.0          -- Filter rows BEFORE grouping
GROUP BY book_genre
HAVING SUM(units_sold) > 200     -- Filter groups AFTER grouping
ORDER BY total_sold DESC;
```

