def same_diff_pairs(arr, diff):
    """ returns all pairs in the arr with difference of diff"""
    complementory_numbers = {}
    same_diff_pairs = []
    for num in arr:
        complement = num + diff if diff > 0 else num - diff
        complement_lookup = complementory_numbers.get(num)
        if complement_lookup is not None:
            same_diff_pairs.append((complement_lookup,num))
        complementory_numbers[complement] = num
        complementory_numbers[num] = complement
    return same_diff_pairs


print(same_diff_pairs([1, 3, 5], 2))
print(same_diff_pairs([1, 3, 5], -2))
print(same_diff_pairs([1, 3, 5], -4))
