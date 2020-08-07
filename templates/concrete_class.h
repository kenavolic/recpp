{% extends 'class.h' %}

{% block classcontent %}
public:
    //
    // Types and aliases
    //
    // MAINT [recpp.internal]: put public type and aliases here

    {% if custom_allocators %}
    //
    // Custom alloc/dealloc
    // REL [cppcore.C.40,CCS.45,CERT.DCL54-CPP]: always overload matched allocation/deallocation pairs
    // REL [CCS.46]: consider providing all new/delete forms here
    void* operator new(std::size_t s) {
        // CORRECT [ECPP.50...ECPP.52,CERT.MEM55-CPP]: implement standard conforming new/delete pairs
    }
    void operator delete(void*) {
        // CORRECT [ECPP.50...ECPP.52,CERT.MEM55-CPP]: implement standard conforming new/delete pairs
    }

    {% endif -%}

    //
    // Constructors
    //

    {%- if init_list_ctor %}
    // USA,REL [recpp.internal]: beware usage compatibility break if added after first release (will be chosen in priority)
    // 
    explicit {{classname}}(/*std::initializer_list*/);
    {% endif %}

    {%- if invariant or raii %} 
    // CORRECT [cppcore.C.40]: constructor should set the invariants
    // PERF [cppcore.C.45]: prefer NSDMI for data init only and constant values
    // USA [cppcore.C.41]:  use a factory function if a valid object cannot conveniently be constructed by a constructor
    explicit {{classname}}(/*Some params here*/);
    {% endif -%}
    {%- if invariant and not raii %} 
    // USA,INTEROP [cppcore.C.43]: provide a defaut ctor for interopability and ease of use
    // USA [cppcore.C.44]: prefer default constructors to be simple and non-throwing
    {{classname}}() noexcept /*= custom, default*/;
    {% endif -%}
    {%- if invariant or raii %}
    // TIPS [recpp.internal]: constructor implementation tips
    // REL [CCS.47]: initialize members in definition order
    // {{classname}}(/*params*/) : /*in order init list, delegating ctor or NSDMI*/ {{"{"}}
    //      // CORRECT [cppcore.E.5]: throw if invariants cannot be set
    // {{"}"}}
    {% endif -%}
    {%- if specials %}

    // TIPS [recpp.internal]: perfect forwarding constructor implementation tips
    // template <typename U, typename = std::enable_if_t<std::is_convertible_v<U, SomeType>>>
    // {{classname}}(U&& param);
    //
    // template <typename U, typename... Args,
    //         typename = std::enable_if_t<!std::is_same_v<std::decay_t<U>,{{classname}}>>
    //         >
    // explicit {{classname}}(U&& param, Args&&... args); 

    //
    // Special members
    //

    // REL [cppcore.C.31]: should release resources
    // REL [CCS.51,ECPP.8]: dtors never fail (noexcept)
    ~{{classname}}() /*= custom, default*/;
    {%- if raii %}
    // USA [ECPP.14]: enable copy if needed
    {{classname}}(const {{classname}}&) = delete;
    {{classname}}& operator=(const {{classname}}&) = delete;
    {% elif abstraction == "verythick" %}
    // USA [recpp.internal]: disable copy if needed
    {{classname}}(const {{classname}}&);
    {{classname}}& operator=(const {{classname}}&);
    {% else %}
    // MAINT [recpp.internal]: consider taking out the rule of 5
    //                         burden in an helper class to focus
    //                         on class responsability only
    {{classname}}(const {{classname}}&) /*= custom, default */;
    // TIPS [recpp.internal]: copy constructor implementation tips
    // {{classname}}(const {{classname}}& other) {{"{"}}
    //      // Initialize resource from other
    // {{"}"}}
    {{classname}}& operator=(const {{classname}}&) /*= custom, default */;
    // TIPS [recpp.internal]: copy assignment implementation tips
    //       - If Resource can be reused -> custom impl,
    //       - Elif Move assigment needs perf -> custom impl,
    //       - Else Use unifying assignment op
    // {{classname}}& operator=(const {{classname}}& other) {{"{"}}
    //      // REL [ECPP.11]: Check other against *this or order ops in the right manner
    //      // Custom impl:
    //      //  - No strong guarantee: init resource from other
    //      //  - Strong guarantee: a) create temporary (no need for self-assignment check) b) swap
    // {{"}"}}
    {% endif -%}
    {% if abstraction == "verythick" %}
    {{classname}}({{classname}}&&) noexcept;
    {{classname}}& operator=({{classname}}&&) noexcept;
    {% else %}
    {{classname}}({{classname}}&&) noexcept /*= custom, default*/;
    // TIPS [recpp.internal]: move constructor implementation tips
    // {{classname}}({{classname}}&& other) /*: a) steal other representation by mean of member-wise move (std::move)*/ {{"{"}}
    //      // b) set other representation to valid state
    //      // MAINT [recpp.internal]: use std::exchange to mix a) and b)
    //      // PERF [recpp.internal]: for b), setting to default state or minimal valid state if perf is critical
    //      // CORRECT [recpp.internal]: if there is no b), = default should be sufficient
    //      // MAINT,PERF [recpp.internal]: alternative with less performance but more code reuse
    //      //                              a) default delegate ctor
    //      //                              b) swap(other)
    // {{"}"}}
    {{classname}}& operator=({{classname}}&&) noexcept /*= custom, default*/;
    // TIPS [recpp.internal]: move assignment implementation tips
    //       - If No assignment op -> custom impl,
    //       - Elif Needs perf -> custom impl,
    //       - Else Use unifying assignment op below
    // {{classname}}& operator=({{classname}}&& other) {{"{"}}
    //      // PERF [recpp.internal]: Check other against *this if perf is critical
    //      // MAINT [recpp.internal]: use std::exchange to mix a) and b)
    //      // a) destroy visible resources
    //      // b) move assign all bases and members
    //      // c) reset other resources
    // {{"}"}}

    {%- if not raii %}
    // TIPS [recpp.internal]: unifiying copy assignment assignment with strong guarantees
    // {{classname}}& operator=({{classname}} other) {{"{"}}
    //      // a) swap objects with your own swap
    //      // return *this;
    // {{"}"}}
    {% endif %}
    {% endif %}
    {% endif %}

    //
    // INTEROP [cppcore.C.83,cppcore.C.84]: swap convenience method 
    //

    void swap({{classname}}& rhs) noexcept;
    // TIPS [recpp.internal]: swap implementation tips
    // void swap({{classname}}&& rhs) {{"{"}}
    //     using std::swap;  // CORRECT [cppcore.C.165]: make std::swap available
    //     //...
    // {{"}"}}

    //
    // Non-symmetric operators
    //

    // {{classname}}* operator->();
    // {{classname}} operator*();
    // U operator()(T val) const;

    // const T& operator[](std::size_t) const;
    // TIPS [ECPP.3]: implement non const from const
    // T& operator[](std::size_t i) {{"{"}}
    //     return const_cast<T&>(static_cast<const {{classname}}&>(*this)[i]);
    // {{"}"}}
    
    // TIPS [recpp.internal]: arithmetics operator implementation tips
    // {{classname}}& operator+=(const {{classname}}& rhs);
    // {{classname}}& operator++() {{"{"}}
    //    // actual increment
    //    // return *this;
    // {{"}"}}
    // {{classname}}& operator++(int) {{"{"}}
    //    {{classname}} tmp(*this);
    //    operator++();
    //    return tmp;
    // {{"}"}}

    //
    // Symmetric friend function (only if necessary, see annotations in non-members section)
    {%- if tparams %}
    // REL [ECPP.46]: friend non-member functions could be necessary to handle
    //                the issue of implicit conversions not beeing used for 
    //                template argument deduction (class template do not depend on TAD)
    {%- endif %}

    //
    // USA,REL [cppcore.C.164]: explicit conversion ops
    // {% if raii %} USA [ECPP.15]: consider providing access to raw resource implicitly {% endif %}

    // explicit operator T*();
    
    //
    // Public API
    // USA,MAINT [ECPP.23]: do not define as members functions that could be defined as non-members 
    //                      (e.g. utility functions that just call public methods)
    //

    // NOTE [recpp.internal]: use recpp function recipe to build your interface
    // USA [recpp.internal]: interface usefulness for client should be all or nothing (interface segregation)
    {% if abstraction == "thick" -%} // CORRECT [recpp.internal]: thick abstraction means no inline method {% endif %}
    // ...
private:
    {% if abstraction == "verythick" %}
    class Impl;

    // TIPS [cppref]: https://en.cppreference.com/w/cpp/language/pimpl
    // TIPS [recpp.internal]: to propagate const to pointer member
    //                        const Impl* impl() const { return _impl.get(); }
    //                        Impl* impl() { return _impl.get(); }
    // TIPS [recpp.internal]: use std::unique_ptr<Impl, void (*)(Impl *)> impl_;
    //                        to rely on compiler generated special functions
    std::unique_ptr<Impl> _impl;
    {% else %}
    // Private types and aliases

    // Private methods
    // ...

    // Private members
    // PERF [recpp.internal]: order types from larger to smaller
    // PERF [ECPP.31]: do not use object when reference will do
    {% endif %}
{% endblock %}

{%- block nonmembers %}

// USA [CCS.54,CCS.58]: type and non-member RELATED functions in the same namespace
namespace recpp {{"{"}}

//
// USA [cppcore.C.161,cppcore.C.168,CCS.44,ECPP.23]: non-members functions
//
// TIPS [recpp.internal]: prefer non-member non-friend function. However, friend
//                        non-member function can be used for the sake of simplicity
//                        (access private members, lack of clarity due to template
//                         notation,...)
//
// PERF [CCS.29]: consider overloading to avoid implicit type conversions
//
{%- if tparams %}
// TIPS [recpp.internal]: friend non-member functions could be necessary to handle
//                        the issue of implicit conversions for template parameter
//                        substitution
{%- endif %}
//

// TIPS [recpp.internal]: swap implementation tips for non-generic class
// USA [ECPP.25]: consider an additional std::swap specialization for non class template 
//                for caller using qualified std::swap
// USA,INTEROP [recpp.internal]: see super swap for a library https://github.com/kostasrim/cppcon_2019
// inline void swap({{classname}}& lhs, {{classname}}& rhs) {{"{"}}
//    lhs.swap(rhs);
// {{"}"}}

// TIPS [recpp.internal]: arithmetic operator implementation tips for non-generic class
// inline {{classname}} operator+({{classname}} a, const {{classname}}& b) {{"{"}}
//    // Implemented with their compound counter-part
//    a += b;
//    return a;
// {{"}"}}

// TIPS [recpp.internal]: relational operator implementation tips for non-generic class without c++20
// NOTE [recpp.internal]: pre c++20, keep in mind that operator are not symmetric when writing heterogeneous
//                        comparison operators
// inline bool operator< (const {{classname}}& lhs, const {{classname}}& rhs) {{"{"}} 
//    // actual comparison
//    // TIPS [recpp.internal]: do not write lexical comparison as lhs.a < rhs.b && lhs.c < rhs.c && ...
// {{"}"}}
// inline bool operator> (const {{classname}}& lhs, const {{classname}}& rhs) {{"{"}}
//    return rhs < lhs; 
// {{"}"}}
// inline bool operator<=(const {{classname}}& lhs, const {{classname}}& rhs) {{"{"}}
//    // TIPS [recpp.internal]: holds only for trichotomy
//    return !(lhs > rhs); 
// {{"}"}}
// inline bool operator>=(const {{classname}}& lhs, const {{classname}}& rhs) {{"{"}}
//    // TIPS [recpp.internal]: holds only for trichotomy
//    return !(lhs < rhs); 
// {{"}"}}
// ...
// TIPS [recpp.internal]: relational operator implementation tips for non-generic class with c++20
// TIPS [recpp.internal]: In c++20, only one operator<=> per homogeneous and heterogenous comp should be necessary
// NOTE [recpp.internal]: In c++20, primary operator operator<=> is symmetric and reversible
// NOTE [recpp.internal]: In c++20, using non-member JUST for the sake of heterogeneous comp is no more required
// std::{weak|strong|partial}_ordering operator<=>(const {{classname}}& lhs, const {{classname}}& rhs) const {{"{"}}
//    // Implementation here
// {{"}"}}

// TIPS [recpp.internal]: equality operator implementation tips for non-generic class
// inline bool operator==(const {{classname}}& a, const {{classname}}& b) noexcept {{"{"}}
//    // return a.mi == b.mi && ...;
//    // return a.checkEquals(b)
// {{"}"}}
// NOTE [recpp.internal]: in c++20, primary operators operator== is symmetric and reversible. Thus
//                        the operator!= might not be useful
// inline bool operator!=(const X& lhs, const X& rhs) {{"{"}}
//    return !(lhs == rhs);
// {{"}"}}

// TIPS [recpp.internal]: insertion operator implementation tips for non-generic class
// inline std::ostream& operator<<(std::ostream& os, const {{classname}}& c) {{"{"}}
//    return os << /* class members here */;
// {{"}"}}

{{"}"}}

{%- if not tparams %}

//
// Non-members function in namespace std for non-generic class
//

namespace std {{"{"}}
// TIPS [recpp.internal]: custom specialization of std::to_string example
// inline std::string to_string(const {{classname}} & t) {{"{"}}
//  std::ostringstream os;
//  os << t;
//  return os.str();
// {{"}"}}

// TIPS [cppref]: custom specialization of std::hash
// template<> struct hash<{{classname}}>
// {{"{"}}
//     std::size_t operator()(const {{classname}}& o) const noexcept
//     {
//         std::size_t h1 = std::hash<std::string>{}(s.first_name);
//         std::size_t h2 = std::hash<std::string>{}(s.last_name);
//         // ...
//         return h1 ^ (h2 << 1); // or use boost::hash_combine
//     }
// {{"}"}};
{{"}"}}

{% endif -%}

{% endblock -%}