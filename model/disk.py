
# 所有和磁盘操作有关的方法都在此模块中
# 1.查询文件状态
#   1.1 大小
#   1.2 名称
#   1.3 属性
#   1.4 建立时间
# 2.创建文件夹
# 3.创建文件
# 4.删除文件
# 5.删除文件夹
# 6.修改文件
# 7.修改文件夹名称
# 8.获取文件列表
# 9.查询磁盘信息
#   9.1 磁盘大小
#   9.2 磁盘占用
#   9.3 磁盘扇区占用情况
# 10.移动文件/文件夹


# 磁盘属性
# 128个扇区
# 每个扇区64B
# 每个文件最大64B
# 系统占用3个扇区
# C盘
# D盘


# 创建文件
def create_file(mes: dict) -> bool:
    '''
    传入字典{
        name: str,
        ext: str,
        text: str,
        attribute: int
    }
    '''
    pass


# 删除文件
def remove_file(path: str) -> bool:
    '''
    传入文件路径
    '''
    pass


# 修改文件
def modify_file(path: str, new_mes: dict) -> bool:
    '''
    传入文件路径和文件信息{
        name: str,
        ext: str,
        text: str,
        attribute: int
    }
    '''
    pass


# 打开文件
def open_file(path: str) -> dict:
    '''
    传入文件路径
    返回文件信息{
        name: str,
        ext: str,
        text: str,
        time: str,
        attribute: int
    }
    '''
    pass


# 获取文件列表
def list_dir(path: str) -> list:
    '''
    传入文件夹路径
    返回当前文件夹内的所有文件和文件夹[str, str, ...]
    '''
    pass


# 修改文件夹
def modify_dir(path: str, new_name: str) -> bool:
    '''
    传入原始路径和文件夹的新名字
    '''
    pass


# 创建文件夹
def creat_dir(path: str) -> bool:
    '''
    传入文件夹路径
    '''
    pass


# 移动
def move(now_path: str, new_path: str) -> bool:
    '''
    传入旧地址和新地址
    '''


# 获取磁盘内容
def get_disk(disk: str = 'c'):
    '''
    传入磁盘名，打印出磁盘内所有信息
    '''
    with open('virtual_disk_'+disk, 'rb') as d:
        f = d.readline()
    print(f, len(f))


# 获取磁盘信息
def disk_info(disk: str = 'c') -> list:
    '''
    传入磁盘名，默认为c盘
    以列表的形式返回磁盘表项
    '''
    pass


# 格式化磁盘
def format_disk(disk: str = 'c') -> bool:
    '''
    传入磁盘号，默认为c盘
    '''
    with open('virtual_disk_' + disk, 'w') as d:
        for i in range(128):
            for j in range(64):
                d.write('0')
            d.write('\n')

    with open('virtual_disk_' + disk, 'rb+') as d:
        d.seek(0)
        d.write(bytes([129, 129, 129]))


# 字符串分割
def divide(val):
    val_length = len(val)
    ans = []
    i = 0
    while i < val_length:
        ans.append(val[i:i+64])
        i += 64
    return ans


if __name__ == '__main__':
    format_disk()
