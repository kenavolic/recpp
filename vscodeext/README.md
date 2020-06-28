# recpp README

This is an experimental extension for recpp. Presently, it is just a bunch of shortcut commands to launch recpp in vscode terminal.

## Features

The available commands are (CTRL+SHIFT+P):

* recpp function generator
* recpp class generator

## Requirements

* [recpp](https://github.com/kenavolic/recpp)
* python >= 3.6

## Extension Settings

This extension contributes the following settings:

* `recpp.python`: path to the python interpreter
* `recpp.recpp`: path to recpp

## Known Issues

Actually, it is just a handy terminal launcher. The will to integrate it more into the code will depend on future extension API versions (e.g. details about a task end in the terminal, terminal output retrieval).

## Import

Import manually the extension binary (.vsix) shipped with a given release in vscode.

## Edit, Build and Package

On Ubuntu 18.04:

~~~
# npm
$ sudo apt install npm
$ sudo npm install -g npm@latest
$ sudo npm install -g vsce
$ sudo npm install vscode
$ sudo npm install -g typescript

# deps
$ cd vscodeext
$ sudo npm install

# Package
$ cd vscodeext
$ sudo vsce package
~~~
