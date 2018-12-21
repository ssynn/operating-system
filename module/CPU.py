import memory
import copy
import device


class CPU():

    _DR = 0                          # 数据缓存寄存器保存变量名
    _EAX = 0                         # 累加器
    _PSW = [1, 0, 0]                 # [程序结束, 时钟中断, I/O中断]
    _IR = 'NOP'                      # 指令寄存器
    _PC = 0                          # 程序计数器

    def __init__(self, master):
        self.master = master
        self._running_time = 0
        self._timeslice = 5
        self._remaining_time = 5
        self._memory = memory.Memory()
        self._device = device.Device(self)
        self._PCB_id = [0]*10
        self._ready_queue = []
        self._block_queue = []
        self._result_queue = []
        self._need_wake = []
        self._running_process = None

    def run(self):
        self.execute()
        info = {
            'PID': self._running_process.id if self._running_process else 'None',
            'pages': self.get_locks(),
            'order': self._IR,
            'program': self.get_orders_all(),
            'tempRes': str(self._DR) + '=' + str(self._EAX) if self._DR else 'None',
            'time': self._running_time,
            'timeSlice': self._timeslice,
            'PSW': ''.join([str(i) for i in self._PSW]),
            'PC': str(self._PC),
            'ready': self._ready_queue,
            'block': self._block_queue,
            'memory': self._memory.get_table(),
            'device': self._device.get_status()
        }
        self._device.run()
        return info

    # 检查中断, 同时处理中断
    def check_interrupt(self):
        '''
        If（进程结束软中断）撤销进程；进程调度；
        If（输入输出完成）输入输出中断处理；
        If（时间片到）进程调度
        '''
        # 软中断, 如果没有进程从就绪队列取出则不关闭中断
        if self._PSW[0] == 1:
            if self._running_process:
                self.destroy(self._running_process)
            self._running_process = None
            if self._PSW[2] == 0:
                self.process_schedule()
            if self._running_process:
                self._PSW[0] = 0

        # io中断
        if self._PSW[1] == 1:
            if self._DR:
                self._running_process.device = 'A'
                # 成功申请到设备
                if self._device.request(self._running_process.id, self._DR, self._EAX):
                    self._running_process.cause = 2

                # 没有成功申请到设备
                else:
                    self._running_process.cause = 1

            for i in self._need_wake:
                self.wake(i)

            self._running_process = None
            if self._PSW[2] == 0:
                self.process_schedule()
            self._PSW[1] = 0

        # 时钟中断
        if self._PSW[2] == 1:
            self._remaining_time = self._timeslice
            self.process_schedule()
            self._PSW[2] = 0

    # 执行方法，此方法每秒会被调用一次
    def execute(self):
        '''
        L:检测有无中断，有进行处理
        根据pc取指令，若pc所指指令在主存，将指令放入IR寄存器；若不在主存，置中断，延时，goto L;
        执行IR指令；//解释执行课程设计中的指令
        pc++
        延时
        '''
        # 检查中断
        self.check_interrupt()

        # 取指令
        if self._running_process:
            order = self.page_access(
                self._running_process, int(self._PC/16), self._PC % 16, 4)
            self._IR = ''.join(order)
            self._PC += 4
        else:
            self._IR = 'NOP'

        # 执行指令
        self.interpreter()

        # 时间片用完设置时钟中断
        self._remaining_time -= 1
        if self._remaining_time == 0:
            self._PSW[2] = 1

        self._running_time += 1

    # 进程调度
    def process_schedule(self):
        '''
        将正在运行的进程保存在该进程对应进程控制块中
        从就绪队列中选择一个进程
        将这个进程中进程控制块中记录的各寄存器内容恢复到CPU各个寄存器内
        '''
        # 如果当前有正在运行的进程则需要把当前进程就绪
        if self._running_process is not None:
            self.save()
            self._ready_queue.append(self._running_process)
            self._running_process.status = 0
            self._running_process = None

        # 当前主机内没有进程
        if len(self._ready_queue) == 0:
            return

        # 从就绪队列出队
        self._running_process = self._ready_queue[0]
        self._ready_queue = self._ready_queue[1:]

        # 恢复现场
        self.load(self._running_process)
        self._running_process.status = 1
        self._running_process.cause = 0

    # 创建进程
    def create(self, orders: str) -> bool:
        '''
        传入程序
        创建FCB
        存入主存
        加入就绪队列
        '''
        if self._PCB_id.count(0) == 0:
            print('进程数已达10')
            return False

        # 创建FCB
        new_PCB = PCB()

        # 存入主存
        new_PCB.page_address, new_PCB.length = self._memory.allocate(orders)
        if new_PCB.page_address == -1:
            print('申请内存失败')
            return False

        # 创建进程标识符
        new_PCB.id = self._PCB_id.index(0)
        self._PCB_id[new_PCB.id] = 1

        # 记录创建时间
        new_PCB.start = self._running_time

        # 加入就绪队列
        self._ready_queue.append(new_PCB)
        return True

    # 撤销进程
    def destroy(self, pcb) -> bool:
        '''
        传入PCB
        释放内存
        删除PCB
        显示结果
        '''
        self._memory.delete(pcb.page_address)
        self._PCB_id[pcb.id] = 0
        pcb.end = self._running_time
        self._result_queue.append(pcb)
        # print("\nDESTROY", pcb)

    # 阻塞进程
    def block(self) -> bool:
        '''
        保存运行进程的CPU现场
        修改进程状态
        将进程加入对应的阻塞队列
        阻塞之后一定要调用进程调度函数
        '''
        self.save()
        self._running_process.status = 2
        self._running_process.cause = 1
        self._block_queue.append(self._running_process)
        self._running_process = None
        self.process_schedule()

    # 唤醒进程
    def wake(self, _id: int) -> bool:
        '''
        将进程由阻塞队列中摘下
        修改进程状态为就绪
        链入就绪队列，根据情况决定是否转向进程调度
        '''
        for p in self._block_queue:
            if p.id == _id:
                self._ready_queue.append(p)
                self._block_queue.remove(p)
                p.status = 0
                p.cause = 0
                return True
        return False

    # 通过页表访问内存
    def page_access(self, pcb, block_num: int, inner_address: int, length: int = 1):
        page = self._memory.read(pcb.page_address, 0, pcb.length)

        # 页表不存在
        if page is None:
            print('页表不存在')
            return None

        # 页号越界
        if block_num >= pcb.length:
            print('页号越界')
            return None

        # 块内访问越界
        if inner_address + length > 16:
            print('块内访问越界')
            return None
        return self._memory.read(page[block_num], inner_address, length)

    # 从内存中读取整个程序
    def get_orders_all(self):
        '''
        传入页表地址
        '''
        if self._running_process is None:
            return ''
        temp_pc = 0
        ans = ''
        order = ''
        while order != 'end.':
            order = ''.join(self.page_access(
                self._running_process,
                temp_pc//16,
                temp_pc % 16,
                4
            ))
            ans += order
            temp_pc += 4
        return ans

    # 保存CPU现场
    def save(self):
        self._running_process.DR = self._DR
        self._running_process.IR = self._IR
        self._running_process.PSW = copy.deepcopy(self._PSW)
        self._running_process.PC = self._PC
        self._running_process.EAX = self._EAX

    # 恢复CPU现场
    def load(self, pcb):
        self._DR = pcb.DR
        self._IR = pcb.IR
        self._PSW = copy.deepcopy(pcb.PSW)
        self._PC = pcb.PC
        self._EAX = pcb.EAX

    # 指令解释器
    def interpreter(self):
        # 赋值指令
        if self._IR[1] == '=':
            self._DR = self._IR[0]
            self._EAX = int(self._IR[2])
            self._running_process.varDict[self._DR] = self._EAX

        # 自增指令
        elif self._IR[1] == '+':
            self._DR = self._IR[0]
            self._EAX = self._running_process.varDict[self._DR]
            self._EAX += 1
            self._running_process.varDict[self._DR] = self._EAX

        # 自减指令
        elif self._IR[1] == '-':
            self._DR = self._IR[0]
            self._EAX = self._running_process.varDict[self._DR]
            self._EAX -= 1
            self._running_process.varDict[self._DR] = self._EAX

        # 结束指令
        elif self._IR == 'end.':
            self._PSW[0] = 1

        # 空指令
        elif self._IR == 'NOP':
            self._DR = None
            self._EAX = None

        # 申请设备指令
        else:
            self._DR = self._IR[0]
            self._EAX = int(self._IR[1:3])
            self._PSW[1] = 1

    def process_status(self):
        print(self)
        print(self._running_process)

    # 获取当前进程拥有的内存块
    def get_locks(self):
        if self._running_process is None:
            return []
        temp = self._running_process
        return self._memory.read(temp.page_address, 0, temp.length)

    def __str__(self):
        dr = 'DR ' + str(self._DR)
        ir = 'IR ' + str(self._IR)
        psw = 'PSW ' + str(self._PSW)
        pc = 'PC ' + str(self._PC)
        PCB_id = 'PCB_id ' + str(self._PCB_id)
        running_time = 'running_time ' + str(self._running_time)
        timeslice = 'timeslice ' + str(self._timeslice)
        # memory = 'memory ' + str(self._memory.memory)
        ready_queue = 'ready_queue ' + str(self._ready_queue)
        block_queue = 'block_queue ' + str(self._block_queue)
        return '\n'.join(['\nCPU', dr, ir, psw, pc, PCB_id, running_time, timeslice, ready_queue, block_queue])

    @property
    def timeslice(self):
        return self._timeslice

    @timeslice.setter
    def timeslice(self, length: int):
        if length >= 1:
            self._timeslice = length

    @property
    def running_time(self):
        return self._running_time


class PCB():
    def __init__(self):
        '''
        status:
        0 就绪
        1 运行
        2 阻塞
        cause:
        0 未阻塞
        1 未申请到IO设备阻塞
        2 占用IO设备阻塞
        '''
        self.status = 0
        self.cause = 0
        self.id = None
        self.page_address = None
        self.length = None
        self.EAX = 0
        self.DR = 0
        self.IR = None
        self.PSW = [0, 0, 0]
        self.PC = 0
        self.varDict = dict()
        self.device = None
        self.start = 0
        self.end = 0

    def __str__(self):
        eax = 'EAX ' + str(self.EAX)
        dr = 'DR ' + str(self.DR)
        ir = 'IR ' + str(self.IR)
        psw = 'PSW ' + str(self.PSW)
        pc = 'PC ' + str(self.PC)
        length = 'length ' + str(self.length)
        _id = 'PROCESS id ' + str(self.id)
        status = 'status ' + str(self.status)
        cause = 'cause ' + str(self.cause)
        add = 'page_address ' + str(self.page_address)
        var = 'varDict ' + str(self.varDict)
        return '\n'.join(['\nPCB', _id, eax, dr, ir, psw, pc, length, status, cause, add, var])


if __name__ == "__main__":
    temp_exe = {
        'path': 'C:/a.ex',
        'orders': 'A=2;A--;A--;A--;A--;A--;A--;end.'
    }
    temp = CPU()
    for i in range(2):
        temp.create(temp_exe)
    for i in range(17):
        # print('\n\nTime', temp.running_time+1)
        temp.execute()
        # temp.process_status()
