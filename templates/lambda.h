//
// recpp auto generated lambda pseudo code
//

{% for item in annotations -%}
// {{ item.type }} [{{ item.ref }}]: {{ item.msg }}
{% endfor -%}

// Lambda skeleton
// {% if recursive %}std::function<ret(Ts,...)>{% else %}auto{%endif%} l = [{%- for item in captures %}{{item}}{{ "," if not loop.last }}{%- endfor %}{% if recursive %}{% if captures %},{% endif %}&l{%endif%}]{% if tparams -%}<{%- for item in tparams %}{{ item.name}}{{ "," if not loop.last }}{%- endfor %}>{%- endif %} {{attr}} ({%- for item in params %}{{ item.type}} {{ item.name }}{{ "," if not loop.last }} {%- endfor %}) {{"{"}}
//    // Core implementation
// {{"}"}}
//