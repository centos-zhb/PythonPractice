def bubble_sort(lists):
    # 冒泡排序
    count = len(lists)
    for i in range(0,count):
        for j in range(i+1,count):
            if lists[i]>lists[j]:
                temp = lists[j]
                lists[j] = lists[i]
                lists[i] = temp
    return lists