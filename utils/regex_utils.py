import re


def group_and_split(text, group_re, split_re):

    matches = re.finditer(group_re, text, re.MULTILINE)
    groups = []
    for _, match in enumerate(matches):
        for i in range(len(match.groups())):
            groups.append(match.group(i + 1))

    splits = []
    i = 0
    for split in re.split(split_re, text):
        if len(split.strip()) > 0:
            splits.append((split.strip(), groups[i]))
            i += 1
    return groups, splits