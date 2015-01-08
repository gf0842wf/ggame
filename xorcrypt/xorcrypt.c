#include <Python.h>
#include <stdio.h>

static PyObject* xor_crypt(PyObject* self, PyObject* args)
{
    char* s;
    unsigned int key = 0;
    unsigned int M1 = 0;
    unsigned int IA1 = 0;
    unsigned int IC1 = 0;
    unsigned int size;
     
    PyObject* v;
    char *p;
    unsigned int i = 0;
    unsigned char c;
     
    // 解析参数 s#表示字符串和它的长度, |后的表示可选参数, I表示unsigned int
    if (!PyArg_ParseTuple(args, "s#|IIII", &s, &size, &key, &M1, &IA1, &IC1))
        return NULL;
     
    if (key == 0)
        key = 1;
    if (M1 == 0)
        M1 = 1 << 19;
    if (IA1 == 0)
        IA1 = 2 << 20;
    if (IC1 == 0)
        IC1 = 3<< 21;
     
    // v是python的空字符串, 长度为size
    v = PyString_FromStringAndSize((char*)NULL, size);
    if (v == NULL)
        return NULL;
     
    // p是把python的字符串v转换为c的字符串, 对p进行操作也会影响v
    p = PyString_AS_STRING(v);
    for (i = 0; i < size; i++) {
        c = (unsigned char)s[i];
        key = IA1 * (key % M1) + IC1;
        *p = c ^ (unsigned char)((key >> 20)&0xff);
		p++;
    }
    return v;
}

// 方法列表, 要传到初始化函数里
static PyMethodDef xorcrypt_methods[] = {
    // 对应python的模块名.方法名 | 对应的c函数 | METH_VARARGS用来告诉python, crypt是用c实现的 | 函数说明
 	{"encrypt", (PyCFunction)xor_crypt, METH_VARARGS, PyDoc_STR("encrypt(s, key, M1, IA1, IC1) -> encrypt the string.")},
    {"decrypt", (PyCFunction)xor_crypt, METH_VARARGS, PyDoc_STR("decrypt(s, key, M1, IA1, IC1) -> decrypt the string.")},
    {"crypt", (PyCFunction)xor_crypt, METH_VARARGS, PyDoc_STR("crypt(s, key, M1, IA1, IC1) -> encrypt/decrypt the string.")},
    {NULL, NULL}  // sentinel
};

PyDoc_STRVAR(module_doc, "xor encrypt/decrypt module.");

/* 当初始化模块时, 这个函数自动被调用, 函数名要固定为 <init+模块名> */
PyMODINIT_FUNC initxorcrypt(void)
{
    PyObject *m;
 
    m = Py_InitModule3("xorcrypt", xorcrypt_methods, module_doc);
 
    if (m == NULL)
        return;
 
    PyModule_AddStringConstant(m, "__version__", "0.1.0");
}