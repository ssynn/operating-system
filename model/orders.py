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
    path = disk.format_path(path)
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
    if order == 'format':
        if args == []:
            args = ' '
        return __format(args[0].strip())
    if order == 'rmdir':
        if args[0].count('$') != 0 or args[0].count('.') != 0 or args[0].count('/') != 0:
            return ['display', 'Not dir name!']
        if len(args) != 1:
            return ['display', 'Parameter error!']
        return ['display', __rmdir(path, args[0])]
    if order == 'create':
        if len(args) == 0:
            return ['display', 'Parameter error!']
        if len(args) == 1:
            return ['display', __create_file(path, args[0])]
        if len(args) == 2:
            return ['display', __create_file(path, args[0], args[1])]
        return ['display', __create_file(path, args[0], args[1], ' '.join(args[2:]))]
    if order == 'delete':
        if len(args) != 1:
            return ['display', 'Parameter error!']
        return ['display', __delete_file(path, args[0])]
    if order == 'parser':
        if len(args) != 1:
            return ['display', 'Parameter error!']
        return ['display', disk.path_parser(path, args[0])]
    if order == 'move':
        if len(args) != 2:
            return ['display', 'Parameter error!']
        return ['display', __move(path, args[0], args[1])]
    if order == 'copy':
        if len(args) != 2:
            return ['display', 'Parameter error!']
        return ['display', __copy(path, args[0], args[1])]

    # 根目录移动
    if order in ('C:', 'c:', 'd:', 'D:'):
        return ['path', order.capitalize()]
    if __is_file_name(order):
        return ['display', __open_file(path+'/'+order)]
    if disk.is_absolute_path(order):
        return ['display', __open_file(order)]
    return ['display', order + '不是命令，也不是可执行的程序']


# 移动当前目录
def __cd(path: str, dest: str) -> str:
    '''
    输入当前目录和操作
    返回操作后的路径
    移动失败则返回 Path Error!
    '''
    path = disk.path_parser(path, dest)
    block = disk.get_block(path)
    if block[0] == -1:
        return 'Path Error!'
    path = disk.my_upper(path)
    print(path)
    return path


# 列出当前目录下所有文件
def __dir(path: str) -> str:
    '''
    输入当前目录路径
    返回格式化后的信息
    '''
    temp = disk.list_dir(path)
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
    path = disk.format_path(path)
    if disk.create_dir(path+'/'+name):
        return 'Success'
    else:
        return 'Fail'


# 删除文件夹
def __rmdir(path: str, name: str) -> str:
    '''
    传入当前路径和需要删除的子目录, 此方法只能删除
    '''
    path = disk.format_path(path)
    if disk.delete_dir(path+'/'+name):
        return 'Seccuss!'
    else:
        return 'Error!'


# 移动
def __move(path: str, old: str, new: str) -> str:
    '''
    传入当前地址 源路径 目标路径
    '''
    old_path = disk.path_parser(path, old)
    new_path = disk.path_parser(path, new)
    print(old_path, new_path)
    if disk.move(old_path, new_path):
        return 'Seccuss!'
    else:
        return 'Fail!'


# 复制
def __copy(path: str, old: str, new: str) -> str:
    '''
    传入当前地址 源路径 目标路径
    '''
    old_path = disk.path_parser(path, old)
    new_path = disk.path_parser(path, new)
    print(old_path, new_path)
    if disk.copy(old_path, new_path):
        return 'Seccuss!'
    else:
        return 'Fail!'


# TODO 删除当前目录的空目录
def __rdir(path: str):
    pass


# 格式化
def __format(driver: str = '') -> list:
    '''
    格式化磁盘，返回根目录
    '''
    if driver not in ('C:', 'c:', 'd:', 'D:', ''):
        return ['display', 'Disk name error!']
    disk.format_disk(driver)
    if driver == '':
        return ['path', 'C:']
    driver = driver.capitalize()
    return ['path', driver]


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
    (C:/, a.tx, 4, 'asdads')
    传入文件路径 文件名.扩展 属性(可选默认为4) 余下为内容(可选默认为空字符串)
    '''
    if len(text.encode()) > 255:
        return 'Text is too long'
    if not __is_file_name(name):
        return 'File name error!'
    name, ext = disk.file_name_split(name)
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
    path = disk.format_path(path)
    if not __is_file_name(file_name):
        return 'Not a file name!'
    name, ext = disk.file_name_split(file_name)
    if disk.delete_file(path + '/' + name):
        return 'Seccuss!'
    else:
        return 'Fail!'


# 打开文件
def __open_file(path: str):
    dot = path.find('.')
    ext = path[dot:]
    # print(path)
    if ext != 'ex':
        ans = disk.open_file(path)
        if ans:
            return str(ans)
    return 'Open error!'


# 判断文件名是否合法
def __is_file_name(name: str) -> bool:
    name, ext = disk.file_name_split(name)
    if len(name.encode()) > 3:
        return False
    if len(ext.encode()) > 2:
        return False
    return True


if __name__ == "__main__":
    print(__is_file_name('a.tx'))
