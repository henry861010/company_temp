#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

// --- FUNCTION 1: WRITE NODES ---
static PyObject* method_write_nodes(PyObject* self, PyObject* args) {
    const char* filename;
    const char* mode; // "w" for overwrite, "a" for append
    Py_buffer nodes_view;

    if (!PyArg_ParseTuple(args, "ssy*", &filename, &mode, &nodes_view)) {
        return NULL;
    }

    double* nodes = (double*)nodes_view.buf;
    int n_nodes = nodes_view.len / (3 * sizeof(double));

    FILE *f = fopen(filename, mode);
    if (!f) {
        PyBuffer_Release(&nodes_view);
        return PyErr_SetFromErrno(PyExc_IOError);
    }

    for (int i = 0; i < n_nodes; i++) {
        fprintf(f, "NODE %d %.6f %.6f %.6f\n", i, nodes[i*3], nodes[i*3+1], nodes[i*3+2]);
    }

    fclose(f);
    PyBuffer_Release(&nodes_view);
    Py_RETURN_NONE;
}

// --- FUNCTION 2: WRITE ELEMENTS ---
static PyObject* method_write_elements(PyObject* self, PyObject* args) {
    const char* filename;
    const char* mode;
    Py_buffer elems_view;
    int p1, p2, p3;

    if (!PyArg_ParseTuple(args, "ssy*iii", &filename, &mode, &elems_view, &p1, &p2, &p3)) {
        return NULL;
    }

    long* elems = (long*)elems_view.buf;
    int n_elems = elems_view.len / (8 * sizeof(long));

    FILE *f = fopen(filename, mode);
    if (!f) {
        PyBuffer_Release(&elems_view);
        return PyErr_SetFromErrno(PyExc_IOError);
    }

    for (int i = 0; i < n_elems; i++) {
        fprintf(f, "%d %d %d %d", i, p1, p2, p3);
        for (int j = 0; j < 8; j++) {
            fprintf(f, "%10ld", elems[i*8 + j]);
        }
        fprintf(f, "\n");
    }

    fclose(f);
    PyBuffer_Release(&elems_view);
    Py_RETURN_NONE;
}

// --- MODULE REGISTRATION ---

static PyMethodDef FastIOMethods[] = {
    {"write_nodes", method_write_nodes, METH_VARARGS, "Writes only nodes."},
    {"write_elements", method_write_elements, METH_VARARGS, "Writes only elements."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef fastiomodule = {
    PyModuleDef_HEAD_INIT, "fastio", NULL, -1, FastIOMethods
};

PyMODINIT_FUNC PyInit_fastio(void) {
    return PyModule_Create(&fastiomodule);
}