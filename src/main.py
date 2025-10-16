import flet as ft
from typing import List
from datetime import datetime
from license.license import LicenseManager
from model.db import SQLiteManager, License

def main(page: ft.Page):
    page.title = "激活码授权"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 许可证
    lc = LicenseManager(24)
    # 初始化数据库
    db = SQLiteManager()
    db.setup()
        
    # 表单字段
    fingerprint: str = ""
    def id_field_change(e: ft.ControlEvent):
        nonlocal fingerprint
        fingerprint = e.data
    id_field = ft.TextField(
        label="指纹",
        width=300,
        autofocus=True,
        on_change=id_field_change
    )
    unit: str = ""
    def unit_field_change(e: ft.ControlEvent):
        nonlocal unit
        unit = e.data
    unit_field = ft.Dropdown(
        label="单位",
        width=300,
        options=[
            ft.dropdownm2.Option(key="month",text="月"),
            ft.dropdownm2.Option(key="year",text="年"),
        ],
        on_change=unit_field_change
    )
    
    period:int = 1
    def period_field_change(e: ft.ControlEvent):
        nonlocal period
        period = e.control.value
    period_field = ft.Slider(
        min=1,
        max=12,
        divisions=11,
        label="{value}",
        on_change=period_field_change,
    )

    def apply_license_dialog_to_db(e: ft.ControlEvent):
        # 确认数据，添加到数据库
        license_info = lc.generate_license(fingerprint, unit, period,)
        info = lc.decrypt_data(license_info)
        db.create_license(
            fingerprint=fingerprint,
            unit=unit,
            period=period,
            gen_timestamp=info['gen_timestamp'],
            expire_timestamp=info['expire_timestamp'],
            license=license_info,
        )
        
        # 更新页面
        update_datalist(db.list_license())
        
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
    
    __tables = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("指纹")),
                    ft.DataColumn(ft.Text("单位")),
                    ft.DataColumn(ft.Text("周期")),
                    ft.DataColumn(ft.Text("申请日期")),
                    ft.DataColumn(ft.Text("到期日期")),
                    ft.DataColumn(ft.Text("证书")),
                    ft.DataColumn(ft.Text("操作")),
                ],
                rows=[],
            )
    
    # 更新数据
    def update_datalist(infos: List[License]):
        # 根据模型数据重建表格行
        __tables.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(lic.device_fingerprint, width=200, overflow=ft.TextOverflow.VISIBLE)),
                    ft.DataCell(ft.Text(lic.unit)),
                    ft.DataCell(ft.Text(lic.period)),
                    ft.DataCell(ft.Text(datetime.fromtimestamp(lic.gen_timestamp))),
                    ft.DataCell(ft.Text(datetime.fromtimestamp(lic.expire_timestamp))),
                    ft.DataCell(ft.Text(lic.license, width=200)),
                    ft.DataCell(ft.ElevatedButton(text="复制证书", on_click=lambda a: page.set_clipboard(lic.license))),
                ],
            ) for lic in infos
        ]
    
    app_tabs = ft.Tabs(
        expand=True,
        animation_duration=300,
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
                                    on_click=lambda e:page.open(apply_license_dialog)
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        __tables
                    ]
                )
            )
        ]
    )

    update_datalist(db.list_license())
    page.add(app_tabs)
    
if __name__ == "__main__":
    ft.app(main)
