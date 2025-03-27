def merge_sort(books):
    if len(books) <= 1:
        return books
    
    mid = len(books) // 2
    left_half = merge_sort(books[:mid])
    right_half = merge_sort(books[mid:])
    
    return merge(left_half, right_half)

def merge(left, right):
    result = []
    left_index = right_index = 0
    
    while left_index < len(left) and right_index < len(right):
        if left[left_index].title < right[right_index].title:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1
            
    result.extend(left[left_index:])
    result.extend(right[right_index:])
    
    return result

def sort_books(books):
    return merge_sort(books)

def binary_search(books, target):
    left, right = 0, len(books) - 1
    while left <= right:
        mid = (left + right) // 2
        if books[mid].title == target:
            return books[mid]
        elif books[mid].title < target:
            left = mid + 1
        else:
            right = mid - 1
    return None
