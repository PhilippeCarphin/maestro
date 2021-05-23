cmake_minimum_required(VERSION 3.14)

project(maestro C)

if("${CMAKE_INSTALL_PREFIX}" STREQUAL /usr/local OR "${CMAKE_INSTALL_PREFIX}" STREQUAL "")
    set(CMAKE_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/install-site/maestro_1.7.0_ubuntu_18.04-skylake-64)
    message(STATUS "Setting CMAKE_INSTALL_PREFIX to ${CMAKE_INSTALL_PREFIX}")
endif()

add_subdirectory(src)
add_subdirectory(man)

configure_file(use-maestro.in.sh use-maestro.sh @ONLY)
install(FILES ${CMAKE_BINARY_DIR}/use-maestro.sh DESTINATION ${CMAKE_INSTALL_PREFIX})
