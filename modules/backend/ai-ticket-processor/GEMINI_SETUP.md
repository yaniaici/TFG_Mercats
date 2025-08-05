# Configuración de Gemini API

Esta guía te ayudará a configurar la API key de Google Gemini para el procesamiento de tickets.

## 🔑 Obtener API Key de Gemini

### 1. Acceder a Google AI Studio

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Si es la primera vez, acepta los términos de servicio

### 2. Crear API Key

1. En la página principal, haz clic en "Create API Key"
2. Se generará una nueva API key
3. **IMPORTANTE**: Copia la key inmediatamente, no podrás verla de nuevo

### 3. Configurar Variables de Entorno

1. Crea un archivo `.env` en el directorio del proyecto:
```bash
cp env.example .env
```

2. Edita el archivo `.env` y reemplaza la línea:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

Con tu API key real:
```bash
GEMINI_API_KEY=AIzaSyC...  # Tu API key real aquí
```

## 🧪 Verificar Configuración

### Prueba Rápida

Ejecuta el script de prueba para verificar que todo funciona:

```bash
python test_gemini.py
```

Deberías ver:
```
🧪 TESTING GEMINI API CONNECTION
==================================================
🔑 API Key encontrada
🚀 Probando conexión con Gemini API...
✅ Conexión exitosa!
   Respuesta: OK

🧠 Probando inicialización del sistema de IA...
✅ Sistema de IA inicializado correctamente

🎉 ¡Todo listo! El sistema está funcionando correctamente
```

### Probar con Docker

Si usas Docker, asegúrate de pasar el archivo `.env`:

```bash
docker run -p 8003:8003 --env-file .env ai-ticket-processor
```

## 🔒 Seguridad

### Protección de la API Key

- **NUNCA** subas tu API key al repositorio
- El archivo `.env` ya está en `.gitignore`
- Usa variables de entorno en producción
- Rota las keys regularmente

### Límites de Uso

- **Gratuito**: 15 requests por minuto
- **Pago**: Hasta 1500 requests por minuto
- Consulta [Google AI Studio](https://makersuite.google.com/app/apikey) para más detalles

## 🚨 Solución de Problemas

### Error: "GEMINI_API_KEY no encontrada"

```bash
❌ Error: GEMINI_API_KEY no encontrada en variables de entorno
```

**Solución:**
1. Verifica que el archivo `.env` existe
2. Asegúrate de que la variable está definida correctamente
3. Reinicia el servicio después de cambiar el archivo

### Error: "Error en la API: 400"

```bash
❌ Error en la API: 400
```

**Solución:**
1. Verifica que la API key es válida
2. Asegúrate de que no hay espacios extra
3. Comprueba que tienes acceso a Gemini API

### Error: "Error de conexión"

```bash
❌ Error de conexión: Connection timeout
```

**Solución:**
1. Verifica tu conexión a internet
2. Comprueba que no hay firewall bloqueando
3. Intenta desde otra red si es posible

## 📞 Soporte

Si tienes problemas:

1. **Google AI Studio**: [Documentación oficial](https://ai.google.dev/docs)
2. **API Status**: [Google Cloud Status](https://status.cloud.google.com/)
3. **Quotas**: [Google AI Studio Quotas](https://makersuite.google.com/app/apikey)

## 💡 Consejos

- **Desarrollo**: Usa la API key gratuita para pruebas
- **Producción**: Considera el plan de pago para mayor rendimiento
- **Backup**: Guarda tu API key en un lugar seguro
- **Monitoreo**: Revisa el uso en Google AI Studio regularmente 