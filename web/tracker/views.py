import json
import io
import sys
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Añadir directorio raiz al path para encontrar database.py
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # c:\ki\
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import database

# Forzar ruta absoluta de la DB para que funcione sin importar el CWD
database.DB_FILE = str(ROOT_DIR / 'nico_kiwi.db')
database.create_tables()

CAJAS = ["18/20", "20/60", "23/80", "25/70", "27/100", "30", "33", "36", "39", "42", "46", "48", "pl6", "pl-m", "pl-ch", "PL-G"]


# ============================================================
# Decoradores de autenticación
# ============================================================

def login_required(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario'):
            if request.path.startswith('/api/'):
                return JsonResponse({'ok': False, 'error': 'No autenticado'}, status=401)
            return redirect('login')
        return f(request, *args, **kwargs)
    return wrapper


def solo_admin(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if request.session.get('rol') != 'admin':
            return JsonResponse({'ok': False, 'error': 'Solo el administrador puede realizar esta acción'}, status=403)
        return f(request, *args, **kwargs)
    return wrapper


# ============================================================
# Páginas HTML
# ============================================================

@csrf_exempt
def login_view(request):
    if request.session.get('usuario'):
        return redirect('dashboard')

    if request.method == 'POST':
        data, err = parse_json(request)
        if err: return JsonResponse({'ok': False, 'error': err}, status=400)

        usuario = data.get('usuario', '').strip()
        password = data.get('password', '').strip()

        if not usuario or not password:
            return JsonResponse({'ok': False, 'error': 'Complete usuario y contraseña'})

        ok = database.verify_user(usuario, password)
        if ok:
            users = database.list_users()
            rol = next((u['role'] for u in users if u['username'] == usuario), 'operador')
            request.session['usuario'] = usuario
            request.session['rol'] = rol
            return JsonResponse({'ok': True})
        return JsonResponse({'ok': False, 'error': 'Usuario o contraseña incorrectos'})

    return render(request, 'tracker/login.html')


@login_required
def logout_view(request):
    request.session.flush()
    return redirect('login')


@login_required
def dashboard(request):
    return render(request, 'tracker/dashboard.html', {
        'usuario': request.session.get('usuario'),
        'rol': request.session.get('rol'),
    })


@login_required
def pallets_page(request):
    return render(request, 'tracker/pallets.html', {
        'usuario': request.session.get('usuario'),
        'rol': request.session.get('rol'),
        'cajas': CAJAS,
    })


@login_required
def ventas_page(request):
    return render(request, 'tracker/ventas.html', {
        'usuario': request.session.get('usuario'),
        'rol': request.session.get('rol'),
        'cajas': CAJAS,
    })


@login_required
def reportes_page(request):
    return render(request, 'tracker/reportes.html', {
        'usuario': request.session.get('usuario'),
        'rol': request.session.get('rol'),
    })


@login_required
def usuarios_page(request):
    return render(request, 'tracker/usuarios.html', {
        'usuario': request.session.get('usuario'),
        'rol': request.session.get('rol'),
    })


def parse_json(request):
    try:
        return json.loads(request.body), None
    except Exception:
        return None, "Petición inválida: formato JSON incorrecto"


# ============================================================
# API — Pallets
# ============================================================

@login_required
@csrf_exempt
def api_pallets(request):
    if request.method == 'GET':
        return JsonResponse({'ok': True, 'data': database.list_pallets()})

    if request.method == 'POST':
        data, err = parse_json(request)
        if err: return JsonResponse({'ok': False, 'error': err}, status=400)
        try:
            pid = database.add_pallet(
                float(data['peso']),
                data['calibre'],
                data['fecha'],
                request.session['usuario'],
            )
            return JsonResponse({'ok': True, 'id': pid, 'mensaje': f'Pallet #{pid} registrado'})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required
@csrf_exempt
def api_pallet_detail(request, pallet_id):
    if request.method == 'GET':
        p = database.get_pallet(pallet_id)
        if not p:
            return JsonResponse({'ok': False, 'error': 'Pallet no encontrado'}, status=404)
        return JsonResponse({'ok': True, 'data': p})

    if request.method == 'PUT':
        data, err = parse_json(request)
        if err: return JsonResponse({'ok': False, 'error': err}, status=400)
        try:
            database.update_pallet(pallet_id, float(data['peso']), data['calibre'], data['fecha'], request.session['usuario'])
            return JsonResponse({'ok': True, 'mensaje': 'Pallet actualizado'})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    if request.method == 'DELETE':
        try:
            database.delete_pallet(pallet_id)
            return JsonResponse({'ok': True, 'mensaje': 'Pallet eliminado'})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ============================================================
# API — Ventas
# ============================================================

@login_required
@csrf_exempt
def api_ventas(request):
    if request.method == 'GET':
        ventas = database.list_sales()
        for v in ventas:
            v['total'] = round(v['cantidad'] * v['precio_unitario'], 2)
        return JsonResponse({'ok': True, 'data': ventas})

    if request.method == 'POST':
        data, err = parse_json(request)
        if err: return JsonResponse({'ok': False, 'error': err}, status=400)
        try:
            sid = database.add_sale(
                data['fecha'], data['caja_tipo'],
                int(data['cantidad']), float(data['precio_unitario']),
                request.session['usuario'],
            )
            return JsonResponse({'ok': True, 'id': sid, 'mensaje': f'Venta #{sid} registrada'})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required
@csrf_exempt
def api_venta_detail(request, venta_id):
    if request.method == 'GET':
        v = database.get_sale(venta_id)
        if not v:
            return JsonResponse({'ok': False, 'error': 'Venta no encontrada'}, status=404)
        return JsonResponse({'ok': True, 'data': v})

    if request.method == 'PUT':
        data, err = parse_json(request)
        if err: return JsonResponse({'ok': False, 'error': err}, status=400)
        try:
            database.update_sale(venta_id, data['fecha'], data['caja_tipo'],
                                 int(data['cantidad']), float(data['precio_unitario']),
                                 request.session['usuario'])
            return JsonResponse({'ok': True, 'mensaje': 'Venta actualizada'})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    if request.method == 'DELETE':
        try:
            database.delete_sale(venta_id)
            return JsonResponse({'ok': True, 'mensaje': 'Venta eliminada'})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ============================================================
# API — Usuarios
# ============================================================

@csrf_exempt
def api_usuarios(request):
    if request.method == 'GET':
        # Para listar usuarios sí requerimos estar logueados
        if not request.session.get('usuario'):
            return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=401)
        return JsonResponse({'ok': True, 'data': database.list_users()})

    if request.method == 'POST':
        data, err = parse_json(request)
        if err: return JsonResponse({'ok': False, 'error': err}, status=400)
        
        # Lógica de registro público vs admin
        is_admin = request.session.get('rol') == 'admin'
        
        # Si no es admin, forzamos el rol a 'operador' por seguridad
        role = data.get('role', 'operador')
        if not is_admin:
            role = 'operador'

        ok, msg = database.add_user(
            data.get('username', '').strip(),
            data.get('password', '').strip(),
            role,
        )
        if ok:
            return JsonResponse({'ok': True, 'mensaje': 'Usuario creado'})
        return JsonResponse({'ok': False, 'error': msg or 'Error al crear usuario'}, status=400)


@login_required
@csrf_exempt
def api_usuario_detail(request, user_id):
    if request.session.get('rol') != 'admin':
        return JsonResponse({'ok': False, 'error': 'Solo el administrador puede modificar usuarios'}, status=403)

    if request.method == 'PUT':
        data, err = parse_json(request)
        if err: return JsonResponse({'ok': False, 'error': err}, status=400)
        ok, msg = database.update_user(
            user_id,
            data.get('username', '').strip(),
            data.get('password', '').strip(),
            data.get('role', 'operador'),
        )
        if ok:
            return JsonResponse({'ok': True, 'mensaje': 'Usuario actualizado'})
        return JsonResponse({'ok': False, 'error': msg}, status=400)

    if request.method == 'DELETE':
        try:
            database.delete_user(user_id)
            return JsonResponse({'ok': True, 'mensaje': 'Usuario eliminado'})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ============================================================
# API — Reportes y estadísticas
# ============================================================

@login_required
def api_reportes_por_dia(request):
    desde = request.GET.get('desde', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    hasta = request.GET.get('hasta', datetime.now().strftime('%Y-%m-%d'))
    rows = database.sales_aggregate_by_day(desde, hasta)
    return JsonResponse({'ok': True, 'data': rows})


@login_required
def api_reportes_por_mes(request):
    desde = request.GET.get('desde', (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
    hasta = request.GET.get('hasta', datetime.now().strftime('%Y-%m-%d'))
    rows = database.sales_aggregate_by_month(desde, hasta)
    return JsonResponse({'ok': True, 'data': rows})


@login_required
def api_estadisticas(request):
    pallets = database.list_pallets()
    ventas = database.list_sales()
    total_ingresos = sum(v['cantidad'] * v['precio_unitario'] for v in ventas)
    total_cajas = sum(v['cantidad'] for v in ventas)
    hace7 = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
    hoy = datetime.now().strftime('%Y-%m-%d')
    ultimos_7 = database.sales_aggregate_by_day(hace7, hoy)
    return JsonResponse({
        'ok': True,
        'data': {
            'total_pallets': len(pallets),
            'total_ventas': len(ventas),
            'total_ingresos': round(total_ingresos, 2),
            'total_cajas': total_cajas,
            'ultimos_7_dias': ultimos_7,
        }
    })


# ============================================================
# Exportar a Excel
# ============================================================

@login_required
def export_ventas(request):
    try:
        import pandas as pd
        conn = database.get_conn()
        df = pd.read_sql_query("SELECT * FROM ventas ORDER BY fecha DESC, id DESC", conn)
        df['total'] = df['cantidad'] * df['precio_unitario']
        conn.close()
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        resp = HttpResponse(output.getvalue(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = f'attachment; filename="ventas_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        return resp
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@login_required
def export_pallets(request):
    try:
        import pandas as pd
        conn = database.get_conn()
        df = pd.read_sql_query("SELECT * FROM palets ORDER BY fecha DESC, id DESC", conn)
        conn.close()
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        resp = HttpResponse(output.getvalue(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = f'attachment; filename="pallets_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        return resp
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)
