# Especificación: Autenticación y Autorización

## Tecnología

- **Método**: Email/Password con JWT
- **Hashing**: bcrypt (10 rounds)
- **Tokens**: JWT con firma HS256

## Endpoints de Autenticación

### POST /api/auth/register

Registrar nuevo usuario.

**Request:**
```json
{
  "email": "consultor@blackandorange.com",
  "password": "SecurePass123!",
  "fullName": "Juan Pérez"
}
```

**Validaciones:**
- Email válido y único
- Password mínimo 8 caracteres, al menos 1 mayúscula, 1 número
- Full name no vacío

**Response (201):**
```json
{
  "user": {
    "id": "uuid",
    "email": "consultor@blackandorange.com",
    "fullName": "Juan Pérez"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errores:**
- `400`: Validación fallida
- `409`: Email ya registrado

### POST /api/auth/login

Iniciar sesión.

**Request:**
```json
{
  "email": "consultor@blackandorange.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "user": {
    "id": "uuid",
    "email": "consultor@blackandorange.com",
    "fullName": "Juan Pérez"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errores:**
- `401`: Credenciales inválidas

### GET /api/auth/me

Obtener usuario actual (requiere autenticación).

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "id": "uuid",
  "email": "consultor@blackandorange.com",
  "fullName": "Juan Pérez"
}
```

**Errores:**
- `401`: Token inválido o expirado

## Estructura del JWT

### Payload

```json
{
  "userId": "uuid",
  "email": "consultor@blackandorange.com",
  "iat": 1234567890,
  "exp": 1234654290
}
```

### Configuración

- **Expiración**: 7 días
- **Secret**: Variable de entorno `JWT_SECRET`
- **Algoritmo**: HS256

## Middleware de Autenticación

### authenticateToken

Middleware para rutas protegidas.

```javascript
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Token no proporcionado' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(401).json({ error: 'Token inválido' });
    }
    req.user = user;
    next();
  });
}
```

### Uso

```javascript
router.get('/api/accounts', authenticateToken, getAccounts);
```

## Autorización (Resource Ownership)

Validar que el usuario solo acceda a sus propios recursos.

### checkAccountOwnership

```javascript
async function checkAccountOwnership(req, res, next) {
  const { accountId } = req.params;
  const { userId } = req.user;

  const account = await db.query(
    'SELECT user_id FROM accounts WHERE id = $1',
    [accountId]
  );

  if (!account.rows[0]) {
    return res.status(404).json({ error: 'Cuenta no encontrada' });
  }

  if (account.rows[0].user_id !== userId) {
    return res.status(403).json({ error: 'Acceso denegado' });
  }

  next();
}
```

### Uso

```javascript
router.get(
  '/api/accounts/:accountId',
  authenticateToken,
  checkAccountOwnership,
  getAccount
);
```

## Seguridad

### Password Hashing

```javascript
const bcrypt = require('bcrypt');

// Al registrar
const passwordHash = await bcrypt.hash(password, 10);

// Al login
const isValid = await bcrypt.compare(password, user.password_hash);
```

### Variables de Entorno

```env
JWT_SECRET=your-super-secret-key-min-32-chars
JWT_EXPIRATION=7d
BCRYPT_ROUNDS=10
```

### Headers de Seguridad

Usar helmet.js:

```javascript
const helmet = require('helmet');
app.use(helmet());
```

## Frontend: Manejo de Tokens

### Almacenamiento

```javascript
// Guardar token al login/register
localStorage.setItem('authToken', token);

// Leer token
const token = localStorage.getItem('authToken');

// Eliminar al logout
localStorage.removeItem('authToken');
```

### Axios Interceptor

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

## Flujo Completo

1. Usuario llena formulario de registro
2. Frontend envía POST `/api/auth/register`
3. Backend valida, hashea password, crea usuario
4. Backend genera JWT
5. Frontend recibe token y lo guarda en localStorage
6. Frontend redirige a dashboard
7. Todas las requests subsecuentes incluyen token en header
8. Middleware valida token en cada request
9. Al logout, frontend elimina token
