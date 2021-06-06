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

#include "analyze_amplitude.h"

#include <cstdint>
#include <cmath>

static int32_t AnalyzeAmplitude_max_amplitude = 0;
static bool AnalyzeAmplitude_reset = true;

void AnalyzeAmplitude_Reset(void) {
    AnalyzeAmplitude_reset = true;
}

float AnalyzeAmplitude_Get(void) {
    if (AnalyzeAmplitude_max_amplitude <= 0) AnalyzeAmplitude_max_amplitude = 1;
    return 20 * log10f(AnalyzeAmplitude_max_amplitude / 32768.f);
}

void AnalyzeAmplitude_Add(int16_t value[], int32_t num) {
    if (num == 0) return;
    if (AnalyzeAmplitude_reset) {
        AnalyzeAmplitude_reset = false;
        AnalyzeAmplitude_max_amplitude = 0;
    }

#if 0
    int32_t max = 0;
    for (int i = 0; i < num; i++) {
        int32_t value_abs = std::abs(value[i]);
        if (value_abs > max) {
            max = value_abs;
        }
    }
    static constexpr float kMixRatio = 0.5f;
    AnalyzeAmplitude_max_amplitude = static_cast<int32_t>(max * kMixRatio + AnalyzeAmplitude_max_amplitude * (1 - kMixRatio));
#else
    for (int i = 0; i < num; i++) {
        int32_t value_abs = std::abs(value[i]);
        if (value_abs > AnalyzeAmplitude_max_amplitude) {
            AnalyzeAmplitude_max_amplitude = value_abs;
        }
    }
#endif
}

