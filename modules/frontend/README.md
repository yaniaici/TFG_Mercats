# Frontend - Mercats de Tarragona

Aplicació web per als usuaris dels mercats de Tarragona per escanejar i enviar tiquets de compra.

## Característiques

- **Autenticació d'usuaris**: Registre i inici de sessió
- **Escaneig de tiquets**: Captura de tiquets de compra amb la càmera
- **Pujada d'imatges**: Possibilitat de pujar fotos de tiquets des de la galeria
- **Dashboard**: Interfície principal per gestionar tiquets
- **Interfície en català**: Completament localitzada per als mercats de Tarragona

## Tecnologies

- React 18
- TypeScript
- Tailwind CSS
- React Router
- Lucide React (icones)
- React Webcam

## Instal·lació

```bash
npm install
```

## Desenvolupament

```bash
npm start
```

## Construcció

```bash
npm run build
```

## Estructura del Projecte

```
src/
├── components/
│   ├── auth/
│   │   ├── Login.tsx          # Pàgina d'inici de sessió
│   │   ├── Register.tsx       # Pàgina de registre
│   │   └── PrivateRoute.tsx   # Component de ruta protegida
│   ├── dashboard/
│   │   └── Dashboard.tsx      # Dashboard principal
│   └── tickets/
│       └── CreateTicket.tsx   # Escaneig de tiquets
├── contexts/
│   └── AuthContext.tsx        # Context d'autenticació
└── App.tsx                    # Component principal
```

## Funcionalitats Principals

### Escaneig de Tiquets
- Captura directa amb la càmera del dispositiu
- Pujada d'imatges des de la galeria
- Validació d'imatges obligatòries
- Interfície intuïtiva per a usuaris

### Dashboard
- Vista general dels tiquets enviats
- Estadístiques de processament
- Accés ràpid a noves funcionalitats
- Informació específica dels mercats de Tarragona

### Autenticació
- Registre d'usuaris nous
- Inici de sessió segur
- Gestió de sessions
- Interfície en català

## Configuració

L'aplicació està configurada per connectar-se amb els serveis backend dels mercats de Tarragona. Assegura't que els endpoints de l'API estiguin correctament configurats.

## Desplegament

L'aplicació pot ser desplegada en qualsevol servei d'hosting estàtic (Vercel, Netlify, etc.) o en un servidor web tradicional. 