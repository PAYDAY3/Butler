#include <pypy/include/Python.h>
#include <stdlib.h>
#include <stdio.h>

// PyBox 结构定义
typedef struct {
    PyObject* main_module;
    PyObject* sys_module;
    PyObject* globals;
} PyBox;

// PyBox 初始化函数
PyBox* pybox_init() {
    PyBox* box = malloc(sizeof(PyBox));

    Py_Initialize();
    box->main_module = PyImport_AddModule("__main__");
    box->sys_module = PyImport_AddModule("sys");
    box->globals = PyModule_GetDict(box->main_module);
    
    // 添加包含Python文件的文件夹到Python模块搜索路径
    PyObject* sys_path = PyDict_GetItemString(box->globals, "path");
    PyList_Append(sys_path, PyUnicode_FromString("./modules"));

    return box;
}

// PyBox 执行 Python 文件函数
int pybox_execute_file(PyBox* box, const char* filename) {
    FILE* fp = fopen(filename, "r");
    if (fp == NULL) {
        fprintf(stderr, "Cannot open file: %s\n", filename);
        return -1;
    }

    PyObject* result = PyRun_FileEx(fp, filename, Py_file_input, box->globals, box->globals, 1);
    if (result == NULL) {
        PyErr_Print();
        fclose(fp);
        return -1;
    }

    Py_DECREF(result);
    fclose(fp);
    return 0;
}

// PyBox 销毁函数
void pybox_destroy(PyBox* box) {
    Py_Finalize();
    free(box);
}

// 主函数
int main() {
    PyBox* box = pybox_init(); // 创建一个盒子

    // 执行位于'modules'文件夹中的文件中的Python代码
    pybox_execute_file(box, "./modules/file1.py");
    pybox_execute_file(box, "./modules/file2.py");

    pybox_destroy(box); // 清理箱子

    return 0;
}

// gcc -I/path/to/pypy3/include -L/path/to/pypy3/lib -o myprogram myprogram.c -lpypy3-c
