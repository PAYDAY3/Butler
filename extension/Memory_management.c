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

// 写入内存的方法
static PyObject* mymemory_write(PyObject* self, PyObject* args) {
    MyMemory* memory;
    const char* data;
    Py_ssize_t length;
    Py_ssize_t offset;

    if (!PyArg_ParseTuple(args, "O!s#n", &MyMemoryType, &memory, &data, &length, &offset)) {
        return NULL;
    }

    if (offset < 0 || (size_t)offset + (size_t)length > memory->size) {
        PyErr_SetString(PyExc_IndexError, "Offset and length out of bounds");
        return NULL;
    }

    memcpy((char*)memory->data + offset, data, length);
    Py_RETURN_NONE;
}

// 读取内存的方法
static PyObject* mymemory_read(PyObject* self, PyObject* args) {
    MyMemory* memory;
    Py_ssize_t length;
    Py_ssize_t offset;

    if (!PyArg_ParseTuple(args, "O!nn", &MyMemoryType, &memory, &offset, &length)) {
        return NULL;
    }

    if (offset < 0 || (size_t)offset + (size_t)length > memory->size) {
        PyErr_SetString(PyExc_IndexError, "Offset and length out of bounds");
        return NULL;
    }

    return PyBytes_FromStringAndSize((char*)memory->data + offset, length);
}

// 复制内存的方法
static PyObject* mymemory_copy(PyObject* self, PyObject* args) {
    MyMemory* src_memory;
    MyMemory* dest_memory;
    Py_ssize_t src_offset;
    Py_ssize_t dest_offset;
    Py_ssize_t length;

    if (!PyArg_ParseTuple(args, "O!nO!nn", &MyMemoryType, &src_memory, &src_offset, &MyMemoryType, &dest_memory, &dest_offset, &length)) {
        return NULL;
    }

    if (src_offset < 0 || dest_offset < 0 || (size_t)src_offset + (size_t)length > src_memory->size || (size_t)dest_offset + (size_t)length > dest_memory->size) {
        PyErr_SetString(PyExc_IndexError, "Offset and length out of bounds");
        return NULL;
    }

    memcpy((char*)dest_memory->data + dest_offset, (char*)src_memory->data + src_offset, length);
    Py_RETURN_NONE;
}

// 移动内存的方法
static PyObject* mymemory_move(PyObject* self, PyObject* args) {
    MyMemory* src_memory;
    MyMemory* dest_memory;
    Py_ssize_t src_offset;
    Py_ssize_t dest_offset;
    Py_ssize_t length;

    if (!PyArg_ParseTuple(args, "O!nO!nn", &MyMemoryType, &src_memory, &src_offset, &MyMemoryType, &dest_memory, &dest_offset, &length)) {
        return NULL;
    }

    if (src_offset < 0 || dest_offset < 0 || (size_t)src_offset + (size_t)length > src_memory->size || (size_t)dest_offset + (size_t)length > dest_memory->size) {
        PyErr_SetString(PyExc_IndexError, "Offset and length out of bounds");
        return NULL;
    }

    memmove((char*)dest_memory->data + dest_offset, (char*)src_memory->data + src_offset, length);
    Py_RETURN_NONE;
}

// 调整内存大小的方法
static PyObject* mymemory_resize(PyObject* self, PyObject* args) {
    MyMemory* memory;
    Py_ssize_t new_size;

    if (!PyArg_ParseTuple(args, "O!n", &MyMemoryType, &memory, &new_size)) {
        return NULL;
    }

    if (new_size <= 0) {
        PyErr_SetString(PyExc_ValueError, "New size must be positive");
        return NULL;
    }

    void* new_data = MM_Alloc(new_size);
    if (!new_data) {
        PyErr_SetString(PyExc_MemoryError, "Memory reallocation failed");
        return NULL;
    }

    memcpy(new_data, memory->data, (new_size < memory->size) ? new_size : memory->size);
    MM_Free(memory->data);

    memory->data = new_data;
    memory->size = new_size;
    Py_RETURN_NONE;
}

// 填充内存的方法
static PyObject* mymemory_fill(PyObject* self, PyObject* args) {
    MyMemory* memory;
    int value;
    Py_ssize_t offset;
    Py_ssize_t length;

    if (!PyArg_ParseTuple(args, "O!inn", &MyMemoryType, &memory, &value, &offset, &length)) {
        return NULL;
    }

    if (offset < 0 || (size_t)offset + (size_t)length > memory->size) {
        PyErr_SetString(PyExc_IndexError, "Offset and length out of bounds");
        return NULL;
    }

    memset((char*)memory->data + offset, value, length);
    Py_RETURN_NONE;
}

// 比较内存的方法
static PyObject* mymemory_compare(PyObject* self, PyObject* args) {
    MyMemory* memory1;
    MyMemory* memory2;
    Py_ssize_t offset1;
    Py_ssize_t offset2;
    Py_ssize_t length;

    if (!PyArg_ParseTuple(args, "O!nO!nn", &MyMemoryType, &memory1, &offset1, &MyMemoryType, &memory2, &offset2, &length)) {
        return NULL;
    }

    if (offset1 < 0 || offset2 < 0 || (size_t)offset1 + (size_t)length > memory1->size || (size_t)offset2 + (size_t)length > memory2->size) {
        PyErr_SetString(PyExc_IndexError, "Offset and length out of bounds");
        return NULL;
    }

    int result = memcmp((char*)memory1->data + offset1, (char*)memory2->data + offset2, length);
    return PyLong_FromLong(result);
}


// MyMemory 对象的方法表
static PyMethodDef MyMemoryMethods[] = {
    {"retain", (PyCFunction)mymemory_retain, METH_VARARGS, "增加引用计数"},
    {"release", (PyCFunction)mymemory_release, METH_VARARGS, "减少引用计数"},
    {"get_data", (PyCFunction)mymemory_get_data, METH_VARARGS, "获取数据指针"},
    {"get_size", (PyCFunction)mymemory_get_size, METH_VARARGS, "获取内存大小"},
    {"write", (PyCFunction)mymemory_write, METH_VARARGS, "写入内存"},
    {"read", (PyCFunction)mymemory_read, METH_VARARGS, "读取内存"},
    {"copy", (PyCFunction)mymemory_copy, METH_VARARGS, "复制内存"},
    {"move", (PyCFunction)mymemory_move, METH_VARARGS, "移动内存"},
    {"resize", (PyCFunction)mymemory_resize, METH_VARARGS, "调整内存大小"},
    {"fill", (PyCFunction)mymemory_fill, METH_VARARGS, "填充内存"},
    {"compare", (PyCFunction)mymemory_compare, METH_VARARGS, "比较内存"},
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
