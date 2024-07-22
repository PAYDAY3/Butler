#include "mymemory.h"
#include <stdint.h>
#include <stdio.h>

static uint8_t memPool[Pool_Size];
static uint8_t memAllocTabel[AllocTabel_Size];

void MM_MemPoolInit()
{
    for (int i = 0; i < Pool_Size; i++)
    {
        memPool[i] = 0;
        if(memPool[i])
            memAllocTabel[i / 8] = memAllocTabel[i / 8] |= (1 << i % 8);
        else
            memAllocTabel[i / 8] = memAllocTabel[i / 8] &= (~(1 << i % 8));
    }
}

static int16_t MM_SpaceSearch(size_t s)
{
    size_t spaceSize = 0;
    for (int i = 0; i < Pool_Size; i++)
    {
        uint8_t tmp = memAllocTabel[i / 8];
        if (!(tmp & (0x80 >> (i % 8))))
            spaceSize++;
        else
            spaceSize = 0;
        if (spaceSize == s + 2)
        {
            return (int16_t)(i - s);
        }
    }
    return -1;
}

void* MM_Alloc(size_t s)
{
    int spaceIndex = MM_SpaceSearch(s);
    if (spaceIndex == -1)
    {
        return NULL;
    }
    for (size_t i = spaceIndex; i < spaceIndex + s; i++)
    {
        memAllocTabel[i / 8] = memAllocTabel[i / 8] |= (0x80 >> i % 8);
    }
    return &memPool[spaceIndex];
}

uint8_t MM_Free(void* Block)
{
    if (Block == NULL)
    {
        return 0;
    }
    uint8_t* poolP = memPool;
    uint16_t blockIndex = (uint16_t)((uint8_t*)Block - poolP);
    uint16_t pDev = blockIndex;
    while ((memAllocTabel[pDev / 8] & (0x80 >> (pDev % 8))))
    {
        memAllocTabel[pDev / 8] = memAllocTabel[pDev / 8] &= (~(0x80 >> pDev % 8));
        pDev++;
    }
    if(!(memAllocTabel[blockIndex / 8] & (0x80 >> (blockIndex % 8))))
        return 1;
    else
        return 0;
}

uint8_t MM_Set(void *Block, int val, size_t s)
{
    uint8_t *pBlock = (uint8_t*)Block;
    size_t valBlock = (size_t)Block;
    if(pBlock >= &memPool[0] && pBlock <= &memPool[Pool_Size-1])
    {
        size_t blockIndex = valBlock - (size_t)memPool;
        for(size_t i = blockIndex; i < blockIndex + s; i++)
            memPool[i] = val;
    }
    else
        return 0;
    return 1;
}

int MM_Occupation()
{
    int count = 0;
    for (int i = 0; i < Pool_Size; i++)
    {
        uint8_t tmp = memAllocTabel[i / 8];
        if ((tmp & (0x80 >> (i % 8))))
            count++;
    }
    return count;
}
