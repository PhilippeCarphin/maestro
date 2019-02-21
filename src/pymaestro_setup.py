from distutils.core import setup, Extension

pymaestro_module = Extension('pymaestro', sources=['pymaestro.c'])

setup(name='Python Maestro Package',
        version='1.0',
        description='Python extension giving access to maestro functionnality',
        ext_modules=[pymaestro_module]
)
