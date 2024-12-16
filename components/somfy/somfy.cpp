#include "esphome/core/log.h"
#include "esphome/core/helpers.h"
#include "esphome/core/hal.h"
#include "somfy.h"
#include <cinttypes>

namespace esphome {
namespace somfy {

static const char *const TAG = "somfy";
static const int32_t SYMBOL = 640;

void SomfyComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "Somfy:");
  ESP_LOGCONFIG(TAG, "  Name: %" PRIx32, this->address_);
  ESP_LOGCONFIG(TAG, "  Code: %" PRIu16, this->code_);
}

void SomfyComponent::setup() {
  uint32_t type = fnv1_hash(std::string("Somfy: ") + format_hex(this->address_));
  this->preferences_ = global_preferences->make_preference<uint16_t>(type);
  this->preferences_.load(&this->code_);
  this->rx_->register_listener(this);
}

void SomfyComponent::set_code(uint16_t code) {
  ESP_LOGD(TAG, "Somfy updating code to %" PRIu16 " from %" PRIu16, code, this->code_);
  this->code_ = code;
  this->preferences_.save(&this->code_);
}

void SomfyComponent::send_command(SomfyCommand command, uint32_t repeat) {
  uint8_t frame[7];
  frame[0] = 0xA7;                   // encryption key. Doesn't matter much
  frame[1] = command << 4;           // which button did  you press? The 4 LSB will be the checksum
  frame[2] = this->code_ >> 8;       // rolling code (big endian)
  frame[3] = this->code_;            // rolling code
  frame[4] = this->address_ >> 16;   // remote address
  frame[5] = this->address_ >> 8;    // remote address
  frame[6] = this->address_;         // remote address

  ESP_LOGD(TAG, "Somfy sending 0x%" PRIX8 " repeated %" PRIu32 " times", command, repeat);

  // crc
  uint8_t crc = 0;
  for (uint8_t i = 0; i < 7; i++) {
    crc ^= frame[i];
    crc ^= frame[i] >> 4;
  }
  frame[1] |= crc & 0xF;

  // obfuscation
  for (uint8_t i = 1; i < 7; i++) {
    frame[i] ^= frame[i - 1];
  }

  // update code
  this->code_ += 1;
  this->preferences_.save(&this->code_);

  // send wakup
  esphome::remote_base::RawTimings timings = {+9415, -9565};
  auto call = id(this->tx_).transmit();
  call.get_data()->set_data(timings);
  call.perform();
  delay(80);

  // send frame
  for (uint32_t i = 0; i < (repeat + 1); i++) {
    esphome::remote_base::RawTimings timings = {};

    // hardware sync, two sync for the first frame, seven for the following ones
    uint32_t syncs = (i == 0) ? 2 : 7;
    for (uint32_t j = 0; j < syncs; j++) {
      timings.push_back(+SYMBOL * 4);
      timings.push_back(-SYMBOL * 4);
    }

    // software sync
    timings.push_back(+4550);
    timings.push_back(-SYMBOL);

    // data
    for (uint8_t byte : frame) {
      for (uint32_t j = 0; j < 8; j++) {
        if ((byte & 0x80) != 0) {
          timings.push_back(-SYMBOL);
          timings.push_back(+SYMBOL);
        } else {
          timings.push_back(+SYMBOL);
          timings.push_back(-SYMBOL);
        }
        byte <<= 1;
      }
    }
    timings.push_back(-415);

    // send + inter frame silence
    auto call = id(this->tx_).transmit();
    call.get_data()->set_data(timings);
    call.perform();
    if (i < repeat) {
      delay(30);
    }
  }
}

bool SomfyComponent::on_receive(remote_base::RemoteReceiveData data) {
  for (uint32_t i = 0; i < 2; i++) {
    if (!data.expect_item(SYMBOL * 4, SYMBOL * 4)) {
      return true;
    }
  }
  if (!data.expect_mark(4550)) {
    for (uint32_t i = 0; i < 5; i++) {
      if (!data.expect_item(SYMBOL * 4, SYMBOL * 4)) {
        return true;
      }
    }
    if (!data.expect_mark(4550)) {
      return true;
    }
  }
  data.expect_space(SYMBOL);

  uint8_t frame[7];
  for (uint8_t &byte : frame) {
    for (uint32_t i = 0; i < 8; i++) {
      byte <<= 1;
      if (data.expect_mark(SYMBOL) || data.expect_mark(SYMBOL * 2)) {
        data.expect_space(SYMBOL);
        byte |= 0;
      } else if (data.expect_space(SYMBOL) || data.expect_space(SYMBOL * 2)) {
        data.expect_mark(SYMBOL);
        byte |= 1;
      } else {
        return true;
      }
    }
  }

  for (uint8_t i = 6; i >= 1; i--) {
    frame[i] ^= frame[i - 1];
  }

  uint8_t crc = 0;
  for (uint8_t i = 0; i < 7; i++) {
    crc ^= frame[i];
    crc ^= frame[i] >> 4;
  }
  if ((crc & 0xF) == 0) {
    uint8_t command = frame[1] >> 4;
    uint16_t code = (frame[2] << 8) | frame[3];
    uint32_t address = (frame[4] << 16) | (frame[5] << 8) | frame[6];
    ESP_LOGD(TAG, "Received: command: %" PRIx8 ", code: %" PRIu16 ", address %" PRIx32,
             command, code, address);
  }

  return true;
}

}  // namespace somfy
}  // namespace esphome
