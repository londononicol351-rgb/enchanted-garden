import flet as ft
from database import *

def main(page: ft.Page):
    page.title = "Enchanted Garden - Floristería Boutique"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 430
    page.window_height = 800
    
    crear_tablas()
    
    usuario = None
    carrito = []
    producto_editando = None

    LOGO_SRC = "logo.png"

    def toast(t):
        page.snack_bar = ft.SnackBar(ft.Text(t))
        page.snack_bar.open = True
        page.update()

    def cerrar_sesion(e=None):
        nonlocal usuario, carrito, producto_editando
        usuario = None
        carrito.clear()
        producto_editando = None
        toast("Sesión cerrada correctamente")
        login_view()

    def appbar(titulo):
        actions = []
        if usuario:
            actions.append(ft.IconButton(ft.Icons.HOME, tooltip="Inicio", on_click=lambda e: home()))
            
            num_items = sum(x["cantidad"] for x in carrito)
            stack_controls = [
                ft.IconButton(ft.Icons.SHOPPING_CART, tooltip="Carrito", on_click=lambda e: carrito_view())
            ]
            
            if num_items > 0:
                stack_controls.append(
                    ft.Container(
                        content=ft.Text(str(num_items), size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        bgcolor=ft.Colors.RED_500,
                        border_radius=10,
                        padding=3,
                        right=4,
                        top=4
                    )
                )

            actions.append(ft.Stack(stack_controls))
            actions.append(ft.IconButton(ft.Icons.LOGOUT, tooltip="Cerrar sesión", on_click=cerrar_sesion))

        return ft.AppBar(
            leading=ft.Container(
                padding=5,
                content=ft.Image(src=LOGO_SRC, width=35, height=35, fit="contain")
            ) if usuario else None,
            title=ft.Text(titulo, weight=ft.FontWeight.BOLD),
            center_title=True,
            bgcolor=ft.Colors.PURPLE_100,
            color=ft.Colors.PURPLE_900,
            actions=actions
        )

    def login_view(mensaje_inicial=""):
        page.clean()
        
        email = ft.TextField(
            label="Correo", 
            prefix_icon=ft.Icons.EMAIL,
            focused_border_color=ft.Colors.PURPLE_600
        )
        password = ft.TextField(
            label="Contraseña", 
            password=True, 
            can_reveal_password=True, 
            prefix_icon=ft.Icons.LOCK,
            focused_border_color=ft.Colors.PURPLE_600
        )
        
        lbl_mensaje = ft.Text(
            value=mensaje_inicial, 
            color=ft.Colors.GREEN_700 if "correctamente" in mensaje_inicial else ft.Colors.RED_600, 
            weight=ft.FontWeight.BOLD,
            size=13
        )
        
        def entrar(e):
            nonlocal usuario
            email.border_color = None
            email.bgcolor = None
            password.border_color = None
            password.bgcolor = None
            lbl_mensaje.value = ""
            
            e_val = email.value.strip() if email.value else ""
            p_val = password.value.strip() if password.value else ""

            if not e_val or not p_val:
                lbl_mensaje.value = "Por favor, completa todos los campos"
                lbl_mensaje.color = ft.Colors.RED_600
                if not e_val:
                    email.border_color = ft.Colors.RED_300
                    email.bgcolor = ft.Colors.RED_50
                if not p_val:
                    password.border_color = ft.Colors.RED_300
                    password.bgcolor = ft.Colors.RED_50
                page.update()
                return

            exito, codigo_error, datos_usuario = iniciar_sesion(e_val, p_val)

            if exito:
                usuario = datos_usuario
                home()
            else:
                lbl_mensaje.color = ft.Colors.RED_600
                if codigo_error == "CORREO_INCORRECTO":
                    lbl_mensaje.value = "El correo ingresado no existe o es incorrecto"
                    email.border_color = ft.Colors.RED_300
                    email.bgcolor = ft.Colors.RED_50
                elif codigo_error == "PASSWORD_INCORRECTO":
                    lbl_mensaje.value = "La contraseña es incorrecta"
                    password.border_color = ft.Colors.RED_300
                    password.bgcolor = ft.Colors.RED_50
                page.update()
                
        page.add(
            ft.Container(
                expand=True,
                padding=25,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Image(src=LOGO_SRC, width=160, height=160, fit="contain"),
                        ft.Text("Enchanted Garden", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_800),
                        ft.Text("Floristería Boutique - Flores de Cinta de Tela", size=13, color=ft.Colors.GREY_700),
                        ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                        lbl_mensaje,
                        email,
                        password,
                        ft.FilledButton("Iniciar sesión", icon=ft.Icons.LOGIN, on_click=entrar, width=300, bgcolor=ft.Colors.PURPLE_600, color=ft.Colors.WHITE),
                        ft.TextButton("Crear una cuenta", on_click=lambda e: registro_view()),

                    ]
                )
            )
        )

    def registro_view():
        page.clean()
        n = ft.TextField(label="Nombre completo")
        em = ft.TextField(label="Correo electrónico")
        pw = ft.TextField(label="Contraseña", password=True)
        d = ft.TextField(label="Dirección de envío")
        
        lbl_msg_reg = ft.Text(size=13, weight=ft.FontWeight.BOLD)
        
        def reg(e):
            em.border_color = None
            em.bgcolor = None
            
            ok, msg = registrar_usuario(n.value or "", em.value or "", pw.value or "", d.value or "")
            
            if ok:
                login_view(mensaje_inicial=msg)
            else:
                lbl_msg_reg.value = msg
                lbl_msg_reg.color = ft.Colors.RED_600
                em.border_color = ft.Colors.RED_300
                em.bgcolor = ft.Colors.RED_50
                page.update()
                
        page.add(
            appbar("Crear Cuenta"),
            ft.Container(
                padding=20,
                content=ft.Column([
                    lbl_msg_reg,
                    n, em, pw, d,
                    ft.FilledButton("Registrarme", on_click=reg, width=300, bgcolor=ft.Colors.PURPLE_600, color=ft.Colors.WHITE),
                    ft.TextButton("Volver al Inicio de Sesión", icon=ft.Icons.ARROW_BACK, on_click=lambda e: login_view())
                ])
            )
        )

    def navbar(active_index=0):
        items = [
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.LOCAL_FLORIST_OUTLINED, selected_icon=ft.Icons.LOCAL_FLORIST, label="Catálogo"),
            ft.NavigationBarDestination(icon=ft.Icons.RECEIPT_LONG_OUTLINED, selected_icon=ft.Icons.RECEIPT_LONG, label="Mis Pedidos")
        ]
        if usuario and usuario.get("rol") == "admin":
            items.append(ft.NavigationBarDestination(icon=ft.Icons.INVENTORY_2_OUTLINED, selected_icon=ft.Icons.INVENTORY_2, label="CRUD Admin"))
        
        def change(e):
            idx = e.control.selected_index
            if idx == 0: home()
            elif idx == 1: catalogo()
            elif idx == 2: mis_pedidos()
            elif idx == 3 and usuario.get("rol") == "admin": crud()
            
        return ft.NavigationBar(destinations=items, selected_index=active_index, on_change=change, bgcolor=ft.Colors.PURPLE_50)

    def home():
        page.clean()
        page.add(
            appbar("Enchanted Garden"),
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text(f"¡Hola, {usuario['nombre']}! 🌸", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_900),
                    ft.Text("Especialistas en arreglos de flores eternas hechas a mano con cinta de tela satinada."),
                    ft.Container(
                        height=150,
                        border_radius=20,
                        bgcolor=ft.Colors.PURPLE_100,
                        padding=15,
                        content=ft.Row([
                            ft.Image(src=LOGO_SRC, width=90, height=90, fit="contain"),
                            ft.Column([
                                ft.Text("Elegancia & Durabilidad", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_900),
                                ft.Text("Ramos personalizados\nque duran para siempre", size=12)
                            ], alignment=ft.MainAxisAlignment.CENTER)
                        ])
                    ),
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    ft.FilledButton("Ver Catálogo de Flores", icon=ft.Icons.STORE, on_click=lambda e: catalogo(), width=300, bgcolor=ft.Colors.PURPLE_600, color=ft.Colors.WHITE),
                    ft.OutlinedButton("Ver Mi Carrito", icon=ft.Icons.SHOPPING_CART, on_click=lambda e: carrito_view(), width=300)
                ])
            ),
            navbar(0)
        )

    def catalogo():
        page.clean()
        cards = []
        productos = obtener_productos()

        for p in productos:
            img = p["imagen"] if p.get("imagen") else "https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=500"
            cards.append(
                ft.Card(
                    elevation=3,
                    content=ft.Container(
                        padding=10,
                        content=ft.Row([
                            ft.Image(src=img, width=100, height=100, fit="cover", border_radius=10),
                            ft.Column(
                                expand=True,
                                controls=[
                                    ft.Text(p["nombre"], weight=ft.FontWeight.BOLD, size=15),
                                    ft.Text(f"Categoría: {p.get('categoria', 'Flores Eternas')}", size=11, color=ft.Colors.GREY_700),
                                    ft.Text(f"${p['precio']:,.2f}", weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_800, size=16),
                                    ft.Text(f"Disponibles: {p['stock']}", size=11)
                                ]
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD_SHOPPING_CART_ROUNDED,
                                icon_color=ft.Colors.PURPLE_700,
                                tooltip="Añadir al carrito",
                                on_click=lambda e, x=p: agregar_carrito(x)
                            )
                        ])
                    )
                )
            )
            
        page.add(
            appbar("Catálogo de Flores Eternas"),
            ft.Container(
                expand=True,
                padding=10,
                content=ft.Column([
                    ft.FilledButton("Volver al Inicio", icon=ft.Icons.ARROW_BACK, on_click=lambda e: home()),
                    ft.ListView(expand=True, spacing=8, controls=cards)
                ])
            ),
            navbar(1)
        )

    def agregar_carrito(p):
        for x in carrito:
            if x["id"] == p["id"]:
                x["cantidad"] += 1
                toast(f"Se incrementó la cantidad de '{p['nombre']}'")
                catalogo()
                return
        carrito.append({"id": p["id"], "nombre": p["nombre"], "precio": p["precio"], "cantidad": 1})
        toast(f"'{p['nombre']}' añadido al carrito")
        catalogo()

    def carrito_view():
        page.clean()
        total = sum(x["precio"] * x["cantidad"] for x in carrito)
        
        def cambiar_cantidad(item, delta):
            item["cantidad"] += delta
            if item["cantidad"] <= 0:
                carrito.remove(item)
            carrito_view()

        rows = []
        for x in carrito:
            rows.append(
                ft.Card(
                    content=ft.ListTile(
                        title=ft.Text(x["nombre"], weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(f"${x['precio']:,.2f} c/u"),
                        trailing=ft.Row(
                            width=140,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, on_click=lambda e, item=x: cambiar_cantidad(item, -1)),
                                ft.Text(str(x["cantidad"]), weight=ft.FontWeight.BOLD),
                                ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, on_click=lambda e, item=x: cambiar_cantidad(item, 1)),
                            ]
                        )
                    )
                )
            )

        def comprar(e):
            if not carrito:
                toast("El carrito está vacío")
                return
            if crear_pedido(usuario["id"], carrito):
                carrito.clear()
                toast("¡Pedido realizado con éxito! 🌸")
                mis_pedidos()
            else:
                toast("Ocurrió un error al procesar la compra")

        page.add(
            appbar("Mi Carrito de Compras"),
            ft.Container(
                expand=True,
                padding=15,
                content=ft.Column([
                    ft.FilledButton("Volver al Catálogo", icon=ft.Icons.ARROW_BACK, on_click=lambda e: catalogo()),
                    ft.Divider(),
                    ft.ListView(expand=True, spacing=5, controls=rows or [ft.Text("Tu carrito está vacío 🛒", size=16, color=ft.Colors.GREY_600)]),
                    ft.Divider(),
                    ft.Row([
                        ft.Text("Total:", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"${total:,.2f}", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_800)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.FilledButton("Finalizar Compra", icon=ft.Icons.CHECK_CIRCLE, on_click=comprar, width=350, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE)
                ])
            ),
            navbar(1)
        )

    def mis_pedidos():
        page.clean()
        pedidos = obtener_pedidos_usuario(usuario["id"])
        cards = []

        for p in pedidos:
            items_str = "\n".join([f"• {it['cantidad']}x {it['nombre']} (${it['precio_unitario']:,.2f})" for it in p["items"]])
            cards.append(
                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"Pedido #{p['id']}", weight=ft.FontWeight.BOLD, size=16),
                                ft.Container(
                                    content=ft.Text(p['estado'].upper(), size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.Colors.GREEN_600 if p['estado'] == 'completado' else ft.Colors.ORANGE_600,
                                    padding=5, border_radius=5
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"Fecha: {p['fecha_pedido']}", size=11, color=ft.Colors.GREY_600),
                            ft.Divider(),
                            ft.Text("Detalle de Compra:", weight=ft.FontWeight.BOLD, size=12),
                            ft.Text(items_str if items_str else "Sin detalles", size=12),
                            ft.Divider(),
                            ft.Row([
                                ft.Text("Total Pagado:", weight=ft.FontWeight.BOLD),
                                ft.Text(f"${p['total']:,.2f}", weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_800, size=16)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ])
                    )
                )
            )

        page.add(
            appbar("Mis Compras Realizadas"),
            ft.Container(
                expand=True,
                padding=10,
                content=ft.Column([
                    ft.ListView(expand=True, spacing=10, controls=cards or [
                        ft.Container(padding=20, content=ft.Text("Aún no has realizado pedidos 🌸", size=16))
                    ])
                ])
            ),
            navbar(2)
        )

    def crud():
        nonlocal producto_editando
        page.clean()
        
        def cambiar_estado_admin(pid, estado):
            cambiar_estado_pedido(pid, estado)
            toast(f"Pedido #{pid} actualizado a {estado}")
            crud()

        pedidos_globales = obtener_todos_pedidos()
        pedidos_cards = []
        for p in pedidos_globales:
            items_str = "\n".join([f"• {it['cantidad']}x {it['nombre']} (${it['precio_unitario']:,.2f})" for it in p["items"]])
            pedidos_cards.append(
                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"Pedido #{p['id']} - {p['cliente']}", weight=ft.FontWeight.BOLD, size=14),
                                ft.Text(f"${p['total']:,.2f}", weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_800)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"Cliente: {p['email']} | {p['fecha_pedido']}", size=11, color=ft.Colors.GREY_600),
                            ft.Text(items_str, size=12),
                            ft.Row([
                                ft.FilledButton("Marcar Completado", icon=ft.Icons.CHECK, 
                                                on_click=lambda e, x=p['id']: cambiar_estado_admin(x, "completado"),
                                                bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                                ft.OutlinedButton("Pendiente", 
                                                  on_click=lambda e, x=p['id']: cambiar_estado_admin(x, "pendiente"))
                            ], alignment=ft.MainAxisAlignment.END)
                        ])
                    )
                )
            )

        cats = obtener_categorias()
        cat = ft.Dropdown(label="Categoría", options=[ft.dropdown.Option(str(x["id"]), x["nombre"]) for x in cats])
        nombre = ft.TextField(label="Nombre del Ramo/Flor")
        precio = ft.TextField(label="Precio ($)", keyboard_type=ft.KeyboardType.NUMBER)
        stock = ft.TextField(label="Cantidad en Stock", keyboard_type=ft.KeyboardType.NUMBER)
        desc = ft.TextField(label="Descripción (Detalles)", multiline=True)
        talla = ft.TextField(label="Tamaño/Talla")
        color = ft.TextField(label="Color de Cinta")
        imagen = ft.TextField(label="URL de Imagen")
        
        lista = ft.Column()

        def limpiar(): 
            nonlocal producto_editando
            producto_editando = None
            for f in [nombre, precio, stock, desc, talla, color, imagen]:
                f.value = ""
            cat.value = None

        def cargar_form(p):
            nonlocal producto_editando
            producto_editando = p["id"]
            nombre.value = p["nombre"]
            precio.value = str(p["precio"])
            stock.value = str(p["stock"])
            desc.value = p["descripcion"] or ""
            talla.value = p["talla"] or ""
            color.value = p["color"] or ""
            imagen.value = p["imagen"] or ""
            cat.value = str(p["categoria_id"]) if p["categoria_id"] else None
            page.update()

        def guardar(e):
            if not nombre.value or not precio.value or not stock.value:
                toast("Campos requeridos: Nombre, Precio y Stock")
                return
            try:
                data = (
                    nombre.value.strip(),
                    float(precio.value),
                    int(cat.value) if cat.value else None,
                    int(stock.value),
                    desc.value,
                    talla.value or "Única",
                    color.value,
                    imagen.value
                )
                if producto_editando:
                    editar_producto(producto_editando, *data)
                    toast("Producto actualizado correctamente")
                else:
                    agregar_producto(*data)
                    toast("Flor/Ramo agregado al catálogo")
                
                limpiar()
                crud()
            except Exception as ex:
                toast(f"Error al guardar: {ex}")

        def borrar(pid):
            eliminar_producto(pid)
            toast("Producto eliminado")
            crud()

        def render_lista():
            lista.controls.clear()
            for p in obtener_productos():
                lista.controls.append(
                    ft.ListTile(
                        title=ft.Text(p["nombre"]),
                        subtitle=ft.Text(f"${p['precio']:,.2f} | Stock: {p['stock']}"),
                        trailing=ft.Row(
                            width=100,
                            controls=[
                                ft.IconButton(ft.Icons.EDIT, on_click=lambda e, x=p: cargar_form(x)),
                                ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED_400, on_click=lambda e, x=p: borrar(x["id"]))
                            ]
                        )
                    )
                )

        vista_inventario = ft.Container(
            padding=10,
            content=ft.Column(
                controls=[
                    ft.Text("Administrar Flores Eternas", size=18, weight=ft.FontWeight.BOLD),
                    nombre, precio, cat, stock, desc, talla, color, imagen,
                    ft.Row([
                        ft.FilledButton("Guardar Producto", icon=ft.Icons.SAVE, on_click=guardar, bgcolor=ft.Colors.PURPLE_600, color=ft.Colors.WHITE),
                        ft.OutlinedButton("Limpiar Formulario", on_click=lambda e: (limpiar(), page.update()))
                    ]),
                    ft.Divider(),
                    lista
                ]
            )
        )

        vista_pedidos = ft.Container(
            padding=10,
            content=ft.Column(
                controls=[
                    ft.Text("Ventas Realizadas", size=18, weight=ft.FontWeight.BOLD),
                    ft.Column(controls=pedidos_cards or [ft.Text("No hay pedidos registrados.")])
                ]
            )
        )

        def obtener_vista_reportes():
            rep = generar_reporte_negocio()
            
            tarjetas_metricas = ft.Row([
                ft.Card(content=ft.Container(padding=12, content=ft.Column([
                    ft.Text("Ingresos Totales", size=11, color=ft.Colors.GREY_700),
                    ft.Text(f"${rep['ingresos_totales']:,.2f}", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
                ]))),
                ft.Card(content=ft.Container(padding=12, content=ft.Column([
                    ft.Text("Clientes", size=11, color=ft.Colors.GREY_700),
                    ft.Text(str(rep['total_usuarios']), size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_800)
                ]))),
                ft.Card(content=ft.Container(padding=12, content=ft.Column([
                    ft.Text("Pedidos Totales", size=11, color=ft.Colors.GREY_700),
                    ft.Text(str(rep['total_pedidos']), size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
                ]))),
            ], wrap=True)

            stock_items = [ft.Text(f"• {s['nombre']} (Quedan: {s['stock']} un.)", color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD) for s in rep["stock_bajo"]]
            top_items = [ft.Text(f"• {m['nombre']} - {m['total_vendido']} un. (${m['recaudado']:,.2f})", size=12) for m in rep["mas_vendidos"]]

            return ft.Container(
                padding=10,
                content=ft.Column(
                    controls=[
                        ft.Text("Reporte del Negocio 📊", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_900),
                        ft.Divider(),
                        ft.Text("Métricas Principales", weight=ft.FontWeight.BOLD, size=13),
                        tarjetas_metricas,
                        ft.Divider(height=15),
                        ft.Text("⚠️ Alerta de Stock Bajo (≤ 5 unidades)", weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.RED_700),
                        ft.Column(controls=stock_items or [ft.Text("Sin alertas de stock bajo", size=12)]),
                        ft.Divider(height=15),
                        ft.Text("🏆 Productos Más Vendidos", weight=ft.FontWeight.BOLD, size=13),
                        ft.Column(controls=top_items or [ft.Text("Aún no hay ventas suficientes", size=12)])
                    ]
                )
            )

        vista_reportes = obtener_vista_reportes()

        contenedor_principal = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[vista_inventario]
        )

        def cambiar_seccion(e):
            idx = e.control.selected_index
            if idx == 0:
                contenedor_principal.controls = [vista_inventario]
            elif idx == 1:
                contenedor_principal.controls = [vista_pedidos]
            elif idx == 2:
                contenedor_principal.controls = [obtener_vista_reportes()]
            page.update()

        selector_tabs = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.INVENTORY_OUTLINED, selected_icon=ft.Icons.INVENTORY, label="Inventario"),
                ft.NavigationRailDestination(icon=ft.Icons.SHOPPING_BAG_OUTLINED, selected_icon=ft.Icons.SHOPPING_BAG, label="Pedidos"),
                ft.NavigationRailDestination(icon=ft.Icons.BAR_CHART_OUTLINED, selected_icon=ft.Icons.BAR_CHART, label="Reporte"),
            ],
            on_change=cambiar_seccion,
            bgcolor=ft.Colors.PURPLE_50
        )

        page.add(
            appbar("Módulo Administrador"),
            ft.Row([
                selector_tabs,
                ft.VerticalDivider(width=1),
                ft.Container(expand=True, content=contenedor_principal)
            ], expand=True),
            navbar(3)
        )
        render_lista()

    login_view()

ft.run(main)