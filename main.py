# main.py
# Interfaz gráfica con Tkinter: login, menús desplegables con CRUD, reportes y exportación.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import database
from datetime import datetime, timedelta
import os

# Para gráficos
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Opciones de caja / calibres
CAJAS = ["18/20", "20/60", "23/80", "25/70", "27/100", "30", "33", "39", "42", "48", "pl6", "pl-m", "pl-ch"]

class NicoKiwiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nico-Kiwi Tracker 🍃")
        # pantalla completa
        try:
            self.state('zoomed')  # Windows
        except:
            self.attributes('-fullscreen', True)  # alternativa
        self.current_user = None
        self.content_frame = None
        self.current_canvas = None

        # preparar DB
        database.create_tables()

        # iniciar login
        self.show_login()

    def clear_content(self):
        if self.content_frame:
            for w in self.content_frame.winfo_children():
                w.destroy()
            self.content_frame.destroy()
            self.content_frame = None
        # limpiar canvas si existe
        if self.current_canvas:
            try:
                self.current_canvas.get_tk_widget().destroy()
            except:
                pass
            self.current_canvas = None

    # ----------------------
    # LOGIN / REGISTER
    # ----------------------
    def show_login(self):
        self.clear_content()
        frame = tk.Frame(self, bg="#f0f8ff")
        frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame = frame

        tk.Label(frame, text="Nico-Kiwi Tracker", font=("Arial", 28, "bold"), bg="#f0f8ff").pack(pady=20)
        entry_frame = tk.Frame(frame, bg="#f0f8ff")
        entry_frame.pack()

        tk.Label(entry_frame, text="Usuario:", bg="#f0f8ff").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        usuario_entry = tk.Entry(entry_frame, width=25)
        usuario_entry.grid(row=0, column=1, pady=5)
        tk.Label(entry_frame, text="Contraseña:", bg="#f0f8ff").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        password_entry = tk.Entry(entry_frame, width=25, show="*")
        password_entry.grid(row=1, column=1, pady=5)

        def intentar_login():
            user = usuario_entry.get().strip()
            pw = password_entry.get().strip()
            if not user or not pw:
                messagebox.showwarning("Datos incompletos", "Ingrese usuario y contraseña")
                return
            ok = database.verify_user(user, pw)
            if ok:
                self.current_user = user
                self.build_menu()
                self.show_dashboard()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")

        def ir_registro():
            self.show_register()

        tk.Button(frame, text="Iniciar sesión", command=intentar_login, bg="#4CAF50", fg="white", width=15).pack(pady=8)
        tk.Button(frame, text="Registrar nuevo usuario", command=ir_registro, width=20).pack()

    def show_register(self):
        self.clear_content()
        frame = tk.Frame(self, bg="#f7fff0")
        frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame = frame
        tk.Label(frame, text="Crear cuenta", font=("Arial", 20, "bold"), bg="#f7fff0").pack(pady=15)

        form = tk.Frame(frame, bg="#f7fff0")
        form.pack()

        tk.Label(form, text="Usuario:", bg="#f7fff0").grid(row=0, column=0, sticky="e")
        user_e = tk.Entry(form, width=25)
        user_e.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(form, text="Contraseña:", bg="#f7fff0").grid(row=1, column=0, sticky="e")
        pw_e = tk.Entry(form, width=25, show="*")
        pw_e.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(form, text="Rol:", bg="#f7fff0").grid(row=2, column=0, sticky="e")
        rol_cb = ttk.Combobox(form, values=["operador", "admin"], state="readonly", width=22)
        rol_cb.set("operador")
        rol_cb.grid(row=2, column=1, padx=5, pady=5)

        def crear():
            u = user_e.get().strip()
            p = pw_e.get().strip()
            r = rol_cb.get()
            if not u or not p:
                messagebox.showwarning("Datos incompletos", "Complete usuario y contraseña")
                return
            ok, msg = database.add_user(u, p, r)
            if ok:
                messagebox.showinfo("Listo", "Usuario creado correctamente")
                self.show_login()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(frame, text="Crear usuario", command=crear, bg="#2196F3", fg="white").pack(pady=10)
        tk.Button(frame, text="Volver", command=self.show_login).pack()

    # ----------------------
    # MENU PRINCIPAL
    # ----------------------
    def build_menu(self):
        menubar = tk.Menu(self)
        # Archivo
        archivo = tk.Menu(menubar, tearoff=0)
        archivo.add_command(label="Salir", command=self.quit)
        archivo.add_separator()
        archivo.add_command(label="Cerrar sesión", command=self.logout)
        menubar.add_cascade(label="Archivo", menu=archivo)
        # Palets
        palets = tk.Menu(menubar, tearoff=0)
        palets.add_command(label="Alta", command=self.pallet_add)
        palets.add_command(label="Consulta", command=lambda: self.pallet_list(mode="view"))
        palets.add_command(label="Modificar", command=lambda: self.pallet_list(mode="modify"))
        palets.add_command(label="Baja", command=lambda: self.pallet_list(mode="delete"))
        menubar.add_cascade(label="Empaquetadora (Palets)", menu=palets)
        # Ventas
        ventas = tk.Menu(menubar, tearoff=0)
        ventas.add_command(label="Alta", command=self.sale_add)
        ventas.add_command(label="Consulta", command=lambda: self.sale_list(mode="view"))
        ventas.add_command(label="Modificar", command=lambda: self.sale_list(mode="modify"))
        ventas.add_command(label="Baja", command=lambda: self.sale_list(mode="delete"))
        menubar.add_cascade(label="Ventas", menu=ventas)
        # Usuarios
        usuarios = tk.Menu(menubar, tearoff=0)
        usuarios.add_command(label="Alta", command=self.user_add)
        usuarios.add_command(label="Consulta", command=self.user_list)
        usuarios.add_command(label="Modificar", command=self.user_list)
        usuarios.add_command(label="Baja", command=self.user_list)
        menubar.add_cascade(label="Usuarios", menu=usuarios)
        # Reportes
        reportes = tk.Menu(menubar, tearoff=0)
        reportes.add_command(label="Ver reportes y gráficos", command=self.reports_view)
        reportes.add_command(label="Exportar ventas a Excel", command=self.export_sales)
        reportes.add_command(label="Sincronizar ventas con Google Sheets", command=self.sync_google_sheet)
        menubar.add_cascade(label="Reportes", menu=reportes)

        self.config(menu=menubar)

    def logout(self):
        self.current_user = None
        self.clear_content()
        # eliminar menu
        self.config(menu=tk.Menu(self))
        self.show_login()

    # ----------------------
    # DASHBOARD
    # ----------------------
    def show_dashboard(self):
        self.clear_content()
        frame = tk.Frame(self, bg="#fffaf0")
        frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame = frame

        tk.Label(frame, text=f"Bienvenido, {self.current_user}", font=("Arial", 20, "bold"), bg="#fffaf0").pack(pady=10)
        btn_frame = tk.Frame(frame, bg="#fffaf0")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Registrar venta", width=18, height=2, command=self.sale_add, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="Nuevo pallet", width=18, height=2, command=self.pallet_add, bg="#2196F3", fg="white").grid(row=0, column=1, padx=8)
        tk.Button(btn_frame, text="Ver reportes", width=18, height=2, command=self.reports_view, bg="#9C27B0", fg="white").grid(row=0, column=2, padx=8)

        # Resumen simple
        pallets = database.list_pallets()
        ventas = database.list_sales()
        tk.Label(frame, text=f"Pallets registrados: {len(pallets)}", bg="#fffaf0", font=("Arial", 12)).pack(pady=5)
        tk.Label(frame, text=f"Ventas registradas: {len(ventas)}", bg="#fffaf0", font=("Arial", 12)).pack(pady=5)

    # ----------------------
    # PALLETS CRUD
    # ----------------------
    def pallet_add(self):
        win = tk.Toplevel(self)
        win.title("Nuevo Pallet")
        tk.Label(win, text="Registrar nuevo pallet", font=("Arial", 14, "bold")).pack(pady=10)
        form = tk.Frame(win)
        form.pack(padx=10, pady=10)

        tk.Label(form, text="Peso (kg):").grid(row=0, column=0, sticky="e")
        peso_v = tk.DoubleVar(value=25.0)
        tk.Entry(form, textvariable=peso_v).grid(row=0, column=1, pady=4)

        tk.Label(form, text="Calibre:").grid(row=1, column=0, sticky="e")
        calibre_v = tk.StringVar(value=CAJAS[0])
        ttk.Combobox(form, values=CAJAS, textvariable=calibre_v, state="readonly").grid(row=1, column=1, pady=4)

        tk.Label(form, text="Fecha (YYYY-MM-DD):").grid(row=2, column=0, sticky="e")
        fecha_v = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(form, textvariable=fecha_v).grid(row=2, column=1, pady=4)

        def guardar():
            try:
                pid = database.add_pallet(float(peso_v.get()), calibre_v.get(), fecha_v.get(), self.current_user)
                messagebox.showinfo("Éxito", f"Pallet registrado (id={pid})")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Guardar", command=guardar, bg="#2196F3", fg="white").pack(pady=8)
        tk.Button(win, text="Cancelar", command=win.destroy).pack()

    def pallet_list(self, mode="view"):
        self.clear_content()
        frame = tk.Frame(self, bg="#f0fff0")
        frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame = frame
        tk.Label(frame, text=f"Palets - modo: {mode}", font=("Arial", 14, "bold"), bg="#f0fff0").pack(pady=8)
        cols = ("id", "peso", "calibre", "fecha", "usuario")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.capitalize())
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def cargar():
            for r in tree.get_children():
                tree.delete(r)
            for row in database.list_pallets():
                tree.insert("", "end", values=(row["id"], row["peso"], row["calibre"], row["fecha"], row["usuario"]))

        cargar()

        btnf = tk.Frame(frame, bg="#f0fff0")
        btnf.pack(pady=6)
        tk.Button(btnf, text="Refrescar", command=cargar).grid(row=0, column=0, padx=4)
        tk.Button(btnf, text="Exportar a Excel", command=self.export_pallets).grid(row=0, column=1, padx=4)

        def editar():
            sel = tree.focus()
            if not sel:
                messagebox.showwarning("Seleccione", "Seleccione un pallet para editar")
                return
            vals = tree.item(sel)["values"]
            pid = vals[0]
            self.pallet_edit(pid, cargar)

        def eliminar():
            sel = tree.focus()
            if not sel:
                messagebox.showwarning("Seleccione", "Seleccione un pallet para eliminar")
                return
            vals = tree.item(sel)["values"]
            pid = vals[0]
            if messagebox.askyesno("Confirmar", f"Eliminar pallet id={pid}?"):
                database.delete_pallet(pid)
                messagebox.showinfo("Borrado", "Pallet eliminado")
                cargar()

        if mode in ("modify", "delete"):
            tk.Button(btnf, text="Editar", command=editar).grid(row=0, column=2, padx=4)
            tk.Button(btnf, text="Eliminar", command=eliminar).grid(row=0, column=3, padx=4)

    def pallet_edit(self, pallet_id, on_saved_callback=None):
        data = database.get_pallet(pallet_id)
        if not data:
            messagebox.showerror("Error", "Pallet no encontrado")
            return
        win = tk.Toplevel(self)
        win.title(f"Editar pallet {pallet_id}")
        form = tk.Frame(win)
        form.pack(padx=10, pady=10)
        tk.Label(form, text="Peso (kg):").grid(row=0, column=0, sticky="e")
        peso_v = tk.DoubleVar(value=data["peso"])
        tk.Entry(form, textvariable=peso_v).grid(row=0, column=1, pady=4)
        tk.Label(form, text="Calibre:").grid(row=1, column=0, sticky="e")
        calibre_v = tk.StringVar(value=data["calibre"])
        ttk.Combobox(form, values=CAJAS, textvariable=calibre_v, state="readonly").grid(row=1, column=1, pady=4)
        tk.Label(form, text="Fecha:").grid(row=2, column=0, sticky="e")
        fecha_v = tk.StringVar(value=data["fecha"])
        tk.Entry(form, textvariable=fecha_v).grid(row=2, column=1, pady=4)

        def guardar():
            try:
                database.update_pallet(pallet_id, float(peso_v.get()), calibre_v.get(), fecha_v.get(), self.current_user)
                messagebox.showinfo("Ok", "Pallet actualizado")
                win.destroy()
                if on_saved_callback:
                    on_saved_callback()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Guardar", command=guardar, bg="#2196F3", fg="white").pack(pady=6)
        tk.Button(win, text="Cancelar", command=win.destroy).pack()

    # ----------------------
    # VENTAS CRUD
    # ----------------------
    def sale_add(self):
        win = tk.Toplevel(self)
        win.title("Nueva Venta")
        tk.Label(win, text="Registrar venta", font=("Arial", 14, "bold")).pack(pady=8)
        form = tk.Frame(win)
        form.pack(padx=10, pady=10)

        tk.Label(form, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, sticky="e")
        fecha_v = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(form, textvariable=fecha_v).grid(row=0, column=1, pady=4)

        tk.Label(form, text="Tipo de caja:").grid(row=1, column=0, sticky="e")
        caja_v = tk.StringVar(value=CAJAS[0])
        ttk.Combobox(form, values=CAJAS, textvariable=caja_v, state="readonly").grid(row=1, column=1, pady=4)

        tk.Label(form, text="Cantidad (cajas):").grid(row=2, column=0, sticky="e")
        cant_v = tk.IntVar(value=1)
        tk.Entry(form, textvariable=cant_v).grid(row=2, column=1, pady=4)

        tk.Label(form, text="Precio unitario ($):").grid(row=3, column=0, sticky="e")
        precio_v = tk.DoubleVar(value=2.50)
        tk.Entry(form, textvariable=precio_v).grid(row=3, column=1, pady=4)

        def guardar():
            try:
                sid = database.add_sale(fecha_v.get(), caja_v.get(), int(cant_v.get()), float(precio_v.get()), self.current_user)
                messagebox.showinfo("Éxito", f"Venta registrada (id={sid})")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Guardar", command=guardar, bg="#4CAF50", fg="white").pack(pady=8)
        tk.Button(win, text="Cancelar", command=win.destroy).pack()

    def sale_list(self, mode="view"):
        self.clear_content()
        frame = tk.Frame(self, bg="#fff5f5")
        frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame = frame
        tk.Label(frame, text=f"Ventas - modo: {mode}", font=("Arial", 14, "bold"), bg="#fff5f5").pack(pady=8)
        cols = ("id", "fecha", "caja_tipo", "cantidad", "precio_unitario", "usuario", "total")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.capitalize())
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def cargar():
            for r in tree.get_children():
                tree.delete(r)
            for row in database.list_sales():
                total = row["cantidad"] * row["precio_unitario"]
                tree.insert("", "end", values=(row["id"], row["fecha"], row["caja_tipo"], row["cantidad"], row["precio_unitario"], row["usuario"], total))

        cargar()

        btnf = tk.Frame(frame, bg="#fff5f5")
        btnf.pack(pady=6)
        tk.Button(btnf, text="Refrescar", command=cargar).grid(row=0, column=0, padx=4)
        tk.Button(btnf, text="Exportar a Excel", command=self.export_sales).grid(row=0, column=1, padx=4)
        tk.Button(btnf, text="Gráfico periodo", command=self.reports_view).grid(row=0, column=2, padx=4)

        def editar():
            sel = tree.focus()
            if not sel:
                messagebox.showwarning("Seleccione", "Seleccione una venta para editar")
                return
            vals = tree.item(sel)["values"]
            sid = vals[0]
            self.sale_edit(sid, cargar)

        def eliminar():
            sel = tree.focus()
            if not sel:
                messagebox.showwarning("Seleccione", "Seleccione una venta para eliminar")
                return
            vals = tree.item(sel)["values"]
            sid = vals[0]
            if messagebox.askyesno("Confirmar", f"Eliminar venta id={sid}?"):
                database.delete_sale(sid)
                messagebox.showinfo("Borrado", "Venta eliminada")
                cargar()

        if mode in ("modify", "delete"):
            tk.Button(btnf, text="Editar", command=editar).grid(row=0, column=3, padx=4)
            tk.Button(btnf, text="Eliminar", command=eliminar).grid(row=0, column=4, padx=4)

    def sale_edit(self, sale_id, on_saved_callback=None):
        data = database.get_sale(sale_id)
        if not data:
            messagebox.showerror("Error", "Venta no encontrada")
            return
        win = tk.Toplevel(self)
        win.title(f"Editar venta {sale_id}")
        form = tk.Frame(win)
        form.pack(padx=10, pady=10)
        tk.Label(form, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, sticky="e")
        fecha_v = tk.StringVar(value=data["fecha"])
        tk.Entry(form, textvariable=fecha_v).grid(row=0, column=1, pady=4)
        tk.Label(form, text="Tipo de caja:").grid(row=1, column=0, sticky="e")
        caja_v = tk.StringVar(value=data["caja_tipo"])
        ttk.Combobox(form, values=CAJAS, textvariable=caja_v, state="readonly").grid(row=1, column=1, pady=4)
        tk.Label(form, text="Cantidad:").grid(row=2, column=0, sticky="e")
        cant_v = tk.IntVar(value=data["cantidad"])
        tk.Entry(form, textvariable=cant_v).grid(row=2, column=1, pady=4)
        tk.Label(form, text="Precio unitario:").grid(row=3, column=0, sticky="e")
        precio_v = tk.DoubleVar(value=data["precio_unitario"])
        tk.Entry(form, textvariable=precio_v).grid(row=3, column=1, pady=4)

        def guardar():
            try:
                database.update_sale(sale_id, fecha_v.get(), caja_v.get(), int(cant_v.get()), float(precio_v.get()), self.current_user)
                messagebox.showinfo("Ok", "Venta actualizada")
                win.destroy()
                if on_saved_callback:
                    on_saved_callback()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Guardar", command=guardar, bg="#4CAF50", fg="white").pack(pady=6)
        tk.Button(win, text="Cancelar", command=win.destroy).pack()

    # ----------------------
    # USUARIOS CRUD (requiere admin)
    # ----------------------
    def user_add(self):
        # Solo admin puede crear usuarios (por seguridad)
        if not self._is_admin():
            messagebox.showwarning("Permiso denegado", "Solo el admin puede crear usuarios")
            return
        win = tk.Toplevel(self)
        win.title("Nuevo Usuario")
        form = tk.Frame(win)
        form.pack(padx=10, pady=10)
        tk.Label(form, text="Usuario:").grid(row=0, column=0, sticky="e")
        user_v = tk.Entry(form)
        user_v.grid(row=0, column=1, pady=4)
        tk.Label(form, text="Contraseña:").grid(row=1, column=0, sticky="e")
        pw_v = tk.Entry(form, show="*")
        pw_v.grid(row=1, column=1, pady=4)
        tk.Label(form, text="Rol:").grid(row=2, column=0, sticky="e")
        rol_v = ttk.Combobox(form, values=["operador", "admin"], state="readonly")
        rol_v.set("operador")
        rol_v.grid(row=2, column=1, pady=4)

        def guardar():
            u = user_v.get().strip()
            p = pw_v.get().strip()
            r = rol_v.get()
            if not u or not p:
                messagebox.showwarning("Datos", "Ingrese usuario y contraseña")
                return
            ok, msg = database.add_user(u, p, r)
            if ok:
                messagebox.showinfo("Ok", "Usuario agregado")
                win.destroy()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(win, text="Guardar", command=guardar, bg="#2196F3", fg="white").pack(pady=6)
        tk.Button(win, text="Cancelar", command=win.destroy).pack()

    def user_list(self):
        # lista + opciones editar/borrar (solo admin para borrar/editar)
        self.clear_content()
        frame = tk.Frame(self, bg="#f0f0ff")
        frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame = frame
        tk.Label(frame, text="Usuarios", font=("Arial", 14, "bold"), bg="#f0f0ff").pack(pady=8)
        cols = ("id", "username", "role")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.capitalize())
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def cargar():
            for r in tree.get_children():
                tree.delete(r)
            for row in database.list_users():
                tree.insert("", "end", values=(row["id"], row["username"], row["role"]))

        cargar()
        btnf = tk.Frame(frame, bg="#f0f0ff")
        btnf.pack(pady=6)
        tk.Button(btnf, text="Refrescar", command=cargar).grid(row=0, column=0, padx=4)

        def editar():
            if not self._is_admin():
                messagebox.showwarning("Permiso", "Solo el admin puede editar usuarios")
                return
            sel = tree.focus()
            if not sel:
                messagebox.showwarning("Seleccione", "Seleccione un usuario")
                return
            vals = tree.item(sel)["values"]
            uid = vals[0]
            self.user_edit(uid, cargar)

        def eliminar():
            if not self._is_admin():
                messagebox.showwarning("Permiso", "Solo el admin puede borrar usuarios")
                return
            sel = tree.focus()
            if not sel:
                messagebox.showwarning("Seleccione", "Seleccione un usuario")
                return
            vals = tree.item(sel)["values"]
            uid = vals[0]
            if messagebox.askyesno("Confirmar", f"Eliminar usuario id={uid}?"):
                database.delete_user(uid)
                messagebox.showinfo("Borrado", "Usuario eliminado")
                cargar()

        tk.Button(btnf, text="Editar", command=editar).grid(row=0, column=1, padx=4)
        tk.Button(btnf, text="Eliminar", command=eliminar).grid(row=0, column=2, padx=4)

    def user_edit(self, user_id, on_saved_callback=None):
        data = None
        for u in database.list_users():
            if u["id"] == user_id:
                data = u
                break
        if not data:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
        win = tk.Toplevel(self)
        win.title(f"Editar usuario {user_id}")
        form = tk.Frame(win)
        form.pack(padx=10, pady=10)
        tk.Label(form, text="Usuario:").grid(row=0, column=0, sticky="e")
        user_v = tk.Entry(form)
        user_v.insert(0, data["username"])
        user_v.grid(row=0, column=1)
        tk.Label(form, text="Nueva contraseña:").grid(row=1, column=0, sticky="e")
        pw_v = tk.Entry(form, show="*")
        pw_v.grid(row=1, column=1)
        tk.Label(form, text="Rol:").grid(row=2, column=0, sticky="e")
        rol_v = ttk.Combobox(form, values=["operador", "admin"], state="readonly")
        rol_v.set(data["role"])
        rol_v.grid(row=2, column=1)

        def guardar():
            newu = user_v.get().strip()
            newp = pw_v.get().strip()
            newr = rol_v.get()
            if not newu or not newp:
                messagebox.showwarning("Datos", "Usuario y contraseña no pueden quedar vacíos")
                return
            ok, msg = database.update_user(user_id, newu, newp, newr)
            if ok:
                messagebox.showinfo("Ok", "Usuario actualizado")
                win.destroy()
                if on_saved_callback:
                    on_saved_callback()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(win, text="Guardar", command=guardar, bg="#2196F3", fg="white").pack(pady=6)
        tk.Button(win, text="Cancelar", command=win.destroy).pack()

    def _is_admin(self):
        # pequeño helper: chequear role del usuario actual
        if not self.current_user:
            return False
        users = database.list_users()
        for u in users:
            if u["username"] == self.current_user:
                return u["role"] == "admin"
        return False

    # ----------------------
    # REPORTES / GRAFICOS
    # ----------------------
    def reports_view(self):
        self.clear_content()
        frame = tk.Frame(self, bg="#fffaf0")
        frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame = frame
        tk.Label(frame, text="Reportes de Ventas", font=("Arial", 14, "bold"), bg="#fffaf0").pack(pady=8)

        form = tk.Frame(frame, bg="#fffaf0")
        form.pack(pady=6)
        tk.Label(form, text="Desde (YYYY-MM-DD):", bg="#fffaf0").grid(row=0, column=0, padx=4, sticky="e")
        desde_v = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        tk.Entry(form, textvariable=desde_v).grid(row=0, column=1, padx=4)
        tk.Label(form, text="Hasta (YYYY-MM-DD):", bg="#fffaf0").grid(row=1, column=0, padx=4, sticky="e")
        hasta_v = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(form, textvariable=hasta_v).grid(row=1, column=1, padx=4)

        rb_frame = tk.Frame(form, bg="#fffaf0")
        rb_frame.grid(row=0, column=2, rowspan=2, padx=8)
        grp = tk.StringVar(value="day")
        tk.Radiobutton(rb_frame, text="Por día", variable=grp, value="day", bg="#fffaf0").pack(anchor="w")
        tk.Radiobutton(rb_frame, text="Por mes", variable=grp, value="month", bg="#fffaf0").pack(anchor="w")

        def generar():
            d = desde_v.get().strip()
            h = hasta_v.get().strip()
            if grp.get() == "day":
                rows = database.sales_aggregate_by_day(d, h)
                x = [r["fecha"] for r in rows]
                y = [r["total_revenue"] for r in rows]
                title = f"Ventas por día {d} a {h}"
            else:
                rows = database.sales_aggregate_by_month(d, h)
                x = [r["mes"] for r in rows]
                y = [r["total_revenue"] for r in rows]
                title = f"Ventas por mes {d} a {h}"
            # limpiar canvas anterior
            if self.current_canvas:
                try:
                    self.current_canvas.get_tk_widget().destroy()
                except:
                    pass
            fig = Figure(figsize=(8, 4))
            ax = fig.add_subplot(111)
            ax.bar(x, y, color="#4CAF50")
            ax.set_title(title)
            ax.set_ylabel("Ingreso total")
            ax.set_xticklabels(x, rotation=45, ha="right")
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.current_canvas = canvas

            # Mostrar promedio
            avg = database.average_daily_revenue(d, h)
            messagebox.showinfo("Promedio", f"Promedio diario de ingresos en el periodo: {avg:.2f}")

        tk.Button(form, text="Generar gráfico", command=generar, bg="#9C27B0", fg="white").grid(row=0, column=3, padx=8, rowspan=2)

    # ----------------------
    # EXPORT / SYNC
    # ----------------------
    def export_sales(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return
        try:
            database.export_sales_to_excel(path)
            messagebox.showinfo("Exportado", f"Ventas exportadas a:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_pallets(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return
        try:
            database.export_pallets_to_excel(path)
            messagebox.showinfo("Exportado", f"Pallets exportados a:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def sync_google_sheet(self):
        # Ventana para seleccionar archivo credentials.json y pedir spreadsheet id
        cred = filedialog.askopenfilename(title="Seleccionar credentials JSON (cuenta de servicio)", filetypes=[("JSON files","*.json")])
        if not cred:
            return
        sid = simpledialog.askstring("Spreadsheet ID", "Ingrese el ID del Google Spreadsheet (parte del URL):")
        if not sid:
            return
        sheet_name = simpledialog.askstring("Hoja", "Nombre de la hoja (ej: Ventas)", initialvalue="Ventas")
        try:
            cantidad = database.sync_sales_to_google(cred, sid, sheet_name or "Ventas")
            messagebox.showinfo("Sincronización", f"Sincronizadas {cantidad} filas nuevas a Google Sheets")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo sincronizar:\n{e}")

if __name__ == "__main__":
    app = NicoKiwiApp()
    app.mainloop()