/* Copyright 2021 iwatake2222

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/
#include "pdm_buffer.h"

#include <cstdint>
#include <cstdlib>
#include <cstdio>

#include "pico/stdlib.h"
extern "C" {
#include "pico/pdm_microphone.h"
}
#include "utility_macro.h"

/*** MACRO ***/
#define TAG "PdmBuffer"
#define PRINT(...)   UTILITY_MACRO_PRINT(TAG, __VA_ARGS__)
#define PRINT_E(...) UTILITY_MACRO_PRINT_E(TAG, __VA_ARGS__)

/*** FUNCTION ***/

/*** GLOBAL VARIABLE ***/
static struct pdm_microphone_config pdm_config = {
  .gpio_data = 26,
  .gpio_clk = 27,
  .pio = pio0,
  .pio_sm = 0,
  .sample_rate = 16000,
  .sample_buffer_size = 16,
};

std::function<void(void)> PdmBuffer::on_pdm_samples_ready_static_;

static void on_pdm_samples_ready() {
    PdmBuffer::on_pdm_samples_ready_static_();
}

void PdmBuffer::on_pdm_samples_ready_static() {

    int16_t* p = block_buffer_.WritePtr();
    if (p == nullptr) {
        PRINT_E("PdmBuffer: overflow\n");
        // Stop();
        p = block_buffer_.GetLatestWritePtr();
    }
    int32_t samples_read = pdm_microphone_read(p, block_size_);
    if (samples_read != block_size_) {
        PRINT_E("read size error\n");
    }
}


int32_t PdmBuffer::Initialize(const Config& config) {
    on_pdm_samples_ready_static_ = [this] { on_pdm_samples_ready_static(); };
    /* Set parameters */
    buffer_size_ = config.buffer_size;
    block_size_ = config.block_size;
    sampling_rate_ = config.sampling_rate;
    pdm_config.sample_rate = sampling_rate_;
    pdm_config.sample_buffer_size = block_size_;

    /* Reset buffer */
    block_buffer_.Initialize(buffer_size_, block_size_);

    /* Initialize PDM Microphone */
    if (pdm_microphone_init(&pdm_config) < 0) {
        PRINT_E("PDM microphone initialization failed!\n");
        HALT();
    }

    return kRetOk;
}

int32_t PdmBuffer::Finalize(void) {
    pdm_microphone_deinit();
    return kRetOk;
}

int32_t PdmBuffer::Start(void) {
    pdm_microphone_set_samples_ready_handler(on_pdm_samples_ready);
    if (pdm_microphone_start() < 0) {
        PRINT_E("PDM microphone start failed!\n");
        HALT();
    }
    return kRetOk;
}

int32_t PdmBuffer::Stop(void) {
    pdm_microphone_stop();
    return kRetOk;
}

bool PdmBuffer::IsInt16(void) {
    return true;
}

RingBlockBuffer<uint8_t>& PdmBuffer::GetRingBlockBuffer8(void) {
    PRINT_E("Not supported\n");
    HALT();
    static RingBlockBuffer<uint8_t> dummy;
    return dummy;
}

RingBlockBuffer<int16_t>& PdmBuffer::GetRingBlockBuffer16(void) {
    return block_buffer_;
}
