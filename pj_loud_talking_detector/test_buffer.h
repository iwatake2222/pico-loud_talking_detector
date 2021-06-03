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

#ifndef TEST_BUFFER_H_
#define TEST_BUFFER_H_

#include <cstdint>
#include "ring_block_buffer.h"
#include "audio_buffer.h"

class TestBuffer : public AudioBuffer {
public:
    TestBuffer()
        : buffer_size_(0)
        , block_size_(0)
        , sampling_rate_(0)
    {};
    ~TestBuffer() {}
    int32_t Initialize(const Config& config) override;
    int32_t Finalize(void) override;
    int32_t Start(void) override;
    int32_t Stop(void) override;
    bool    IsInt16(void) override;
    RingBlockBuffer<uint8_t>& GetRingBlockBuffer8(void) override;
    RingBlockBuffer<int16_t>& GetRingBlockBuffer16(void) override;

public:
    void DebugWriteData(int32_t duration_ms);

private:
    int32_t buffer_size_;
    int32_t block_size_;
    int32_t sampling_rate_;
    RingBlockBuffer<uint8_t> test_block_buffer_;
};

#endif  // TEST_BUFFER_H_
