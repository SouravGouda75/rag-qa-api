# Python Fundamentals

## Variables and Data Types

Python is a dynamically typed language. Variables do not require explicit type declarations. The common data types include integers, floats, strings, booleans, lists, tuples, dictionaries, and sets.

Strings in Python are immutable sequences of characters. They can be created using single quotes, double quotes, or triple quotes for multi-line strings. String concatenation uses the + operator, and f-strings provide formatted string literals since Python 3.6.

Lists are ordered, mutable sequences. They support indexing, slicing, appending, and removing elements. List comprehensions provide a concise way to create lists based on existing iterables.

Dictionaries store key-value pairs and provide O(1) average lookup time. Keys must be hashable (immutable), while values can be any type. Since Python 3.7, dictionaries maintain insertion order.

## Functions

Functions are defined using the def keyword. Python supports default arguments, keyword arguments, and variable-length argument lists using *args and **kwargs. Functions are first-class objects and can be passed as arguments to other functions.

Lambda functions are anonymous functions defined with the lambda keyword. They are limited to a single expression and are commonly used with functions like map(), filter(), and sorted().

## Object-Oriented Programming

Python supports object-oriented programming with classes and inheritance. Classes are defined using the class keyword. The __init__ method serves as the constructor. Python supports multiple inheritance and uses the Method Resolution Order (MRO) to determine which method to call.

Encapsulation in Python is achieved by convention rather than enforcement. Single underscore prefix (_var) indicates internal use, while double underscore prefix (__var) triggers name mangling.

## Error Handling

Python uses try-except blocks for error handling. Multiple except clauses can catch different exception types. The finally block executes regardless of whether an exception occurred. Custom exceptions are created by subclassing the Exception class.

The with statement provides context management for resource handling, ensuring proper cleanup even when exceptions occur. Common use cases include file operations and database connections.

## Modules and Packages

A module is a single Python file. A package is a directory containing an __init__.py file and one or more modules. The import system supports absolute and relative imports.

Virtual environments isolate project dependencies. The venv module creates lightweight virtual environments. pip is the standard package installer for Python, and requirements.txt files list project dependencies.
