message(STATUS "Implement me")
add_custom_command(
	OUTPUT manvenv
	COMMAND virtualenv -p python3 manvenv || python3 -m venv manvenv
    # COMMAND source manvenv/bin/activate
	COMMAND manvenv/bin/pip3 install -r ${CMAKE_CURRENT_SOURCE_DIR}/requirements.txt
	DEPENDS requirements.txt
)
add_custom_target(venv DEPENDS manvenv)


set(MARKDOWN_INPUT
	markdown/chaindot.py.1.md
	markdown/evaluate_vars.1.md
	markdown/expbegin.1.md
	markdown/expclean.1.md
	markdown/getdef.1.md
	markdown/logreader.1.md
	markdown/madmin.1.md
	markdown/maestro.1.md
	markdown/mflow.1.md
	markdown/mserver.1.md
	markdown/mserver_check.1.md
	markdown/nodeinfo.1.md
	markdown/nodelister.1.md
	markdown/nodelogger.1.md
	markdown/scanexp.1.md
	markdown/task_setup.dot.1.md
	markdown/task_setup.ksh.1.md
	markdown/task_setup.py.1.md
	markdown/varsed.py.1.md
	markdown/xflow.1.md
	markdown/xflow_overview.1.md
)

set(MARKDOWN_OUTPUT
	roff/chaindot.py.1
	roff/evaluate_vars.1
	roff/expbegin.1
	roff/expclean.1
	roff/getdef.1
	roff/logreader.1
	roff/madmin.1
	roff/maestro.1
	roff/mflow.1
	roff/mserver.1
	roff/mserver_check.1
	roff/nodeinfo.1
	roff/nodelister.1
	roff/nodelogger.1
	roff/scanexp.1
	roff/task_setup.dot.1
	roff/task_setup.ksh.1
	roff/task_setup.py.1
	roff/varsed.py.1
	roff/xflow.1
	roff/xflow_overview.1
)

add_custom_command(
	OUTPUT ${MARKDOWN_OUTPUT}
	COMMAND source manvenv/bin/activate \; ${CMAKE_CURRENT_SOURCE_DIR}/create_roffs_from_markdown.sh ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR}/roff
	DEPENDS venv ${MARKDOWN_INPUT}
)
add_custom_target(man ALL DEPENDS ${MARKDOWN_OUTPUT})

INSTALL(
	DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/roff/
	DESTINATION ${CMAKE_INSTALL_PREFIX}/man/man1
)
