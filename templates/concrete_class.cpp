//
// recpp auto generated class/struct impl pseudo code
//

#include "concrete_class.h"

namespace recpp {{"{"}}

{% if abstraction == "verythick" %}

{{classname}}::{{classname}}() : _impl(std::make_unique<Impl>()) {}

// NOTE [recpp.internal]:
//  dtor explicit and in .cpp, otherwise implicit is inlined in .h
//  and {{classname}} dtor calls unique_ptr dtor that uses default deletor on _impl.
//  This fails because Impl type is not complete
//  (Not true for shared pointer because deleter is not part of the type)
{{classname}}::~{{classname}}() = default;

// NOTE [recpp.internal]: as custom dtor prevent move special members
//                        auto generation
{{classname}}::{{classname}}({{classname}}&&) noexcept = default;
{{classname}}::{{classname}}& operator=({{classname}}&&) noexcept = default;

// TIPS [EMCPP.22]: pimpl implementation tips
{{classname}}::{{classname}}(const {{classname}}& rhs) : _impl(nullptr) {{"{"}}
    if(rhs._impl) _impl = std::make_unique(*rhs._impl);
{{"}"}}

{{classname}}& {{classname}}=(const {{classname}}& rhs) {{"{"}}
    if (!rhs._impl) _impl.reset();
    else if (!_impl) _impl = std::make_unique(*rhs.pImpl);
    else *_impl = *rhs._impl;
{{"}"}}
{% endif %}

{{"}"}}