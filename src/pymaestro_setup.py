from distutils.core import setup, Extension

pymaestro_module = Extension(
    'pymaestro',
    sources=[
        'pymaestro.c',
        'SeqNodeCensus.c',

        'FlowVisitor.c',
        'ResourceVisitor.c',
        'SeqDatesUtil.c',
        'SeqLoopsUtil.c',
        'SeqListNode.c',
        'SeqDepends.c',
        'SeqNameValues.c',
        'SeqNode.c',
        'SeqUtil.c',
        'XmlUtils.c',

        'nodeinfo.c',
        'l2d2_commun.c',
        'tictac.c',
        'SeqUtilServer.c',

        'l2d2_roxml-internal.c',
        'maestro.c',
        'ocmjinfo.c',
        'QueryServer.c',
        'l2d2_roxml-parse-engine.c',
        'getopt_long.c',
        'l2d2_roxml.c',
        'runcontrollib.c',
        'l2d2_Util.c',
        'l2d2_server.c',
        # 'l2d2_admin.c',
        'l2d2_socket.c',
        'logreader.c',
        'nodelogger.c',
        'tsvinfo.c',
        'expcatchup.c',
        'l2d2_lists.c',
        # 'logreader_main.c',
        # 'nodelogger_main.c',
        # 'tsvinfo_main.c',
        # 'expcatchup_main.c',
        # 'getdef_main.c',
        # 'maestro_main.c',
        # 'nodeinfo_main.c',
        # 'tictac_main.c',
        # 'mtest_main.c',
    ],
    include_dirs=[
        '/usr/local/Cellar/libxml2/2.9.9_2/include/libxml2',
        '/usr/local/Cellar/include',
        '/usr/local/Cellar/openssl//1.0.2q/include/'
    ],
    library_dirs=[
        '/usr/local/Cellar/libxml2/2.9.9_2/lib',
        '/usr/local/Cellar/openssl/1.0.2q/lib/'
    ],
    libraries=['crypto', 'xml2'],
    extra_compile_args=["-Wall", "-Wextra" '-lc', '-lcrypto', '-lssl'],
)

setup(name='Python Maestro Package',
      version='1.0',
      description='Python extension giving access to maestro functionnality',
      ext_modules=[pymaestro_module]
)
