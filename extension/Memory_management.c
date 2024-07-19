#include <Python.h>
#include <stdlib.h>
#include <string.h>

// 定义 MyMemory 结构体，用于封装内存块
typedef struct {
    PyObject_HEAD  // Python 对象头
    int refcount;   // 引用计数
    void* data;     // 指向分配内存的指针
    size_t size;    // 分配内存的大小
} MyMemory;

// MyMemory 对象的析构函数
static void mymemory_dealloc(MyMemory* self) {
    // 如果引用计数为 0，释放内存
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
        // 初始化引用计数、数据指针和大小
        self->refcount = 1;
        self->data = NULL;
        self->size = 0;
    }
    return (PyObject*)self;
}

// MyMemory 对象的初始化方法
static int mymemory_init(MyMemory* self, PyObject* args, PyObject* kwds) {
    int size;
    // 解析参数，获取分配内存的大小
    if (!PyArg_ParseTuple(args, "i", &size)) {
        return -1;
    }
    // 检查大小是否有效
    if (size <= 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid size");
        return -1;
    }
    // 分配内存
    self->data = malloc(size);
    if (!self->data) {
        PyErr_SetString(PyExc_MemoryError, "Memory allocation failed");
        return -1;
    }
    // 设置内存大小
    self->size = size;
    return 0;
}

// 获取数据指针的方法
static PyObject* mymemory_get_data(PyObject* self, PyObject* args) {
    MyMemory* memory;
    // 解析参数，获取 MyMemory 对象
    if (!PyArg_ParseTuple(args, "O!", &MyMemoryType, &memory)) {
        return NULL;
    }
    // 检查引用计数是否为 0
    if (memory->refcount == 0) {
        PyErr_SetString(PyExc_RuntimeError, "Memory block is already freed");
        return NULL;
    }
    // 返回数据指针
    return PyLong_FromVoidPtr(memory->data);
}

// 获取内存大小的方法
static PyObject* mymemory_get_size(PyObject* self, PyObject* args) {
    MyMemory* memory;
    // 解析参数，获取 MyMemory 对象
    if (!PyArg_ParseTuple(args, "O!", &MyMemoryType, &memory)) {
        return NULL;
    }
    // 检查引用计数是否为 0
    if (memory->refcount == 0) {
        PyErr_SetString(PyExc_RuntimeError, "Memory block is already freed");
        return NULL;
    }
    // 返回内存大小
    return PyLong_FromSize_t(memory->size);
}

// 增加引用计数的方法
static PyObject* mymemory_retain(PyObject* self, PyObject* args) {
    MyMemory* memory;
    // 解析参数，获取 MyMemory 对象
    if (!PyArg_ParseTuple(args, "O!", &MyMemoryType, &memory)) {
        return NULL;
    }
    // 检查引用计数是否为 0
    if (memory->refcount == 0) {
        PyErr_SetString(PyExc_RuntimeError, "Memory block is already freed");
        return NULL;
    }
    // 增加引用计数
    Py_INCREF(memory);
    return (PyObject*)memory;
}

// 减少引用计数的方法
static PyObject* mymemory_release(PyObject* self, PyObject* args) {
    MyMemory* memory;
    // 解析参数，获取 MyMemory 对象
    if (!PyArg_ParseTuple(args, "O!", &MyMemoryType, &memory)) {
        return NULL;
    }
    // 检查引用计数是否为 0
    if (memory->refcount == 0) {
        PyErr_SetString(PyExc_RuntimeError, "Memory block is already freed");
        return NULL;
    }
    // 减少引用计数
    Py_DECREF(memory);
    Py_RETURN_NONE;
}

// MyMemory 对象的方法表
static PyMethodDef MyMemoryMethods[] = {
    // 增加引用计数的方法
    {"retain", (PyCFunction)mymemory_retain, METH_VARARGS, "增加引用计数"},
    // 减少引用计数的方法
    {"release", (PyCFunction)mymemory_release, METH_VARARGS, "减少引用计数"},
    // 获取数据指针的方法
    {"get_data", (PyCFunction)mymemory_get_data, METH_VARARGS, "获取数据指针"},
    // 获取内存大小的方法
    {"get_size", (PyCFunction)mymemory_get_size, METH_VARARGS, "获取内存大小"},
    {NULL, NULL, 0, NULL}  // 方法表结束标志
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

// 模块定义
static struct PyModuleDef mymemorymodule = {
    PyModuleDef_HEAD_INIT,
    "mymemory",
    "MyMemory 模块",
    -1,
    MyMemoryMethods
};

// 模块初始化函数
PyMODINIT_FUNC PyInit_mymemory(void) {
    PyObject* module;
    // 初始化 MyMemory 类型
    if (PyType_Ready(&MyMemoryType) < 0) {
        return NULL;
    }
    // 创建模块对象
    module = PyModule_Create(&mymemorymodule);
    if (module == NULL) {
        return NULL;
    }
    // 将 MyMemory 类型添加到模块
    Py_INCREF(&MyMemoryType);
    if (PyModule_AddObject(module, "MyMemory", (PyObject*)&MyMemoryType) < 0) {
        Py_DECREF(&MyMemoryType);
        Py_DECREF(module);
        return NULL;
    }
    // 返回模块对象
    return module;
}
