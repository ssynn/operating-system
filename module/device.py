
class Device():
    '''
    一共有三个设备
    A有三个
    B有两个
    C有一个
    '''

    def __init__(self, cpu):
        self.CPU = cpu
        self.deviceA = [0, 0, 0]
        self.useA = [-1, -1, -1]
        self.deviceB = [0, 0]
        self.useB = [-1, -1]
        self.deviceC = [0]
        self.useC = [-1]
        self.waiting = []

    def request(self, _id: int, device: str, time: int) -> bool:
        '''
        传入申请的设备ID，请求的设备名，需要使用的时长
        '''
        if device == 'A' and self.deviceA.count(0) != 0:
            index = self.deviceA.index(0)
            self.deviceA[index] = time
            self.useA[index] = _id
            return True

        if device == 'B' and self.deviceB.count(0) != 0:
            index = self.deviceB.index(0)
            self.deviceB[index] = time
            self.useB[index] = _id
            return True

        if device == 'C' and self.deviceC[0] == 0:
            self.deviceC[0] = time
            self.useC[0] = _id
            return True

        # 没有空闲的设备可供分配则进入等待队列
        for p in self.waiting:
            if p[0] == _id:
                return False
        self.waiting.append([_id, device, time])
        return False

    def run(self):
        temp = []
        # 如果有空出来的设备则将设备分配给设备
        for p in self.waiting:
            if self.request(p[0], p[1], p[2]):
                # 如果分配成功则在阻塞队列中改变对应PCB的阻塞原因
                for pcb in self.CPU._block_queue:
                    if pcb.id == p[0]:
                        pcb.cause = 2
                        temp.append(p)
                        break
        for p in temp:
            self.waiting.remove(p)

        for i in range(3):
            if self.deviceA[i] != 0:
                self.deviceA[i] -= 1
            if self.deviceA[i] == 0 and self.useA[i] != -1:
                self.wake(self.useA[i])
                self.useA[i] = -1

        for i in range(2):
            if self.deviceB[i] != 0:
                self.deviceB[i] -= 1
            if self.deviceB[i] == 0 and self.useB[i] != -1:
                self.wake(self.useB[i])
                self.useB[i] = -1

        if self.deviceC[0] != 0:
            self.deviceC[0] -= 1
        if self.deviceC[0] == 0 and self.useC[0] != -1:
            self.wake(self.useC[0])
            self.useC[0] = -1

    def wake(self, _id: int):
        self.CPU._need_wake.append(_id)
        self.CPU._PSW[1] = 1

    def get_status(self):
        '''
        返回六个设备的状态[
            [使用A1的设备, 剩余时间],
            ...
        ]
        '''
        return [
            [self.useA[0], self.deviceA[0]],
            [self.useA[1], self.deviceA[1]],
            [self.useA[2], self.deviceA[2]],
            [self.useB[0], self.deviceB[0]],
            [self.useB[1], self.deviceB[1]],
            [self.useC[0], self.deviceC[0]],
        ]