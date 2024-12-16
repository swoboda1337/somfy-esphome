#pragma once

#include "esphome/core/preferences.h"
#include "esphome/components/remote_transmitter/remote_transmitter.h"
#include "esphome/components/remote_receiver/remote_receiver.h"

namespace esphome {
namespace somfy {

enum SomfyCommand : uint8_t {
    SOMFY_MY = 0x1,
    SOMFY_UP = 0x2,
    SOMFY_MYUP = 0x3,
    SOMFY_DOWN = 0x4,
    SOMFY_MYDOWN = 0x5,
    SOMFY_UPDOWN = 0x6,
    SOMFY_PROG = 0x8,
    SOMFY_SUNFLAG = 0x9,
    SOMFY_FLAG = 0xA
};

class SomfyComponent : public Component, public remote_base::RemoteReceiverListener {
 public:
  float get_setup_priority() const override { return setup_priority::LATE; }
  void setup() override;
  void dump_config() override;
  bool on_receive(remote_base::RemoteReceiveData data) override;
  void send_command(SomfyCommand command, uint32_t repeat = 4);
  void set_code(uint16_t code);
  void set_tx(remote_transmitter::RemoteTransmitterComponent *tx) { this->tx_ = tx; }
  void set_rx(remote_receiver::RemoteReceiverComponent *rx) { this->rx_ = rx; }
  void set_address(uint32_t address) { this->address_ = address; }
 protected:
  remote_transmitter::RemoteTransmitterComponent *tx_{nullptr};
  remote_receiver::RemoteReceiverComponent *rx_{nullptr};
  ESPPreferenceObject preferences_;
  uint32_t address_;
  uint16_t code_;
};

}  // namespace acurite
}  // namespace esphome
