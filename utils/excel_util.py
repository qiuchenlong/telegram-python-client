import xlrd2



class ExcelUtil:

    def __init__(self):
        pass

    def read_file(self, file_path):
        # 打开excel表格
        data_excel = xlrd2.open_workbook(file_path)
        # 获取所有sheet名称
        names = data_excel.sheet_names()
        # 获取book中的sheet工作表的三种方法,返回一个xlrd.sheet.Sheet()对象
        table = data_excel.sheets()[0]     # 通过索引顺序获取sheet
        # table = data_excel.sheet_by_index(sheetx=0)     # 通过索引顺序获取sheet
        # table = data_excel.sheet_by_name(sheet_name='Sheet1')    # 通过名称获取
        # excel工作表的行列操作
        # n_rows = table.nrows    # 获取该sheet中的有效行数
        # n_cols = table.ncols    # 获取该sheet中的有效列数
        # row_list = table.row(rowx=0)    # 返回某行中所有的单元格对象组成的列表
        # cols_list = table.col(colx=0)    # 返回某列中所有的单元格对象组成的列表
        # # 返回某行中所有单元格的数据组成的列表
        # row_data=table.row_values(0,start_colx=0,end_colx=None)
        # # 返回某列中所有单元格的数据组成的列表
        # cols_data=table.col_values(0,start_rowx=0,end_rowx=None)
        # row_lenth=table.row_len(0)   # 返回某行的有效单元格长度
        # # excel工作表的单元格操作
        # row_col=table.cell(rowx=0,colx=0) # 返回单元格对象
        # row_col_data=table.cell_value(rowx=0,colx=0) # 返回单元格中的数据

        list = []
        n_rows = table.nrows
        for i in range(1, n_rows):
            row_list = table.row_values(rowx=i)
            list.append(row_list)

        return list