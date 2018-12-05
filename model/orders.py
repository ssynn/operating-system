'''
指令操作
'''
import disk


def parser(order: str) -> str:
    '''
    命令解析器
    '''
    order = order.split('>')
    if order[1] == '':
        return ''
    path = order[0]
    order = order[1].lower().split()
    args = order[1:]
    order = order[0]
    # print(path, order, args)
    if order == 'mkdir':
        if len(args) != 1:
            return ['display', 'Parameter error!']
        if args[0].count('$') != 0 or args[0].count('.') != 0 or args[0].count('/') != 0:
            return ['display', 'Name error!']
        return ['display', __mkdir(path, args[0])]
    if order == 'dir':
        return ['display', __dir(path)]
    if order == 'cd':
        ans = __cd(path, args[0])
        if ans[0] != 'P':
            return ['path', ans]
        else:
            return ['display', ans]
    if order == 'formate':
        if args == []:
            args = "C:"
        return ['path', __format(args)]
    if order == 'rmdir':
        if args[0].count('$') != 0 or args[0].count('.') != 0 or args[0].count('/') != 0:
            return ['display', 'Not dir name!']
        if len(args) != 1:
            return ['display', 'Parameter error!']
        return ['display', __rmdir(path, args[0])]
    if order == 'create':
        if len(args) == 0:
            return ['display', 'Parameter error!']
        if args[0].count('.') != 1:
            return ['display', 'Not file name!']
        if len(args) == 1:
            return ['display', __create_file(path, args[0])]
        if len(args) == 2:
            return ['display', __create_file(path, args[0], args[1])]
        return ['display', __create_file(path, args[0], args[1], ' '.join(args[2:]))]
    if order == 'delete':
        if len(args) == 0:
            return ['display', 'Parameter error!']
        if args[0].count('.') != 1:
            return ['display', 'Not file name!']
        return ['display', __delete_file(path, args[0])]
    return ['display', order + '不是命令，也不是可执行的程序']


# 移动当前目录
def __cd(path: str, dest: str) -> str:
    '''
    输入当前目录和操作
    返回操作后的路径
    移动失败则返回 Path Error!
    '''
    if path[-1] == '/':
        path = path[:-1]
    path_list = path.split('/')
    if path_list[-1] == '':
        path_list.pop(-1)
    if dest == '..':
        if len(path_list) == 1:
            return path
        path_list.pop(-1)
        return '/'.join(path_list)
    if dest == '/':
        return path_list[0]
    path = path + '/' + dest
    block = disk.get_block(path)
    if block[0] == -1:
        return 'Path Error!'
    return path


# 列出当前目录下所有文件
def __dir(path: str) -> str:
    '''
    输入当前目录路径
    返回格式化后的信息
    '''
    temp = disk.list_dir(path)
    print(temp)
    if not temp:
        return ''
    ans = ''
    for f in temp:
        # 文件夹
        if f['attribute'] == 8:
            ans += "{0:17}    <DIR> {1:>14}   {2:3}\n".format(
                __to_time(f['time']), '-', f['name'])
        else:
            ans += '{0:17}    <FILE>{1:10}B   {2:3}\n'.format(
                __to_time(f['time']), f['length'], f['name'].strip()+'.'+f['ext'])
    if ans == '':
        ans = 'empty'
    return ans


# 创建文件夹
def __mkdir(path: str, name: str) -> str:
    '''
    建立文件夹
    '''
    if len(name.encode()) > 3:
        return 'name is too long!'
    if path[-1] == '/':
        path = path[:-1]
    if disk.create_dir(path+'/'+name):
        return 'Success'
    else:
        return 'Fail'


# 删除文件夹
def __rmdir(path: str, name: str) -> str:
    '''
    传入当前路径和需要删除的子目录, 此方法只能删除
    '''
    if path[-1] == '/':
        path = path[:-1]
    if disk.delete_dir(path+'/'+name):
        return 'Seccuss!'
    else:
        return 'Error!'


# TODO 移动文件夹
def __move(path: str, old: str, new: str):
    pass


# TODO 删除当前目录的空目录
def __rdir(path: str):
    pass


# 格式化
def __format(driver: str = 'C:') -> str:
    '''
    格式化磁盘，返回根目录
    '''
    disk.format_disk(driver)
    return driver


# 把bytes转换为时间
def __to_time(time: bytes) -> str:
    '''
    把5位的bytes串转换为 yyyy/MM/dd  hh:mm格式的字符串
    '''
    year = time[0]
    month = time[1]
    day = time[2]
    hour = time[3]
    minute = time[4]
    return '2{0:0>3}/{1:02}/{2:02}  {3:02}:{4:02}'.format(year, month, day, hour, minute)


# 创建文件
def __create_file(path: str, name: str, attribute: str = '4', text: str = '') -> str:
    '''
    创建文件
    传入文件路径 文件名.扩展 属性(可选默认为4) 余下为内容(可选默认为空字符串)
    '''
    if len(text.encode()) > 255:
        return 'Text is too long'
    name, ext = name.split('.')
    if len(name.encode()) > 3:
        return 'Name is too long!'
    if ext not in ('ex', 'tx'):
        return 'Extension name error!'
    if attribute not in ('3', '4', '5'):
        return 'Attribute error!'
    value = {
        'path': path,
        'name': name,
        'ext': ext,
        'text': text,
        'attribute': int(attribute)
    }
    if disk.create_file(value):
        return 'Seccuss!'
    return 'Fail!'


# 删除文件
def __delete_file(path: str, file_name: str) -> str:
    '''
    传入文件路径, 文件名，判断是否为文件
    '''
    if path[-1] == '/':
        path = path[:-1]
    name, ext = file_name.split('.')
    if len(name.encode()) > 3 or ext not in ('ex', 'tx'):
        return 'Not a file name!'
    if disk.delete_file(path + '/' + name):
        return 'Seccuss!'
    else:
        return 'Fail!'


if __name__ == "__main__":
    # while True:
    #     order = input()
    #     print(parser(order))
    print(__to_time(b'\x12\x0c\x04\x10)'))
