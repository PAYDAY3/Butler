#include "mymemory.h"
#include <stdlib.h>
#include <string.h>

// MyMemory 对象定义
typedef struct {
    PyObject_HEAD
    int refcount;
    void *data;
    size_t size;
} MyMemory;

// MyMemory 对象的析构函数
static void mymemory_dealloc(MyMemory* self) {
    if (--self->refcount == 0) {
        free(self->data);
        Py_TYPE(self)->tp_free((PyObject*)self);
    }
}

// MyMemory 对象的构造函数
static PyObject* mymemory_new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
    MyMemory* self;
    self = (MyMemory*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->refcount = 1;
        self->data = NULL;
        self->size = 0;
    }
    return (PyObject*)self;
}

// MyMemory 对象的初始化方法
static int mymemory_init(MyMemory* self, PyObject* args, PyObject* kwds) {
    int size;
    if (!PyArg_ParseTuple(args, "i", &size)) {
        return -1;
    }
    if (size <= 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid size");
        return -1;
    }
    self->data = malloc(size);
    if (!self->data) {
        PyErr_SetString(PyExc_MemoryError, "Memory allocation failed");
        return -1;
    }
    self->size = size;
    return 0;
}

// 获取数据指针的方法
static PyObject* mymemory_get_data(PyObject* self, PyObject* args) {
    MyMemory* memory;
    if (!PyArg_ParseTuple(args, "O!", &MyMemoryType, &memory)) {
        return NULL;
    }
    if (memory->refcount == 0) {
        PyErr_SetString(PyExc_RuntimeError, "Memory block is already freed");
        return NULL;
    }
    return PyLong_FromVoidPtr(memory->data);
}

// 获取内存大小的方法
static PyObject* mymemory_get_size(PyObject* self, PyObject* args) {
    MyMemory* memory;
    if (!PyArg_ParseTuple(args, "O!", &MyMemoryType, &memory)) {
        return NULL;
    }
    if (memory->refcount == 0) {
        PyErr_SetString(PyExc_RuntimeError, "Memory block is already freed");
        return NULL;
    }
    return PyLong_FromSize_t(memory->size);
}

// 增加引用计数的方法
static PyObject* mymemory_retain(PyObject* self, PyObject* args) {
    MyMemory* memory;
    if (!PyArg_ParseTuple(args, "O!", &MyMemoryType, &memory)) {
        return NULL;
    }
    if (memory->refcount == 0) {
        PyErr_SetString(PyExc_RuntimeError, "Memory block is already freed");
        return NULL;
    }
    Py_INCREF(memory);
    return (PyObject*)memory;
}

// 减少引用计数的方法
static PyObject* mymemory_release(PyObject* self, PyObject* args) {
    MyMemory* memory;
    if (!PyArg_ParseTuple(args, "O!", &MyMemoryType, &memory)) {
        return NULL;
    }
    if (memory->refcount == 0) {
        PyErr_SetString(PyExc_RuntimeError, "Memory block is already freed");
        return NULL;
    }
    Py_DECREF(memory);
    Py_RETURN_NONE;
}

// MyMemory 对象的方法表
static PyMethodDef MyMemoryMethods[] = {
    {"retain", (PyCFunction)mymemory_retain, METH_VARARGS, "增加引用计数"},
    {"release", (PyCFunction)mymemory_release, METH_VARARGS, "减少引用计数"},
    {"get_data", (PyCFunction)mymemory_get_data, METH_VARARGS, "获取数据指针"},
    {"get_size", (PyCFunction)mymemory_get_size, METH_VARARGS, "获取内存大小"},
    {NULL, NULL, 0, NULL}
};

// MyMemory 对象类型定义
static PyTypeObject MyMemoryType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "mymemory.MyMemory",
    .tp_doc = "MyMemory 对象",
    .tp_basicsize = sizeof(MyMemory),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)mymemory_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = mymemory_new,
    .tp_init = (initproc)mymemory_init,
    .tp_methods = MyMemoryMethods,
};

// 模块方法定义
static PyMethodDef MyMemoryModuleMethods[] = {
    {"MemPoolInit", py_MM_MemPoolInit, METH_NOARGS, "Initialize memory pool"},
    {"Alloc", py_MM_Alloc, METH_VARARGS, "Allocate memory"},
    {"Free", py_MM_Free, METH_VARARGS, "Free memory"},
    {"Set", py_MM_Set, METH_VARARGS, "Set memory value"},
    {"Occupation", py_MM_Occupation, METH_NOARGS, "Get memory occupation"},
    {NULL, NULL, 0, NULL}
};

// 模块定义
static struct PyModuleDef mymemorymodule = {
    PyModuleDef_HEAD_INIT,
    "mymemory",
    "Memory management module",
    -1,
    MyMemoryModuleMethods
};

// 模块初始化函数
PyMODINIT_FUNC PyInit_mymemory(void) {
    PyObject* module;
    if (PyType_Ready(&MyMemoryType) < 0) {
        return NULL;
    }
    module = PyModule_Create(&mymemorymodule);
    if (module == NULL) {
        return NULL;
    }
    Py_INCREF(&MyMemoryType);
    if (PyModule_AddObject(module, "MyMemory", (PyObject*)&MyMemoryType) < 0) {
        Py_DECREF(&MyMemoryType);
        Py_DECREF(module);
        return NULL;
    }
    return module;
}
