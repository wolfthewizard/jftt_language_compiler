# jftt Language Compiler

## Introduction
This is a compiler for a simple programming language defined by dr Maciej Gębala. The language rules and virtual machine specification are given in *labor4.pdf* in polish.
The compiler is programmed in python using SLY (sly lex-yacc), a library similar to original lex/flex and yacc/bison - tools used for tokenization and constructing parse trees of given context-free grammar.

This compiler was ranked 5th of around 90 entries for efficiency of generated code, based on average of ranks achieved for each test.

## Prerequisites
The compiler is based on sly, which can be installed using:
```
sudo pip3 install sly
```

Virtual machine (author: dr Maciej Gębala) is compiled using `g++` with the addition of `cln` library. The machine itself utilises *flex* and* bison* so they need to be installed too. We use *make* to compile.
```
sudo apt install g++
sudo apt install cln-dev
sudo apt install flex
sudo apt install bison
sudo apt install make
```

## Setup
To run the program, we need to compile the virtual machine.
```
make
```

## Compilation
```
python3 kompilator.py source_file destination_file
```
*source_file* is where the source code is written
*destination_file* is where generated assembly code will be put

## Running the program
```
./vm destination_file
```
