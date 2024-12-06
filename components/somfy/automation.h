#pragma once

#include "esphome/core/component.h"
#include "esphome/core/automation.h"
#include "esphome/components/somfy/somfy.h"

namespace esphome {
namespace somfy {

template<typename... Ts> class SomfySetCodeAction : public Action<Ts...> {
 public:
  SomfySetCodeAction(SomfyComponent *somfy) : somfy_(somfy) {}
  TEMPLATABLE_VALUE(uint16_t, code)

  void play(Ts... x) override {
    this->somfy_->set_code(this->code_.value(x...));
  }

 protected:
  SomfyComponent *somfy_;
};

template<typename... Ts> class SomfySendCommandAction : public Action<Ts...> {
 public:
  SomfySendCommandAction(SomfyComponent *somfy) : somfy_(somfy) {}
  TEMPLATABLE_VALUE(SomfyCommand, command)
  TEMPLATABLE_VALUE(uint32_t, repeat)

  void play(Ts... x) override {
    this->somfy_->send_command(this->command_.value(x...), this->repeat_.value(x...));
  }

 protected:
  SomfyComponent *somfy_;
};

}  // namespace somfy
}  // namespace esphome
