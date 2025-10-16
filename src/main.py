import flet as ft

def main(page: ft.Page):
    page.title = "激活码授权"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    
    # 表单字段
    id_field = ft.TextField(
        label="指纹",
        width=300,
        autofocus=True
    )
    
    unit_field = ft.TextField(
        label="单位",
        width=300
    )
    
    period_field = ft.TextField(
        label="周期",
        width=300,
        input_filter=ft.NumbersOnlyInputFilter()
    )

    def apply_license_dialog_to_db(e: ft.ControlEvent):
        # 确认数据，添加到数据库
                
        
        # 关闭对话框
        page.close(apply_license_dialog)
           
    apply_license_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("申请证书"),
        content=ft.Column(
            controls=[
                id_field,
                unit_field,
                period_field
            ]
        ),
        actions=[
            ft.TextButton("确认", on_click=apply_license_dialog_to_db),
            ft.TextButton("取消", on_click=lambda e: page.close(apply_license_dialog)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    tab = ft.Tabs(
        selected_index=1,
        tabs=[
            ft.Tab(
                text="证书授权",
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("证书管理", size=24, weight=ft.FontWeight.BOLD),
                                ft.ElevatedButton(
                                    "申请证书",
                                    # icon=ft.Icons.ADD,
                                    on_click=lambda e:page.open(apply_license_dialog)
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("指纹")),
                                ft.DataColumn(ft.Text("姓名")),
                                ft.DataColumn(ft.Text("邮箱")),
                            ],
                            rows=[
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(ft.Text("John")),
                                        ft.DataCell(ft.Text("Smith")),
                                        ft.DataCell(ft.Text("43")),
                                        ],
                                    ),
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(ft.Text("Jack")),
                                        ft.DataCell(ft.Text("Brown")),
                                        ft.DataCell(ft.Text("19")),
                                    ],
                                ),
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(ft.Text("Alice")),
                                        ft.DataCell(ft.Text("Wong")),
                                        ft.DataCell(ft.Text("25")),
                                    ],
                                ),
                            ],
                        ),
                    ]
                )
            )
        ]
    )

    page.add(tab)
    
if __name__ == "__main__":
    ft.app(main)
