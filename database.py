import sqlite3
import hashlib

DB_NAME = "enchanted.db"

def conectar():
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def crear_tablas():
    con = conectar(); c = con.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
      id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
      password TEXT NOT NULL, direccion TEXT, rol TEXT NOT NULL DEFAULT 'cliente',
      creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
      
    CREATE TABLE IF NOT EXISTS categorias (
      id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE);
      
    CREATE TABLE IF NOT EXISTS productos (
      id INTEGER PRIMARY KEY AUTOINCREMENT, categoria_id INTEGER, nombre TEXT NOT NULL,
      descripcion TEXT, precio REAL NOT NULL, talla TEXT DEFAULT 'Única', color TEXT DEFAULT '',
      stock INTEGER NOT NULL DEFAULT 0, imagen TEXT,
      FOREIGN KEY(categoria_id) REFERENCES categorias(id));
      
    CREATE TABLE IF NOT EXISTS pedidos (
      id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER, total REAL NOT NULL DEFAULT 0,
      estado TEXT DEFAULT 'pendiente', fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(usuario_id) REFERENCES usuarios(id));
      
    CREATE TABLE IF NOT EXISTS detalle_pedido (
      id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER, producto_id INTEGER,
      cantidad INTEGER NOT NULL, precio_unitario REAL NOT NULL,
      FOREIGN KEY(pedido_id) REFERENCES pedidos(id), FOREIGN KEY(producto_id) REFERENCES productos(id));
    """)
    
    # Migraciones para compatibilidad de esquemas
    cols = [r[1] for r in c.execute("PRAGMA table_info(productos)")]
    for col, typ, default in [("categoria_id","INTEGER","NULL"), ("descripcion","TEXT","''"), ("talla","TEXT","'Única'"), ("color","TEXT","''"), ("imagen","TEXT","NULL")]:
        if col not in cols:
            c.execute(f"ALTER TABLE productos ADD COLUMN {col} {typ} DEFAULT {default}")
            
    ucols = [r[1] for r in c.execute("PRAGMA table_info(usuarios)")]
    if "rol" not in ucols: 
        c.execute("ALTER TABLE usuarios ADD COLUMN rol TEXT DEFAULT 'cliente'")
        
    if not c.execute("SELECT 1 FROM usuarios WHERE email='admin@enchantedgarden.com'").fetchone():
        c.execute("INSERT INTO usuarios(nombre,email,password,rol) VALUES(?,?,?,?)",
                  ("Administrador", "admin@enchantedgarden.com", hash_password("admin123"), "admin"))
                  
    for n in ["Flores", "Plantas", "Macetas", "Accesorios"]:
        c.execute("INSERT OR IGNORE INTO categorias(nombre) VALUES(?)", (n,))
        
    con.commit(); con.close()

# --- GESTIÓN DE USUARIOS Y AUTENTICACIÓN ---

def registrar_usuario(nombre, email, password, direccion=""):
    try:
        con = conectar()
        con.execute("INSERT INTO usuarios(nombre,email,password,direccion) VALUES(?,?,?,?)",
                    (nombre.strip(), email.strip().lower(), hash_password(password), direccion.strip()))
        con.commit()
        return True, "Cuenta creada correctamente"
    except sqlite3.IntegrityError:
        return False, "El correo ya está registrado"
    finally:
        try: con.close()
        except: pass

def iniciar_sesion(email, password):
    con = conectar()
    email_clean = email.strip().lower()
    
    # 1. Verificar si el correo existe en la base de datos
    usuario = con.execute("SELECT * FROM usuarios WHERE email=?", (email_clean,)).fetchone()
    
    if not usuario:
        con.close()
        return False, "CORREO_INCORRECTO", None
    
    # 2. Verificar si la contraseña coincide con ese usuario
    pass_hash = hash_password(password)
    if usuario["password"] != pass_hash:
        con.close()
        return False, "PASSWORD_INCORRECTO", None
        
    con.close()
    return True, "OK", dict(usuario)

# --- GESTIÓN DE CATEGORÍAS Y PRODUCTOS (INVENTARIO) ---

def obtener_categorias():
    con = conectar()
    rows = con.execute("SELECT * FROM categorias ORDER BY nombre").fetchall()
    con.close()
    return [dict(x) for x in rows]

def obtener_productos():
    con = conectar()
    rows = con.execute("""
        SELECT p.*, COALESCE(c.nombre, 'Sin categoría') AS categoria
        FROM productos p 
        LEFT JOIN categorias c ON c.id = p.categoria_id 
        ORDER BY p.id DESC
    """).fetchall()
    con.close()
    return [dict(x) for x in rows]

def obtener_producto(pid):
    con = conectar()
    r = con.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()
    con.close()
    return dict(r) if r else None

def agregar_producto(nombre, precio, categoria_id, stock, descripcion="", talla="Única", color="", imagen=""):
    con = conectar()
    con.execute("""
        INSERT INTO productos(nombre, precio, categoria_id, stock, descripcion, talla, color, imagen)
        VALUES(?,?,?,?,?,?,?,?)
    """, (nombre, float(precio), categoria_id or None, int(stock), descripcion, talla, color, imagen))
    con.commit(); con.close()

def editar_producto(pid, nombre, precio, categoria_id, stock, descripcion="", talla="Única", color="", imagen=""):
    con = conectar()
    cur = con.execute("""
        UPDATE productos 
        SET nombre=?, precio=?, categoria_id=?, stock=?, descripcion=?, talla=?, color=?, imagen=? 
        WHERE id=?
    """, (nombre, float(precio), categoria_id or None, int(stock), descripcion, talla, color, imagen, pid))
    con.commit()
    n = cur.rowcount
    con.close()
    return n

def eliminar_producto(pid):
    con = conectar()
    cur = con.execute("DELETE FROM productos WHERE id=?", (pid,))
    con.commit()
    n = cur.rowcount
    con.close()
    return n

# --- GESTIÓN DE PEDIDOS Y VENTAS ---

def crear_pedido(usuario_id, carrito):
    if not carrito: 
        return None
    con = conectar(); c = con.cursor()
    total = sum(x["precio"] * x["cantidad"] for x in carrito)
    c.execute("INSERT INTO pedidos(usuario_id, total) VALUES(?,?)", (usuario_id, total))
    pedido = c.lastrowid
    
    for x in carrito:
        c.execute("""
            INSERT INTO detalle_pedido(pedido_id, producto_id, cantidad, precio_unitario) 
            VALUES(?,?,?,?)
        """, (pedido, x["id"], x["cantidad"], x["precio"]))
        c.execute("UPDATE productos SET stock=MAX(stock-?, 0) WHERE id=?", (x["cantidad"], x["id"]))
        
    con.commit(); con.close()
    return pedido

def obtener_pedidos_usuario(usuario_id):
    con = conectar()
    pedidos = con.execute("""
        SELECT id, total, estado, fecha_pedido 
        FROM pedidos 
        WHERE usuario_id=? 
        ORDER BY id DESC
    """, (usuario_id,)).fetchall()
    
    resultado = []
    for p in pedidos:
        p_dict = dict(p)
        detalles = con.execute("""
            SELECT d.cantidad, d.precio_unitario, pr.nombre 
            FROM detalle_pedido d 
            JOIN productos pr ON d.producto_id = pr.id 
            WHERE d.pedido_id=?
        """, (p_dict["id"],)).fetchall()
        p_dict["items"] = [dict(d) for d in detalles]
        resultado.append(p_dict)
        
    con.close()
    return resultado

def obtener_todos_pedidos():
    con = conectar()
    pedidos = con.execute("""
        SELECT p.id, p.total, p.estado, p.fecha_pedido, u.nombre AS cliente, u.email 
        FROM pedidos p 
        JOIN usuarios u ON p.usuario_id = u.id 
        ORDER BY p.id DESC
    """).fetchall()
    
    resultado = []
    for p in pedidos:
        p_dict = dict(p)
        detalles = con.execute("""
            SELECT d.cantidad, d.precio_unitario, pr.nombre 
            FROM detalle_pedido d 
            JOIN productos pr ON d.producto_id = pr.id 
            WHERE d.pedido_id=?
        """, (p_dict["id"],)).fetchall()
        p_dict["items"] = [dict(d) for d in detalles]
        resultado.append(p_dict)
        
    con.close()
    return resultado

def cambiar_estado_pedido(pedido_id, nuevo_estado):
    con = conectar()
    con.execute("UPDATE pedidos SET estado=? WHERE id=?", (nuevo_estado, pedido_id))
    con.commit()
    con.close()

    # --- REPORTE Y ESTADÍSTICAS (ADMINISTRADOR) ---

def generar_reporte_negocio():
    con = conectar()
    
    # 1. Indicadores generales
    total_usuarios = con.execute("SELECT COUNT(*) FROM usuarios WHERE rol='cliente'").fetchone()[0]
    total_productos = con.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    total_pedidos = con.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    
    # 2. Ventas e Ingresos de pedidos completados
    res_ventas = con.execute("SELECT SUM(total), COUNT(*) FROM pedidos WHERE estado='completado'").fetchone()
    ingresos_totales = res_ventas[0] if res_ventas[0] else 0.0
    pedidos_completados = res_ventas[1] if res_ventas[1] else 0
    
    # 3. Productos con bajo stock (Menor o igual a 5 unidades)
    stock_bajo = con.execute("""
        SELECT nombre, stock, precio 
        FROM productos 
        WHERE stock <= 5 
        ORDER BY stock ASC
    """).fetchall()
    
    # 4. Productos más vendidos
    mas_vendidos = con.execute("""
        SELECT pr.nombre, SUM(d.cantidad) as total_vendido, SUM(d.cantidad * d.precio_unitario) as recaudado
        FROM detalle_pedido d
        JOIN productos pr ON d.producto_id = pr.id
        GROUP BY pr.id
        ORDER BY total_vendido DESC
        LIMIT 5
    """).fetchall()
    
    con.close()
    
    return {
        "total_usuarios": total_usuarios,
        "total_productos": total_productos,
        "total_pedidos": total_pedidos,
        "ingresos_totales": ingresos_totales,
        "pedidos_completados": pedidos_completados,
        "stock_bajo": [dict(x) for x in stock_bajo],
        "mas_vendidos": [dict(x) for x in mas_vendidos]
    }