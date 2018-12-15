
class Memory():
    def __init__(self):
        '''
        第一个内存块作为位视图
        只使用前四个字节
        '''
        self.memory = [0 for i in range(512)]
        self.memory[0] = 1

    def allocate(self, orders: str) -> int:
        '''
        外部调用
        查看空闲块总数是否够用
        如果够用，先分配一块用来存放页表
        页表占一个物理块，最多可以申请16个物理块
        一个物理块可以存储4条指令
        返回分配到的地址
        '''
        pass

    def _to_one(self, address: int) -> bool:
        '''
        传入块表的地址
        把位视图图对应位置置1
        '''
        pass

    def delete(self, address: int) -> bool:
        '''
        传入页表地址
        外部调用
        先把页表内的页内存释放
        最后释放页表的内存
        '''
        pass

    def _to_zero(self, address: int) -> bool:
        '''
        传入块表的地址
        把位视图对应位置置0
        '''
        pass

    def get_table(self) -> list:
        '''
        返回位视图，长度为32的列表
        '''
        pass
    
    def get_info(self, address: int, inner_address: int, length: int) -> list:
        '''
        传入块地址，块内地址，读取长度
        返回读取到的列表
        如果读取失败则返回None
        '''
        pass
