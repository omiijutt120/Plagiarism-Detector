"""
database.py – DB setup for Academic Plagiarism Detector
ACP Project · Flask + SQLite + NLP
"""

import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'plagiarism.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS vault (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            author      TEXT    NOT NULL DEFAULT 'Unknown',
            subject     TEXT,
            content     TEXT    NOT NULL,
            word_count  INTEGER,
            submitted   DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS checks (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            doc1_title      TEXT,
            doc2_title      TEXT,
            doc1_snippet    TEXT,
            doc2_snippet    TEXT,
            overall_pct     REAL,
            cosine_pct      REAL,
            jaccard_pct     REAL,
            ngram_pct       REAL,
            risk_level      TEXT,
            matched_count   INTEGER,
            checked_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    # Seed sample documents in vault
    count = conn.execute('SELECT COUNT(*) FROM vault').fetchone()[0]
    if count == 0:
        samples = [
            ('Introduction to OOP', 'Ali Khan', 'CS-401',
             'Object-oriented programming is a programming paradigm that uses objects and classes. '
             'It organizes code around data and the operations that manipulate that data. '
             'The four pillars of OOP are encapsulation, abstraction, inheritance, and polymorphism. '
             'Encapsulation hides internal state and requires all interaction through methods. '
             'Inheritance allows new classes to receive the properties of existing classes. '
             'Polymorphism allows objects of different types to be treated as the same type.'),

            ('Data Structures Overview', 'Sara Ahmed', 'CS-402',
             'Data structures are a way of organizing and storing data in a computer so it can be accessed efficiently. '
             'The most common data structures include arrays, linked lists, stacks, queues, trees, and graphs. '
             'Arrays store elements in contiguous memory locations and provide O(1) access time. '
             'Linked lists store elements with pointers connecting each node to the next. '
             'Stacks follow the Last-In-First-Out principle and are used in recursion and expression evaluation. '
             'Queues follow the First-In-First-Out principle and are used in scheduling algorithms.'),

            ('Database Management Systems', 'Ahmed Raza', 'CS-403',
             'A database management system is software that allows users to define, create, maintain and control a database. '
             'The relational model organizes data into tables with rows and columns. '
             'SQL stands for Structured Query Language and is used to communicate with relational databases. '
             'Normalization is the process of organizing data to reduce redundancy and improve data integrity. '
             'ACID properties ensure reliable database transactions: Atomicity, Consistency, Isolation, and Durability. '
             'Indexes are used to speed up data retrieval operations in a database.'),
        ]
        for title, author, subject, content in samples:
            wc = len(content.split())
            conn.execute(
                'INSERT INTO vault (title, author, subject, content, word_count) VALUES (?,?,?,?,?)',
                (title, author, subject, content, wc)
            )
    conn.commit()
    conn.close()
