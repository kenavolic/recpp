# -*- coding: utf-8 -*-
#! /usr/bin/env/python3

# ---------------------------------------------
# Imports
# ---------------------------------------------
import json
import copy
import re
from enum import IntEnum, Enum
from functools import wraps, partial
from typing import List, Dict
from argparse import ArgumentParser, RawTextHelpFormatter
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


# ---------------------------------------------
# Globals
# ---------------------------------------------
_recpp_header = r"""

 ________________________________________
|  .--,--.                               |
|  `.   .'                               |
|   |___|                                |
|  <:o o:>        Recpp: Cook your Cpp!  |
|  _'-^-'_                               |
| /   *   \                              |
|________________________________________|
"""
_recpp_dish_served = r"""
      (   )   (
      )   (   )
     __..---..__
 ,-='  /  |  \  `=-.   Dish served!
:--..___________..--;
 \.,_____________,./
"""

_recpp_recipe = r"""
 __________
|  RECIPE  |
|&&& ======|
|=== ======|
|=== == %%$|  Here is the recipe!
|[_] ======|
|=== ===!##|
|__________|
"""

_recpp_cpp_id_regex = re.compile("[a-zA-Z_][a-zA-Z0-9_]*")

# ---------------------------------------------
# Utilities
# ---------------------------------------------


class InputType(Enum):
    INT = 1
    LIST = 2
    IDENTIFIER = 3
    TYPE = 4
    FLAG = 5
    MISC = 6


class RecppError(Exception):
    def __init__(self, message=""):
        super().__init__(message)


def print_msg(msg, level="ERROR"):
    '''Print error message'''
    print(f"{level}: {msg}")


class strong_input(object):
    '''Class used process input in an homogeneous manner'''

    def __init__(self, input_type, *args, **kwargs):
        if input_type == InputType.INT:
            self.input = partial(self.strong_int, *args, **kwargs)
        elif input_type == InputType.LIST:
            self.input = partial(self.strong_list, *args, **kwargs)
        elif input_type == InputType.IDENTIFIER:
            self.input = partial(self.strong_identifier, *args, **kwargs)
        elif input_type == InputType.FLAG:
            self.input = partial(self.strong_flag, *args, **kwargs)
        elif input_type == InputType.TYPE:
            self.input = partial(self.strong_type, *args, **kwargs)
        elif input_type == InputType.MISC:
            self.input = partial(self.strong_misc, *args, **kwargs)
        else:
            raise RecppError("input type not handled")

    def strong_identifier(self, f: callable, *args, **kwargs):
        while True:
            identifier = f(*args, **kwargs).strip()
            if _recpp_cpp_id_regex.fullmatch(identifier):
                return identifier
            print_msg("expecting cpp identifier")

    def strong_type(self, f: callable, *args, **kwargs):
        t = f(*args, **kwargs).strip()
        if not t:
            t = "auto"
        return t

    def strong_misc(self, f: callable, *args, **kwargs):
        t = ""
        while not t:
            t = f(*args, **kwargs).strip()

        return t

    def strong_flag(self, f: callable, *args, **kwargs):
        flag_list = ["1", "y", "yes", "0", "n", "no"]
        while True:
            flag = f(*args, **kwargs).strip()
            if flag in flag_list:
                return flag in flag_list[0:3]
            print_msg(f"expecting one of {'/'.join(flag_list)}")

    def strong_int(self, f: callable, *args, **kwargs):
        while True:
            try:
                return int(f(*args, **kwargs).strip())
            except:
                print_msg("expecting an integer")

    def strong_list(self, l: List[str], default_val: str, f: callable, *args, **kwargs):
        while True:
            item = f(*args, **kwargs).strip() or default_val
            if item in l:
                return item
            print_msg(f"expecting one of {'/'.join(l)}")

    def __call__(self, f: callable):
        @wraps(f)
        def wrapped(*args, **kwargs):
            return self.input(f, *args, **kwargs)
        return wrapped

# ---------------------------------------------
# Recipe handling classes
# ---------------------------------------------


class RecipeCook(object):
    '''Base class for cooking recipes'''

    def __init__(self, desc: Dict, template_path="templates"):
        '''
        Contructor
        :param desc: Recipe description
        :template_path: path to the template to patch
        '''
        self.env = Environment(
            loader=FileSystemLoader(template_path)
        )
        self.desc = desc
        self.annotations = []

    def cookstep(self, name: str, ref: str):
        '''Process a recipe cook step'''
        step_exec = getattr(self, name, None)

        if step_exec:
            step_exec(ref)
        else:
            raise RecppError(f"{name} step is not implemented")

    def print_live_annotations(self, annots: List):
        '''Print live annotation list'''
        for annot in annots:
            self.print_live_annotation(
                annot["type"], annot["ref"], annot["msg"])

        if annots:
            print("")

    def print_live_annotation(self, type, ref, msg):
        '''Print annotation'''
        print(f"(!) {type} [{ref}]: {msg}")

    def handle_annotations(self, annotations: List[str], do_live_annot: bool):
        '''
        Process annotations
        :param annotations: list of annotations
        :param do_live_annot: set to True to display annotations during recipe
        '''
        if annotations and do_live_annot:
            self.print_live_annotations(annotations)
        else:
            self.annotations.extend(annotations)

    def handle_steps(self, metastep: str, steps: List):
        '''
        Process steps
        :param metastep: name of the metastep
        :param steps: metastep list of steps

        The child class responsible for a dish must
        implement a callback for each step with the name: metastep_step
        '''
        for step in steps:
            self.cookstep(
                "_".join([metastep, "step", step["id"]]), step["ref"])

    def initialize_cook_metastep(self, name: str):
        '''
        Initialize a metastep

        The child class responsible for a dish must optionally
        implement a callback with the name: metastep_initialize to
        have the job done
        '''
        cb = getattr(self, name + "_initialize", None)
        if cb:
            cb()

    def finalize_cook_metastep(self, name: str):
        '''
        Finalize a metastep

        The child class responsible for a dish must optionally
        implement a callback with the name: metastep_finalize to
        have the job done
        '''
        cb = getattr(self, name + "_finalize", None)
        if cb:
            cb()

    def repeat_count_metastep(self, name: str):
        '''
        Query the repeat count for a repeatable metastep

        The child class responsible for a dish MUST
        implement a callback with the name: metastep_repeat to
        have the job done
        '''
        cb = getattr(self, name + "_repeat", None)
        return cb() if cb else 0

    def cook(self, do_live_annot: bool):
        '''
        Process a recipe
        :param do_live_annot: set to True to display live annotation
        '''
        self.annotations = []
        for metastep in self.desc:
            print(f"\n~~~ Recipe step - {metastep['desc']} ~~~\n")
            self.handle_annotations(metastep["annotations"], do_live_annot)

            loop_count = 1 if not metastep["repeatable"] else self.repeat_count_metastep(
                metastep["id"])

            for i in range(0, loop_count):
                if loop_count > 1:
                    print(f"\n~~~ Repeat count - {i+1} ~~~\n")
                self.initialize_cook_metastep(metastep["id"])
                self.handle_steps(
                    metastep["id"], metastep["steps"])
                self.finalize_cook_metastep(metastep["id"])

    def serve_dish(self, odir: str):
        '''
        Serve dish
        :param odir: output dir

        If no output dir is given, dish is served on console
        '''
        if not odir:
            self.show_dish_console()
        else:
            self.write_dish(odir)

    def show_dish_console(self):
        print("\n" + _recpp_dish_served)
        self.show_dish_console_impl()

    def show_dish_console_impl(self):
        raise NotImplementedError

    def write_dish(self, odir):
        raise NotImplementedError

    @staticmethod
    def format_input(query: str, ref: str):
        return query + (f" [ref: {ref}]" if ref else "")

    @staticmethod
    def custom_input(query: str, ref=""):
        return input(RecipeCook.format_input(query, ref) + ": ")

    @strong_input(InputType.FLAG)
    def generic_yesno_input(self, query, ref):
        return RecipeCook.custom_input(f"{query} (y/n)", ref)

    @strong_input(InputType.IDENTIFIER)
    def generic_identifier_input(self, query, ref):
        return RecipeCook.custom_input(query, ref)

    @strong_input(InputType.TYPE)
    def generic_type_input(self, query, ref):
        return RecipeCook.custom_input(f"{query} (default: auto)", ref)

    @strong_input(InputType.MISC)
    def generic_misc_input(self, query, ref):
        return RecipeCook.custom_input(f"{query}", ref)


class DesignRecipeCook(RecipeCook):
    '''Recipe to help you design'''

    def __init__(self, desc, template_path="templates"):
        super().__init__(desc, template_path)
        self.pattern = ""

    def show_dish_console_impl(self):
        self.print_live_annotations(self.annotations)
        print_msg(f"You could consider the following patterns in your design -> {self.pattern}", "SUGGEST")

    def write_dish(self, odir: str):
        self.show_dish_console()
        print_msg("This recipe has nothing to write to disk", "WARN")

    @strong_input(InputType.LIST, ["unit", "system"], "unit")
    def design_root_step_primary_concern_cb(self, ref):
        return RecipeCook.custom_input("Enter primary concern about the design either whole system design or system unit design (system, unit, default: unit)", ref)

    def design_root_step_primary_concern(self, ref):
        self.concern = self.design_root_step_primary_concern_cb(ref)

    def design_root_step_system(self, ref):
        if self.concern != "system":
            return

        if self.generic_yesno_input("Do you build a distributed system", ref):
            self.pattern = "Client-Dispatcher-Server, Broker, Master-Slave, Proxy"
        elif self.generic_yesno_input("Do you build a system that has user interaction", ref):
            self.pattern = "MVC, Presentation-Abstraction-Control, ViewHandler, Command Processor"
        elif self.generic_yesno_input("Do you build a system that processes a stream of data", ref):
            self.pattern = "Pipe and Filters"
        elif self.generic_yesno_input("Do you build a system that requires cooperating components", ref):
            self.pattern = "Forward-Receiver, Publisher-Subscriber"
        else:
            self.pattern = "Whole-Part, Layers, Blackboard, Microkernel, Reflection, ..."

    def design_root_step_unit(self, ref):
        if self.concern != "unit":
            return

        if self.generic_yesno_input("Do you need to create objects or a plugin mechanism", ref):
            self.pattern = "Abstract Factory, Builder, Factory Method, Prototype"
        elif self.generic_yesno_input("Do you need to handle a hierarchy of objects", ref):
            self.pattern = "Composite, Visitor, Chain of Responsability"
        elif self.generic_yesno_input("Do you need a ABI stable or open–closed principle compliant interface", ref):
            self.pattern = "Bridge, Pimpl Idiom (see class recipe for possible implementation)"
        elif self.generic_yesno_input("Do you need to switch between different implementations of an interface", ref):
            self.pattern = "Bridge"
        elif self.generic_yesno_input("Do you need to add responsability to an object dynamically", ref):
            self.pattern = "Decorator"
        elif self.generic_yesno_input("Do you need to add generic or orthogonal feature to an existing class statically", ref):
            self.pattern = "CRTP Idiom, Parameterized Base Class / Mixin-from-below Idiom, Non-member template function"
        elif self.generic_yesno_input("Do you need static polymorphism", ref):
            self.pattern = "CRTP Idiom, discriminated union with Visitor"
        elif self.generic_yesno_input("Do you need to wrap one or many components to make it usable by another one", ref):
            self.pattern = "Adapter, Facade"
        elif self.generic_yesno_input("Do you need to adapt an interface to make incompatible objects collaborate", ref):
            self.pattern = "Adapter (with CRTP)"
        elif self.generic_yesno_input("Do you need to define new types that have to meet the requirements of an existing interface", ref):
            self.pattern = "Facade with CRTP"
        elif self.generic_yesno_input("Do you need to add access control to an existing object (e.g. make a class thread-safe, resilient to network access loss)", ref):
            self.pattern = "Proxy"
        elif self.generic_yesno_input("Do you need copy-on-write capabilities for performance", ref):
            self.pattern = "Flyweight, Proxy"
        elif self.generic_yesno_input("Do you need loose-coupling between components", ref):
            self.pattern = "Observer (and variant signal-slot etc.), Mediator"
        elif self.generic_yesno_input("Do you need do-undo capabilities for a request-based component", ref):
            self.pattern = "Command, Memento"
        elif self.generic_yesno_input("Do you need to implement a component that processes requests according to its current state", ref):
            self.pattern = "State (Note: you can use libraries that implement the state machine concept)"
        elif self.generic_yesno_input("Do you need to enforce pre or post conditions in a hierarchy", ref):
            self.pattern = "Template Method (implemented as NVI Idiom in C++)"
        elif self.generic_yesno_input("Do you need method chaining in a hierarchy", ref):
            self.pattern = "CRTP Idiom"
        elif self.generic_yesno_input("Do you need to create a set of components out of a set of orthogonal concepts", ref):
            self.pattern = "Policy design, Mixins"
        elif self.generic_yesno_input("Do you need to group a list of overloads (e.g. for visiting)", ref):
            self.pattern = "Variadic Base Class with using directive"
        elif self.generic_yesno_input("Do you need to regroup natural dependent properties of a type", ref):
            self.pattern = "Traits Class"
        else:
            self.pattern = "Check GoF patterns and typical C++ idioms"


class ClassRecipeCook(RecipeCook):
    '''Recipe to generate a class'''

    def __init__(self, desc, template_path="templates"):
        super().__init__(desc, template_path)
        self.classattr = {}
        self.has_impl = False

    def show_dish_console_impl(self):
        tpl_h = self.env.get_template(f"{self.classattr['type']}_class.h")
        self.classattr["annotations"] = self.annotations
        print(tpl_h.render(self.classattr))

        if self.has_impl:
            tpl_cpp = self.env.get_template(f"{self.classattr['type']}_class.cpp")
            print("\n" + tpl_cpp.render(self.classattr))

    def write_dish(self, odir: str):
        header = f"{self.classattr['type']}_class.h"
        tpl_h = self.env.get_template(header)
        self.classattr["annotations"] = self.annotations
        with open(Path(odir)/header, "w", encoding="utf8") as f:
            f.write(tpl_h.render(self.classattr))

        if not self.has_impl:
            return

        impl = f"{self.classattr['type']}_class.cpp"
        tpl_cpp = self.env.get_template(impl)
        with open(Path(odir)/impl, "w", encoding="utf8") as f:
            f.write(tpl_cpp.render(self.classattr))

    def class_root_step_name(self, ref):
        self.classattr["classname"] = self.generic_identifier_input(
            "Enter class name", ref)

    def class_root_step_responsability(self, ref):
        self.classattr["responsability"] = RecipeCook.custom_input(
            "Enter class single role/responsability", ref)

    def class_root_step_invariant(self, ref):
        self.classattr["invariant"] = RecipeCook.custom_input(
            "Enter class invariants description", ref)

    @strong_input(InputType.LIST, ["thread-safe", "thread-compatible", "thread-incompatible"], "thread-incompatible")
    def root_step_thread_safe_cb(self, ref):
        return RecipeCook.custom_input("Enter thread-safety contrat (thread-safe: no api race, thread-compatible: no api race if not mutated, thread-incompatible, default: thread-incompatible)", ref)

    def class_root_step_thread_safe(self, ref):
        self.classattr["thread_safety"] = self.root_step_thread_safe_cb(ref)

    @strong_input(InputType.LIST, ["concrete", "hierarchy"], "concrete")
    def class_root_step_type_cb(self, ref):
        return RecipeCook.custom_input("Enter class type (concrete, hierarchy, default: concrete)", ref)

    def class_root_step_type(self, ref):
        self.classattr["type"] = self.class_root_step_type_cb(ref)

    @strong_input(InputType.INT)
    def tpl_parameters_repeat(self):
        return RecipeCook.custom_input("Enter template parameters count")

    def tpl_parameters_initialize(self):
        self.tparam = {}

    def tpl_parameters_step_name(self, ref):
        self.tparam["name"] = self.generic_misc_input(
            "Enter template parameter full desc e.g. typename T, ...", ref)

    def tpl_parameters_finalize(self):
        self.classattr.setdefault("tparams", []).append(
            copy.deepcopy(self.tparam))

    @strong_input(InputType.LIST, ["thin", "thick", "verythick"], "thin")
    def concrete_step_abstraction_cb(self, ref):
        return RecipeCook.custom_input("Enter class abstraction (verythick for pimpl, thick for no-inline, thin otherwise, default: thin)", ref)

    def concrete_step_abstraction(self, ref):
        if not self.classattr["type"] in ["concrete"]:
            return

        if "tparams" in self.classattr:
            self.classattr["abstraction"] = "thin"
        else:
            self.classattr["abstraction"] = self.concrete_step_abstraction_cb(
                ref)

        self.has_impl = (self.classattr["abstraction"] == "verythick")

    def concrete_step_raii(self, ref):
        if not self.classattr["type"] in ["concrete"]:
            return

        if self.classattr["abstraction"] == "verythick":
            # Force raii attribute
            self.classattr["raii"] = False
        else:
            self.classattr["raii"] = self.generic_yesno_input(
                "Does the class acquire-release a resource at contruction/destruction", ref)

    def concrete_step_specials(self, ref):
        if not self.classattr["type"] in ["concrete"]:
            return

        if self.classattr["abstraction"] == "verythick" or self.classattr["raii"]:
            self.classattr["specials"] = True
        else:
            self.classattr["specials"] = self.generic_yesno_input(
                "Should one of the special members be defined", ref)

    def concrete_step_alloc(self, ref):
        if not self.classattr["type"] in ["concrete"]:
            return

        self.classattr["custom_allocators"] = self.generic_yesno_input(
            "Does the class need custom allocation/deallocation overloads", ref)

    def concrete_step_init_list_ctor(self, ref):
        if not self.classattr["type"] in ["concrete"]:
            return

        self.classattr["init_list_ctor"] = self.generic_yesno_input(
            "Does the class need an initializer list ctor", ref)

    def hierarchy_step_base(self, ref):
        if not self.classattr["type"] in ["hierarchy"]:
            return

        self.classattr["base"] = self.generic_yesno_input(
            "Is it the base class in hierarchy", ref)

        if not self.classattr["base"]:
            self.classattr["basename"] = RecipeCook.custom_input(
                "Enter the main base class name", ref)

    def hierarchy_step_clonable(self, ref):
        if not self.classattr["type"] in ["hierarchy"]:
            return

        self.classattr["clonable"] = self.generic_yesno_input(
            "Is is part of a clonable hierarchy", ref)

    def hierarchy_step_interface(self, ref):
        if not self.classattr["type"] in ["hierarchy"]:
            return

        if self.classattr["base"]:
            self.classattr["interface"] = self.generic_yesno_input(
                "Does the hierarchy need a complete separation of interface", ref)

    def hierarchy_step_inherited_init(self, ref):
        if not self.classattr["type"] in ["hierarchy"]:
            return

        if not self.classattr["base"]:
            self.classattr["init_with_base"] = not self.generic_yesno_input(
                "Does the class need specific initialization (data members, ...)", ref)


class FunctionRecipeCook(RecipeCook):
    '''Recipe to generate a function'''

    def __init__(self, desc, template_path="templates"):
        super().__init__(desc, template_path)
        self.funcattr = {}
        self.param = {}
        self.tparam = {}
        self.ret = {}
        self.attr = {}
        self.virtual = False

    def show_dish_console_impl(self):
        tpl_h = self.env.get_template("function.h")
        self.funcattr["annotations"] = self.annotations
        print(tpl_h.render(self.funcattr))

    def write_dish(self, odir: str):
        tpl_h = self.env.get_template("function.h")
        self.funcattr["annotations"] = self.annotations
        with open(Path(odir)/"function.h", "w", encoding="utf8") as f:
            f.write(tpl_h.render(self.funcattr))

    def func_root_step_name(self, ref):
        self.funcattr["name"] = self.generic_identifier_input(
            "Enter function name", ref)

    def func_root_step_type(self, ref):
        if self.generic_yesno_input("Is it a virtual method", ref):
            self.funcattr["type"] = "method"
            self.virtual = True
        elif self.generic_yesno_input("Does it need access to a class internal representation aka a method", ref):
            self.funcattr["type"] = "method"
            self.virtual = False
        else:
            self.funcattr["type"] = "free"

    def func_root_step_responsability(self, ref):
        self.funcattr["responsability"] = RecipeCook.custom_input(
            "Enter function single role/responsability", ref)

    def func_root_step_thread_safe(self, ref):
        self.funcattr["thread_hostile"] = self.generic_yesno_input(
            "Can it cause API races at sites other than its inputs (e.g. static local variable)", ref)

    @strong_input(InputType.INT)
    def tpl_parameters_repeat(self):
        return "0" if self.virtual else RecipeCook.custom_input("Enter template parameters count")

    def tpl_parameters_initialize(self):
        self.tparam = {}

    def tpl_parameters_step_name(self, ref):
        self.tparam["name"] = self.generic_misc_input(
            "Enter template parameter full desc e.g. typename T, ...", ref)

    def tpl_parameters_finalize(self):
        self.funcattr.setdefault("tparams", []).append(
            copy.deepcopy(self.tparam))

    @strong_input(InputType.INT)
    def func_parameters_repeat(self):
        return RecipeCook.custom_input("Enter regular parameters count")

    def func_parameters_initialize(self):
        self.param = {}
        self.param.setdefault("comments", [])

    def func_parameters_step_name(self, ref):
        self.param["name"] = self.generic_identifier_input(
            "Enter parameter name (without type)", ref)

    def func_parameters_step_type_react(self, ref, msg):
        self.print_live_annotation("TIPS", ref, msg)
        if self.generic_yesno_input("Would you like to update param type according to tips", ref):
            self.param["type"] = self.generic_type_input(
                f"Enter parameter type to replace {self.param['type']}", ref)

    def func_parameters_step_type(self, ref):
        self.param["type"] = self.generic_type_input(
            "Enter parameter type e.g. int, const Obj&, ...", ref)

        if not self.generic_yesno_input("Would you like to trigger advanced mode for parameter type fine-tuning", ref):
            return

        param_type = "const X&"
        if self.generic_yesno_input("Is it an in-out param", ref):
            param_type = "X&"
        elif self.generic_yesno_input("Will the arg be passed onward to other code and not directly used by this function", ref):
            param_type = "T&& + std::forward"
        elif self.generic_yesno_input("Is it cheap to copy e.g. int, pointer, smart pointers", ref) or \
                "unique_ptr" in self.param["type"]:
            param_type = "X"
        elif not self.generic_yesno_input("Is it going to be stored or moved", ref):
            param_type = "const X&"
        elif self.generic_yesno_input("Will it be unconditionnaly moved", ref):
            param_type = "X&&"
        elif self.generic_yesno_input("Will it be copied", ref):
            if self.generic_yesno_input("Is it expansive to move (e.g. bigPOD, large array)", ref):
                param_type = "const X&"
            elif self.generic_yesno_input("Is it copyable, copied on all paths, cheap to move (e.g. std::string, std::vector) and move constructed", ref):
                param_type = "X"
            else:
                param_type = "const X& + X&& overloads or T&& + std::forward"

        self.func_parameters_step_type_react(ref, f"pass arg of type X as {param_type}")

    def func_parameters_step_weaktype(self, ref):
        if "void" in self.param["type"]:
            self.func_parameters_step_type_react(ref, "void is a weak type")

    def func_parameters_step_array(self, ref):
        if any(p in self.param["type"] for p in ["*", "[]"]) and \
                self.generic_yesno_input("Does the param represent an array", ref):
            self.func_parameters_step_type_react(
                ref, "array should be passed as std::array or span")

    def func_parameters_step_smartpointer(self, ref):
        if any(p in self.param["type"] for p in ["shared_ptr", "unique_ptr"]) and \
                not self.generic_yesno_input("Will ownership be transferred or shared", ref):
            self.func_parameters_step_type_react(
                ref, "T* or T& is better for general use")

    def func_parameters_step_cstring(self, ref):
        if re.match(".*char\s*\*", self.param["type"]):
            self.func_parameters_step_type_react(
                ref, "consider alternative like string_view")

    def func_parameters_step_collision(self, ref):
        if "params" in self.funcattr and \
                self.param["type"] == self.funcattr["params"][-1]["type"]:
            self.func_parameters_step_type_react(
                ref, "same type as previous param can be confusing")

    def func_parameters_step_boollist(self, ref):
        if "params" in self.funcattr and \
            "bool" == self.param["type"] and \
                any("bool" == p["type"] for p in self.funcattr["params"]):
            self.param["comments"].append(RecipeCook.format_input(
                "more than one bool param, consider using flags", ref))

    def func_parameters_step_argscount(self, ref):
        if "params" in self.funcattr and len(self.funcattr["params"]) >= 4:
            self.param["comments"].append(RecipeCook.format_input(
                "more than 4 params, maybe missing an abstration or function has too many responsabilities", ref))

    def func_parameters_finalize(self):
        self.param["comments"] = ",".join(self.param["comments"])
        self.funcattr.setdefault("params", []).append(
            copy.deepcopy(self.param))

    def func_ret_step_type_react(self, ref, msg):
        self.print_live_annotation("TIPS", ref, msg)
        if self.generic_yesno_input("Would you like to update return type according to tips", ref):
            self.ret["rtype"] = self.generic_type_input(
                "Enter return type", ref)
        else:
            self.ret["comments"].append(RecipeCook.format_input(
                msg, ref))

    def func_ret_initialize(self):
        self.ret = {}
        self.ret.setdefault("comments", [])

    def func_ret_step_type(self, ref):
        self.ret["rtype"] = self.generic_type_input(
            "Enter return type", ref)

    def func_ret_step_ownership(self, ref):
        if "*" in self.ret["rtype"] and self.generic_yesno_input("Is it a transfer of ownership", ref):
            self.func_ret_step_type_react(
                ref, "beware ownership transferred with raw pointer, consider smart pointer")

    def func_ret_step_byvalue(self, ref):
        if self.ret["rtype"] == "void":
            return

        force_not_byvalue = self.generic_yesno_input(
            "Does it return a container item, enable write access to some representation, or enable chain calls", ref)

        if force_not_byvalue and (self.ret["rtype"] == "auto" or
                                  not any(ret in self.ret["rtype"] for ret in ["*", "&"])):
            self.func_ret_step_type_react(
                ref, "you should not return by value (e.g. auto -> decltype(auto))")
        elif not force_not_byvalue and any(ret in self.ret["rtype"] for ret in ["*", "&"]):
            self.func_ret_step_type_react(
                ref, "prefer return by value if suitable")

    def func_ret_step_nonconst(self, ref):
        if "const" in self.ret["rtype"]:
            self.func_ret_step_type_react(
                ref, "move semantics could be suppressed by 'const'")

    def func_ret_step_rvalueref(self, ref):
        if "&&" in self.ret["rtype"]:
            self.func_ret_step_type_react(ref, "never return &&")

    def func_ret_finalize(self):
        self.ret["comments"] = ",".join(self.ret["comments"])
        self.funcattr["ret"] = self.ret

    def func_attr_initialize(self):
        self.funcattr["attr"] = {}
        self.attr["pre"] = []
        self.attr["post"] = []

    def func_attr_step_virtual(self, ref):
        if self.virtual:
            self.attr["pre"].append("virtual")

    def func_attr_step_constexpr(self, ref):
        if not self.virtual and \
                self.generic_yesno_input("Should it be evaluated at compile-time", ref):
            self.attr["pre"].append("constexpr")

    def func_attr_step_inline(self, ref):
        if not self.virtual and \
                not "constexpr" in self.attr["pre"] and \
                not "tparams" in self.funcattr and \
                self.generic_yesno_input("Is it small, time-critical and part of a thin abstraction", ref):
            self.attr["pre"].append("inline")

    def func_attr_step_const(self, ref):
        if self.funcattr["type"] == "method" and \
                not self.generic_yesno_input("Will the method modify the object state", ref):
            self.attr["post"].append("const")

    def func_attr_step_noexcept(self, ref):
        if not self.generic_yesno_input("Can it throw exceptions", ref):
            self.attr["post"].append("noexcept")

    def func_attr_step_override(self, ref):
        if self.virtual and \
                self.generic_yesno_input("Does the function override a base method behavior", ref):
            self.attr["post"].append("override")
            # Override implies virtual
            self.attr["pre"] = filter(
                lambda x: x != "virtual", self.attr["pre"])

    def func_attr_finalize(self):
        self.funcattr["attr"]["pre"] = " ".join(self.attr["pre"])
        self.funcattr["attr"]["post"] = " ".join(self.attr["post"])

    def func_impl_step_pure(self, ref):
        if "tparams" not in self.funcattr and \
            self.funcattr["type"] == "method" and \
            "virtual" in self.funcattr["attr"]["pre"] \
                and self.generic_yesno_input("Is it pure", ref):
            self.funcattr["pure"] = True
        else:
            self.funcattr["pure"] = False


class LambdaRecipeCook(FunctionRecipeCook):
    '''Recipe to generate a lambda'''

    def __init__(self, desc, template_path="templates"):
        super().__init__(desc, template_path)
        self.attr = []

    def show_dish_console_impl(self):
        tpl_h = self.env.get_template("lambda.h")
        self.funcattr["annotations"] = self.annotations
        print(tpl_h.render(self.funcattr))

    def write_dish(self, odir: str):
        self.show_dish_console()
        print_msg("This recipe has nothing to write to disk", "WARN")

    def lambda_root_step_scope(self, ref):
        self.local = self.generic_yesno_input(
            "Would the scope of the lambda be local (not returned, neither stored on the heap or pass to another thread)", ref)

    def lambda_root_step_recursion(self, ref):
        self.funcattr["recursive"] = self.generic_yesno_input(
            "Should the lambda be recursive", ref)

    @strong_input(InputType.INT)
    def capture_list_repeat(self):
        return RecipeCook.custom_input("Enter capture list item count")

    def capture_list_step_react(self, ref, msg):
        self.print_live_annotation("TIPS", ref, msg)
        if self.generic_yesno_input("Would you like to update captured item according to tips", ref):
            self.capture = self.generic_misc_input(
                "Enter captured item full desc e.g. a = std::move(b), &c, d ...", ref)

    def capture_list_step_name(self, ref):
        self.capture = self.generic_misc_input(
            "Enter captured item full desc e.g. a = std::move(b), &c, d ...", ref)

    def capture_list_step_ref(self, ref):
        if self.local and self.capture != "this" and not "&" in self.capture:
            self.capture_list_step_react(
                ref, "You might want to capture by reference for local scope lambda")

    def capture_list_step_nonref(self, ref):
        if not self.local and (self.capture == "this" or "&" in self.capture):
            self.capture_list_step_react(
                ref, "You might want to capture by value for non-local scope lambda")

    def capture_list_step_this(self, ref):
        if not "captures" in self.funcattr:
            return

        should_fix = False
        if self.capture == "this" and \
                any(c in self.funcattr["captures"] for c in ["&", "="]):
            should_fix = True

        if (self.capture == "&" or self.capture == "=") and \
                "this" in self.funcattr["captures"]:
            should_fix = True

        if should_fix:
            self.capture_list_step_react(
                ref, "If this is captured, all variables should be captured explicitly")

    def capture_list_finalize(self):
        self.funcattr.setdefault("captures", []).append(self.capture)

    def lambda_attr_step_constexpr(self, ref):
        if self.generic_yesno_input("Should it be evaluated at compile-time", ref):
            self.attr.append("constexpr")

    def lambda_attr_step_mutable(self, ref):
        if any("=" in capt or "*this" in capt for capt in self.funcattr["captures"]) and \
                self.generic_yesno_input("Should the capture by value items be mutable", ref):
            self.attr.append("mutable")

    def lambda_attr_finalize(self):
        self.funcattr["attr"] = " ".join(self.attr)


class DataStructureRecipeCook(RecipeCook):
    '''Recipe to select a data structure'''

    def __init__(self, desc, template_path="templates"):
        super().__init__(desc, template_path)
        self.ds = "std::vector"
        self.comment = ""

    def show_dish_console_impl(self):
        self.print_live_annotations(self.annotations)
        print_msg(f"You should probably use a data structure of type {self.ds}", "SUGGEST")
        if self.comment:
            print_msg(self.comment, "NOTE")

    def write_dish(self, odir: str):
        self.show_dish_console()
        print_msg("This recipe has nothing to write to disk", "WARN")

    @strong_input(InputType.LIST, ["random_access", "insertion/removal", "lookup", ""], "")
    def ds_root_step_primary_concern_cb(self, ref):
        return RecipeCook.custom_input("Enter primary concern about the data structure (random_access, insertion/removal: insert often, traverse rarely, lookup, default: no special concern)", ref)

    def ds_root_step_primary_concern(self, ref):
        self.concern = self.ds_root_step_primary_concern_cb(ref)

    def ds_root_step_random_access(self, ref):
        if self.concern != "random_access":
            return

        if self.generic_yesno_input("Is it a fixed size container with size known at compile-time", ref):
            self.ds = "std::array"
        else:
            self.ds = "std::vector"

    def ds_root_step_insertion_removal(self, ref):
        if self.concern != "insertion/removal":
            return
        self.ds = "std::list"
        self.comment = "measure first because std::vector may still meet your criteria for reasonable size"

    def ds_root_step_lookup(self, ref):
        if self.concern != "lookup":
            return

        has_value = self.generic_yesno_input(
            "Do you need key-value capable data structure (at the opposite of key-only)", ref)
        associative = False
        if self.generic_yesno_input("Is readibility more important than performance", ref):
            associative = True
        elif self.generic_yesno_input("Will size be large and/or will there be frequent insert", ref):
            associative = True
            self.comment = "measure first because sorted std::vector may still meet your criteria"

        if associative and self.generic_yesno_input("Do you need ordered keys (no if you don't know)", ref):
            self.ds = "std::map" if has_value else "std::set"
        elif associative:
            self.ds = "std::unordered_map" if has_value else "std::unordered_set"
        else:
            self.ds = "sorted std::vector of pair" if has_value else "sorted std::vector with maintained uniqueness"


class AlgorithmRecipeCook(RecipeCook):
    '''Recipe to select an algorithm'''

    def __init__(self, desc, template_path="templates"):
        super().__init__(desc, template_path)
        self.algo = ""

    def show_dish_console_impl(self):
        self.print_live_annotations(self.annotations)
        print_msg(f"You should probably use one of the following algorithms -> {self.algo}", "SUGGEST")

    def write_dish(self, odir: str):
        self.show_dish_console()
        print_msg("This recipe has nothing to write to disk", "WARN")

    @strong_input(InputType.LIST, ["find", "sort", "traversal"], "find")
    def algo_root_step_primary_concern_cb(self, ref):
        return RecipeCook.custom_input("Enter primary concern about the algorithm (find, sort, traversal, default: find)", ref)

    def algo_root_step_primary_concern(self, ref):
        self.concern = self.algo_root_step_primary_concern_cb(ref)

    def algo_root_step_find(self, ref):
        if self.concern != "find":
            return

        if self.generic_yesno_input("Do you need to search a sorted range", ref):
            self.algo = "std::binary_search, std::lower_bound, std::upper_bound or std::equal_range"
        else:
            self.algo = "std::find, std::find_if or custom find member if available"

    def algo_root_step_sort(self, ref):
        if self.concern != "sort":
            return

        if self.generic_yesno_input("Do you need to separate data according to a criteria", ref):
            self.algo = "std::partition or std::stable_partition if relative order of items should be preserved"
        elif self.generic_yesno_input("Do you need to know the value of the nth element if the data structure was sorted with all others correctly dispatched around it", ref):
            self.algo = "std::nth_element"
        elif self.generic_yesno_input("Do you need to sort part of a data structure", ref):
            self.algo = "std::partial_sort"
        else:
            self.algo = "std::sort or std::stable_sort"

    def algo_root_step_traversal(self, ref):
        if self.concern != "traversal":
            return

        self.algo = "std::for_each or custom range-based for loop if more convenient"


class ImplRecipeCook(RecipeCook):
    '''Recipe for implementation code'''

    def __init__(self, desc, template_path="templates"):
        super().__init__(desc, template_path)
        self.implattr = {}

    def show_dish_console_impl(self):
        tpl_h = self.env.get_template("impl.h")
        self.implattr["annotations"] = self.annotations
        print(tpl_h.render(self.implattr))

    def write_dish(self, odir: str):
        self.show_dish_console()
        print_msg("This recipe has nothing to write to disk", "WARN")


_recpp_cookbook = {
    "design": DesignRecipeCook,
    "class": ClassRecipeCook,
    "function": FunctionRecipeCook,
    "lambda": LambdaRecipeCook,
    "ds": DataStructureRecipeCook,
    "algo": AlgorithmRecipeCook,
    "impl": ImplRecipeCook
}

# ---------------------------------------------
# Cookbook actions
# ---------------------------------------------


def load_recipe(recipe_type: str):
    '''Load recipe from database file'''
    with open(str(Path("recipes") / f"{recipe_type}_recipe.json"), "r", encoding="utf8") as f:
        return json.load(f)


def cook(dish: str, display_live_annot: bool, odir: str):
    '''
    Dispatch cooking step to the correct handler
    :param dish: dish name
    :param display_live_annot: set to True to display tips while cooking
    :param odir: output directory for generated code
    '''
    cook = _recpp_cookbook[dish](load_recipe(dish))
    cook.cook(do_live_annot=display_live_annot)
    cook.serve_dish(odir)


def recipe(dish: str, with_annot: bool, whitelist: str, with_header=True):
    '''
    List steps in a recipe
    :param dish: dish name
    :param with_annot: display annotations instead of steps
    :param whitelist: whitelist used to filter annotation
    '''
    if dish == "all" and with_annot:
        print(_recpp_recipe)
        for d in ["design", "class", "function", "lambda", "ds", "algo", "impl"]:
            recipe(dish=d, with_annot=with_annot,
                   whitelist=whitelist, with_header=False)
        return

    rec = load_recipe(dish)
    if with_annot:
        if not "*" in whitelist:
            whitelist += ",*"
        steps = [f"{a['type']} [{a['ref']}]: {a['msg']}" for meta in rec
                 for a in meta["annotations"]
                 if (whitelist == "*" or any(w in a['type']
                                             for w in whitelist.split(',')))]
    else:
        steps = [{"cookstep": meta["id"],
                  "description": meta["desc"],
                  "substeps": [f"{s['id']}: {s['desc']}" for s in meta["steps"]]} for meta in rec]

    if with_header:
        print(_recpp_recipe)

    if with_annot and steps:
        print('\n'.join(steps))
    elif steps:
        print(json.dumps(steps, indent=2, sort_keys=False))

# ---------------------------------------------
# Entry point
# ---------------------------------------------


if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('--keep', '-k', dest='annot_whitelist', type=str, default='*',
                        help='desc: annotation whitelist in list annotations mode\n'
                        'depends: -l -a\n'
                        'default: *\n'
                        'example: recpp.py -d class -l -a -k PERF,USA')
    parser.add_argument('--output-dir', '-o', dest='odir', type=str, default='',
                        help='desc: output directory where to store generated code\n'
                        'warning: is only used in recipe mode for class and function dishes\n'
                        'default: output to console\n'
                        'example: recpp.py -d class -o /tmp/recpp')
    parser.add_argument('--annot', '-a', dest='annot', action='store_true',
                        help='desc (list mode,-l): display annotations instead of steps\n'
                        'example: recpp.py -d ds -l -a\n'
                        'desc (recipe mode): display annotations interactively instead of in generated pseudo-code\n'
                        'example: recpp.py -d algo -a')
    parser.add_argument('--list', '-l', dest='act', action='store_const', const='recipe', default='cook',
                        help='desc: list recipe steps or annotations in a recipe\n'
                        'example (list steps): recpp.py -d function -l\n'
                        'example (list annotations): recpp.py -d function -l -a')
    parser.add_argument('--dish', '-d', dest='dish', choices=['design', 'class', 'function', 'lambda', 'ds', 'algo', 'impl', 'all'],
                        type=str, default='design', help='desc: type of dish to cook\n'
                        'warning: "all" can only be used in list mode with annotations\n'
                        'example (recipe mode): reccp.py -d impl\n'
                        'example (list mode,-l): reccp.py -d all -l -a')
    args = parser.parse_args()

    print(_recpp_header)

    try:
        if args.act == 'cook':
            cook(dish=args.dish, display_live_annot=args.annot, odir=args.odir)
        else:
            recipe(dish=args.dish, with_annot=args.annot,
                   whitelist=args.annot_whitelist)
    except Exception as e:
        print_msg(str(e))
