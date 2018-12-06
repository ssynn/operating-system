
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


import time


# 创建文件
def create_file(info: dict) -> bool:
    '''
    传入字典{
        path: str,
        name: str,
        ext: str,
        text: str,
        attribute: int
    }
    传入文件夹路径
    在传入文件名前应该提前做合法检查
    首先判断路径是否合法
    查重
    判断当前目录块是否满
    如果是根目录并且已经满了则不能再创建目录返回False
    如果是普通目录并且已满则为当前目录申请新的磁盘块，如果失败返回False
    把文件分割成多个长度为64的块
    尝试申请对应的盘块数量，失败则返回False
    在内存里的表更新表项
    打开文件
    更新文件表
    在当前目录磁盘块写入创建一个文件
    在对应盘块位置写入文件内容
    '''
    path_list = info['path'].split('/')
    driver = path_list[0]
    # 存入整个磁盘的内容
    disk = open_disk(driver)
    # 检查路径合法性
    parent_block = get_block(info['path'])[0]
    if parent_block == -1:
        return False
    # 查重
    if duplicate_checking(info['path'], format_name(info['name']), info['attribute']):
        return False
    # 在父磁盘块内找一个空位置
    while True:
        for inner_pointer in range(9):
            if inner_pointer == 8:
                break
            if disk[parent_block][inner_pointer*8+5] == 48:
                break
        if disk[parent_block // 64][parent_block % 64] == 129:
            break
        # 需要扫描所有分配给目录的表项
        parent_block = disk[parent_block // 64][parent_block % 64]
    # 父文件块已满, 当前是根目录，不能再申请文件夹
    if inner_pointer == 8 and len(path_list) == 1:
            return False
    # 当前文件夹为普通文件夹，已满
    if inner_pointer >= 7 and len(path_list) > 1:
        # 普通文件夹可以再申请一个文件块
        empty_pointer_parent = get_empty_block(disk)
        # 父文件夹无法新申请文件块
        if empty_pointer_parent == -1:
            return False
        # 把原父表项的内容改为找到的空表项的地址
        disk[parent_block // 64] = assign(
            disk[parent_block // 64],
            parent_block % 64,
            empty_pointer_parent
        )
        # 再文件表项内分配磁盘块
        disk[empty_pointer_parent // 64] = assign(
            disk[empty_pointer_parent // 64],
            empty_pointer_parent % 64,
            129
        )
        inner_pointer = 0
        parent_block = empty_pointer_parent

    time_now = [int(i) for i in time.strftime('%Y %m %d %H %M').split()]
    time_now[0] -= 2000
    text = bytes(time_now) + info['text'].encode()
    info['length'] = len(text)
    # 数据长度超过255
    if info['length'] > 255:
        return False
    text = divide(text)
    pointer_list = []
    for i in range(len(text)):
        # 找一块空闲的磁盘块给文件本体
        empty_pointer = get_empty_block(disk)
        # 没找到就算了
        if empty_pointer == -1:
            return False
        # 把找到的空闲盘块的表项赋值为129
        disk[empty_pointer // 64] = assign(
            disk[empty_pointer // 64],
            empty_pointer % 64,
            129
        )
        # 不是第一个表项, 需要把上一个表项指向当前找到的文件块
        if len(pointer_list) != 0:
            disk[pointer_list[-1] // 64] = assign(
                disk[pointer_list[-1] // 64],
                pointer_list[-1] % 64,
                empty_pointer
            )
        pointer_list.append(empty_pointer)
    with open('virtual_disk_' + path_list[0].lower()[0], 'rb+') as f:
        # 更新表项
        f.seek(0)
        f.write(disk[0])
        f.write(disk[1])
        # 把目录控制块写入父磁盘块
        f.seek(parent_block*66 + inner_pointer*8)
        f.write(file_to_bytes(
            format_name(info['name']),
            info['ext'],
            info['attribute'],
            pointer_list[0],
            info['length']
        ))
        # 在文件分配的磁盘块写入数据
        for index in range(len(text)):
            f.seek(pointer_list[index]*66)
            f.write(text[index])
    return True


# TODO 删除文件
def delete_file(path: str) -> bool:
    '''
    传入文件路径, 如
    C:/a.tx
    获取自己占有的所有表项
    把这些表项置0
    最后删除父表项中的自己
    '''
    # 先检查目录是否存在
    blocks = get_block(path, 4)
    if blocks[0] == -1:
        return False
    if path[-1] == '/':
        path = path[:-1]
    path_list = path.split('/')
    name = format_name(path_list[-1])
    # 找到父块
    with open('virtual_disk_' + path_list[0].lower()[0], 'rb+') as f:
        data = f.read()
    # 在父块内找到自己对应的位置
    father_blocks = get_block(path_list[:-1])
    for father_block in father_blocks:
        is_find = False
        for in_block_pointer in range(8):
            if data[father_block*66 + in_block_pointer*8] == 130:
                break
            position = get_position(father_block, in_block_pointer)
            if name == data[position: position + 3] and data[position + 5] in (3, 4, 5):
                is_find = True
                break
        if is_find:
            break
    # 把修改写入文件
    with open('virtual_disk_' + path_list[0].lower()[0], 'rb+') as f:
        for block in blocks:
            if block > 63:
                block += 2
            f.seek(block)
            f.write(bytes([48]))
        # 在父表项中删除自己的数据
        f.seek(father_block*66 + in_block_pointer*8)
        f.write(bytes([48]*8))
    return True


# TODO 修改文件
def modify_file(path: str, new_mes: dict) -> bool:
    '''
    传入文件路径和文件信息{
        name: str,
        ext: str,
        text: str
    }
    '''
    pass


# TODO 修改文件属性
def change(path: str, attr: int) -> bool:
    '''
    传入文件路径和新的属性
    '''
    pass


# TODO 打开文件
def open_file(path: str) -> dict:
    '''
    传入文件路径如C:/a/a.tx
    返回文件信息{
        name: str,
        ext: str,
        text: str,
        time: str,
        length: int,
        attribute: int
    }
    '''
    path_list = path.split('/')
    name = path_list[-1]
    name, ext = name.split('.')
    blocks = get_block(path, 4)
    if blocks[0] == -1:
        return None
    text = b''
    with open('virtual_disk_' + path_list[0].lower()[0], 'rb+') as f:
        for block in blocks:
            f.seek(block*66)
            text += f.read(64)
    FCB = get_pointer(path, 4)[2]
    length = FCB[-1]
    return {
        'name': name,
        'ext': ext,
        'text': text[5:length],
        'time': text[:5],
        'attribute': FCB[5],
        'length': length
    }


# TODO 复制文件
def copy_file(path: str, new_path: str) -> str:
    '''
    传入原始地址名和新地址名
    '''
    pass


# 用文件信息生成8位bytes
def file_to_bytes(name: bytes, ext: str, attr: int, address: int, length: int) -> bytes:
    return name + '{0:2}'.format(ext).encode() + bytes([attr, address, length])


# 获取文件列表
def list_dir(path: str) -> list:
    '''
    传入文件夹路径
    返回当前文件夹内的所有文件和文件夹[dict, dict, ...]
    {
        'name': str,
        'ext': str,
        'time': str,
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
    with open('virtual_disk_' + path_list[0].lower()[0], 'rb+') as f:
        for _dir in dir_list:
            if _dir['attribute'] == 8:
                f.seek(_dir['address']*66 + 57)
            else:
                f.seek(_dir['address']*66)
            _dir['time'] = f.read(5)
    return dir_list


# TODO 修改文件夹
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
    name = format_name(path_list[-1])
    # 获取所有和子项
    children = list_dir(path)
    # 把当前目录内的子项删除
    for child in children:
        if child['attribute'] == 8:
            delete_dir(path+'/'+child['name'].strip())
        else:
            delete_file(path+'/'+child['name'].strip())
    # 找到父块
    with open('virtual_disk_' + path_list[0].lower()[0], 'rb+') as f:
        data = f.read()
    # 在父块内找到自己对应的位置
    father_blocks = get_block(path_list[:-1])
    for father_block in father_blocks:
        is_find = False
        for in_block_pointer in range(8):
            if data[father_block*66 + in_block_pointer*8] == 130:
                break
            position = get_position(father_block, in_block_pointer)
            if name == data[position: position + 3] and data[position + 5] == 8:
                is_find = True
                break
        if is_find:
            break
    # 把修改写入文件, 不再抹去申请到的文件块内的内容
    with open('virtual_disk_' + path_list[0].lower()[0], 'rb+') as f:
        for block in blocks:
            if block > 63:
                block += 2
            f.seek(block)
            f.write(bytes([48]))
        f.seek(father_block*66 + in_block_pointer*8)
        f.write(bytes([48]*8))
    return True


# 创建文件夹
def create_dir(path: str) -> bool:
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
    new_dir = format_name(new_dir)
    path_list = path_list[:-1]
    # 载入整个磁盘
    disk = open_disk(path_list[0])
    # 块内指针
    block_pointer = 0
    # 指向父目录块
    parent_block = 0
    # 为当前文件夹申请的文件块
    empty_pointer = 0
    # 查重
    if duplicate_checking('/'.join(path_list), new_dir):
        return False
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
    # 父文件块已满, 当前是根目录，不能再申请文件夹
    if block_pointer == 8 and len(path_list) == 1:
            return False
    # 当前文件夹为普通文件夹，已满
    if block_pointer >= 7 and len(path_list) > 1:
        # 普通文件夹可以再申请一个文件块
        empty_pointer_parent = get_empty_block(disk)
        if empty_pointer_parent == -1:
            return False
        # 父表项指向新申请的表项
        disk[parent_block // 64] = assign(
            disk[parent_block // 64],
            parent_block % 64,
            empty_pointer_parent
        )
        # 分配磁盘块
        disk[empty_pointer_parent // 64] = assign(
            disk[empty_pointer_parent // 64],
            empty_pointer_parent % 64,
            129
        )
        block_pointer = 0
        parent_block = empty_pointer_parent
    # print(parent_block, block_pointer)
    # 找一块空闲的磁盘块
    empty_pointer = get_empty_block(disk)
    # 没找到就算了
    if empty_pointer == -1:
        return False
    # 把空闲盘块的表项赋值为129
    disk[empty_pointer // 64] = assign(
        disk[empty_pointer // 64],
        empty_pointer % 64,
        129
    )
    with open('virtual_disk_' + path_list[0].lower()[0], 'rb+') as f:
        # 更新表项
        f.seek(0)
        f.write(disk[0])
        f.write(disk[1])
        # 把目录控制块写入父磁盘块
        f.seek(parent_block*66+block_pointer*8)
        f.write(dirname_to_bytes(new_dir, empty_pointer))
        # 先把申请到的盘块置0
        f.seek(empty_pointer*66)
        f.write(bytes([48]*64))
        # 再空闲盘块的最后一行写入创建时间
        f.seek(empty_pointer*66+56)
        f.write(get_time())
    return True


# 把文件名转换为8Byte串
def dirname_to_bytes(name: bytes, start: int) -> bytes:
    return name + bytes([48, 48, 8, start, 0])


# 文件夹最后一部分，记录当前块产生的时间
def get_time():
    '''
    返回普通文件块的最后一部分
    '''
    time_now = [int(i) for i in time.strftime('%Y %m %d %H %M').split()]
    time_now[0] -= 2000
    val = [130] + time_now + [0, 0]
    return bytes(val)


# 改变bytes串内的值
def assign(old: bytes, pointer: int, val: int):
    '''
    传入一行把位置为pointer的值赋值为val，返回改变后的bytes
    '''
    old = list(old)
    old[pointer] = val
    return bytes(old)


# TODO 移动
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


# 获取磁盘表项信息
def disk_table(disk: str = 'c') -> list:
    '''
    传入磁盘名，默认为c盘
    以列表的形式返回磁盘表项
    '''
    with open('virtual_disk_' + disk, 'rb+') as f:
        data = f.readlines()[:2]
    return data


# 获取盘块号
def get_block(path, attribute: int = 8) -> list:
    '''
    传入绝对路径可以为字符串或列表，返回当前目录占有的盘块号列表
    文件C:/a/a.tx attribute=4
    文件夹C:/a    attribute=8
    如果没有找到则返回[-1]
    '''
    if type(path) is str:
        if path[-1] == '/':
            path = path[:-1]
        path_list = path.split('/')
    else:
        path_list = path
    driver = path_list[0]
    # 文件路径和文件名需要分开匹配
    if attribute != 8:
        file_name = path_list[-1]
        name, ext = file_name.split('.')
        name = format_name(name)
        ext = format_ext(ext)
        path_list = path_list[:-1]
    # 指针指向根目录
    parent_block = 2
    data = open_disk(driver)
    # 匹配到查找目标第一个拥有的文件块
    for item in path_list[1:]:
        is_find = False
        while True:
            # 在当前目录块做匹配，如果没有找到对应的文件则返回-1
            for inner_pointer in range(8):
                # 文件名相等
                item = format_name(item)
                if item == data[parent_block][inner_pointer*8: inner_pointer*8+3]:
                    # 匹配到的文件夹
                    if data[parent_block][inner_pointer*8+5] == 8:
                        parent_block = data[parent_block][inner_pointer*8 + 6]
                        is_find = True
                        break
            # 当前文件夹没有使用后续表项
            if data[parent_block//64][parent_block % 64] == 129 or is_find:
                break
            parent_block = data[parent_block//64][parent_block % 64]
        if not is_find and attribute != 8:
            break
        elif not is_find and attribute == 8:
            return (-1)
    # 如果目标是文件，最后要在当前目录块做匹配，如果没有找到对应的文件则返回-1
    if attribute != 8:
        is_find = False
        while True:
            # 在当前目录块做匹配，如果没有找到对应的文件则返回-1
            for inner_pointer in range(8):
                # 文件名和扩展名相等
                start = inner_pointer*8
                if name == data[parent_block][start: start+3] and ext == data[parent_block][start+3: start+5]:
                    # 匹配到的文件夹
                    parent_block = data[parent_block][inner_pointer*8 + 6]
                    is_find = True
                    break
            # 当前文件夹没有使用后续表项
            if data[parent_block//64][parent_block % 64] == 129 or is_find:
                break
            parent_block = data[parent_block//64][parent_block % 64]
        if not is_find:
            return [-1]
    # 找出本文件所有拥有的表项
    ans = [parent_block]
    while data[parent_block//64][parent_block % 64] != 129:
        parent_block = data[parent_block//64][parent_block % 64]
        ans.append(parent_block)
    return ans


# 获取指针
def get_pointer(path: str, attribute: int = 8) -> tuple:
    '''
    传入文件路径，如
    C:/a
    C:/a.tx
    返回文件控制块所在的位置，以及文件控制块
    (parent_block, inner_pointer, FCB)
    '''
    if type(path) is str:
        if path[-1] == '/':
            path = path[:-1]
        path_list = path.split('/')
    else:
        path_list = path
    driver = path_list[0]
    # 文件路径和文件名需要分开匹配
    if attribute != 8:
        file_name = path_list[-1]
        name, ext = file_name.split('.')
        name = format_name(name)
        ext = format_ext(ext)
        path_list = path_list[:-1]
    # 指针指向根目录
    parent_block = 2
    data = open_disk(driver)
    # 匹配到查找目标第一个拥有的文件块
    for item in path_list[1:]:
        is_find = False
        while True:
            # 在当前目录块做匹配，如果没有找到对应的文件则返回-1
            for inner_pointer in range(8):
                # 文件名相等
                item = format_name(item)
                if item == data[parent_block][inner_pointer*8: inner_pointer*8+3]:
                    # 匹配到的文件夹
                    if data[parent_block][inner_pointer*8+5] == 8:
                        is_find = True
                        break
            # 当前文件夹没有使用后续表项
            if data[parent_block//64][parent_block % 64] == 129 or is_find:
                break
            parent_block = data[parent_block//64][parent_block % 64]
        if not is_find and attribute != 8:
            break
        elif not is_find and attribute == 8:
            return (-1)
    # 如果目标是文件，最后要在当前目录块做匹配，如果没有找到对应的文件则返回-1
    if attribute != 8:
        is_find = False
        while True:
            # 在当前目录块做匹配，如果没有找到对应的文件则返回-1
            for inner_pointer in range(8):
                # 文件名和扩展名相等
                start = inner_pointer*8
                if name == data[parent_block][start: start+3] and ext == data[parent_block][start+3: start+5]:
                    # 匹配到的文件夹
                    is_find = True
                    break
            # 当前文件夹没有使用后续表项
            if data[parent_block//64][parent_block % 64] == 129 or is_find:
                break
            parent_block = data[parent_block//64][parent_block % 64]
        if not is_find:
            return [-1]
    return (parent_block, inner_pointer, data[parent_block][inner_pointer*8: inner_pointer*8+8])


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
def divide(val, length: int = 64) -> list:
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
        'name': str,
        'ext': str,
        'time': str,
        'attribute': int,
        'address': int,
        'length': int
    }
    '''
    if value[0] == 130:
        return None
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


# 把二位坐标转化为一维坐标
def get_position(block_pointer: int, inner_pointer: int) -> int:
    return block_pointer*66 + inner_pointer * 8


# TODO 查重
def duplicate_checking(path: str, name, attribute: int = 8) -> bool:
    '''
    检查要创建的文件或者文件夹是否已经存在
    attribute默认为8代表文件夹
    否则为文件
    判断是否重名会连扩展名包括在内一起判断
    '''
    children = list_dir(path)
    name = format_name(name)
    for child in children:
        if format_name(child['name']) == name:
            if child['attribute'] == attribute:
                return True
            if child['attribute'] != 8 and attribute != 8:
                return True
    return False


# 规范名字
def format_name(name) -> bytes:
    '''
    传入字符串或bytes
    返回长度为3的bytes
    '''
    if type(name) is str:
        name = name.encode()
    while len(name) < 3:
        name += ' '.encode()
    return name


# 规范扩展名
def format_ext(ext) -> bytes:
    '''
    传入长度小于3的扩展名，如 tx，t，ex
    返回长度为2的bytes
    '''
    if type(ext) is str:
        ext = ext.encode()
    while len(ext) < 2:
        ext += ' '.encode()
    return ext


if __name__ == '__main__':
    temp_file = {
        'path': 'C:',
        'name': 'a',
        'ext': 'tx',
        'text': '大大大苏打    12313',
        'attribute': 4
    }
    # 打印磁盘
    # print_disk('c')

    # 打开磁盘
    # print(open_disk())

    # 格式化磁盘
    # format_disk()

    # 测试文件夹转换bytes
    # for i in range(8):
    #     print(dirname_to_bytes('aa', i), len(dirname_to_bytes('aa', i)))

    # 测试新建文件
    # create_dir('C:/a')
    # for i in range(120):
    #     print(create_dir('C:/a/'+str(i)))

    # 测试获取文件块
    print(get_block('C:/a.tx', 4))

    # 读取文件列表
    # print(list_dir('C:/'))

    # 字符串分割
    # print(divide('1'*123))
    # a = divide('1'*70)

    # 新建文件
    # print(create_file(temp_file))

    # 文件打开测试
    print(open_file('C:/a/a.tx'))

    # 获取指针测试
    print(get_pointer('C:/a/aa.t', 4))
