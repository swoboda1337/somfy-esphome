#include "esphome/core/log.h"
#include "somfy_binary_sensor.h"

namespace esphome {
namespace somfy {

static const char *const TAG = "somfy";

void SomfyBinarySensor::update_windy(uint32_t address, bool value) {
  if (this->windy_binary_sensor_ && this->address_ == address) {
    this->windy_binary_sensor_->publish_state(value);
  }
}

void SomfyBinarySensor::update_sunny(uint32_t address, bool value) {
  if (this->sunny_binary_sensor_ && this->address_ == address) {
    this->sunny_binary_sensor_->publish_state(value);
  }
}

void SomfyBinarySensor::dump_config() {
  ESP_LOGCONFIG(TAG, "Somfy Binary Sensor: 0x%" PRIx32, this->address_);
  LOG_BINARY_SENSOR("  ", "Windy", this->windy_binary_sensor_);
  LOG_BINARY_SENSOR("  ", "Sunny", this->sunny_binary_sensor_);
}

}  // namespace somfy
}  // namespace esphome
