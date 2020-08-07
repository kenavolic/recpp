{% extends 'class.h' %}

{% block classexternals%}

{% if base and clonable %}
{% raw %}
// REL [CCS.45]: use a clonable hierarchy to avoid slicing
// TIPS [recpp.internal]: remove the template param and return ClonableBase* 
//                        if you need covariant return type or raw pointer
// TIPS [recpp.internal]: free function to ensure smart memory management
//                        in a raw pointer based clonable hierachy
// template<typename Clonable>
// std::unique_ptr<Clonable> clone(const Clonable* obj)
// {
//    return std::unique_ptr<Clonable>(obj->clone());
// }
template <typename Derived>
class ClonableBase {
public:
    // TIPS [CCS.39]: nvi idiom
    virtual std::unique_ptr<Derived> clone() const {
        return std::unique_ptr<Derived>(this->cloneImpl());
    }

    virtual ~ClonableBase() = default;
    ClonableBase& operator=(const ClonableBase&) = delete;
    ClonableBase(ClonableBase&&) = delete;
    ClonableBase& operator=(ClonableBase&&) = delete;
protected:
    ClonableBase(const ClonableBase&) = default;
private:
    // Covariant return type implemented through the private impl
    virtual Derived* cloneImpl() const = 0;
};
{% endraw %}
{% elif base %}
// NOTE [recpp.internal]: the default for hierarchy is to be uncopyable
{% raw %}
class Uncopyable {
    public:
        virtual ~Uncopyable() = default;
        Uncopyable& operator=(const Uncopyable&) = delete;
        Uncopyable(const Uncopyable&) = delete;
        Uncopyable(Uncopyable&&) = delete;
        Uncopyable& operator=(Uncopyable&&) = delete;
};
{% endraw %}
{% endif -%}
{% endblock %}

{%- block baseclasses -%}
{%- if base and clonable -%}
 : public virtual ClonableBase<{{classname}}>
{% elif base %}
 : public virtual Uncopyable
{% else %}
: public /*virtual*/ {{basename}} /*,...*/
{%- endif -%}
{%- endblock -%}

{%- block classcontent %}
public:
    //
    // Types and aliases
    //
    // MAINT [recpp.internal]: put public type and aliases here

    {% if not base and init_with_base %}
    using {{basename}}::{{basename}};
    {% elif not interface %}
    //
    // Constructors
    //
    explicit {{classname}}(/*Some params here*/);
    // USA,INTROP [cppcore.C.43]: provide a defaut ctor for interopability and ease of use
    // USA [cppcore.C.44]: prefer default constructors to be simple and non-throwing
    {{classname}}() noexcept /*= custom, default*/;
    // TIPS [recpp.internal]: constructors implementation tips
    // REL [CCS.47]: initialize members in definition order
    // {{classname}}(/*params*/) : /*in order init list, delegating ctor or NSDMI*/ {{"{"}}
    //      // CORRECT,REL [cppcore.C.82,CCS.49,ECPP.9]: don't call virtual functions, use factory method instead
    //      // CORRECT [cppcore.E.5]: throw if invariants cannot be set
    // {{"}"}}

    // TIPS [recpp.internal]: perfect forwarding constructor implementation tips
    //  template <typename U, typename = std::enable_if_t<std::is_convertible_v<U, SomeType>>>
    //  {{classname}}(U&& param);
    //
    // template <typename U,
    //         typename = std::enable_if_t<!std::is_base_of_v<{{classname}},std::decay_t<U>> && 
    //                                    !std::is_same_v<SomeType,std::remove_ref_t<U>>>
    //         >
    // explicit {{classname}}(U&& param); 

    //
    // Destructors
    // REL [cppcore.C.31]: should release resources
    // REL [CCS.51,ECPP.8]: dtors never fail (noexcept)
    // REL [ECPP.9]: don't call virtual functions
    // Destructor if needed

    {% endif -%}

    //
    // Public API
    // USA,MAINT [ECPP.23]: do not define as members functions that could be defined as non-members 
    //                      (e.g. utility functions that just call public methods)


    {%- if interface %}
    // NOTE [recpp.internal]: use recpp function recipe to build your interface
    // USA [recpp.internal]: interface usefulness for client should be all or nothing (interface segregation)
    // virtual void method() = 0;
    // ...
    {% else %}
    // NOTE [recpp.internal]: use recpp function recipe to build your interface
    // TIPS [CCS.39]: nvi idiom
    // REL,CORRECT [cppcore.C.138]: create an overload set for a derived class and its bases with using
    // ...
    {% endif %}
{%- if not interface %}
protected:
    // Protected methods
    // NOTE [recpp.internal]: use recpp function recipe
    // USA,REL [cppcore.C.133]: avoid protected data
    // ...
    {%- if clonable %}
    {{classname}}(const {{classname}}&) = default;
    {% endif %}

private:
    // Private type and aliases

    // Private methods
    // NOTE [recpp.internal]: use recpp function recipe
    // ...
    {%- if clonable %}
    virtual {{classname}}* cloneImpl() const override {{"{"}}
        return new {{classname}}(*this);
    {{"}"}}
    {% endif %}

    // Private members
    // PERF [ECPP.31]: do not use object when reference will do
{% endif -%}
{% endblock -%}

{%- block nonmembers %}

// USA [CCS.54,CCS.58]: type and non-member RELATED functions in the same namespace
namespace recpp {{"{"}}

// USA [cppcore.C.161,cppcore.C.168,CCS.44,ECPP.23]: non-members functions

// Insertion operator implementation tips
// print is the virtual method implemented with nvi or not in the hierarchy
// template <typename T>
// inline auto operator << (std::ostream& os, const T& obj) -> decltype(std::declval<T>().print(os), os)
//{
//    obj.print(os);
//    return os;
//}

{{"}"}}

{% endblock %}