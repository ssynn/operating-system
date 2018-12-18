import memory


class CPU():

    _DR = 0                          # 数据缓存寄存器
    _PSW = [0, 0, 0]                 # [程序结束, 时钟中断, I/O中断]
    _IR = None                       # 指令寄存器
    _PC = 0                          # 程序计数器

    def __init__(self):
        self._running_time = 0
        self._timeslice = 5
        self._memory = memory.Memory()
        self._PCB_id = [0]*10
        self._ready_queue = []
        self._block_queue = []
        self._running_process = None

    # TODO CPU运行方法
    def run(self):
        '''
        一旦主机启动此方法就会开始运行
        直到主机被关闭
        '''
        pass

    # TODO 检查中断
    def check_interrupt(self):
        pass

    # TODO 执行
    def execute(self):
        '''
        L:检测有无中断，有进行处理
        If（进程结束软中断）撤销进程；进程调度；
            If（输入输出完成）输入输出中断处理；
            If（时间片到）进程调度
        根据pc取指令，若pc所指指令在主存，将指令放入IR寄存器；若不在主存，置中断，延时，goto L;
        执行IR指令；//解释执行课程设计中的指令
        pc++
        延时
        '''
        pass

    # TODO 进程调度
    def process_schedule(self):
        '''
        将正在运行的进程保存在该进程对应进程控制块中
        从就绪队列中选择一个进程
        将这个进程中进程控制块中记录的各寄存器内容恢复到CPU各个寄存器内
        '''
        pass

    # TODO 中断处理
    def handle_interrupt(self):
        pass

    # 创建进程
    def create(self, info: dict) -> bool:
        '''
        传入{
            path: str,
            orders: str
        }
        创建FCB
        存入主存
        加入就绪队列
        '''
        if self._PCB_id.count(0) == 0:
            print('进程数已达10')
            return False

        # 创建FCB
        new_PCB = PCB(info)

        # 存入主存
        new_PCB.page_address, new_PCB.length = self._memory.allocate(
            info['orders'])
        if new_PCB.page_address == -1:
            print('申请内存失败')
            return False

        # 需要把PCB内的IR赋值为第一条指令
        new_PCB.IR = self.page_access(new_PCB, 0, 0, 4)

        # 创建进程标识符
        new_PCB.id = self._PCB_id.index(0)
        self._PCB_id[new_PCB.id] = 1

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
        print(pcb)

    # TODO 阻塞进程
    def block(self, pcb) -> bool:
        '''
        保存运行进程的CPU现场
        修改进程状态
        将进程链入对应的阻塞队列，然后转向进程调度
        阻塞之后一定要调用进程调度函数
        '''
        pass

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

    def __str__(self):
        dr = 'DR ' + str(self._DR)
        ir = 'IR ' + str(self._IR)
        psw = 'PSW ' + str(self._PSW)
        pc = 'PC ' + str(self._PC)
        PCB_id = 'PCB_id ' + str(self._PCB_id)
        running_time = 'running_time ' + str(self._running_time)
        timeslice = 'timeslice ' + str(self._timeslice)
        memory = 'memory ' + str(self._memory.memory)
        ready_queue = 'ready_queue ' + str(self._ready_queue)
        block_queue = 'block_queue ' + str(self._block_queue)
        return '\n'.join([dr, ir, psw, pc, PCB_id, running_time, timeslice, ready_queue, block_queue, memory])

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
    def __init__(self, info: dict):
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
        self.path = info['path']
        self.status = 0
        self.cause = 0
        self.id = None
        self.page_address = None
        self.length = None
        self.DR = 0
        self.IR = None
        self.PSW = [0, 0, 0]
        self.PC = 4

    def __str__(self):
        dr = 'DR ' + str(self.DR)
        ir = 'IR ' + str(self.IR)
        psw = 'PSW ' + str(self.PSW)
        pc = 'PC ' + str(self.PC)
        length = 'length ' + str(self.length)
        _id = 'id ' + str(self.id)
        status = 'status ' + str(self.status)
        cause = 'cause ' + str(self.cause)
        add = 'page_address ' + str(self.page_address)
        return '\n'.join([dr, ir, psw, pc, length, _id, status, cause, add])


if __name__ == "__main__":
    temp_exe = {
        'path': 'C:/a.ex',
        'orders': 'A=2;A--;A23;end.'
    }
    temp = CPU()
    print(temp.create(temp_exe))
    print(temp)
    temp.destroy(temp._ready_queue[0])
    print(temp)
