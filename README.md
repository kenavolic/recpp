# Disclaimer

This tool is not fully tested and usability is very bad!

Currently works for my needs but if you find any bugs or something missing, please do send a PR.

# Description

recpp (re-ci-pe) lets you cook your cpp! 

recpp either provides interactive recipes for some dishes or
simple list of ingredients.

The following dishes can be cooked in recpp kitchen:

* design: help you cook your design by suggesting patterns,
* class: help you cook your class prototypes by generating [annotated](#Annotations) pseudo-code,
* function: help you cook your function prototypes by generating [annotated](#Annotations) pseudo-code,
* lambda: help you cook your lambda prototypes by generating [annotated](#Annotations) pseudo-code,
* ds: help you select your data structures,
* algo: help you select your algorithms,
* impl: provide you a list of tips for your core implementation.

# Requirements

* python >= 3.6
* jinja2
~~~
python3.6 -m pip install jinja2
~~~

# Use cases

There are two main modes of execution:
* list mode (***-l -a***): just display a list of tips,
* recipe mode (default): interactive mode that output suggestions or pseudo-code.

## Annotated pseudo-code generation

[Annotated](#Annotations) pseudo-code is some standard C++ code mixed with [annotations](#Annotations).

> :information_source: Most of the code generating recipes requires user inputs

> :information_source: Use ***-a*** for interative annotations, ***-o*** for in-file code generation

* Generating a class with [annotations](#Annotations) in the generated pseudo-code
~~~
python3.6 recpp.py -d class
~~~
* Generating a function with [annotations](#Annotations) displayed step-by-step on console
~~~
python3.6 recpp.py -d function -a
~~~
* Generating a lambda in a file
~~~
python3.6 recpp.py -d lambda -o /tmp/recpp
~~~
* Generating [annotated](#Annotations) code snippets for the core implementation
~~~
python3.6 recpp.py -d impl -a
~~~

## Decision making

* Suggesting some patterns/idioms to a design problem
~~~
python3.6 recpp.py -d design -a
~~~
* Suggesting a standard data structure or algorithm
~~~
python3.6 recpp.py -d ds -a
python3.6 recpp.py -d algo -a
~~~

## Aggregating tips

> :warning: For tips listing, ***-a*** is mandatory

* List all tips needed to build a class
~~~
python3.6 recpp.py -d class -l -a
~~~
* List performance and reliability tips to build a function
~~~
python3.6 recpp.py -d function -l -a -k PERF,REL
~~~
* List concurrency tips for your core implementation
~~~
python3.6 recpp.py -d impl -l -a -k CON
~~~
* List all performance tips
~~~
python3.6 recpp.py -d all -l -a -k PERF
~~~

# Annotations

An annotation has the following format:
~~~
type,... [reference]: message
~~~
with:
* *type,...*: list of type tokens use to classify the annotation 
* *reference*: source of the annotation
* *message*: short descriptive message

recpp provides different modes for annotations:
* recipe annotations displayed before each recipe step (***-a*** option)
* recipe annotations displayed as a block on top of the recipe dish (either a suggestion or some generated pseudo-code)
* code annotations interleaved with pseudo-code (only for recipes that generate some pseudo-code)

The following type tokens are used and can be listed with the ***-k*** option is list mode:
* *REF*: reference to another recipe,
* *REL*: reliability,
* *PERF*: performance (scalibiltiy, efficiency, in time/size, at compile-time/runtime),
* *MAINT*: maintainability (understandability, modifiability...),
* *USA*: usability,
* *TEST*: testability,
* *COMP*: compatibility,
* *EXT*: extensibility,
* *INTEROP*: interopability,
* *SEC*: security,
* *CORRECT*: correctness,
* *PORT*: portability,
* *CON*: concurrency.

In addition, the following tokens can be found only in code annotations:
* *NOTE*: note in code,
* *TIPS*: implementation tips in code

Here are the references you can find in annotations:
* *recpp.internal*: sources that could unfortunatly not be tracked i.e. notes from cppcon, [blog articles](https://isocpp.org/blog), some lost books etc.
* *cppcore.\**:
[CPP Core guidelines](https://isocpp.github.io/CppCoreGuidelines).
* *CERT.\**: [SEI CERT C++ Coding Standard](https://wiki.sei.cmu.edu/confluence/pages/viewpage.action?pageId=88046682)
* *cppref*: [cppreference.com](https://en.cppreference.com/w/)
* *CCS*:
 ***C++ Coding Standards, Sutter, Alexandrescu***.
* *ECPP*: ***Effective C++, Meyers***
* *EMCPP*: ***Effective Modern C++, Meyers***
* *CPPTPL*: ***C++ Templates, The Complete  Guide, 2nd edition, Vandevoorde, Josuttis, Gregor***
* *SECCPP*: ***Secure Coding in C and C++, Seacord***

# Extensions

A feature-limited extension for vscode is available.

Read the extension README in vscodeext directory.
