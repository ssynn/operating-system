import re
import math


class Memory():
    def __init__(self):
        '''
        第一个内存块作为位视图
        只使用前四个字节
        '''
        self.memory = [0 for i in range(512)]
        self.memory[0] = 1
        self.PCB = []

    def allocate(self, orders: str) -> tuple:
        '''
        外部调用
        查看空闲块总数是否够用
        如果够用，先分配一块用来存放页表
        页表占一个物理块，最多可以申请16个物理块
        一个物理块可以存储4条指令
        返回页表分配到的地址
        -1代表申请失败
        '''
        if not Memory.order_check(orders):
            return (-1, -1)
        table = self.get_table()
        empty_block_num = table.count(0)

        # 计算内存是否有足够的剩余空间
        needed_num = int(math.ceil(len(orders) / 16)+1)
        if empty_block_num < needed_num or needed_num > 16:
            return (-1, -1)

        allocated_block = []
        for index in range(len(table)):
            if table[index] == 0:
                allocated_block.append(index)
                self._to_one(index)
            if len(allocated_block) == needed_num:
                break

        # 把分配到的物理块写入页表
        page = allocated_block[0]
        for index, block in enumerate(allocated_block[1:]):
            self.write(page, index, [block])

        # 把命令写入物理块
        splited_orders = self.order_split(orders)
        for order, block in zip(splited_orders, allocated_block[1:]):
            self.write(block, 0, list(order))
        return (page, needed_num-1)

    def _to_one(self, address: int) -> bool:
        '''
        传入块表的地址
        把位视图图对应位置置1
        '''
        if address < 0 or address > 31:
            return False
        byte_num = int(address / 8)
        bit_num = address % 8
        self.memory[byte_num] |= (1 << bit_num)
        # print(self.format_num(self.memory[byte_num]))

    def delete(self, address: int) -> bool:
        '''
        传入页表地址
        外部调用
        先把页表内的页内存释放
        最后释放页表的内存
        '''
        if address < 0 or address > 31:
            return False
        page = self.read(address, 0, 16)
        for block in page:
            if block == 0:
                break
            self._to_zero(block)
        self._to_zero(address)
        return True

    def _to_zero(self, address: int) -> bool:
        '''
        传入块表的地址
        把位视图对应位置置0
        '''
        # print(address)
        byte_num = int(address / 8)
        bit_num = address % 8
        bin_num = list(Memory.format_num(self.memory[byte_num]))
        bin_num[7-bit_num] = '0'
        # print(bin_num)
        self.memory[byte_num] = int(''.join(bin_num), base=2)

        # 把物理块内的内容也置0
        self.memory[address*16: address*16+16] = [0]*16
        return True

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

    def read(self, address: int, inner_address: int, length: int = 1) -> list:
        '''
        传入块地址，块内地址，读取长度
        返回读取到的列表
        如果读取失败则返回None
        '''
        # 块地址错误
        if address < 0 or address > 31:
            return None

        # 内地址越界
        if inner_address + length > 16:
            return None

        start = address*16+inner_address
        return self.memory[start: start+length]

    def write(self, address: int, inner_address: int, value: list) -> bool:
        '''
        传入块地址，块内地址，需要写入的信息
        '''
        # 块地址错误
        if address < 0 or address > 31:
            return False

        # 内地址越界
        if inner_address + len(value) > 16:
            return False

        start = address*16+inner_address
        self.memory[start: start+len(value)] = value
        return True

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
        patterns = [r'[a-zA-Z]=\d',
                    r'[a-zA-Z](\+\+|\-\-)', r'[ABC]\d\d', r'end.']
        exists_val = set()
        orders = orders.split(';')
        if orders[-1] != 'end.':
            return False
        # print(orders)
        for index, order in enumerate(orders):
            # print(order, exists_val)
            if re.fullmatch(patterns[0], order):
                exists_val.add(order[0])
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
    orders = ['A=2;A++;A++;A++;A--;A23;end.', 'A=2;A++;B++;A23;end.',
              'A=2;A++;A23;', '', 'A20;end.', 'A0', 'A', 'A++;', 'A=5', 'end.', 'A=2;end.']
    for i in orders:
        print(Memory.order_check(i))
    # temp = Memory()
    # print(temp.get_table())
    # page = []
    # for i in range(10):
    #     page.append(temp.allocate(orders[0]))
    # print('page', page)
    # print(temp.memory)
    # print('table', temp.get_table())
    # print('read', temp.read(1, 0, 16))
    # for p in page:
    #     print(temp.delete(p))
    # print(temp.memory)
    # print('table', temp.get_table())
