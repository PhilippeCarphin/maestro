cmake_minimum_required(VERSION 3.14)

project(maestro C)

if("${CMAKE_INSTALL_PREFIX}" STREQUAL /usr/local OR "${CMAKE_INSTALL_PREFIX}" STREQUAL "")
    set(CMAKE_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/install-site)
    message(STATUS "Setting CMAKE_INSTALL_PREFIX to ${CMAKE_INSTALL_PREFIX}")
endif()

add_subdirectory(src)
add_subdirectory(man)
