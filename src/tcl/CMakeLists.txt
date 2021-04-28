include(ExternalProject)
macro(add_tcl_external_project tcl_thing)
    ExternalProject_Add(
        tcl8.5.11
        SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}
        DOWNLOAD_COMMAND cd ${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}/unix
        CONFIGURE_COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}/unix/configure
                          --prefix=${CMAKE_CURRENT_SOURCE_DIR}
        PREFIX ${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}/unix
        BUILD_IN_SOURCE 1
        BUILD_COMMAND make
        INSTALL_COMMAND make install
    )
endmacro()

macro(add_tcl_external_dep_project tcl_thing subdir)
    ExternalProject_Add(
        ${tcl_thing}
        SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}
        DOWNLOAD_COMMAND cd ${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}/${subdir}
        CONFIGURE_COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}/${subdir}/configure
        # --srcdir=${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}/${surdir}
                          -with-tcl=${CMAKE_CURRENT_SOURCE_DIR}/lib
                          --with-tclinclude=${CMAKE_CURRENT_SOURCE_DIR}/include
                          --prefix=${CMAKE_CURRENT_SOURCE_DIR}
        PREFIX ${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}/${subdir}
        BUILD_IN_SOURCE 1
        BUILD_COMMAND make
        INSTALL_COMMAND make install
    )
    add_dependencies(${tcl_thing} tcl8.5.11)
endmacro()

macro(add_tk_external_dep_project tcl_thing)
    ExternalProject_Add(
        ${tcl_thing}
        SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}
        DOWNLOAD_COMMAND cd ${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}/${subdir}
        CONFIGURE_COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}/${subdir}/configure
        # --srcdir=${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}/${surdir}
                          -with-tcl=${CMAKE_CURRENT_SOURCE_DIR}/lib
                          --with-tclinclude=${CMAKE_CURRENT_SOURCE_DIR}/include
                          --with-tk=${CMAKE_CURRENT_SOURCE_DIR}/lib
                          --prefix=${CMAKE_CURRENT_SOURCE_DIR}
        PREFIX ${CMAKE_CURRENT_SOURCE_DIR}/${tcl_thing}/${subdir}
        BUILD_IN_SOURCE 1
        BUILD_COMMAND make
        INSTALL_COMMAND export PATH=${CMAKE_CURRENT_SOURCE_DIR}/bin make install
    )
    add_dependencies(${tcl_thing} tcl8.5.11 tk8.5.11)
endmacro()

add_tcl_external_project(tcl8.5.11)
add_tcl_external_dep_project(thread2.6.7 "")
add_tcl_external_dep_project(tk8.5.11 unix)
add_tcl_external_dep_project(tDOM-0.8.3 "")
add_tcl_external_dep_project(tcllib-1.13 "")
add_tcl_external_dep_project(tklib-0.5 "")
add_tk_external_dep_project(Tktable2.10)
add_tk_external_dep_project(tkimg1.4)
