
# 所有和磁盘操作有关的方法都在此模块中
# 1.查询文件状态
#   1.1 创建时间
#   1.2 大小
#   1.3 名称
#   1.4 修改时间
#   1.5 文件路径
#   1.6 只读
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


# 磁盘属性
# 400个扇区
# 每个扇区64B
# 每个文件最大64B
# 系统占用40个扇区
# C盘从41开始到220结束
# D盘从221开始到400结束


# mes = {
#     'create_time': str,
#     'name': str,
#     'ext': str,
#     'path': str,
#     'size': int,            # 大小为64B的整数倍
#     'edit_time': str,
#     'read_only': int
# }

import time
import json


# 创建文件
def mkfile(mes: dict):
    file_tree = getTree()
    path = mes['path'].split('/')
    


# 创建文件夹
def mkdir(path: str):
    pass


# 删除文件
def rmfile(path: str):
    pass


# 删除文件夹
def rmdir(path: str):
    pass


# 获取文件列表
def listdir(path: str):
    pass


# 修改文件
def modifyfile(path: str, new_mes: dict):
    pass


# 修改文件夹
def modifydir(path: str, new_name: str):
    pass


# 获取磁盘信息
def getDiskMes():
    pass


# 获取文件信息
def getFileMes(path: str):
    pass


# 获取文件树
def getTree():
    ans = ""
    with open('virtual_disk', 'r+') as d:
        for i in range(40):
            ans += (d.readline()[:-1])
        p = len(ans) - 1
        while ans[p] != '}':
            p -= 1
        ans = ans[:p+1]

    root = json.loads(ans)
    return root


# 格式化磁盘
def formatDisk():
    with open('virtual_disk', 'w') as disk:
        for i in range(400):
            for j in range(64):
                disk.write('0')
            disk.write('\n')
    tree = {
        'root': ['C:', 'D:'],
        'END': 20,
        'size': 25600,          # 单位字节
        'allocated': 2560,
        'c_allocated': 0,
        'd_allocated': 0,
        'C:': [],
        'D:': [],
    }

    tree_json = json.dumps(tree)
    mes_list = divide(tree_json)

    with open('virtual_disk', 'r+') as d:
        for i in range(len(mes_list)):
            d.seek(66*i)
            d.writelines(mes_list[i])


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
    # formatDisk()
    # print(getTree())
    mes = {
        'create_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'name': 'a.txt',
        'ext': '.txt',
        'path': 'C:/a.txt',
        'size': '64',            # 大小为64B的整数倍
        'edit_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'read_only': 0
    }


