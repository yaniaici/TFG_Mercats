#!/usr/bin/env python3
"""
Script para generar claves VAPID para WebPush
"""

import os
import sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import base64


def generate_vapid_keys():
    """
    Genera un nuevo par de claves VAPID para WebPush
    """
    try:
        # Generar clave privada
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        
        # Convertir clave privada a formato PEM
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        # Obtener coordenadas X e Y de la clave pública
        numbers = public_key.public_numbers()
        x = numbers.x
        y = numbers.y
        
        # Convertir a bytes
        x_bytes = x.to_bytes(32, 'big')
        y_bytes = y.to_bytes(32, 'big')
        
        # Concatenar y codificar en base64 URL safe
        raw_key = b'\x04' + x_bytes + y_bytes  # Prefijo 0x04 indica formato uncompressed
        public_key_b64 = base64.urlsafe_b64encode(raw_key).decode('utf-8').rstrip('=')
        
        return {
            "private_key": private_key_pem,
            "public_key": public_key_b64
        }
        
    except Exception as e:
        print(f"Error generando claves VAPID: {e}")
        return None


def main():
    """
    Función principal del script
    """
    print("Generando claves VAPID para WebPush...")
    
    keys = generate_vapid_keys()
    if not keys:
        print("Error: No se pudieron generar las claves")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("CLAVES VAPID GENERADAS")
    print("="*50)
    
    print("\n🔑 CLAVE PRIVADA (VAPID_PRIVATE_KEY):")
    print("-" * 40)
    print(keys["private_key"])
    
    print("\n🔑 CLAVE PÚBLICA (VAPID_PUBLIC_KEY):")
    print("-" * 40)
    print(keys["public_key"])
    
    print("\n" + "="*50)
    print("INSTRUCCIONES DE USO")
    print("="*50)
    print("\n1. Copia estas claves a tu archivo .env:")
    print(f"   VAPID_PRIVATE_KEY='{keys['private_key']}'")
    print(f"   VAPID_PUBLIC_KEY='{keys['public_key']}'")
    print("   VAPID_EMAIL='noreply@mercat.com'")
    
    print("\n2. La clave pública se usará en el frontend para suscribirse a notificaciones")
    print("3. La clave privada se usará en el backend para firmar las notificaciones")
    
    print("\n⚠️  IMPORTANTE:")
    print("- Mantén la clave privada segura y nunca la expongas públicamente")
    print("- Puedes regenerar las claves en cualquier momento ejecutando este script")
    
    # Guardar en archivo si se solicita
    save_to_file = input("\n¿Quieres guardar las claves en un archivo? (y/n): ").lower().strip()
    if save_to_file in ['y', 'yes', 'sí', 'si']:
        filename = input("Nombre del archivo (default: vapid_keys.txt): ").strip()
        if not filename:
            filename = "vapid_keys.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("VAPID_PRIVATE_KEY=" + repr(keys["private_key"]) + "\n")
                f.write("VAPID_PUBLIC_KEY=" + repr(keys["public_key"]) + "\n")
                f.write("VAPID_EMAIL=noreply@mercat.com\n")
            
            print(f"\n✅ Claves guardadas en {filename}")
        except Exception as e:
            print(f"\n❌ Error guardando archivo: {e}")


if __name__ == "__main__":
    main()


