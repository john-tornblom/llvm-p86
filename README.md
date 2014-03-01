LLVM-P86
========
LLVM-P86 is a compiler and mutation testing framework intended for the programming language Pascal-86. Compared to a regular compiler, LLVM-P86 is able to create mutated versions of its input and encode several mutants into a single program. The compiler front-end is written entirely in Python, while the code generation provided by LLVM is written in C++.

Some of the most noteworthy features found in LLVM-P86 include:
* Support for most language constructs, such as modules, records, with-statements, nested functions and recursive function calls.
* Support for several mutation operators, including ROR, AOR, COR, SDL and BSR.
* Ability to regenerate Pascal-86 source code after mutants has been encoded into a metaprogram, i.e. source-to-source.
* Individual mutants can be visualized in a [web-based interface](http://john-tornblom.github.io/llvm-p86/triangle/). 



### About Mutation Testing
Mutation testing is an automatic fault-based testing technique that makes syntactic changes to a program under test in order to simulate real faults otherwise caused by a programmer. Similar to structural coverage criteria such as _statement coverage_, mutation testing is used to assess the quality of a test suite. After a syntactic change has been made, the program is referred to as a _mutant_ that can either _survive_ a test suite, or be _killed_ by one. If a mutant is killed, it means that the test suite has detected the syntactic change and reported it as an error, resulting in an increased _mutation score_. If a mutant survives, it means that the test suite failed to detect the fault and the mutation score is decreased.

More information is available in my master thesis, soon to be published at [DiVA](http://diva-portal.org).

### Getting Started
LLVM-P86 depend on the following software packages:
* [python](http://python.org) (tested with 2.7 and 3.3)
* [ply](http://www.dabeaz.com/ply) (tested with 3.4)
* [llvmpy](http://www.llvmpy.org) (tested with 0.11.3, compiled for llvm-3.2)

For people running Ubuntu 13.10, all packages are available via apt-get.
```
$ sudo apt-get install python2.7 python-ply python-llvm
```

Once the dependencies have been met, the source code needs to be prepared by issuing the following set of commands.

```
$ git clone https://github.com/john-tornblom/llvm-p86.git
$ cd llvm-p86
$ python setup.py prepare
```

There are a few small sample applications available in [the samples folder](https://github.com/john-tornblom/llvm-p86/blob/master/samples/snippets). To execute one of them directly using the LLVM JIT compiler, just type:
```
$ ./llvm-p86 -e samples/snippets/if.p
```

LLVM-P86 also ships with two Pascal-86 modules used to demonstrates how mutation testing can be put into practice. Unfortunately, LLVM-P86 is not able to link object files into a single binary, and thus gcc is required. From the project root folder, execute the following set of commands:
```
$ cd samples/triangle
$ ./run_mutants.sh operator
```
where _operator_ is one of the following:
* ror - relational operator replacement (<, <=, =, <>, >=, >)
* cor - conditional operator replacement (and, or)
* aor - arithmetic operator replacement (+, -, *, /, div, mod)
* sdl - statement deletion
* dcc - decision/condition coverage
* sc  - statement coverage

To view each individual mutant, launch the small python webserver located in the root folder of LLVM-86 (preferably from a second terminal window)

```
./llvm-p86-webserver -r wwwroot/
```

Now, point your browser to [localhost:8000](http://localhost:8000).

### Missing Language Features
Since LLVM-P86 was designed with a specific code base in mind, some language features are missing.
* There is no support for reading or writing files, other than stdin and stdout.
* Procedures and functions cannot be passed as arguments.
* The packed keyword is not supported.
* None of the I/O port procedures has been implemented, e.g. _Inwrd_ and _Outwrd_.
* None of the interrupt procedures has been implemented.
* Reading Boolean values from the keyboard using _Read_ will result in a crash.
