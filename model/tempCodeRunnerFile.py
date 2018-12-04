def print_disk(disk: str = 'c', *lines):
    '''
    传入磁盘名，打印出磁盘内所有信息
    '''
    with open('virtual_disk_'+disk, 'rb') as d:
        f = d.read()
    ans = divide(f, 66)
    for index, i in enumerate(list(ans[3])):
        print(index, i)
print_disk()