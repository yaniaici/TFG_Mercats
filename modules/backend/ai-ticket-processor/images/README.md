# 📸 Imágenes de Ejemplo

Esta carpeta contiene imágenes de tickets para pruebas del sistema.

## 🎫 Archivos Disponibles

- **ticket.jpg** - Ticket de Mercadona (ejemplo principal para pruebas)

## 🧪 Cómo Usar

Para probar el sistema con estas imágenes:

```bash
# Probar con el ticket principal
python test_ticket.py

# O usar curl directamente
curl -X POST "http://localhost:8003/process-ticket" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@images/ticket.jpg"
```

## 📝 Notas

- Las imágenes se procesan temporalmente y no se almacenan
- El sistema soporta formatos: JPG, JPEG, PNG
- Tamaño máximo recomendado: 10MB por imagen 