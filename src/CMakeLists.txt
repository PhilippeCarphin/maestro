cmake_minimum_required(VERSION 3.0)
project(maestro)

find_package(libxml2 REQUIRED)
# find_package(PkgConfig REQUIRED)

include_directories( /usr/local/opt/openssl/include ${LIBXML2_INCLUDE_DIRS})
link_directories(/usr/local/opt/openssl/lib ${LIBXML2_LIBRARY_DIRS})

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
        expcatchup_main.c
        getdef_main.c
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
        nodelogger_main.c
        ocmjinfo.c
        runcontrollib.c
        tictac.c
        tsvinfo.c
        )

message("-- PROJECT_NAME : ${PROJECT_NAME}")

add_library(${PROJECT_NAME} ${lib_sources})

target_compile_options(${PROJECT_NAME} PUBLIC -Wno-pointer-sign -Werror=incompatible-pointer-types)

# pymaestro.c
# tsvinfo_main.c
# tictac_main.c
# l2d2_server_main.c
# logreader_main.c
# maestro_main.c
# mtest_main.c
# nodeinfo_main.c
