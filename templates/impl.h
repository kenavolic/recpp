//
// recpp auto generated misc pseudo code
//

{% for item in annotations -%}
// {{ item.type }} [{{ item.ref }}]: {{ item.msg }}
{% endfor -%}

//
// Resource management
//

// Basic not optimized version of an raii wrapper
{% raw %}
template <typename Callable>
class RaiiWrapper{
private:
  Callable m_c;
  bool     m_do{ true };

public:
  explicit RaiiWrapper(Callable && c)
    : m_c{ std::move(c) }
  {}

  ~RaiiWrapper()
  {
    if (m_do)
    {
      m_c();
    }
  }

  RaiiWrapper(const RaiiWrapper &) = delete;
  RaiiWrapper(const RaiiWrapper &&) = delete;
  RaiiWrapper& operator=(const RaiiWrapper &) = delete;
  RaiiWrapper& operator=(RaiiWrapper &&) = delete;

  void set() {
    m_do = true;
  }

  void unset() {
    m_do = false;
  }
};

template <typename Callable>
inline auto finally(Callable && c) {
  return RaiiWrapper(std::forward<Callable>(c));
}
{% endraw %}

//
// Initialization
//
// REL,USA [cppcore.ES.23, CERT.DCL53-CPP]: prefer the {}-initializer syntax 
//                                          because it prevents narrowing, most vexing parse, and is trully uniform
// NOTE [recpp.internal]: ={} gives copy initialization whereas {} gives direct initialization
// NOTE [recpp.internal]: {} accepts explicit ctor, ={} does not
{% raw %}
auto val = {1,2,3}; // Get an initializer list to forward to std::make_xxx
{% endraw %}


//
// If/Else
//

// MAINT [cppcore.ES.6]: declare names in for-statement initializers and conditions to limit scope
// PERF [recpp.internal]: put the straight case in the if
// PERF [recpp.internal]: avoid data-dependant expression in ifs to enable dynamic branch prediction

{% raw %}
if (auto pc = dynamic_cast<MyClass*>(ptr)) {
    // TODO
}
if (auto [val, success] = init(); success) {
    // TODO
}
{% endraw %}

//
// For loop
//

{% raw %}
bool state_flag{true};
// ...
// Code that modifies state_flag
// ...
// Bad
for (int i = 0; i < 1000000; ++i) {
  if (state_flag) {
    // TODO
  } else {
    // TODO
  }
}
// Better
if (state_flag) {
  // Copy loop or function call
} else {
  // Copy loop or function call
}
{% endraw %}

{% raw %}
template <typename Container> 
void g(Container c)
{
    // case 1
    for (auto&& v : c) // REL [recpp.internal]: we don't know the signature of the container interface
                       //                       thus prefer auto&&, use std::forward if needed
    {
      // TODO
    }

    // case 2
    // use using to fallback to std version
    using std::cbegin;
    using std::cend;
    std::for_each(cbegin(c), cend(c), ...);
}
{% endraw %}
