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

/* store amplitude valeu to calculate average */
static uint32_t AmplitudeAnalyzer_acc_num = 0;
static uint32_t AmplitudeAnalyzer_acc_value = 0;
static bool AmplitudeAnalyzer_reset = true;

void AmplitudeAnalyzer_Reset(void) {
    AmplitudeAnalyzer_reset = true;
}

float AmplitudeAnalyzer_Get(void) {
    if (AmplitudeAnalyzer_acc_num == 0) {
        return 0;
    }
    return AmplitudeAnalyzer_acc_value / (AmplitudeAnalyzer_acc_num * 65536.f);
}

void AmplitudeAnalyzer_Add(int16_t value[], int32_t num) {
    if (num == 0) return;
    if (AmplitudeAnalyzer_reset) {
        AmplitudeAnalyzer_reset = false;
        AmplitudeAnalyzer_acc_num = 0;
        AmplitudeAnalyzer_acc_value = 0;
    }

    int16_t amplitude_max = 0;
    int16_t amplitude_min = 0;
    for (int i = 0; i < num; i++) {
        if (value[i] > amplitude_max) {
            amplitude_max = value[i];
        }
        if (value[i] < amplitude_min) {
            amplitude_min = value[i];
        }
    }
    int32_t amplitude = static_cast<int32_t>(amplitude_max) - amplitude_min;
    AmplitudeAnalyzer_acc_num++;
    AmplitudeAnalyzer_acc_value += amplitude;
}

