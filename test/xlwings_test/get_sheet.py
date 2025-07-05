import xlwings as xw
app = xw.apps.active
wb = wb = app.books.active
#print([s.name for s in wb.sheets])
my_list = [s.name for s in wb.sheets]
target_elements = ['2308', '3711', '8926', '2480', '2912', '0050', '0052', '0056', '006208', '00690', '00692', '00701', '00713', '00728', '00730', '00731', '00850', '00878', '00881', '00888']

# 创建字典以加快查找
target_dict = {target: True for target in target_elements}

for i, element in enumerate(my_list):
    for target in target_dict:
        if target in element:
            print(f"Element '{element}' contains target '{target}' at position {i}")
            print(wb.sheets[i].name)