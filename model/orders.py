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
            return ['display', 'parameter error!']
        if args[0].count('$') != 0 or args[0].count('.') != 0 or args[0].count('/') != 0:
            return ['display', 'name error!']
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
        if len(args) != 1:
            return ['display', 'parameter error!']
        return ['display', __rmdir(path, args[0])]
    return ['display', order + '不是命令，也不是可执行的程序']


# 移动当前目录
def __cd(path: str, dest: str) -> str:
    '''
    输入当前目录和操作
    返回操作后的路径
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
            ans += f"   <DIR>          {f['name']}\n"
        else:
            ans += '  <FILE>{0:10}{1}\n'.format(f['length']*64, f['name'])
    if ans == '':
        ans = 'empty'
    return ans


# 创建文件夹
def __mkdir(path: str, name: str) -> str:
    '''
    建立文件夹
    '''
    if len(name) > 3:
        return 'name is too long!'
    if path[-1] == '/':
        path = path[:-1]
    if disk.creat_dir(path+'/'+name):
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


# 移动文件夹
def __move(path: str, old: str, new: str):
    pass


# 删除当前目录的空目录
def __rdir(path: str):
    pass


# 格式化
def __format(driver: str = 'C:') -> str:
    '''
    格式化磁盘，返回根目录
    '''
    disk.format_disk(driver)
    return driver


if __name__ == "__main__":
    # while True:
    #     order = input()
    #     print(parser(order))
    __dir()
