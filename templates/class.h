//
// recpp auto generated class/struct header pseudo code
//

// PORT,CORRECT [recpp.internal,CCS.24]: protect header against multiple inclusions with ifndef
// REL [CERT.DCL51-CPP]: header guard without trailing underscores
#ifndef MYLIB_{{classname}}_H 
#define MYLIB_{{classname}}_H 

{% for item in annotations -%}
// {{ item.type }} [{{ item.ref}}]: {{ item.msg }}
{% endfor %}
{%- if tparams %}
// PERF [cppcore.T.60]: minimize a template's context dependencies
// PERF [cppcore.T.61]: do not over-parameterize members (SCARY)
{%- endif %}

// REL [cppcore.T.60,CCS.23]: include from more specific (your library) to less specific std library headers
//                            or use module (c++20)
// #include "mylib.h"
// #include <otherlib> // PORT [cppcore.SF.12]: prefer the angle bracket 
// #include <iosfwd> // PERF [ECPP.31]: use declaration when you don't need more

// PERF,MAINT [recpp.internal,CCS.22,ECPP.31]: forward declare what can be (e.g. scoped enum, ...)

namespace recpp {{"{"}}

{%- block classexternals%}
{% endblock %}

///
/// \class {{classname}}
{%- if responsability %}
/// \brief {{responsability}} 
{%- endif %}
{%- if invariant %}
/// \invariant {{invariant}} 
{%- endif %}
/// \note thread safety contract: {{thread_safety}}
///
{% if tparams -%}
template <
    {%- for item in tparams %}
    {{ item.name}}{{ "," if not loop.last }}
    {%- endfor %}
>
// MAINT,REL [cppcore.I.9,cppcore.T.13,cppcore.T.48]: use concept via 'requires', shorthand notation or enable_if
{% endif -%}
class {{classname}} {% block baseclasses %} {% endblock -%} {{"{"}}
{%block classcontent %}
{% endblock%}
{{"}"}};

{{"}"}}

{%- block nonmembers %}
{% endblock %}

#endif
