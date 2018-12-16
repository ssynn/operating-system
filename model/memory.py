import re
import numpy as np


class Memory():
    def __init__(self):
        '''
        第一个内存块作为位视图
        只使用前四个字节
        '''
        self.memory = [0 for i in range(512)]
        self.memory[0] = 1
        self.PCB = []

    # TODO
    def allocate(self, orders: str) -> int:
        '''
        外部调用
        查看空闲块总数是否够用
        如果够用，先分配一块用来存放页表
        页表占一个物理块，最多可以申请16个物理块
        一个物理块可以存储4条指令
        返回页表分配到的地址
        '''
        if not Memory.order_check(orders):
            return False
        needed_num = int(np.ceil(len(orders) / 16)+1)
        table = self.get_table()

    def _to_one(self, address: int) -> bool:
        '''
        传入块表的地址
        把位视图图对应位置置1
        '''
        if address < 0 or address > 31:
            return False
        byte_num = address / 8
        bit_num = address % 8
        self.memory[byte_num] &= (1 << bit_num)

    # TODO
    def delete(self, address: int) -> bool:
        '''
        传入页表地址
        外部调用
        先把页表内的页内存释放
        最后释放页表的内存
        '''
        if address < 0 or address > 31:
            return False

    def _to_zero(self, address: int) -> bool:
        '''
        传入块表的地址
        把位视图对应位置置0
        '''
        if address < 0 or address > 31:
            return False
        byte_num = address / 8
        bit_num = address % 8
        bin_num = list(Memory.format_num(self.memory[byte_num]))
        bin_num[bit_num] = 0
        self.memory[byte_num] = int(''.join(bin_num), base=2)

    def get_table(self) -> list:
        '''
        返回位视图，长度为32的列表
        '''
        table = self.memory[:4]
        ans = []
        for i in range(4):
            temp = list(Memory.format_num(table[i]))
            temp.reverse()
            ans += temp
        ans = [int(i) for i in ans]
        return ans

    # TODO
    def get_info(self, address: int, inner_address: int, length: int = 1) -> list:
        '''
        传入块地址，块内地址，读取长度
        返回读取到的列表
        如果读取失败则返回None
        '''
        self.format_num
        pass

    @staticmethod
    def format_num(num: int) -> str:
        return bin(num)[2:].zfill(8)

    @staticmethod
    def order_check(orders: str) -> bool:
        """
        首先每一条指令长度只能为4
        初始化指令
        操作指令的第一个字符必须之前使用初始化指令初始化过
        申请设备指令开头指令为ABC选一
        末尾必须为end.
        """
        patterns = [r'[a-zA-Z]=\d', r'[a-zA-Z][++|--]', r'[ABC]\d\d', r'end.']
        exists_val = []
        orders = orders.split(';')
        for index, order in enumerate(orders):
            if re.fullmatch(patterns[0], order):
                exists_val.append(order[0])
                continue
            if re.fullmatch(patterns[1], order) and order[0] in exists_val:
                continue
            if re.fullmatch(patterns[2], order):
                continue
            if index == len(orders) - 1 and order == 'end.':
                continue
            return False
        return True

    @staticmethod
    def order_split(order: str):
        ans = []
        i = 0
        while i < len(order):
            ans.append(order[i:i+16])
            i += 16
        return ans


if __name__ == "__main__":
    # for i in range(256):
    #     print(Memory.format_num(i), i, int(Memory.format_num(i), base=2))
    temp = Memory()
    print(temp.get_table())
