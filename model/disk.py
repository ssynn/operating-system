
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
    if duplicate_checking(info['path'], info['name']+'.'+info['ext'], info['attribute']):
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

    # 数据长度超过255则非法
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


# 删除文件
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
    path = format_path(path)
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


# 修改文件, 内容
def modify_file(path: str, new_text: str) -> bool:
    '''
    传入文件路径和新内容
    删除原来的文件
    新建文件
    '''
    _file = open_file(path)
    if not _file:
        return False
    _file['text'] = new_text
    if delete_file(path):
        return create_file(_file)
    return False


# 修改文件属性
def change(path: str, attr: int) -> bool:
    '''
    传入文件路径和新的属性
    '''
    path_list = path.split('/')
    father_block, inner_pointer, FCB = get_pointer(path)
    if father_block == -1:
        return False
    new_fcb = list(FCB)
    new_fcb[6] = attr
    new_fcb = bytes(new_fcb)
    with open('virtual_disk_' + path_list.lower()[0], 'rb+') as f:
        f.seek(father_block*66+inner_pointer*8)
        f.write(new_fcb)
    return True


# 打开文件
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
    name, ext = file_name_split(name)
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


# 复制文件
def copy_file(path: str, new_path: str) -> bool:
    '''
    传入原始地址名和新地址名
    path包含源文件名
    new_path为文件夹路径，不包含文件名
    读出原有的文件信息
    查重
    在目标位置建立文件
    '''
    _file = open_file(path)
    if not _file:
        return False
    _file['path'] = new_path
    return create_file(_file)


# 用文件信息生成8位bytes
def file_to_bytes(name: bytes, ext: str, attr: int, address: int, length: int) -> bytes:
    return name + '{0:2}'.format(ext).encode() + bytes([attr, address, length])


# 移动文件
def move_file(path: str, new_path: str) -> bool:
    '''
    删了重建，
    path包含源文件名
    新路径为文件夹路径，不包含文件名
    '''
    _file = open_file(path)
    if not _file:
        return False
    _file['path'] = new_path
    if delete_file(path):
        return create_file(_file)
    return False


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
    if blocks[0] == -1:
        return []
    # 把当前文件夹拥有的盘块读入
    block_list = []
    with open('virtual_disk_' + path_list[0].lower()[0], 'rb+') as f:
        for b in blocks:
            f.seek(b*66)
            block_list.append(f.read(64))

    # 把每个盘块分割成独立的FCB
    dir_list = []
    for block in block_list:
        for i in range(8):
            dir_list.append(converter(block[i*8: i*8+8]))
            if dir_list[-1] is None:
                dir_list.pop(-1)

    # 读入每个FCB的时间
    with open('virtual_disk_' + path_list[0].lower()[0], 'rb+') as f:
        for _dir in dir_list:
            if _dir['attribute'] == 8:
                f.seek(_dir['address']*66 + 57)
            else:
                f.seek(_dir['address']*66)
            _dir['time'] = f.read(5)
    return dir_list


# 修改文件夹
def modify_dir(path: str, new_name: str) -> bool:
    '''
    传入原始路径和文件夹的新名字
    '''
    path_list = path.split('/')
    father_block, inner_pointer, FCB = get_pointer(path)
    if father_block == -1:
        return False
    new_fcb = dirname_to_bytes(new_name, FCB[6])
    with open('virtual_disk_' + path_list.lower()[0], 'rb+') as f:
        f.seek(father_block*66+inner_pointer*8)
        f.write(new_fcb)
    return True


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
    path = format_path(path)
    path_list = path.split('/')
    name = format_name(path_list[-1])

    # 获取所有和子项
    children = list_dir(path)

    # 把当前目录内的子项删除
    for child in children:
        if child['attribute'] == 8:
            delete_dir(path+'/'+child['name'].strip())
        else:
            delete_file(path+'/'+child['name'].strip()+'.'+child['ext'])

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

    # 规范文件名
    new_dir = format_name(new_dir)

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

    # 父文件块已满, 当前是根目录，不能再申请文件夹
    if block_pointer == 8 and len(path_list) == 1:
        return False

    # 当前文件夹为普通文件夹，已满, 则再申请一个文件夹
    if block_pointer >= 7 and len(path_list) > 1:
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
def get_time() -> bytes:
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


# 复制文件夹
def copy_dir(path: str, new_path: str) -> bool:
    '''
    在新路径建立新文件夹
    把文件复制进新文件夹
    对子文件夹调用copy_dir
    '''
    # 在目标文件夹内建立所新文件夹
    if not create_dir(new_path):
        return False

    # 获取到文件夹内所有内容
    file_list = list_dir(path)
    if len(file_list) == 0:
        return False

    # 复制所有文件到新文件夹内
    for item in file_list:
        if item['attribute'] != 8:
            copy_file(
                path+'/'+item['name']+'.'+item['ext'],
                new_path+'/'+item['name']+'.'+item['ext']
            )

    # 复制所有子文件夹到新文件夹内
    for item in file_list:
        if item['attribute'] != 8:
            copy_dir(
                path+'/'+item['name'],
                new_path+'/'+item['name']
            )

    return True


# 移动文件夹 TODO 优化同一磁盘内的移动
def move_dir(path: str, new_path: str) -> bool:
    '''
    传入旧地址和新地址
    如果在同一磁盘内:
    找到原先目标的FCB位置
    在新位置申请FCB
    把FCB拷贝到新位置
    删除原来位置的FCB
    不在同一个磁盘内:
    复制文件夹
    删除
    '''
    if not copy_dir(path, new_path):
        return False
    return delete_dir(path)


# TODO 通用移动方法
def move(path: str, new_path: str) -> bool:
    '''
    首先解析文件类型
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
        path = format_path(path)
        path_list = path.split('/')
        if path in ('C:', 'D:', 'c:', 'd:'):
            return [2]
    else:
        path_list = path
        if len(path) == 1 and path[0] in ('C:', 'D:', 'c:', 'd:'):
            return [2]

    # 获取文件的起始盘块
    parent_block = get_pointer(path, attribute)
    if parent_block[0] == -1:
        return [-1]

    # 读入磁盘
    data = open_disk(path_list[0])

    # 获取自己拥有的第一个块号
    self_block = data[parent_block[0]][parent_block[1]*8 + 6]

    # 找出本文件所有拥有的表项
    ans = [self_block]
    while data[self_block//64][self_block % 64] != 129:
        self_block = data[self_block//64][self_block % 64]
        ans.append(self_block)
    return ans


# 获取指向自己文件控制块的指针
def get_pointer(path: str, attribute: int = 8) -> tuple:
    '''
    传入文件路径，如
    C:/a
    C:/a.tx
    返回文件控制块所在的位置，以及文件控制块
    (parent_block, inner_pointer, FCB)
    目标名称与路径名称应该分开 如C:/a/a.tx 应该分为C:/a a.tx
    其中路径进行匹配找到父文件块
    最后再父文件块内匹配找到目标的文件控制块
    '''
    if type(path) is str:
        path = format_path(path)
        path_list = path.split('/')
    else:
        path_list = path
    driver = path_list[0]
    target_name = path_list[-1]
    path_list = path_list[:-1]
    name, ext = '', ''

    # 文件路径和文件名需要分开匹配
    if attribute != 8:
        name, ext = file_name_split(target_name)
        name = format_name(name)
        ext = format_ext(ext)
    else:
        name = format_name(target_name)

    # 指针指向根目录
    parent_block = 2
    inner_pointer = 0
    data = open_disk(driver)

    # 匹配父目录所在的文件块
    for item in path_list[1:]:
        parent_block, inner_pointer = get_inner_pointer(
            parent_block,
            data,
            format_name(item)
        )
        if parent_block == -1:
            return (-1,)
        parent_block = data[parent_block][inner_pointer*8+6]

    # 匹配目标在父文件块内的位置
    inner_pointer = get_inner_pointer(
        parent_block,
        data,
        name,
        attribute,
        ext
    )[1]

    if inner_pointer == -1:
        return (-1,)

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


# 获取目标在父文件块内的位置
def get_inner_pointer(start_pointer: int, data: list, name: str, attribute: int = 8, ext: str = '') -> int:
    '''
    传入文件块的首地址，需要匹配的目标名称，磁盘内容信息，文件属性
    如果只传入三前个参数则默认为匹配文件夹
    磁盘内容为128行66列的数组
    返回(父盘块号，目标在文件中的位置)
    如果没有找到返回(-1, -1)
    '''
    name = format_name(name)
    ext = format_ext(ext)

    # 先获取父文件所有的盘块
    blocks = []
    while start_pointer != 129:
        blocks.append(start_pointer)
        start_pointer = data[start_pointer//64][start_pointer % 64]

    for block in blocks:
        # 在每一个块内进行匹配
        for inner_pointer in range(8):
            start = inner_pointer*8
            # 文件夹匹配
            if attribute == 8 and data[block][start+5] == 8 and name == data[block][start: start+3]:
                return (block, inner_pointer)
                break
            # 文件匹配
            if attribute != 8 and data[block][start+5] != 8 and name == data[block][start: start+3] and ext == data[block][start+3: start+5]:
                return (block, inner_pointer)
                break
    return (-1, -1)


# 查重
def duplicate_checking(path: str, name: str, attribute: int = 8) -> bool:
    '''
    检查要创建的文件或者文件夹是否已经存在
    path为父文件夹路径
    name为除路径以外的完整的文件名包括扩展名
    attribute默认为8代表文件夹
    存在重复则返回True
    如果文件后缀名为空则不能与文件夹同名
    文件夹也不能与后缀名为空的文件同名
    '''
    path = format_path(path)
    # 检查是否有同名同属性的东西
    if get_pointer(path+'/'+name, attribute)[0] != -1:
        return True

    # 如果为文件夹则不能与后缀名为空的文件同名
    if attribute == 8:
        if get_pointer(path+'/'+name, 4)[0] != -1:
            return True

    name, ext = file_name_split(name)
    print(name, ext)
    # 如果文件后缀名为空则不能与文件夹内的文件夹同名
    if ext == '' and attribute != 8:
        if get_pointer(path+'/'+name, 8)[0] != -1:
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


# 规范路径
def format_path(path: str) -> str:
    if path[-1] == '/':
        return path[:-1]
    return path


# 文件名分割
def file_name_split(name: str) -> tuple:
    '''
    传入文件名如a.tx a
    返回('a', 'tx') ('a', '')
    '''
    name = name.split('.')
    if len(name) == 2:
        return tuple(name)
    return (name[0], '')


# TODO 文件路径解析器
def path_parser(path: str, args: str) -> list:
    '''
    传入当前路径和参数
    如果args是绝对路径则返回args
    如果args是相对路径则返回path与args拼接后的路径
    '''
    pass


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
    # print(create_dir('C:/a'))
    # for i in range(120):
    #     print(create_dir('C:/a/'+str(i)))

    # 测试获取文件块
    # print(get_block('C:/', 4))

    # 读取文件列表
    # print(list_dir('C:/'))

    # 字符串分割
    # print(divide('1'*123))
    # a = divide('1'*70)

    # 新建文件
    # print(create_file(temp_file))

    # 文件打开测试
    # print(open_file('C:/a/a.tx'))

    # 获取指针测试
    # print(open_disk()[:2])
    # # print(get_pointer('C:'))

    # 查重测试
    # print(duplicate_checking('C:/', 'a.tx', 4))
