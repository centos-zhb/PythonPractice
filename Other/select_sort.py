def select_sort(lists):
    # 直接选择排序
    count = len(lists)
    for i in range(0,count):
        min = i
        for j in range(i+1,count):
            if lists[min] > lists[j]:
                min = j
        temp = lists[min]
        lists[min] = lists[i]
        lists[i] = temp
    return lists