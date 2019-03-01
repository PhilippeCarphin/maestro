cmake_minimum_required(VERSION 2.8)
project(maestro)

find_package(libxml2 REQUIRED)
# find_package(PkgConfig REQUIRED)

include_directories( /usr/local/opt/openssl/include ${LIBXML2_INCLUDE_DIRS})
link_directories(/usr/local/opt/openssl/lib ${LIBXML2_LIBRARY_DIRS})
link_libraries(${LIBXML2_LIBRARIES} crypto)

# There is a good reason for not using file globs
set(lib_sources
        FlowVisitor.c
        QueryServer.c
        ResourceVisitor.c
        SeqDatesUtil.c
        SeqDepends.c
        SeqListNode.c
        SeqLoopsUtil.c
        SeqNameValues.c
        SeqNode.c
        SeqNodeCensus.c
        SeqUtil.c
        SeqUtilServer.c
        XmlUtils.c
        expcatchup.c
        getopt_long.c
        l2d2_Util.c
        l2d2_admin_main.c
        l2d2_commun.c
        l2d2_lists.c
        l2d2_roxml-internal.c
        l2d2_roxml-parse-engine.c
        l2d2_roxml.c
        l2d2_socket.c
        logreader.c
        maestro.c
        nodeinfo.c
        nodelogger.c
        ocmjinfo.c
        runcontrollib.c
        tictac.c
        tsvinfo.c
        )

message("-- PROJECT_NAME : ${PROJECT_NAME}")

add_library(seq SHARED ${lib_sources})

target_compile_options(seq PUBLIC -Wno-pointer-sign -Werror=incompatible-pointer-types -Werror=sometimes-uninitialized -Werror=uninitialized -Werror=parentheses)


link_libraries(seq)

add_executable(maestro maestro_main.c)
add_executable(tsvinfo tsvinfo_main.c)
add_executable(tictac tictac_main.c)
add_executable(l2d2_server l2d2_server_main.c)
add_executable(mtest mtest_main.c)
add_executable(getdef getdef_main.c)
add_executable(expcatchup expcatchup_main.c)
add_executable(nodeinfo maestro_main.c)
add_executable(nodelogger nodelogger_main.c)

add_custom_target(post_build
        COMMAND echo "Placeholder for custom Post build command or script")

add_dependencies(post_build maestro tsvinfo tictac l2d2_server mtest getdef expcatchup nodeinfo nodelogger)
