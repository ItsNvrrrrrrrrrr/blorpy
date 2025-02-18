Blor Language Compiler

Blor is a simple programming language built on top of Python. It provides an easy-to-understand syntax, designed to help beginners get into programming with ease.

Introduction

Blor is a programming language that compiles directly into Python code. The goal of Blor is to simplify learning programming while still maintaining Python's powerful features.

Blor supports basic structures such as variable declaration, conditionals, loops, functions, and output. Blor code can be easily converted to Python through the Blor Compiler.
Installation

To use Blor, you need to have Python and the Blor Compiler installed.
Step 1: Install Python

Blor requires Python version 3.x. You can download Python from https://www.python.org/downloads/.
Step 2: Install Blor Compiler

    Clone the Blor Compiler source code from the Blor repository.

    Run the following commands in your terminal:

git clone https://github.com/your-repo/blor.git
cd blor

Install the required dependencies:

    pip install -r requirements.txt
Syntax

Here are some basic syntaxes in Blor:
Variable Declaration

    int.x = 10
    str.name = "Blor"

Output

Use outp.println to print to the console:

    outp.println("Hello, World!")

Conditionals

Blor uses if, else if, and else for conditionals:

    if x == 10 {
        outp.println("X is 10")
    }     else if x > 10:
        outp.println("X is greater than 10")
    }     else
        outp.println("X is less than 10")
    }
    }

Loops

Blor supports while loops:

    while.loop(x < 10):
        outp.println(x)
        x = x + 1

Usage

To compile and run your Blor code, use the Blor compiler:

    Save your Blor code to a file with the .or extension.

    Run the following command:

    python blorc_compiler.py <file_name.or>

The compiler will automatically convert your Blor code into Python and execute it.
Examples

Here is a simple example of a Blor program:

    str.name.input("enter your name")
    public new function greet(name){
        outp.println("Hello, " + name)
    }
    private main function() {
        function.greet(name)
    }

Output:

    Hello, <your input name>

Common Issues

    Syntax Errors:
        If you encounter a syntax error, the compiler will point to the line where the issue occurs. Ensure your syntax is correct, especially with parentheses and dots.

    Input Errors:
        Ensure you're entering the correct data type when using .input(). If you enter the wrong type, the program will default to 0.

License

The Blor Compiler is released under the MIT license. See the LICENSE file for more details.
