cmake_minimum_required(VERSION 3.12)

set(PICO_SDK_PATH ${CMAKE_CURRENT_LIST_DIR}/pico-sdk)
include(pico_sdk_import.cmake)

set(ProjectName "pico-work")
project(${ProjectName})
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_subdirectory(pico-tflmicro)

# for pico_pdm_microphone
add_library(pico_pdm_microphone INTERFACE)
target_sources(pico_pdm_microphone INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/pico-microphone/src/pdm_microphone.c
    ${CMAKE_CURRENT_LIST_DIR}/pico-microphone/src/OpenPDM2PCM/OpenPDMFilter.c
)
target_include_directories(pico_pdm_microphone INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/pico-microphone/src/include
)
pico_generate_pio_header(pico_pdm_microphone ${CMAKE_CURRENT_LIST_DIR}/pico-microphone/src/pdm_microphone.pio)
target_link_libraries(pico_pdm_microphone INTERFACE pico_stdlib hardware_dma hardware_pio hardware_clocks)

add_subdirectory(pj_loud_talking_detector)
