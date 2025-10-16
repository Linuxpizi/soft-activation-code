import flet as ft
import datetime

class DataEntryApp:
    def __init__(self):
        self.data_list = []
        
    def main(self, page: ft.Page):
        page.title = "数据添加确认对话框"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.scroll = ft.ScrollMode.ADAPTIVE
        
        # 对话框控件
        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("确认添加"),
            content=ft.Text("您确定要将这些数据添加到数据库吗？"),
            actions=[
                ft.TextButton("取消", on_click=self.close_dialog),
                ft.TextButton("确认", on_click=self.confirm_add_data),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # 表单控件
        self.name_field = ft.TextField(
            label="姓名",
            hint_text="请输入姓名",
            width=300
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
        
        # 数据表格
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("姓名")),
                ft.DataColumn(ft.Text("邮箱")),
                ft.DataColumn(ft.Text("年龄")),
                ft.DataColumn(ft.Text("添加时间")),
            ],
            rows=[],
        )
        
        # 主界面布局
        page.add(
            ft.Column(
                controls=[
                    ft.Text("数据添加表单", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    self.name_field,
                    self.email_field,
                    self.age_field,
                    ft.Container(height=20),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "添加数据",
                                icon=ft.Icons.ADD,
                                on_click=self.show_confirm_dialog
                            ),
                            ft.ElevatedButton(
                                "清空表单",
                                icon=ft.Icons.CLEAR,
                                on_click=self.clear_form
                            ),
                        ]
                    ),
                    ft.Container(height=30),
                    ft.Text("已添加的数据", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    ft.Container(
                        content=self.data_table,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=5,
                        padding=10,
                    )
                ]
            )
        )
    
    def show_confirm_dialog(self, e):
        # 验证表单数据
        if not self.name_field.value:
            self.show_snackbar("请输入姓名")
            return
        if not self.email_field.value:
            self.show_snackbar("请输入邮箱")
            return
        if not self.age_field.value:
            self.show_snackbar("请输入年龄")
            return
        
        # 显示确认对话框
        e.page.dialog = self.confirm_dialog
        self.confirm_dialog.open = True
        e.page.update()
    
    def close_dialog(self, e):
        e.page.dialog.open = False
        e.page.update()
    
    def confirm_add_data(self, e):
        # 关闭对话框
        e.page.dialog.open = False
        
        # 添加数据到列表（模拟数据库）
        new_data = {
            "name": self.name_field.value,
            "email": self.email_field.value,
            "age": self.age_field.value,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data_list.append(new_data)
        
        # 更新数据表格
        self.update_data_table(e.page)
        
        # 显示成功消息
        self.show_snackbar(f"成功添加数据: {self.name_field.value}")
        
        # 清空表单
        self.clear_form(e)
    
    def update_data_table(self, page):
        # 清空现有行
        self.data_table.rows.clear()
        
        # 添加数据行
        for data in self.data_list:
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(data["name"])),
                        ft.DataCell(ft.Text(data["email"])),
                        ft.DataCell(ft.Text(data["age"])),
                        ft.DataCell(ft.Text(data["timestamp"])),
                    ]
                )
            )
        
        page.update()
    
    def clear_form(self, e):
        self.name_field.value = ""
        self.email_field.value = ""
        self.age_field.value = ""
        e.page.update()
    
    def show_snackbar(self, message):
        # 这个方法需要页面引用，我们稍后会在main方法中设置
        if hasattr(self, 'page_ref'):
            self.page_ref.show_snackbar(ft.SnackBar(content=ft.Text(message)))

# 运行应用
def main(page: ft.Page):
    app = DataEntryApp()
    app.page_ref = page  # 保存页面引用用于显示SnackBar
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main)