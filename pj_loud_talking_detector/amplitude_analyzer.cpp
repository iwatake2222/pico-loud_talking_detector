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

#include "amplitude_analyzer.h"

#include <cstdint>
#include <cmath>
#include <algorithm>

static uint32_t AmplitudeAnalyzer_max_amplitude = 0;
static bool AmplitudeAnalyzer_reset = true;

void AmplitudeAnalyzer_Reset(void) {
    AmplitudeAnalyzer_reset = true;
}

float AmplitudeAnalyzer_GetDecibel(void) {
    if (AmplitudeAnalyzer_max_amplitude == 0) return -100.0f;
    float value = 20 * log10f(AmplitudeAnalyzer_max_amplitude / 32768.f);
    if (value <= -50) value = -50.f;
    if (value > 0) value = 0.f;
    return value;
}

void AmplitudeAnalyzer_Add(int16_t value[], int32_t num) {
    if (num == 0) return;
    if (AmplitudeAnalyzer_reset) {
        AmplitudeAnalyzer_reset = false;
        AmplitudeAnalyzer_max_amplitude = 0;
    }

    uint32_t amplitude_acc = 0;
    for (int i = 0; i < num; i++) {
        uint32_t value_abs = std::abs(value[i]);
        amplitude_acc += value_abs;
    }
    amplitude_acc /= num;
    if (amplitude_acc > AmplitudeAnalyzer_max_amplitude) {
        AmplitudeAnalyzer_max_amplitude = amplitude_acc;
    }

}

