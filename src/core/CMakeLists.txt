cmake_minimum_required(VERSION 3.10)

project(masetro C)

find_package(libxml2 REQUIRED)
find_package(OpenSSL REQUIRED)

add_library(maestro_core STATIC
    # r! ls *.c | grep -v main
    expcatchup.c
    FlowVisitor.c
    getopt_long.c
    l2d2_commun.c
    l2d2_lists.c
    l2d2_roxml.c
    l2d2_roxml-internal.c
    l2d2_roxml-parse-engine.c
    l2d2_socket.c
    l2d2_Util.c
    logreader.c
    maestro.c
    nodeinfo.c
    nodelogger.c
    QueryServer.c
    ResourceVisitor.c
    runcontrollib.c
    SeqDatesUtil.c
    SeqDepends.c
    SeqListNode.c
    SeqLoopsUtil.c
    SeqNameValues.c
    SeqNode.c
    SeqNodeCensus.c
    SeqUtil.c
    SeqUtilServer.c
    tictac.c
    tsvinfo.c
    XmlUtils.c
)


link_libraries(maestro_core ${LIBXML2_LIBRARIES} ${OPENSSL_LIBRARIES})
include_directories(${LIBXML2_INCLUDE_DIRS} ${OPENSSL_INCLUDE_DIR})

# r! ls *.c | grep main
# :s/\(.*\)\.c/add_executable(\1 \1.c)
add_executable(getdef getdef_main.c)
add_executable(l2d2_admin l2d2_admin_main.c)
add_executable(l2d2_server l2d2_server_main.c)
add_executable(logreader logreader_main.c)
add_executable(maestro maestro_main.c)
add_executable(mtest mtest_main.c)
add_executable(nodeinfo nodeinfo_main.c)
add_executable(nodelogger nodelogger_main.c)
add_executable(tictac tictac_main.c)
add_executable(tsvinfo tsvinfo_main.c)

# r! ls *.c | grep main
# :s/.c$//
install(TARGETS
    getdef
    l2d2_admin
    l2d2_server
    logreader
    maestro
    mtest
    nodeinfo
    nodelogger
    tictac
    tsvinfo
)


enable_testing()
add_custom_target(check COMMAND ${CMAKE_CTEST_COMMAND})

macro(add_maestro_test test_name test_source)
    add_executable(${test_name} ${test_source})
    add_test(NAME ${test_name} COMMAND ${test_name})
    add_dependencies(check ${test_name})
endmacro()

add_maestro_test(test_datestamp test_datestamp.c)
add_maestro_test(test_MISC test_MISC.c)
add_maestro_test(test_node_stack_functions test_node_stack_functions.c)
add_maestro_test(test_path test_path.c)
add_maestro_test(test_resources test_resources.c)
add_maestro_test(test_validity test_validity.c)
add_maestro_test(test_variables test_variables.c)
add_maestro_test(test_xml test_xml.c)
add_maestro_test(test_nfs_functions test_nfs_functions.c)




