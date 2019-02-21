
#include <Python.h>

#if PY_MAJOR_VERSION >= 3

static PyObject *pymaestro_exported_func(PyObject* self, PyObject* args)
{
	Py_ssize_t argc = PyTuple_Size(args) + 1;

  // Arguments of the python function call arrive as a tuple of
  // PyObjects args.
  printf("I am a C function %s(), I received arguments : \n", __FUNCTION__);
	char *argv[argc];
   argv[0] = __func__;
	for(int i = 1; i < argc; ++i){
      PyObject *bytes = PyUnicode_AsEncodedString(PyTuple_GetItem(args, i-1), "UTF-8", "strict");
        argv[i] = PyBytes_AS_STRING(bytes);
        printf("argv[%d] = : %s\n", i, argv[i]);
	}

	// struct MyOpts *opts;
	// if(parse_args(argc, argv, &opts)){
	// 	return self;
	// }

	// if(my_main(opts)){
	// 	return self;
	// }
  printf(" * Some call to a C function *\n");

	return self;
}

struct module_state {
    PyObject *error;
};

#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

static PyObject *
error_out(PyObject *m) {
    (void) m;
    struct module_state *st = GETSTATE(m);
    PyErr_SetString(st->error, "something bad happened");
    return NULL;
}

static PyMethodDef myextension_methods[] = {
    {"error_out", (PyCFunction)error_out, METH_NOARGS, NULL},
    {"func_name", (PyCFunction)pymaestro_exported_func, METH_VARARGS, NULL},
    {NULL, NULL}
};

static int myextension_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int myextension_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "myextension",
        NULL,
        sizeof(struct module_state),
        myextension_methods,
        NULL,
        myextension_traverse,
        myextension_clear,
        NULL
};

#define INITERROR return NULL

// The name of this function must match the module name
PyMODINIT_FUNC
PyInit_pymaestro(void)
{
    PyObject *module = PyModule_Create(&moduledef);

    if (module == NULL)
        INITERROR;
    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("myextension.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

    return module;
}
#else
#warning "THIS SHOULD ONLY BE USED FOR PYTHON 3"
#endif
