from distutils.core import setup, Extension

pymaestro_module = Extension(
    'pymaestro',
    sources=[
        'pymaestro.c',
        '../src/SeqNodeCensus.c',
        '../src/FlowVisitor.c',
        '../src/ResourceVisitor.c',
        '../src/SeqDatesUtil.c',
        '../src/SeqLoopsUtil.c',
        '../src/SeqListNode.c',
        '../src/SeqDepends.c',
        '../src/SeqNameValues.c',
        '../src/SeqNode.c',
        '../src/SeqUtil.c',
        '../src/XmlUtils.c',
        '../src/nodeinfo.c',
        '../src/l2d2_commun.c',
        '../src/tictac.c',
        '../src/SeqUtilServer.c',
        '../src/l2d2_roxml-internal.c',
        '../src/maestro.c',
        '../src/ocmjinfo.c',
        '../src/QueryServer.c',
        '../src/l2d2_roxml-parse-engine.c',
        '../src/getopt_long.c',
        '../src/l2d2_roxml.c',
        '../src/runcontrollib.c',
        '../src/l2d2_Util.c',
        '../src/l2d2_socket.c',
        '../src/logreader.c',
        '../src/nodelogger.c',
        '../src/tsvinfo.c',
        '../src/expcatchup.c',
        '../src/l2d2_lists.c',
    ],
    include_dirs=[
        '/usr/local/Cellar/libxml2/2.9.9_2/include/libxml2',
        '/usr/local/Cellar/include',
        '/usr/local/Cellar/openssl//1.0.2q/include/',
        '../src'
    ],
    library_dirs=[
        '/usr/local/Cellar/libxml2/2.9.9_2/lib',
        '/usr/local/Cellar/openssl/1.0.2q/lib/',
        '../src'
    ],
    libraries=['crypto', 'xml2'],
    extra_compile_args=["-Wall", "-Wextra" '-lc', '-lcrypto', '-lssl', '-Wno-unused-function', '-Wno-pointer-sign', '-Wno-unused-label'],
)

setup(name='Python Maestro Package',
      version='1.0',
      description='Python extension giving access to maestro functionnality',
      ext_modules=[pymaestro_module]
)
