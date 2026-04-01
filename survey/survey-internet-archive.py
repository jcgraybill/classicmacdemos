from internetarchive import get_item, search_items, get_files

# https://archive.org/developers/internetarchive/python-lib.html

item = get_item("macworld-cd-wwdc-2005")
print(item.metadata)

search = search_items('collection:macworld-cds')
for result in search:
    print(result['identifier'])
    fnames = [f.name for f in get_files(result['identifier'], glob_pattern='*iso')]
    print(fnames)

#    item = get_item(result['identifier'])
#    print(item.metadata)

