
# 所有和磁盘操作有关的方法都在此模块中
# 1.查询文件状态
# 2.创建文件夹
# 3.创建文件
# 4.删除文件
# 5.删除文件夹
# 6.修改文件
# 7.修改文件夹名称
# 8.获取文件列表
# 9.查询磁盘信息
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
        path: str,
        name: str,
        ext: str,
        text: str,
        attribute: int
    }
    '''
    table = disk_table()
    pass


# 删除文件
def delete_file(path: str) -> bool:
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
        text: str
    }
    '''
    pass


# 修改文件属性
def change(path: str, attr: int) -> bool:
    '''
    传入文件路径和新的属性
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


# 复制文件
def copy_file(path: str, new_path: str) -> str:
    '''
    传入原始地址名和新地址名
    '''
    pass


# 获取文件列表
def list_dir(path: str) -> list:
    '''
    传入文件夹路径
    返回当前文件夹内的所有文件和文件夹[dict, dict, ...]
    {
        'name': str,
        'ext': str,
        'attribute': int,
        'address': int,
        'length': int
    }
    '''
    path_list = path.split('/')
    blocks = get_block(path)
    # print(blocks)
    block_list = []
    with open('virtual_disk_' + path_list[0].lower()[0], 'rb+') as f:
        for b in blocks:
            f.seek(b*66)
            block_list.append(f.read(64))
    # print(block_list)
    dir_list = []
    for block in block_list:
        for i in range(8):
            dir_list.append(converter(block[i*8: i*8+8]))
            if dir_list[-1] is None:
                dir_list.pop(-1)
    return dir_list


# 修改文件夹
def modify_dir(path: str, new_name: str) -> bool:
    '''
    传入原始路径和文件夹的新名字
    '''
    pass


# 删除文件夹
def delete_dir(path: str) -> bool:
    '''
    传入文件路径
    此操作会删除当前母录内所有内容
    先获得所有子项
    对所有子项执行删除操作
    最后删除自己
    '''
    # 先检查目录是否存在
    blocks = get_block(path)
    if blocks[0] == -1:
        return False
    if path[-1] == '/':
        path = path[:-1]
    path_list = path.split('/')
    children = list_dir(path)
    print(blocks, children)
    for child in children:
        if child['attribute'] == 8:
            delete_dir(path+'/'+child['name'].strip())
        else:
            delete_file(path+'/'+child['name'].strip())
    print(blocks)
    if blocks[0] == -1:
        return False
    with open('virtual_disk_' + path_list[0].lower()[0], 'wb+') as f:
        for block in blocks:
            f.seek(66*block)
            f.write(('0'*64+'\n').encode())
        for block in blocks:
            f.seek(block)
            f.write(bytes([129]))
    return True


# 创建文件夹
def creat_dir(path: str) -> bool:
    '''
    传入文件夹路径
    在传入文件名前应该提前做合法检查
    首先判断路径是否合法
    判断当前目录块是否满
    如果是根目录并且已经满了则不能再创建目录返回False
    如果是普通目录并且已满则为当前目录申请新的磁盘块，如果失败返回False
    在当前目录磁盘块下创建一个文件
    '''
    path_list = path.split('/')
    new_dir = path_list[-1]
    path_list = path_list[:-1]
    disk = open_disk(path_list[0])
    # 块内指针
    block_pointer = 0
    # 指向父目录块
    parent_block = 0
    # 为当前文件夹申请的文件块
    empty_pointer = 0
    # 找到父文件夹
    parent_block = get_block(path_list)[0]
    if parent_block == -1:
        return False
    while True:
        # 在父磁盘块内找一个空位置
        for block_pointer in range(9):
            if block_pointer == 8:
                break
            if disk[parent_block][block_pointer*8+5] == 48:
                break
        if disk[parent_block//64][parent_block % 64] == 129:
            break
        # 需要扫描所有分配给目录的表项
        parent_block = disk[parent_block//64][parent_block % 64]
    # print(parent_block, block_pointer)
    # 父文件块已满
    if block_pointer == 8:
        # 当前是根目录，不能再申请文件夹
        if len(path_list) == 1 and path_list[0] == 'C:' or path_list[0] == 'D:':
            return False
        # 普通文件夹可以再申请一个文件块
        empty_pointer_parent = get_empty_block(disk)
        if empty_pointer_parent == -1:
            return False
        # 分配磁盘块
        disk[parent_block//64] = assign(
            disk[parent_block//64],
            parent_block % 64,
            empty_pointer_parent
        )
        disk[empty_pointer_parent // 64] = assign(
            disk[empty_pointer_parent//64],
            empty_pointer_parent % 64,
            129
        )
        block_pointer = 0
        parent_block = empty_pointer_parent
    # print(parent_block, block_pointer)
    # 找到一块空闲的磁盘块
    empty_pointer = get_empty_block(disk)
    if empty_pointer == -1:
        return False
    disk[empty_pointer // 64] = assign(
        disk[empty_pointer//64],
        empty_pointer % 64,
        129
    )
    with open('virtual_disk_' + path_list[0].lower()[0], 'rb+') as f:
        # 更新表项
        f.seek(0)
        f.write(disk[0])
        f.write(disk[1])
        # 把目录控制块写入磁盘块
        f.seek(parent_block*66+block_pointer*8)
        f.write(dirname_to_bytes(new_dir, empty_pointer))
    return True


# 把文件名转换为8Byte串
def dirname_to_bytes(name: str, start: int) -> bytes:
    return "{0:<3}00{1:1}{2:1}\x00".format(name, bytes([8]).decode(), bytes([start]).decode()).encode()


# 改变bytes串内的值
def assign(old: bytes, pointer: int, val: int):
    '''
    传入一行把位置为pointer的值赋值为val，返回改变后的bytes
    '''
    old = list(old)
    old[pointer] = val
    return bytes(old)


# 移动
def move(now_path: str, new_path: str) -> bool:
    '''
    传入旧地址和新地址
    '''
    pass


# 获取空磁盘块
def get_empty_block(disk: list) -> int:
    '''
    再文件表内找一个空的文件块
    '''
    for empty_pointer in range(2, 129):
        if empty_pointer == 128:
            empty_pointer = -1
            break
        if disk[empty_pointer//64][empty_pointer % 64] == 48:
            break
    return empty_pointer


# 打开磁盘
def open_disk(disk: str = 'C:/') -> list:
    '''
    返回磁盘所有内容
    '''
    with open('virtual_disk_' + disk.lower()[0], 'rb+') as f:
        data = f.read()
    data = divide(data, 66)
    return data


# 获取磁盘内容
def print_disk(disk: str = 'c', *lines):
    '''
    传入磁盘名，打印出磁盘内所有信息
    '''
    with open('virtual_disk_'+disk, 'rb') as d:
        f = d.read()
    ans = divide(f, 66)
    for index, i in enumerate(list(ans[3])):
        print(index, i)


# 获取磁盘信息
def disk_table(disk: str = 'c') -> list:
    '''
    传入磁盘名，默认为c盘
    以列表的形式返回磁盘表项
    '''
    with open('virtual_disk_' + disk, 'rb+') as f:
        data = f.readlines()[:2]
    return data


# 获取盘块号，目前只支持寻找目录
def get_block(path) -> list:
    '''
    传入绝对路径可以为字符串或列表，返回当前目录占有的盘块号列表
    如果没有找到则返回[-1]
    '''
    if type(path) is str:
        if path[-1] == '/':
            path = path[:-2]
        path_list = path.split('/')
    else:
        path_list = path
    driver = path_list[0]
    # 指针指向根目录
    pointer = 2
    data = open_disk(driver)
    table = data[:2]
    for item in path_list[1:]:
        is_find = False
        while True:
            # 在当前目录块做匹配，如果没有找到对应的文件则返回-1
            for block_pointer in range(8):
                # 文件名相等
                item = '{0:3}'.format(item)
                if item.encode() == data[pointer][block_pointer*8: block_pointer*8+3]:
                    pointer = data[pointer][block_pointer*8 + 6]
                    is_find = True
                    break
            # 当前文件夹没有使用后续表项
            if table[pointer//64][pointer % 64] == 129 or is_find:
                break
            pointer = table[pointer//64][pointer % 64]
        if not is_find:
            return [-1]
    ans = [pointer]
    while table[pointer//64][pointer % 64] != 129:
        pointer = table[pointer//64][pointer % 64]
        ans.append(pointer)
    return ans


# 格式化磁盘
def format_disk(disk: str = 'C:') -> bool:
    '''
    传入磁盘号，默认为c盘
    '''
    with open('virtual_disk_' + disk.lower()[0], 'w') as d:
        for i in range(128):
            d.write('0'*64+'\n')

    with open('virtual_disk_' + disk.lower()[0], 'rb+') as d:
        d.seek(0)
        d.write(bytes([129, 129, 129]))


# 字符串分割
def divide(val, length: int = 64):
    val_length = len(val)
    ans = []
    i = 0
    while i < val_length:
        ans.append(val[i:i+length])
        i += length
    return ans


# 目录项转换为文件或列表
def converter(value: bytes) -> dict:
    '''
    传入8位字符串转换为文件或文件夹的表项{
        'name': name,
        'ext': ext,
        'attribute': attribute,
        'address': address,
        'length': length
    }
    '''
    name = value[:3].decode()
    ext = value[3:5].decode()
    attribute = value[5]
    address = value[6]
    length = value[7]
    if attribute == 48:
        return None
    return {
        'name': name,
        'ext': ext,
        'attribute': attribute,
        'address': address,
        'length': length
    }


if __name__ == '__main__':
    temp_file = {
        'path': 'C:',
        'name': 'aaa',
        'ext': 'tx',
        'text': 'asddadddddddddddddddddddddddddddddddd',
        'attribute': 4
    }
    # 打印磁盘
    print_disk('c')

    # 打开磁盘
    # print(open_disk())

    # 格式化磁盘
    # format_disk()

    # 测试文件夹转换bytes
    # for i in range(8):
    #     print(dirname_to_bytes('aa', i), len(dirname_to_bytes('aa', i)))

    # 测试新建文件
    # print(creat_dir('C:/1/8'))

    # 测试获取文件块
    print(get_block(['C:', 'a']))

    # 读取文件列表
    # print(get_block('C:/'))
    # print(list_dir('C:/'))
    # print_disk()
