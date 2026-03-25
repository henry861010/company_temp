pip install setuptools
cd FOLDE_OF_C_PROGRAM
python /Users/henry/Desktop/company_temp/write_c/setup.py  build_ext --inplace
run main.py



Every function in a Python C-extension must follow this exact template:
static PyObject* function_name(PyObject* self, PyObject* args)

self: Points to the module object (used for internal housekeeping).

args: This is a Python Tuple object that contains everything you sent from your Python script. If you sent a string, two arrays, and three integers, they are all packed inside this one args object.

2. The "Unpacking" Step

Because C cannot automatically "read" a Python Tuple object, we use PyArg_ParseTuple as the middleman.

Think of PyArg_ParseTuple as a decompressor. You give it the packed args and a "map" (the string "sy*y*iii"), and it manually extracts the data into the local variables you defined.