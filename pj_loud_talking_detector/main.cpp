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

/*** INCLUDE ***/
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <algorithm>

#ifndef BUILD_ON_PC
#include "pico/stdlib.h"
#endif

#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "tensorflow/lite/version.h"
#include "micro_features/model.h"
#include "micro_features/yes_micro_features_data.h"
#include "micro_features/no_micro_features_data.h"
#include "micro_features/micro_model_settings.h"
#include "micro_features/model.h"
#include "feature_provider.h"

#include "utility_macro.h"
#include "audio_provider.h"
#include "majority_vote.h"
#include "oled.h"

/*** MACRO ***/
#define TAG "main"
#define PRINT(...)   UTILITY_MACRO_PRINT(TAG, __VA_ARGS__)
#define PRINT_E(...) UTILITY_MACRO_PRINT_E(TAG, __VA_ARGS__)

static constexpr float kScoreThreshold = 0.8;
static constexpr int32_t kCategoryIndexOfTalking = 0;

/*** GLOBAL_VARIABLE ***/
static tflite::MicroErrorReporter micro_error_reporter;
static tflite::ErrorReporter* error_reporter = &micro_error_reporter;

/*** FUNCTION ***/
static tflite::MicroInterpreter* CreateStaticInterpreter(void) {
    constexpr int32_t kTensorArenaSize = 80 * 1024;
    static uint8_t tensor_arena[kTensorArenaSize];
    const tflite::Model* model = tflite::GetModel(g_model);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        PRINT_E("Model provided is schema version %d not equal to supported version %d.", model->version(), TFLITE_SCHEMA_VERSION);
        return nullptr;
    }

    static tflite::AllOpsResolver resolver;
    static tflite::MicroInterpreter static_interpreter(model, resolver, tensor_arena, kTensorArenaSize, error_reporter);
    tflite::MicroInterpreter* interpreter = &static_interpreter;
    TfLiteStatus allocate_status = interpreter->AllocateTensors();
    if (allocate_status != kTfLiteOk) {
        PRINT_E("AllocateTensors() failed");
        return nullptr;
    }

    TfLiteTensor* input = interpreter->input(0);
    TfLiteTensor* output = interpreter->output(0);
    if (input->bytes != kFeatureElementCount) {
        PRINT_E("Input size seems wrong: %d\n", static_cast<int32_t>(input->bytes));
        return nullptr;
    }

    if (output->bytes != kCategoryCount) {
        PRINT_E("Output size seems wrong: %d\n", static_cast<int32_t>(output->bytes));
        return nullptr;
    }

    return interpreter;
}


void DisplayResultOled(Oled& oled, std::array<int32_t, kCategoryCount> current_score_list, int32_t zero_point, float scale) {
    /* Create majority vote to remove noise from the result (use int8 to avoid unnecessary dequantization (calculation)) */
    //MajorityVote<float> majority_vote;
    static MajorityVote<int32_t> majority_vote;

    oled.FillRect(0, 0, 0, Oled::kWidth, Oled::kHeight);
    float score_talking = (current_score_list[kCategoryIndexOfTalking] - zero_point) * scale;
    char buff[Oled::kWidth / Oled::kFontWidth - 1];
    oled.SetCharPos(1, 1);
    snprintf(buff, sizeof(buff), "Talking Level:%5.1f%%\n", score_talking * 100);
    oled.PrintText(buff);
    oled.SetCharPos(2 + 0 * 2, 3);
    oled.PrintText("|");
    oled.SetCharPos(2 + 8 * 2, 3);
    oled.PrintText(":");
    oled.SetCharPos(2 + 1, 3);
    for (int32_t i = 0; i < static_cast<int32_t>(score_talking * 10 * 2 + 0.05); i++) {
        oled.PrintText(">");
    }
    oled.SetCharPos(2 + 10 * 2, 3);
    oled.PrintText("|");

    /* Use low-pass filtered result to judge if talking or not */
    int32_t first_index;
    int32_t score;
    majority_vote.vote(current_score_list, first_index, score);
    if (first_index == kCategoryIndexOfTalking) {
        float score_dequantized = (score - zero_point) * scale;
        if (score_dequantized >= kScoreThreshold && score_talking >= kScoreThreshold) {
            oled.SetCharPos(2, 5);
            oled.PrintText("++++++++++++++++++++++");
            oled.SetCharPos(2, 6);
            oled.PrintText("++ Talking Detected ++");
            oled.SetCharPos(2, 7);
            oled.PrintText("++++++++++++++++++++++");
        }
    }
}

int main(void) {
#ifndef BUILD_ON_PC
    stdio_init_all();
    sleep_ms(1000);		// wait until UART connected
#endif

    PRINT("Talking Detector\n");

    /* Create Display */
    Oled oled;
    oled.Initialize();
    oled.FillRect(0, 0, 0, Oled::kWidth, Oled::kHeight);
    oled.SetCharPos(4, 4);
    oled.PrintText("Talking Detector");

    /* Create feature provider */
    static int8_t feature_buffer[kFeatureElementCount];
    static FeatureProvider feature_provider(kFeatureElementCount, feature_buffer);
    static AudioProvider audio_provider;
    audio_provider.Initialize();
    int32_t previous_time = 0;

#if 0
    /* for recording */
    /* memo. increase (kBufferSize = 200). Call Stop() when overflow */
    while(audio_provider.GetLatestAudioTimestamp() < 0);
    int32_t current_time = audio_provider.GetLatestAudioTimestamp();
    while(1) {
        int16_t* audio_samples = nullptr;
        int32_t audio_samples_size = 0;
        audio_provider.GetAudioSamples(current_time,
                    kFeatureSliceDurationMs, &audio_samples_size,
                    &audio_samples);
        if (audio_samples_size <= 0) continue;
        for (int32_t i = 0; i < audio_samples_size; i++) {
            printf("%d,", audio_samples[i]);
        }
        current_time += audio_samples_size * 1000 / 16000;
    }
#endif

    /* Create interpreter */
    tflite::MicroInterpreter* interpreter = CreateStaticInterpreter();
    if (!interpreter) {
        PRINT_E("CreateStaticInterpreter failed\n");
        HALT();
    }
    TfLiteTensor* input = interpreter->input(0);
    TfLiteTensor* output = interpreter->output(0);

    while (1) {
        /* Generate feature */
        audio_provider.DebugWriteData(500);
        const int32_t current_time = audio_provider.GetLatestAudioTimestamp();
        if (current_time < 0 || current_time == previous_time) continue;

        int32_t how_many_new_slices = 0;
        TfLiteStatus feature_status = feature_provider.PopulateFeatureData(&audio_provider, error_reporter, previous_time, current_time, &how_many_new_slices);
        if (feature_status != kTfLiteOk) {
            /* It may reach here when underflow happens */
            PRINT_E("Feature generation failed\n");
            // HALT();
        }
        previous_time = current_time;
        if (how_many_new_slices == 0) continue;

        /* Copy the generated feature data to input tensor buffer*/
        for (int32_t i = 0; i < kFeatureElementCount; i++) {
            input->data.int8[i] = feature_buffer[i];
        }

        /* Run inference */
        TfLiteStatus invoke_status = interpreter->Invoke();
        if (invoke_status != kTfLiteOk) {
            PRINT_E("Invoke failed\n");
            HALT();
        }

        /* Show result */
        int8_t* y_quantized = output->data.int8;
        std::array<int32_t, kCategoryCount> current_score_list;
        for (int32_t i = 0; i < kCategoryCount; i++) {
            current_score_list[i] = y_quantized[i];
            float y = (y_quantized[i] - output->params.zero_point) * output->params.scale;
            PRINT("%s: %.03f\n", kCategoryLabels[i], y);
        }
        DisplayResultOled(oled, current_score_list, output->params.zero_point, output->params.scale);
    }

    return 0;
}
