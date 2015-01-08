# 异或加密

Usage
--
    import xorcrypt
     
    print xorcrypt.encrypt("abc", 2)
    # 'kde'
    print xorcrypt.decrypt("kde", 2)
    # 'abc'
    
    
API
--
    encrypt(s, key, M1, IA1, IC1)
    s => str
    M1, IA1, IC1 => uint32, 加密因子: 数据传输两端协商,固定
    key => 加密key: 一般又服务器端发给客户端
    其实encrypt和decrypt是同一函数

c语言代码
--

	// XOR RSA 加密/解密算法 -- 加密解密为同一函数(xor_crypt)
	
	// M1 IA1 IC1 是加密因子,即公钥: 服务端和客户端协商好固定
	const unsigned int M1 = 1 << 19; 
	const unsigned int IA1 = 2 << 20;
	const unsigned int IC1 = 3 << 21;
	
	// key 为密钥: 由服务端传输给客户端
	void xor_crypt(unsigned char* buffer, unsigned int size, unsigned int key)
	{
	     
	    if (key == 0)
	        key = 1;
	     
	    int i = 0;
	    
	    for (i = 0; i < size; i++) {
	        key = IA1 * (key % M1) + IC1;
	        buffer[i] ^= (unsigned char)((key >> 20)&0xff);
	    }
	}