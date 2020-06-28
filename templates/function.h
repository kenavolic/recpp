//
// recpp auto generated function pseudo code
//

{% for item in annotations -%}
// {{ item.type }} [{{ item.ref }}]: {{ item.msg }}
{% endfor -%}
{% if ret.comments -%}
// NOTE (on return type) [recpp.internal]: {{ ret.comments }}
{% endif%}

///
/// \brief {% if responsability %} {{responsability}} {% else %} TODO {% endif %}
{%- for item in params %}
/// \param {{item.name}} TODO {% if "*" in item.type -%}(can it be nullptr?){% endif %}
{%- endfor %}
{%- for item in tparams %}
/// \tparam TODO
{%- endfor %}
{%- if ret.rtype != "void" %}
/// \return TODO
{%- endif %}
/// \pre TODO (NOTE [CCS.74]: preconditions should be easily checkable by any caller and
///                           e.g. xml error-free syntax expectation in a file pointed by 
///                                 a string parameter is not reasonable
///                           e.g. expectations on the state of an object is reasonable)
/// \post TODO (e.g. state of an object after the call)
{%- if not "noexcept" in attr.post %}
/// \throw TODO (list the exceptions if possible)
/// \note TODO (document the exception guarantee: not exception-safe, basic guarantee, strong guarantee)
{%- endif %}
{%- if thread_hostile %}
/// \warning This function is thread_hostile
{%- endif %}
///
{% if tparams -%}
// USA [CCS.65]: document the points of customization
template <
    {%- for item in tparams %}
    {{ item.name}}{{ "," if not loop.last }}
    {%- endfor %}
>
// MAINT,REL [cppcore.I.9,cppcore.T.13,cppcore.T.48]: requires, shorthand notation or enable_if
{% endif -%}
{{attr.pre}} {{ret.rtype}} {{name}} (
{%- for item in params %}
{{ item.type}} {{ item.name }}{{ "," if not loop.last }} {% if item.comments %} /* WARNING: {{ item.comments }} */ {% endif %}
{%- endfor %}
) {{attr.post}} {% if pure %}= 0; {% else %}
{{"{"}}
// ----------------- Pre-Check -----------------
// REL [cppcore.I.5,cppcore.I.6,cppcore.E.7]: Precondition check
{% if "override" in attr.post -%} // USA [recpp.internal]: no harder precondition in overidden methods {% endif %}
// REL [recpp.internal]: preconditions should be considered as programmer not recoverable error
// REL,SEC [CERT.INT30-C...CERT.INT30-C]: for arithmetics, check under/overflow, division per zero, out of range index
// REL [recpp.internal]: for pointers, check nullity
// TIPS [recpp.internal]: in c++20, enforce the preconditions with [[expects...]] in function declaration
//                        or [[assert...]] in function body

{% if type == "method" -%}
// ----------------- Invariant Check -----------------
// REL [cppcore.E.4]: check invariants are met
// TIPS [cppcore.E.4]: in c++20, enforce the invariant check with [[expects...]] in function declaration
//                        or [[assert...]] in function body
{% endif %}

// ----------------- User inputs check -----------------
// REL [recpp.internal]: api user input checks should be considered as expected recoverable error
//                       e.g. check a file existence on a string param

// ----------------- Core -----------------
// MAINT [cppcore.F.3]: function body short and simple
// MAINT [recpp.internal]: law of demeter (should call method/function belonging to self, parameters, object it creates, component objects)
// CORRECT,REL [recpp.internal]: move/forward only in the final use of parameter
{%- if tparams %}
// PERF [cppcore.T.60]: minimize a template's context dependencies
// NOTE [cppcore.T.69]: inside a template, don't make an unqualified non-member function call unless you intend it to be a customization point
{%- endif %}
{%- if type == "method" and "const" in attr.post %}
// CON,REL [EMCPP.16]: make const member function thread-safe
{%- endif %}

{% if type == "method" and not "noexcept" in attr.post -%}
// a- Throwable code that does not modify invariant
// b- Noexcept code that modifies invariant
{% endif %}

// ----------------- Post-check -----------------
// REL [cppcore.I.7,cppcore.I.8,cppcore.E.8]: post-condition check (the expected operations were performed)
{% if "override" in attr.post -%} // USA,CORRECT [recpp.internal]: no weaker postconditions in overidden methods {% endif %}
// TIPS [recpp.internal]: release resource with RAII
// TIPS [recpp.internal]: in c++20, enforce the postconditions with [[ensures...]] in function declaration
//                        or [[assert...]] in function body

{% if type == "method" -%}
// ----------------- Invariant Check -----------------
// REL [recpp.internal]: check invariants are still valid
// TIPS [cppcore.E.4]: in c++20, enforce the invariants check with [[ensures...]] in function declaration
//                        or [[assert...]] in function body
{% endif %}

// ----------------- Return -----------------
// PERF [cppcore.F.48,EMCPP.25]: never return std::move(local_variable) because no RVO will take place on reference to local_variable
// PERF [EMCPP.25]: move/forward rvalue/forwarding reference passed as parameter
// PERF [recpp.internal]: do not name if possible to make use of c++ 17 guaranteed copy elision
// REL [recpp.internal]: do not use std::remove_ref for container item, etc.
{% if "&" in  ret.rtype -%}
// REL [recpp.internal]: do not return local variable
{% endif %}
{{"}"}}
{% endif %}