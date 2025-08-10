# Servicio de Tickets con IA

Este servicio gestiona la subida, procesamiento y validación de tickets de compra usando inteligencia artificial.

## 🎯 Funcionalidades

### Estados de Tickets
- **`pending`**: Ticket subido, pendiente de procesamiento
- **`done_approved`**: Ticket procesado y aprobado (es de tienda del mercado)
- **`done_rejected`**: Ticket procesado pero rechazado (no es de tienda del mercado)
- **`failed`**: Error en el procesamiento

### Tiendas del Mercado
El sistema mantiene una lista de tiendas del mercado válidas:
- **Mercadona**
- **Eroski** 
- **Carrefour**

Solo los tickets de estas tiendas serán aprobados y contarán para la feed de los usuarios.

## 🚀 Instalación y Configuración

### 1. Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp env.example .env

# Configurar variables
DATABASE_URL=postgresql://user:password@localhost:5432/tickets_db
GEMINI_API_KEY=tu_api_key_de_gemini
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Crear Base de Datos
```bash
# Las tablas se crean automáticamente al ejecutar el servicio
```

### 4. Poblar Tiendas del Mercado
```bash
python seed_market_stores.py
```

## 📡 Endpoints

### Tiendas del Mercado

#### Crear Tienda
```http
POST /market-stores/
{
    "name": "Nueva Tienda",
    "description": "Descripción de la tienda"
}
```

#### Listar Tiendas
```http
GET /market-stores/
```

#### Verificar Tienda
```http
GET /market-stores/verify/{store_name}
```

### Tickets

#### Subir Ticket
```http
POST /tickets/upload/
Content-Type: multipart/form-data

file: [archivo_imagen]
user_id: "uuid_del_usuario"
```

#### Listar Tickets
```http
GET /tickets/?user_id={user_id}&status={status}
```

#### Procesar Ticket Individual
```http
POST /tickets/{ticket_id}/process/
```

#### Procesar Todos los Pendientes
```http
POST /tickets/process-pending/
```

## 🤖 Procesamiento con IA

### Flujo de Procesamiento
1. **Subida**: El usuario sube una imagen de ticket
2. **Análisis IA**: Gemini AI extrae información del ticket
3. **Verificación**: Se verifica si la tienda está en la lista de tiendas del mercado
4. **Clasificación**:
   - ✅ **Aprobado**: Si es tienda del mercado → `done_approved`
   - ❌ **Rechazado**: Si no es tienda del mercado → `done_rejected`
   - 💥 **Fallido**: Si hay error en el procesamiento → `failed`

### Información Extraída
- Fecha y hora del ticket
- Nombre de la tienda
- Total del ticket
- Lista de productos
- Tipo de ticket (supermercado, restaurante, etc.)

## 🛠️ Scripts Útiles

### Poblar Tiendas del Mercado
```bash
python seed_market_stores.py
```

### Procesar Tickets Pendientes
```bash
python ../ai-ticket-processor/process_pending_tickets.py
```

## 📊 Ejemplo de Respuesta de Procesamiento

```json
{
    "fecha": "15/12/2024",
    "hora": "14:30",
    "tienda": "Mercadona",
    "total": 45.67,
    "tipo_ticket": "supermercado",
    "productos": [
        {
            "cantidad": "2",
            "nombre": "Leche",
            "precio": "1.20"
        }
    ],
    "num_productos": 1,
    "procesado_correctamente": true,
    "es_tienda_mercado": true,
    "ticket_status": "done_approved",
    "status_message": "Ticket aprobado - Tienda del mercado"
}
```

## 🔧 Configuración de IA

El servicio usa **Google Gemini 2.0 Flash** para el procesamiento de imágenes. Asegúrate de tener configurada la variable `GEMINI_API_KEY`.

## 📝 Notas Importantes

- Solo los tickets con estado `done_approved` contarán para la feed de los usuarios
- Los tickets rechazados (`done_rejected`) no afectan las estadísticas del usuario
- El sistema es flexible y permite agregar más tiendas del mercado según sea necesario
- Todos los tickets se procesan de forma asíncrona para mejor rendimiento 