

class CPU():

    DR = 0                          # 数据缓存寄存器
    PSW = 0
    INTERRUPT_VECTOR = [0, 0, 0]    # [程序结束, I/O中断, 时钟中断]
    IR = None                       # 指令寄存器
    PC = 0                          # 程序计数器

    def __init__(self):
        pass

    # 检查中断
    def check_interrupt(self):
        pass

    # 执行
    def exexute(self):
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

    # 进程调度
    def process_schedule(self):
        '''
        将正在运行的进程保存在该进程对应进程控制块中
        从就绪队列中选择一个进程
        将这个进程中进程控制块中记录的各寄存器内容恢复到CPU各个寄存器内
        '''
        pass

    # 中断处理
    def handle_interrupt(Self):
        pass
