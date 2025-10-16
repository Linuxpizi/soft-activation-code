import flet as ft
import datetime

class DataEntryApp:
    def __init__(self):
        self.data_list = []
        
    def main(self, page: ft.Page):
        page.title = "表单确认对话框"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.scroll = ft.ScrollMode.ADAPTIVE
        
        # 表单字段
        self.name_field = ft.TextField(
            label="姓名",
            hint_text="请输入姓名",
            width=300,
            autofocus=True
        )
        
        self.email_field = ft.TextField(
            label="邮箱",
            hint_text="请输入邮箱地址",
            width=300
        )
        
        self.age_field = ft.TextField(
            label="年龄",
            hint_text="请输入年龄",
            width=300,
            input_filter=ft.NumbersOnlyInputFilter()
        )
        
        # 表单对话框控件
        self.form_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("添加新数据"),
            content=ft.Column(
                controls=[
                    self.name_field,
                    self.email_field,
                    self.age_field,
                ],
                width=400,
                tight=True
            ),
            actions=[
                ft.TextButton("取消", on_click=self.close_dialog),
                ft.TextButton("确认添加", on_click=self.confirm_add_data),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # 成功提示对话框
        self.success_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("成功"),
            content=ft.Text("数据已成功添加到数据库！"),
            actions=[
                ft.TextButton("确定", on_click=self.close_success_dialog),
            ],
        )
        
        # 数据表格
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("姓名")),
                ft.DataColumn(ft.Text("邮箱")),
                ft.DataColumn(ft.Text("年龄")),
                ft.DataColumn(ft.Text("添加时间")),
                ft.DataColumn(ft.Text("操作")),
            ],
            rows=[],
        )
        
        # 主界面布局
        page.add(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("数据管理", size=24, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton(
                                "添加数据",
                                icon=ft.Icons.ADD,
                                on_click=self.open_form_dialog
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    ft.Container(
                        content=self.data_table,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=5,
                        padding=10,
                    ),
                    ft.Container(height=10),
                    ft.Text(f"总计: {len(self.data_list)} 条记录", size=14, color=ft.Colors.GREY_600),
                ]
            )
        )
    
    def open_form_dialog(self, e):
        # 清空表单
        self.name_field.value = ""
        self.email_field.value = ""
        self.age_field.value = ""
        
        # 显示表单对话框
        e.page.dialog = self.form_dialog
        self.form_dialog.open = True
        e.page.update()
    
    def close_dialog(self, e):
        e.page.dialog.open = False
        e.page.update()
    
    def close_success_dialog(self, e):
        e.page.dialog.open = False
        e.page.update()
    
    def validate_form(self):
        """验证表单数据"""
        errors = []
        
        if not self.name_field.value or len(self.name_field.value.strip()) < 2:
            errors.append("姓名至少需要2个字符")
            self.name_field.error_text = "姓名至少需要2个字符"
        else:
            self.name_field.error_text = None
            
        if not self.email_field.value or "@" not in self.email_field.value:
            errors.append("请输入有效的邮箱地址")
            self.email_field.error_text = "请输入有效的邮箱地址"
        else:
            self.email_field.error_text = None
            
        if not self.age_field.value:
            errors.append("请输入年龄")
            self.age_field.error_text = "请输入年龄"
        elif int(self.age_field.value) < 1 or int(self.age_field.value) > 120:
            errors.append("年龄必须在1-120之间")
            self.age_field.error_text = "年龄必须在1-120之间"
        else:
            self.age_field.error_text = None
            
        return len(errors) == 0, errors
    
    def confirm_add_data(self, e):
        # 验证表单
        is_valid, errors = self.validate_form()
        
        if not is_valid:
            # 显示第一个错误
            self.show_snackbar(f"表单验证失败: {errors[0]}")
            e.page.update()
            return
        
        # 关闭表单对话框
        e.page.dialog.open = False
        
        # 添加数据到列表（模拟数据库）
        new_data = {
            "id": len(self.data_list) + 1,
            "name": self.name_field.value.strip(),
            "email": self.email_field.value.strip(),
            "age": self.age_field.value,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data_list.append(new_data)
        
        # 更新数据表格
        self.update_data_table(e.page)
        
        # 显示成功对话框
        e.page.dialog = self.success_dialog
        self.success_dialog.open = True
        e.page.update()
    
    def delete_data(self, data_id, page):
        """删除数据"""
        self.data_list = [item for item in self.data_list if item["id"] != data_id]
        self.update_data_table(page)
        self.show_snackbar("数据已删除")
    
    def update_data_table(self, page):
        # 清空现有行
        self.data_table.rows.clear()
        
        # 添加数据行
        for data in self.data_list:
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(data["id"]))),
                        ft.DataCell(ft.Text(data["name"])),
                        ft.DataCell(ft.Text(data["email"])),
                        ft.DataCell(ft.Text(str(data["age"]))),
                        ft.DataCell(ft.Text(data["timestamp"])),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED_400,
                                tooltip="删除",
                                on_click=lambda e, data_id=data["id"]: self.delete_data(data_id, page)
                            )
                        ),
                    ]
                )
            )
        
        page.update()
    
    def show_snackbar(self, message):
        if hasattr(self, 'page_ref'):
            self.page_ref.show_snackbar(
                ft.SnackBar(
                    content=ft.Text(message),
                    duration=3000
                )
            )

# 运行应用
def main(page: ft.Page):
    app = DataEntryApp()
    app.page_ref = page  # 保存页面引用用于显示SnackBar
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main)