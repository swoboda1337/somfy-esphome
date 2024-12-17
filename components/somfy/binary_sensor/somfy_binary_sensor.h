
#pragma once

#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esphome/components/somfy/somfy.h"

namespace esphome {
namespace somfy {

class SomfyBinarySensor : public Component, public SomfySensor {
 public:
  virtual void update_sunny(uint32_t address, bool value) override;
  virtual void update_windy(uint32_t address, bool value) override;
  void dump_config() override;
  void set_address(uint32_t address) { this->address_ = address; }
  SUB_BINARY_SENSOR(windy)
  SUB_BINARY_SENSOR(sunny)
 protected:
  uint32_t address_;
};

}  // namespace somfy
}  // namespace esphome
