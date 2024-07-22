#ifndef MYMEMORY_H
#define MYMEMORY_H

#include <Python.h>

#define Pool_Size (4 * 1024)
#define AllocTabel_Size (Pool_Size / 8)

void MM_MemPoolInit();
void* MM_Alloc(size_t s);
uint8_t MM_Free(void* Block);
uint8_t MM_Set(void* Block, int val, size_t s);
int MM_Occupation();

#endif // MYMEMORY_H
