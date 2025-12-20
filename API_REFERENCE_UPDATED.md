# RealStart API Reference

**Base URL**: `http://localhost:8000/api/v1`

### 1. Register Public User
**URL**: `http://localhost:8000/api/v1/auth/register`

**Success Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/auth/register' -H 'Content-Type: application/json' -d '{"email": "b2_o7oxe5@ex.com", "password": "StrongPass123!", "full_name": "Test", "role": "BUYER"}'
```
```json
{
  "id": "64eb85b4-b925-4a6c-aaaa-4f30ac634e49",
  "email": "b2_o7oxe5@ex.com",
  "full_name": "Test",
  "role": "BUYER",
  "is_active": true
}
```

**Failure Response**
Status: `400`
```bash
curl -X POST 'http://localhost:8000/api/v1/auth/register' -H 'Content-Type: application/json' -d '{"email": "b2_o7oxe5@ex.com", "password": "StrongPass123!", "full_name": "Test", "role": "BUYER"}'
```
```json
{
  "detail": "The user with this email already exists in the system"
}
```

---

### 2. Login
**URL**: `http://localhost:8000/api/v1/auth/login`

**Success Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/auth/login' -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=buyer_o7oxe5@example.com' -d 'password=StrongUserPass123!'
```
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxNDYsInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.3f71iz7nB0GKgW8ndTPwtyhNoB9_mL4r2eU4iRThzJ4",
  "token_type": "bearer"
}
```

**Failure Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/auth/login' -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=buyer_o7oxe5@example.com' -d 'password=StrongUserPass123!'
```
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxNDgsInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9._twBIqugSxYTvu0F7NIISHvXPCH8x4j-zPdFA2yzNAo",
  "token_type": "bearer"
}
```

---

### 3. Get Current User
**URL**: `http://localhost:8000/api/v1/auth/me`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/auth/me' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w'
```
```json
{
  "id": "de814814-727d-482c-998d-de82f825c229",
  "email": "buyer_o7oxe5@example.com",
  "full_name": "Fresh Buyer",
  "role": "BUYER",
  "is_active": true
}
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/auth/me' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 4. Register Admin User
**URL**: `http://localhost:8000/api/v1/admin/register-admin`

**Success Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/register-admin' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE' -H 'Content-Type: application/json' -d '{"email": "adm2_o7oxe5@ex.com", "password": "StrongAdmin123!", "full_name": "Test Admin", "role": "ADMIN"}'
```
```json
{
  "id": "585ac933-f0a8-4f34-bcba-f5ee31a251e8",
  "email": "adm2_o7oxe5@ex.com",
  "full_name": "Test Admin",
  "role": "ADMIN",
  "is_active": true
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/register-admin' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"email": "adm2_o7oxe5@ex.com", "password": "StrongAdmin123!", "full_name": "Test Admin", "role": "ADMIN"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 5. Create Project
**URL**: `http://localhost:8000/api/v1/developers/projects/`

**Success Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/developers/projects/' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0' -H 'Content-Type: application/json' -d '{"name": "Project o7oxe5", "slug": "proj-o7oxe5", "description": "Desc", "city": "Bangalore", "developer_id": "00000000-0000-0000-0000-000000000000"}'
```
```json
{
  "name": "Project o7oxe5",
  "description": "Desc",
  "approval_type": null,
  "rera_number": null,
  "address": null,
  "latitude": null,
  "longitude": null,
  "launch_year": null,
  "id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
  "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
  "slug": "proj-o7oxe5",
  "status": "PENDING",
  "is_hidden": false,
  "created_at": "2025-12-17T12:39:18.795101",
  "updated_at": "2025-12-17T12:39:18.795105"
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/developers/projects/' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"name": "Project o7oxe5", "slug": "proj-o7oxe5", "description": "Desc", "city": "Bangalore", "developer_id": "00000000-0000-0000-0000-000000000000"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 6. List My Projects
**URL**: `http://localhost:8000/api/v1/developers/projects/my-projects`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/developers/projects/my-projects' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0'
```
```json
[
  {
    "name": "Project o7oxe5",
    "description": "Desc",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
    "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
    "slug": "proj-o7oxe5",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-17T12:39:18.795000",
    "updated_at": "2025-12-17T12:39:18.795000"
  }
]
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/developers/projects/my-projects' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 7. Approve Project (Admin)
**URL**: `http://localhost:8000/api/v1/admin/projects/55ec5c12-5811-49f0-881d-7186db2a3f13/approve`

**Success Response**
Status: `200`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/admin/projects/55ec5c12-5811-49f0-881d-7186db2a3f13/approve' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
{
  "name": "Project o7oxe5",
  "description": "Desc",
  "approval_type": null,
  "rera_number": null,
  "address": null,
  "latitude": null,
  "longitude": null,
  "launch_year": null,
  "id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
  "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
  "slug": "proj-o7oxe5",
  "status": "APPROVED",
  "is_hidden": false,
  "created_at": "2025-12-17T12:39:18.795000",
  "updated_at": "2025-12-17T12:39:18.795000"
}
```

**Failure Response**
Status: `403`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/admin/projects/55ec5c12-5811-49f0-881d-7186db2a3f13/approve' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 8. List Public Projects
**URL**: `http://localhost:8000/api/v1/public/projects/`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/public/projects/' 
```
```json
[
  {
    "name": "Project 9xyth1 Updated",
    "description": "Updated desc",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "1495079b-ce4c-4c90-be67-2e4685a200c2",
    "developer_id": "56abf9f0-dfad-43de-9222-edde57b72547",
    "slug": "project-9xyth1",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-17T09:51:10.347000",
    "updated_at": "2025-12-17T09:51:18.750000"
  },
  {
    "name": "Project yjapg2 Updated",
    "description": "Updated desc",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "fe818a45-2cea-4e66-b3e8-9f8744edaccd",
    "developer_id": "4990804b-e7db-4883-b04f-7cc28e8ea692",
    "slug": "project-yjapg2",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-17T09:53:54.738000",
    "updated_at": "2025-12-17T09:54:03.055000"
  },
  {
    "name": "Project o7oxe5",
    "description": "Desc",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
    "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
    "slug": "proj-o7oxe5",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-17T12:39:18.795000",
    "updated_at": "2025-12-17T12:39:18.795000"
  }
]
```

**Failure Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/public/projects/' 
```
```json
[
  {
    "name": "Project 9xyth1 Updated",
    "description": "Updated desc",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "1495079b-ce4c-4c90-be67-2e4685a200c2",
    "developer_id": "56abf9f0-dfad-43de-9222-edde57b72547",
    "slug": "project-9xyth1",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-17T09:51:10.347000",
    "updated_at": "2025-12-17T09:51:18.750000"
  },
  {
    "name": "Project yjapg2 Updated",
    "description": "Updated desc",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "fe818a45-2cea-4e66-b3e8-9f8744edaccd",
    "developer_id": "4990804b-e7db-4883-b04f-7cc28e8ea692",
    "slug": "project-yjapg2",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-17T09:53:54.738000",
    "updated_at": "2025-12-17T09:54:03.055000"
  },
  {
    "name": "Project o7oxe5",
    "description": "Desc",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
    "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
    "slug": "proj-o7oxe5",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-17T12:39:18.795000",
    "updated_at": "2025-12-17T12:39:18.795000"
  }
]
```

---

### 9. Get Project by Slug
**URL**: `http://localhost:8000/api/v1/public/projects/proj-o7oxe5`

**Success Response**
Status: `401`
```bash
curl -X GET 'http://localhost:8000/api/v1/public/projects/proj-o7oxe5' 
```
```json
{
  "detail": "Not authenticated"
}
```

**Failure Response**
Status: `401`
```bash
curl -X GET 'http://localhost:8000/api/v1/public/projects/proj-o7oxe5' 
```
```json
{
  "detail": "Not authenticated"
}
```

---

### 10. Update Profile
**URL**: `http://localhost:8000/api/v1/users/me`

**Success Response**
Status: `200`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/users/me' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w' -H 'Content-Type: application/json' -d '{"phone": "+1234567890"}'
```
```json
{
  "id": "de814814-727d-482c-998d-de82f825c229",
  "email": "buyer_o7oxe5@example.com",
  "full_name": "Fresh Buyer",
  "phone": "+1234567890",
  "role": "BUYER"
}
```

**Failure Response**
Status: `403`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/users/me' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"phone": "+1234567890"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 11. Get Profile
**URL**: `http://localhost:8000/api/v1/users/me`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/users/me' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w'
```
```json
{
  "id": "de814814-727d-482c-998d-de82f825c229",
  "email": "buyer_o7oxe5@example.com",
  "full_name": "Fresh Buyer",
  "phone": "+1234567890",
  "role": "BUYER"
}
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/users/me' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 12. Log View (Interaction)
**URL**: `http://localhost:8000/api/v1/users/interactions/proj-o7oxe5/view`

**Success Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/users/interactions/proj-o7oxe5/view' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w'
```
```json
{
  "message": "View logged"
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/users/interactions/proj-o7oxe5/view' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 13. Toggle Wishlist
**URL**: `http://localhost:8000/api/v1/users/interactions/proj-o7oxe5/wishlist`

**Success Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/users/interactions/proj-o7oxe5/wishlist' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w'
```
```json
{
  "message": "Updated",
  "is_wishlisted": true
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/users/interactions/proj-o7oxe5/wishlist' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 14. View History
**URL**: `http://localhost:8000/api/v1/users/me/history`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/users/me/history' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w'
```
```json
[
  {
    "name": "Project o7oxe5",
    "description": "Desc",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
    "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
    "slug": "proj-o7oxe5",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-17T12:39:18.795000",
    "updated_at": "2025-12-17T12:39:18.795000"
  }
]
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/users/me/history' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 15. Get Wishlist
**URL**: `http://localhost:8000/api/v1/users/me/wishlist`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/users/me/wishlist' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w'
```
```json
[
  {
    "name": "Project o7oxe5",
    "description": "Desc",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
    "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
    "slug": "proj-o7oxe5",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-17T12:39:18.795000",
    "updated_at": "2025-12-17T12:39:18.795000"
  }
]
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/users/me/wishlist' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 16. Create Landmark (Admin)
**URL**: `http://localhost:8000/api/v1/admin/landmarks`

**Success Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/landmarks' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE' -H 'Content-Type: application/json' -d '{"name": "Test Landmark", "city": "Bangalore", "latitude": 12.97, "longitude": 77.59, "type": "SCHOOL"}'
```
```json
{
  "id": "9b098329-55fa-423a-8cb2-44947bacc43c",
  "name": "Test Landmark",
  "city": "Bangalore",
  "zone": null,
  "latitude": 12.97,
  "longitude": 77.59,
  "avg_price_per_sqft": null,
  "median_price": null,
  "growth_forecast_5yr": null,
  "price_trend": null,
  "price_trend_3m": null,
  "total_projects": 0,
  "active_layouts_count": 0,
  "rera_projects_count": 0,
  "description": null,
  "nearby_amenities": null,
  "nearby_projects": [],
  "created_at": "2025-12-17T12:40:04.692878",
  "updated_at": "2025-12-17T12:40:04.692893"
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/landmarks' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"name": "Test Landmark", "city": "Bangalore", "latitude": 12.97, "longitude": 77.59, "type": "SCHOOL"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 17. List Landmarks
**URL**: `http://localhost:8000/api/v1/public/landmarks`

**Success Response**
Status: `500`
```bash
curl -X GET 'http://localhost:8000/api/v1/public/landmarks' 
```
```json
Internal Server Error
```

**Failure Response**
Status: `500`
```bash
curl -X GET 'http://localhost:8000/api/v1/public/landmarks' 
```
```json
Internal Server Error
```

---

### 18. Get Landmark
**URL**: `http://localhost:8000/api/v1/public/landmarks/9b098329-55fa-423a-8cb2-44947bacc43c`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/public/landmarks/9b098329-55fa-423a-8cb2-44947bacc43c' 
```
```json
{
  "id": "9b098329-55fa-423a-8cb2-44947bacc43c",
  "name": "Test Landmark",
  "city": "Bangalore",
  "zone": null,
  "latitude": 12.97,
  "longitude": 77.59,
  "avg_price_per_sqft": null,
  "median_price": null,
  "growth_forecast_5yr": null,
  "price_trend": null,
  "price_trend_3m": null,
  "total_projects": 0,
  "active_layouts_count": 0,
  "rera_projects_count": 0,
  "description": null,
  "nearby_amenities": null,
  "nearby_projects": [
    {
      "id": "25a7010b-d348-4e73-8432-e72de8fb869c",
      "developer_id": "fe64600d-cd54-4e3a-b82b-5b803c66696c",
      "name": "Park View Residency",
      "slug": "park-view-residency-v2",
      "description": null,
      "status": "PENDING",
      "approval_type": null,
      "rera_number": null,
      "address": null,
      "latitude": 12.978,
      "longitude": 77.5946,
      "launch_year": null,
      "is_hidden": false,
      "created_at": "2025-12-15T05:14:00.854000",
      "updated_at": "2025-12-15T05:14:00.854000"
    }
  ],
  "created_at": "2025-12-17T12:40:04.692000",
  "updated_at": "2025-12-17T12:40:04.692000"
}
```

**Failure Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/public/landmarks/9b098329-55fa-423a-8cb2-44947bacc43c' 
```
```json
{
  "id": "9b098329-55fa-423a-8cb2-44947bacc43c",
  "name": "Test Landmark",
  "city": "Bangalore",
  "zone": null,
  "latitude": 12.97,
  "longitude": 77.59,
  "avg_price_per_sqft": null,
  "median_price": null,
  "growth_forecast_5yr": null,
  "price_trend": null,
  "price_trend_3m": null,
  "total_projects": 0,
  "active_layouts_count": 0,
  "rera_projects_count": 0,
  "description": null,
  "nearby_amenities": null,
  "nearby_projects": [
    {
      "id": "25a7010b-d348-4e73-8432-e72de8fb869c",
      "developer_id": "fe64600d-cd54-4e3a-b82b-5b803c66696c",
      "name": "Park View Residency",
      "slug": "park-view-residency-v2",
      "description": null,
      "status": "PENDING",
      "approval_type": null,
      "rera_number": null,
      "address": null,
      "latitude": 12.978,
      "longitude": 77.5946,
      "launch_year": null,
      "is_hidden": false,
      "created_at": "2025-12-15T05:14:00.854000",
      "updated_at": "2025-12-15T05:14:00.854000"
    }
  ],
  "created_at": "2025-12-17T12:40:04.692000",
  "updated_at": "2025-12-17T12:40:04.692000"
}
```

---

### 19. Create Visit Booking
**URL**: `http://localhost:8000/api/v1/users/me/bookings`

**Success Response**
Status: `422`
```bash
curl -X POST 'http://localhost:8000/api/v1/users/me/bookings' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w' -H 'Content-Type: application/json' -d '{"project_id": "{project_id}", "scheduled_time": "2025-12-25T10:00:00", "pickup_location": "Home"}'
```
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": [
        "body",
        "project_id"
      ],
      "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `p` at 2",
      "input": "{project_id}",
      "ctx": {
        "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `p` at 2"
      }
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/users/me/bookings' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"project_id": "{project_id}", "scheduled_time": "2025-12-25T10:00:00", "pickup_location": "Home"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 20. List My Bookings
**URL**: `http://localhost:8000/api/v1/users/me/bookings`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/users/me/bookings' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w'
```
```json
[]
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/users/me/bookings' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 21. Request Legal
**URL**: `http://localhost:8000/api/v1/users/interactions/proj-o7oxe5/legal-request`

**Success Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/users/interactions/proj-o7oxe5/legal-request' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w'
```
```json
{
  "message": "Legal consultation requested"
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/users/interactions/proj-o7oxe5/legal-request' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 22. Book Visit (Interaction)
**URL**: `http://localhost:8000/api/v1/users/interactions/proj-o7oxe5/book-visit`

**Success Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/users/interactions/proj-o7oxe5/book-visit' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w'
```
```json
{
  "message": "Visit booked"
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/users/interactions/proj-o7oxe5/book-visit' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 23. Update Project (Direct)
**URL**: `http://localhost:8000/api/v1/developers/projects/55ec5c12-5811-49f0-881d-7186db2a3f13`

**Success Response**
Status: `200`
```bash
curl -X PUT 'http://localhost:8000/api/v1/developers/projects/55ec5c12-5811-49f0-881d-7186db2a3f13' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0' -H 'Content-Type: application/json' -d '{"name": "Proj o7oxe5 Updated", "slug": "proj-o7oxe5", "description": "Updated", "city": "Bangalore"}'
```
```json
{
  "message": "Update request submitted for approval",
  "request_id": "92f6445f-0c25-4127-9d84-752641c75252"
}
```

**Failure Response**
Status: `403`
```bash
curl -X PUT 'http://localhost:8000/api/v1/developers/projects/55ec5c12-5811-49f0-881d-7186db2a3f13' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"name": "Proj o7oxe5 Updated", "slug": "proj-o7oxe5", "description": "Updated", "city": "Bangalore"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 24. Toggle Visibility
**URL**: `http://localhost:8000/api/v1/developers/projects/55ec5c12-5811-49f0-881d-7186db2a3f13/hide`

**Success Response**
Status: `200`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/developers/projects/55ec5c12-5811-49f0-881d-7186db2a3f13/hide' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0' -H 'Content-Type: application/json' -d '{"is_hidden": true}'
```
```json
{
  "name": "Project o7oxe5",
  "description": "Desc",
  "approval_type": null,
  "rera_number": null,
  "address": null,
  "latitude": null,
  "longitude": null,
  "launch_year": null,
  "id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
  "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
  "slug": "proj-o7oxe5",
  "status": "APPROVED",
  "is_hidden": true,
  "created_at": "2025-12-17T12:39:18.795000",
  "updated_at": "2025-12-17T12:39:18.795000"
}
```

**Failure Response**
Status: `403`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/developers/projects/55ec5c12-5811-49f0-881d-7186db2a3f13/hide' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"is_hidden": true}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 26. Purchase Lead
**URL**: `http://localhost:8000/api/v1/developers/leads/leads/{lead_id}/purchase`

**Success Response**
Status: `422`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/developers/leads/leads/{lead_id}/purchase' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0'
```
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": [
        "path",
        "lead_id"
      ],
      "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `l` at 2",
      "input": "{lead_id}",
      "ctx": {
        "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `l` at 2"
      }
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/developers/leads/leads/{lead_id}/purchase' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 27. Update Lead Status
**URL**: `http://localhost:8000/api/v1/developers/leads/leads/{lead_id}/status`

**Success Response**
Status: `422`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/developers/leads/leads/{lead_id}/status' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0' -H 'Content-Type: application/json' -d '{"status": "CONTACTED", "developer_notes": "Called"}'
```
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": [
        "path",
        "lead_id"
      ],
      "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `l` at 2",
      "input": "{lead_id}",
      "ctx": {
        "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `l` at 2"
      }
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/developers/leads/leads/{lead_id}/status' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"status": "CONTACTED", "developer_notes": "Called"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 28. Developer Dashboard
**URL**: `http://localhost:8000/api/v1/developers/leads/dashboard`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/developers/leads/dashboard' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0'
```
```json
{
  "period_start": "2025-12-17T00:00:00",
  "period_end": "2025-12-17T12:40:52.850828",
  "period_type": "day",
  "total_visitors": 1,
  "total_plot_visits": 1,
  "total_legal_consultations": 1,
  "interested_visitors": 1,
  "total_views": 1,
  "projects": [
    {
      "project_id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
      "project_name": "Project o7oxe5",
      "project_slug": "proj-o7oxe5",
      "visitors": 1,
      "plot_visits": 1,
      "legal_consultations": 1,
      "interested_visitors": 1,
      "total_views": 1
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/developers/leads/dashboard' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 29. Register Webhook
**URL**: `http://localhost:8000/api/v1/developers/webhooks/`

**Success Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/developers/webhooks/' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0' -H 'Content-Type: application/json' -d '{"url": "https://example.com/hook", "events": ["lead.new"], "secret_token": "sec"}'
```
```json
{
  "id": "d0ed884f-eaac-4adc-a73f-26f5f92f7308",
  "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
  "url": "https://example.com/hook",
  "events": [
    "lead.new"
  ],
  "is_active": true,
  "created_at": "2025-12-17T12:40:57.030007"
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/developers/webhooks/' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"url": "https://example.com/hook", "events": ["lead.new"], "secret_token": "sec"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 30. List Webhooks
**URL**: `http://localhost:8000/api/v1/developers/webhooks/`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/developers/webhooks/' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0'
```
```json
[
  {
    "id": "d0ed884f-eaac-4adc-a73f-26f5f92f7308",
    "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
    "url": "https://example.com/hook",
    "events": [
      "lead.new"
    ],
    "is_active": true,
    "created_at": "2025-12-17T12:40:57.030000"
  }
]
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/developers/webhooks/' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 31. Delete Webhook
**URL**: `http://localhost:8000/api/v1/developers/webhooks/d0ed884f-eaac-4adc-a73f-26f5f92f7308`

**Success Response**
Status: `200`
```bash
curl -X DELETE 'http://localhost:8000/api/v1/developers/webhooks/d0ed884f-eaac-4adc-a73f-26f5f92f7308' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0'
```
```json
{
  "message": "Deleted"
}
```

**Failure Response**
Status: `403`
```bash
curl -X DELETE 'http://localhost:8000/api/v1/developers/webhooks/d0ed884f-eaac-4adc-a73f-26f5f92f7308' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 32. Invite Team Member
**URL**: `http://localhost:8000/api/v1/developers/team/invite`

**Success Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/developers/team/invite' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0' -H 'Content-Type: application/json' -d '{"email": "team_o7oxe5@ex.com", "role": "Sales", "permissions": ["leads:view_basic"]}'
```
```json
{
  "detail": "Team member limit reached (0/0). Please upgrade your plan."
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/developers/team/invite' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"email": "team_o7oxe5@ex.com", "role": "Sales", "permissions": ["leads:view_basic"]}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 33. List Team
**URL**: `http://localhost:8000/api/v1/developers/team/`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/developers/team/' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0'
```
```json
[]
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/developers/team/' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 34. Update Member Permissions
**URL**: `http://localhost:8000/api/v1/developers/team/{team_member_id}/permissions`

**Success Response**
Status: `422`
```bash
curl -X PUT 'http://localhost:8000/api/v1/developers/team/{team_member_id}/permissions' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0' -H 'Content-Type: application/json' -d '{"permissions": ["leads:view_basic", "leads:view_full"]}'
```
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": [
        "path",
        "member_id"
      ],
      "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `t` at 2",
      "input": "{team_member_id}",
      "ctx": {
        "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `t` at 2"
      }
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X PUT 'http://localhost:8000/api/v1/developers/team/{team_member_id}/permissions' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"permissions": ["leads:view_basic", "leads:view_full"]}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 35. Remove Team Member
**URL**: `http://localhost:8000/api/v1/developers/team/{team_member_id}`

**Success Response**
Status: `422`
```bash
curl -X DELETE 'http://localhost:8000/api/v1/developers/team/{team_member_id}' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0'
```
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": [
        "path",
        "member_id"
      ],
      "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `t` at 2",
      "input": "{team_member_id}",
      "ctx": {
        "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `t` at 2"
      }
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X DELETE 'http://localhost:8000/api/v1/developers/team/{team_member_id}' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 36. List Sub Plans (Dev)
**URL**: `http://localhost:8000/api/v1/developers/subscriptions/plans`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/developers/subscriptions/plans' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0'
```
```json
[]
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/developers/subscriptions/plans' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 37. Get Current Sub (Dev)
**URL**: `http://localhost:8000/api/v1/developers/subscriptions/current`

**Success Response**
Status: `500`
```bash
curl -X GET 'http://localhost:8000/api/v1/developers/subscriptions/current' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0'
```
```json
Internal Server Error
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/developers/subscriptions/current' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 38. Create Plan (Admin)
**URL**: `http://localhost:8000/api/v1/admin/subscriptions/plans`

**Success Response**
Status: `422`
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/subscriptions/plans' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE' -H 'Content-Type: application/json' -d '{"name": "Pro Plan", "price": 1000, "duration_days": 30, "description": "Pro features", "features": ["leads:unlimited"], "is_active": true}'
```
```json
{
  "detail": [
    {
      "type": "dict_type",
      "loc": [
        "body",
        "features"
      ],
      "msg": "Input should be a valid dictionary",
      "input": [
        "leads:unlimited"
      ]
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/subscriptions/plans' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"name": "Pro Plan", "price": 1000, "duration_days": 30, "description": "Pro features", "features": ["leads:unlimited"], "is_active": true}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 39. List Plans (Admin)
**URL**: `http://localhost:8000/api/v1/admin/subscriptions/plans`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/subscriptions/plans' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
[]
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/subscriptions/plans' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 40. Purchase Subscription
**URL**: `http://localhost:8000/api/v1/developers/subscriptions/purchase`

**Success Response**
Status: `422`
```bash
curl -X POST 'http://localhost:8000/api/v1/developers/subscriptions/purchase' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0' -H 'Content-Type: application/json' -d '{"plan_id": "{plan_id}", "payment_method_id": "tok_visa"}'
```
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": [
        "body",
        "plan_id"
      ],
      "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `p` at 2",
      "input": "{plan_id}",
      "ctx": {
        "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `p` at 2"
      }
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/developers/subscriptions/purchase' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"plan_id": "{plan_id}", "payment_method_id": "tok_visa"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 41. List All Subs (Admin)
**URL**: `http://localhost:8000/api/v1/admin/subscriptions/subscriptions`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/subscriptions/subscriptions' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
[]
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/subscriptions/subscriptions' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 42. List All Projects (Admin)
**URL**: `http://localhost:8000/api/v1/admin/projects/`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/projects/' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
[
  {
    "name": "Luxury Homes",
    "description": "High end villas",
    "approval_type": null,
    "rera_number": null,
    "address": "123 Rich St",
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "21b4cbdd-ce62-44b9-aed9-42b14d9a9468",
    "developer_id": "1e9274f9-7af7-44af-8819-09ce3b044fbd",
    "slug": "luxury-homes-8a31fb",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-09T07:48:16.700000",
    "updated_at": "2025-12-09T07:48:16.700000"
  },
  {
    "name": "Lead Project",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "6729c353-d5fd-4e33-a672-e2045f215a8e",
    "developer_id": "fdf874f9-2723-4270-bef2-0288215df86c",
    "slug": "lead-project-138c38",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-09T08:03:08.065000",
    "updated_at": "2025-12-09T08:03:08.065000"
  },
  {
    "name": "Lead Project",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "b346d3a1-5990-4a30-a3c3-3d7f445f09e8",
    "developer_id": "4d2d86d8-616b-4a21-a2aa-e24c4a631d2d",
    "slug": "lead-project-e2733d",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-09T08:04:39.953000",
    "updated_at": "2025-12-09T08:04:39.953000"
  },
  {
    "name": "Lead Project",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "4b0f2f39-8e4a-4cfb-ad52-6f64d51052df",
    "developer_id": "de58f2c7-e2a1-405e-9bdb-cfc88a4a2c69",
    "slug": "lead-project-192bf9",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-09T08:05:44.956000",
    "updated_at": "2025-12-09T08:05:44.956000"
  },
  {
    "name": "Lead Project",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "1330dae6-c9cd-42f0-b455-f7ad4a2dbb25",
    "developer_id": "325a840e-3a21-42ae-8f8f-157514c2ee2d",
    "slug": "lead-project-d13221",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-09T08:06:30.745000",
    "updated_at": "2025-12-09T08:06:30.745000"
  },
  {
    "name": "Lead Project",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "d50e7ae7-eb65-4dcc-a0b4-b48ba7a25432",
    "developer_id": "23a55e0f-781a-4a9b-adf5-1c60c3a64f9a",
    "slug": "lead-project-df1a9d",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-09T08:07:22.968000",
    "updated_at": "2025-12-09T08:07:22.968000"
  },
  {
    "name": "Lead Project",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "50020c40-2d13-4cad-8e8a-1889081a30eb",
    "developer_id": "833f2450-b5aa-4ca6-bcd7-c1237cd0596a",
    "slug": "lead-project-66f8e8",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-09T08:08:40.753000",
    "updated_at": "2025-12-09T08:08:40.753000"
  },
  {
    "name": "string2",
    "description": "string",
    "approval_type": "RERA",
    "rera_number": "2345698765234765",
    "address": "string",
    "latitude": null,
    "longitude": null,
    "launch_year": 2020,
    "id": "ab05962f-af33-4583-a6bf-490bcef540e3",
    "developer_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "slug": "string",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-09T10:51:14.907000",
    "updated_at": "2025-12-09T10:51:14.907000"
  },
  {
    "name": "Hook Proj",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "7945905c-fc50-477e-9298-a885a8978b7b",
    "developer_id": "717f3889-1388-4ad0-be93-8a28fb3ce2f4",
    "slug": "webhook-proj-d5e590",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-10T07:20:50.552000",
    "updated_at": "2025-12-10T07:20:50.552000"
  },
  {
    "name": "Hook Proj",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "65b45b22-591b-4d06-9ff4-5d53aea1b5f9",
    "developer_id": "aaea06b8-b00f-46e7-8c9b-f1980d598c13",
    "slug": "webhook-proj-8713b2",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-10T07:22:05.286000",
    "updated_at": "2025-12-10T07:22:05.286000"
  },
  {
    "name": "Public Project",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "12e71f52-a67c-4f23-ae17-b6d05a83479f",
    "developer_id": "dc162b75-257f-48df-977a-e9df044955e5",
    "slug": "proj-approve-c41168",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-11T05:12:33.122000",
    "updated_at": "2025-12-11T05:12:33.122000"
  },
  {
    "name": "Pending Project",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "7de8bed5-43ea-4967-9c03-b8fb3ccac6cb",
    "developer_id": "dc162b75-257f-48df-977a-e9df044955e5",
    "slug": "proj-pending-603db7",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-11T05:12:33.218000",
    "updated_at": "2025-12-11T05:12:33.218000"
  },
  {
    "name": "Portal Heaven",
    "description": "Luxury Portal",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "d33ef992-add8-4a7b-8035-2fe322b304e6",
    "developer_id": "57c2ea64-f228-49a1-86fc-ccfb65c7eb5f",
    "slug": "portal-heaven-433bad",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-11T06:21:16.572000",
    "updated_at": "2025-12-11T06:21:16.572000"
  },
  {
    "name": "Portal Heaven",
    "description": "Luxury Portal",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "ec99c24b-a225-49c2-a49b-648e2a7998a0",
    "developer_id": "57c2ea64-f228-49a1-86fc-ccfb65c7eb5f",
    "slug": "portal-heaven-98778b",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-11T06:22:29.360000",
    "updated_at": "2025-12-11T06:22:29.360000"
  },
  {
    "name": "Portal Heaven",
    "description": "Luxury Portal",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "95c72447-9779-4ca3-8ddf-baa78817df6c",
    "developer_id": "57c2ea64-f228-49a1-86fc-ccfb65c7eb5f",
    "slug": "portal-heaven-d3ec95",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-11T06:22:31.447000",
    "updated_at": "2025-12-11T06:22:31.447000"
  },
  {
    "name": "Portal Heaven",
    "description": "Luxury Portal",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "b111be42-e736-444a-ab50-9eabb0142ce4",
    "developer_id": "57c2ea64-f228-49a1-86fc-ccfb65c7eb5f",
    "slug": "portal-heaven-c95448",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-11T06:23:08.605000",
    "updated_at": "2025-12-11T06:23:08.605000"
  },
  {
    "name": "Portal Heaven",
    "description": "Luxury Portal",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "998e66c0-5d1b-4661-8552-3b92af4354ea",
    "developer_id": "57c2ea64-f228-49a1-86fc-ccfb65c7eb5f",
    "slug": "portal-heaven-30d177",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-11T06:24:13.354000",
    "updated_at": "2025-12-11T06:24:13.354000"
  },
  {
    "name": "Portal Heaven",
    "description": "Luxury Portal",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "5cb498a3-1366-4094-aeff-65aff5e2afb5",
    "developer_id": "57c2ea64-f228-49a1-86fc-ccfb65c7eb5f",
    "slug": "portal-heaven-a62ac3",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-11T06:25:24.912000",
    "updated_at": "2025-12-11T06:25:24.912000"
  },
  {
    "name": "Portal Heaven",
    "description": "Luxury Portal",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "cec75ebc-d0a4-42c0-af48-83d2f0137d67",
    "developer_id": "57c2ea64-f228-49a1-86fc-ccfb65c7eb5f",
    "slug": "portal-heaven-120f3e",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-11T06:25:27.661000",
    "updated_at": "2025-12-11T06:25:27.661000"
  },
  {
    "name": "Portal Heaven",
    "description": "Luxury Portal",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "80179e84-2ef3-4c45-bf3b-761c8aa26ae0",
    "developer_id": "57c2ea64-f228-49a1-86fc-ccfb65c7eb5f",
    "slug": "portal-heaven-2311fb",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-11T06:26:18.960000",
    "updated_at": "2025-12-11T06:26:18.960000"
  },
  {
    "name": "Portal Heaven",
    "description": "Luxury Portal",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "88133b47-43ac-465d-b804-b71c0f1b8a16",
    "developer_id": "57c2ea64-f228-49a1-86fc-ccfb65c7eb5f",
    "slug": "portal-heaven-c09106",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-11T06:26:21.776000",
    "updated_at": "2025-12-11T06:26:21.776000"
  },
  {
    "name": "Park View Residency",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "5a5ffc7c-f537-4e39-b0e4-24224852c5c1",
    "developer_id": "fe64600d-cd54-4e3a-b82b-5b803c66696c",
    "slug": "park-view-residency-verified",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-15T05:11:22.151000",
    "updated_at": "2025-12-15T05:11:22.151000"
  },
  {
    "name": "Park View Residency",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": 12.978,
    "longitude": 77.5946,
    "launch_year": null,
    "id": "25a7010b-d348-4e73-8432-e72de8fb869c",
    "developer_id": "fe64600d-cd54-4e3a-b82b-5b803c66696c",
    "slug": "park-view-residency-v2",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-15T05:14:00.854000",
    "updated_at": "2025-12-15T05:14:00.854000"
  },
  {
    "name": "Project 1",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "8b5f7b34-5414-4e75-8af8-bfdc3f9ae8d7",
    "developer_id": "5793f2b4-b254-467c-9b83-3d4fc21a54a5",
    "slug": "proj-419f07",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-17T03:55:09.816000",
    "updated_at": "2025-12-17T03:55:09.816000"
  },
  {
    "name": "Project 1",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "1d3221c1-a41b-452c-a68b-63f393a0c07e",
    "developer_id": "e67a5876-4f97-40ef-ba19-40fba8612f22",
    "slug": "proj-848c09",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-17T03:56:30.520000",
    "updated_at": "2025-12-17T03:56:30.520000"
  },
  {
    "name": "Project 1",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "da5c657f-3582-40b9-b0c0-68bc711afcdb",
    "developer_id": "7156d06a-3839-4ab4-88e8-ecc0b66c1f80",
    "slug": "proj-06a4be",
    "status": "PENDING",
    "is_hidden": true,
    "created_at": "2025-12-17T03:57:01.954000",
    "updated_at": "2025-12-17T03:57:01.954000"
  },
  {
    "name": "Project 1",
    "description": null,
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "a3e44054-a842-4c43-972a-c78996617c16",
    "developer_id": "f44ff5c5-6da5-4929-82fd-b281a1c2389b",
    "slug": "proj-8c5c71",
    "status": "PENDING",
    "is_hidden": true,
    "created_at": "2025-12-17T03:57:27.340000",
    "updated_at": "2025-12-17T03:57:27.340000"
  },
  {
    "name": "Project pegvjr",
    "description": "A great project",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "5d347b0c-8e37-466c-b71f-8911d7ed7445",
    "developer_id": "42e6a5f6-f6cc-433b-a06c-0c39ef4f0378",
    "slug": "project-pegvjr",
    "status": "DELETED",
    "is_hidden": false,
    "created_at": "2025-12-17T09:32:51.611000",
    "updated_at": "2025-12-17T09:32:51.611000"
  },
  {
    "name": "Project eiuiid",
    "description": "A great project",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "ea1a4626-31da-4fff-b34f-accd60387f39",
    "developer_id": "42e6a5f6-f6cc-433b-a06c-0c39ef4f0378",
    "slug": "project-eiuiid",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-17T09:47:27.595000",
    "updated_at": "2025-12-17T09:47:27.595000"
  },
  {
    "name": "Project 63vvtq",
    "description": "A great project",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "65ff51fa-a761-48f1-8f27-bce935e56af6",
    "developer_id": "bc9eb373-bfd6-4271-a548-5920809d7254",
    "slug": "project-63vvtq",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-17T09:49:11.205000",
    "updated_at": "2025-12-17T09:49:11.205000"
  },
  {
    "name": "Project 9xyth1 Updated",
    "description": "Updated desc",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "1495079b-ce4c-4c90-be67-2e4685a200c2",
    "developer_id": "56abf9f0-dfad-43de-9222-edde57b72547",
    "slug": "project-9xyth1",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-17T09:51:10.347000",
    "updated_at": "2025-12-17T09:51:18.750000"
  },
  {
    "name": "Debug Project 3umvzp",
    "description": "Debug",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "cc1abc84-e54a-418d-a0c7-1b73bb5fb95c",
    "developer_id": "4e7ce445-0b0d-484f-a388-8ba45f7972d7",
    "slug": "debug-3umvzp",
    "status": "PENDING",
    "is_hidden": false,
    "created_at": "2025-12-17T09:52:23.513000",
    "updated_at": "2025-12-17T09:52:23.513000"
  },
  {
    "name": "Project yjapg2 Updated",
    "description": "Updated desc",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "fe818a45-2cea-4e66-b3e8-9f8744edaccd",
    "developer_id": "4990804b-e7db-4883-b04f-7cc28e8ea692",
    "slug": "project-yjapg2",
    "status": "APPROVED",
    "is_hidden": false,
    "created_at": "2025-12-17T09:53:54.738000",
    "updated_at": "2025-12-17T09:54:03.055000"
  },
  {
    "name": "Change Req",
    "description": "CR Trigger",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "3dafe44b-ee66-4de7-aed2-3183f36f5ebe",
    "developer_id": "225462ab-80cf-48f0-bd64-bc094add8834",
    "slug": "proj-d6ms4l",
    "status": "APPROVED",
    "is_hidden": true,
    "created_at": "2025-12-17T12:29:14.236000",
    "updated_at": "2025-12-17T12:32:03.153000"
  },
  {
    "name": "Change Req",
    "description": "CR Trigger",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "16fa87c2-8139-444a-9e59-8fc338cf20c4",
    "developer_id": "44a5737d-02e1-4363-83cf-4de61ee872f8",
    "slug": "proj-fmbpsp",
    "status": "APPROVED",
    "is_hidden": true,
    "created_at": "2025-12-17T12:34:16.497000",
    "updated_at": "2025-12-17T12:37:05.133000"
  },
  {
    "name": "Project o7oxe5",
    "description": "Desc",
    "approval_type": null,
    "rera_number": null,
    "address": null,
    "latitude": null,
    "longitude": null,
    "launch_year": null,
    "id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
    "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
    "slug": "proj-o7oxe5",
    "status": "APPROVED",
    "is_hidden": true,
    "created_at": "2025-12-17T12:39:18.795000",
    "updated_at": "2025-12-17T12:39:18.795000"
  }
]
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/projects/' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 43. Reject Project (Admin)
**URL**: `http://localhost:8000/api/v1/admin/projects/55ec5c12-5811-49f0-881d-7186db2a3f13/reject`

**Success Response**
Status: `200`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/admin/projects/55ec5c12-5811-49f0-881d-7186db2a3f13/reject' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
{
  "name": "Project o7oxe5",
  "description": "Desc",
  "approval_type": null,
  "rera_number": null,
  "address": null,
  "latitude": null,
  "longitude": null,
  "launch_year": null,
  "id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
  "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
  "slug": "proj-o7oxe5",
  "status": "REJECTED",
  "is_hidden": true,
  "created_at": "2025-12-17T12:39:18.795000",
  "updated_at": "2025-12-17T12:39:18.795000"
}
```

**Failure Response**
Status: `403`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/admin/projects/55ec5c12-5811-49f0-881d-7186db2a3f13/reject' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 44. Re-Approve Project (Admin)
**URL**: `http://localhost:8000/api/v1/admin/projects/55ec5c12-5811-49f0-881d-7186db2a3f13/approve`

**Success Response**
Status: `200`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/admin/projects/55ec5c12-5811-49f0-881d-7186db2a3f13/approve' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
{
  "name": "Project o7oxe5",
  "description": "Desc",
  "approval_type": null,
  "rera_number": null,
  "address": null,
  "latitude": null,
  "longitude": null,
  "launch_year": null,
  "id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
  "developer_id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
  "slug": "proj-o7oxe5",
  "status": "APPROVED",
  "is_hidden": true,
  "created_at": "2025-12-17T12:39:18.795000",
  "updated_at": "2025-12-17T12:39:18.795000"
}
```

**Failure Response**
Status: `403`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/admin/projects/55ec5c12-5811-49f0-881d-7186db2a3f13/approve' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 45. Update Approved Project (Dev - Trigger CR)
**URL**: `http://localhost:8000/api/v1/developers/projects/55ec5c12-5811-49f0-881d-7186db2a3f13`

**Success Response**
Status: `200`
```bash
curl -X PUT 'http://localhost:8000/api/v1/developers/projects/55ec5c12-5811-49f0-881d-7186db2a3f13' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzUsInN1YiI6ImZhYzljYWM1LWMzNWItNDE0Ni1iYTc4LTJlM2JjMjJkY2E4ZCJ9.jnlHzJDvjVZb4hrO6T21Sfyw3yXAJPCXIatrBFvo4g0' -H 'Content-Type: application/json' -d '{"name": "Change Req", "slug": "proj-o7oxe5", "description": "CR Trigger", "city": "Bangalore"}'
```
```json
{
  "message": "Update request submitted for approval",
  "request_id": "d2c78715-9168-4fb8-8edd-647c244f60bb"
}
```

**Failure Response**
Status: `403`
```bash
curl -X PUT 'http://localhost:8000/api/v1/developers/projects/55ec5c12-5811-49f0-881d-7186db2a3f13' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"name": "Change Req", "slug": "proj-o7oxe5", "description": "CR Trigger", "city": "Bangalore"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 46. Approve Change Request
**URL**: `http://localhost:8000/api/v1/admin/projects/d2c78715-9168-4fb8-8edd-647c244f60bb/approve`

**Success Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/projects/d2c78715-9168-4fb8-8edd-647c244f60bb/approve' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
{
  "id": "d2c78715-9168-4fb8-8edd-647c244f60bb",
  "project_id": "55ec5c12-5811-49f0-881d-7186db2a3f13",
  "request_type": "UPDATE",
  "data": {
    "name": "Change Req",
    "description": "CR Trigger",
    "updated_at": "2025-12-17T12:42:07.748000"
  },
  "status": "APPROVED",
  "admin_notes": null,
  "created_at": "2025-12-17T12:42:03.551000",
  "updated_at": "2025-12-17T12:42:07.779000"
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/projects/d2c78715-9168-4fb8-8edd-647c244f60bb/approve' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 47. Create Developer (Admin)
**URL**: `http://localhost:8000/api/v1/admin/developers/`

**Success Response**
Status: `200`
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/developers/' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE' -H 'Content-Type: application/json' -d '{"name": "Admin Created Dev", "contact_email": "dev2_o7oxe5@ex.com", "contact_phone": "9998887776", "office_address": "Bangalore"}'
```
```json
{
  "name": "Admin Created Dev",
  "legal_name": null,
  "owner_name": null,
  "gst_number": null,
  "rera_number": null,
  "sub_developer": null,
  "office_address": "Bangalore",
  "contact_email": "dev2_o7oxe5@ex.com",
  "contact_phone": "9998887776",
  "logo_url": null,
  "about_text": null,
  "is_verified": false,
  "is_active": true,
  "id": "dcf3096a-015d-4ef0-b1af-f2bb80c7760b",
  "created_at": "2025-12-17T12:42:11.946530",
  "updated_at": "2025-12-17T12:42:11.946533"
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/developers/' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"name": "Admin Created Dev", "contact_email": "dev2_o7oxe5@ex.com", "contact_phone": "9998887776", "office_address": "Bangalore"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 48. List Developers (Admin)
**URL**: `http://localhost:8000/api/v1/admin/developers/`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/developers/' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
[
  {
    "name": "Suspend Test Dev",
    "legal_name": null,
    "owner_name": null,
    "gst_number": null,
    "rera_number": null,
    "sub_developer": null,
    "office_address": null,
    "contact_email": "suspend_test_851e48@example.com",
    "contact_phone": null,
    "logo_url": null,
    "about_text": null,
    "is_verified": false,
    "is_active": true,
    "id": "fe64600d-cd54-4e3a-b82b-5b803c66696c",
    "created_at": "2025-12-09T11:17:47.838000",
    "updated_at": "2025-12-09T11:17:48.073000"
  },
  {
    "name": "Admin Created Dev",
    "legal_name": null,
    "owner_name": null,
    "gst_number": null,
    "rera_number": null,
    "sub_developer": null,
    "office_address": "Bangalore",
    "contact_email": "dev2_o7oxe5@ex.com",
    "contact_phone": "9998887776",
    "logo_url": null,
    "about_text": null,
    "is_verified": false,
    "is_active": true,
    "id": "dcf3096a-015d-4ef0-b1af-f2bb80c7760b",
    "created_at": "2025-12-17T12:42:11.946000",
    "updated_at": "2025-12-17T12:42:11.946000"
  }
]
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/developers/' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 49. Get Developer (Admin)
**URL**: `http://localhost:8000/api/v1/admin/developers/dcf3096a-015d-4ef0-b1af-f2bb80c7760b`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/developers/dcf3096a-015d-4ef0-b1af-f2bb80c7760b' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
{
  "name": "Admin Created Dev",
  "legal_name": null,
  "owner_name": null,
  "gst_number": null,
  "rera_number": null,
  "sub_developer": null,
  "office_address": "Bangalore",
  "contact_email": "dev2_o7oxe5@ex.com",
  "contact_phone": "9998887776",
  "logo_url": null,
  "about_text": null,
  "is_verified": false,
  "is_active": true,
  "id": "dcf3096a-015d-4ef0-b1af-f2bb80c7760b",
  "created_at": "2025-12-17T12:42:11.946000",
  "updated_at": "2025-12-17T12:42:11.946000"
}
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/developers/dcf3096a-015d-4ef0-b1af-f2bb80c7760b' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 50. Update Developer (Admin)
**URL**: `http://localhost:8000/api/v1/admin/developers/dcf3096a-015d-4ef0-b1af-f2bb80c7760b`

**Success Response**
Status: `200`
```bash
curl -X PUT 'http://localhost:8000/api/v1/admin/developers/dcf3096a-015d-4ef0-b1af-f2bb80c7760b' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE' -H 'Content-Type: application/json' -d '{"name": "Updated Dev Name"}'
```
```json
{
  "name": "Updated Dev Name",
  "legal_name": null,
  "owner_name": null,
  "gst_number": null,
  "rera_number": null,
  "sub_developer": null,
  "office_address": "Bangalore",
  "contact_email": "dev2_o7oxe5@ex.com",
  "contact_phone": "9998887776",
  "logo_url": null,
  "about_text": null,
  "is_verified": false,
  "is_active": true,
  "id": "dcf3096a-015d-4ef0-b1af-f2bb80c7760b",
  "created_at": "2025-12-17T12:42:11.946000",
  "updated_at": "2025-12-17T12:42:24.498000"
}
```

**Failure Response**
Status: `403`
```bash
curl -X PUT 'http://localhost:8000/api/v1/admin/developers/dcf3096a-015d-4ef0-b1af-f2bb80c7760b' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"name": "Updated Dev Name"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 51. Delete Developer (Admin)
**URL**: `http://localhost:8000/api/v1/admin/developers/dcf3096a-015d-4ef0-b1af-f2bb80c7760b`

**Success Response**
Status: `200`
```bash
curl -X DELETE 'http://localhost:8000/api/v1/admin/developers/dcf3096a-015d-4ef0-b1af-f2bb80c7760b' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
{
  "name": "Updated Dev Name",
  "legal_name": null,
  "owner_name": null,
  "gst_number": null,
  "rera_number": null,
  "sub_developer": null,
  "office_address": "Bangalore",
  "contact_email": "dev2_o7oxe5@ex.com",
  "contact_phone": "9998887776",
  "logo_url": null,
  "about_text": null,
  "is_verified": false,
  "is_active": true,
  "id": "dcf3096a-015d-4ef0-b1af-f2bb80c7760b",
  "created_at": "2025-12-17T12:42:11.946000",
  "updated_at": "2025-12-17T12:42:24.498000"
}
```

**Failure Response**
Status: `403`
```bash
curl -X DELETE 'http://localhost:8000/api/v1/admin/developers/dcf3096a-015d-4ef0-b1af-f2bb80c7760b' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 52. Create User (Admin)
**URL**: `http://localhost:8000/api/v1/admin/users/`

**Success Response**
Status: `422`
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/users/' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE' -H 'Content-Type: application/json' -d '{"email": "u2_o7oxe5@ex.com", "password": "Pass", "full_name": "Admin User", "role": "BUYER"}'
```
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": [
        "body",
        "password"
      ],
      "msg": "Value error, Password must be at least 8 characters long",
      "input": "Pass",
      "ctx": {
        "error": {}
      }
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X POST 'http://localhost:8000/api/v1/admin/users/' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"email": "u2_o7oxe5@ex.com", "password": "Pass", "full_name": "Admin User", "role": "BUYER"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 53. List Users (Admin)
**URL**: `http://localhost:8000/api/v1/admin/users/`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/users/' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
[
  {
    "id": "a49ab8aa-2073-42e7-bab2-c62a6551f9ec",
    "email": "admin@realstart.com",
    "full_name": "Super Admin",
    "role": "SUPER_ADMIN",
    "is_active": true
  },
  {
    "id": "23717ce0-73bb-4304-8749-1fe8972c8538",
    "email": "dev_c4b43d0d@example.com",
    "full_name": "Test Developer",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "e755f738-fd39-483e-918f-a2929fba35c8",
    "email": "dev_0472c761@example.com",
    "full_name": "Test Developer",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "dcf6647a-2bff-4cd7-83fb-3e78212c6a70",
    "email": "dev_3d51002d@example.com",
    "full_name": "Test Developer",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "feca27eb-3ef1-4bad-84d4-f589555d744b",
    "email": "dev_0a5e6fe8@example.com",
    "full_name": "Test Developer",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "fdcb66e3-20ee-4e5c-8590-ec82d5a513e4",
    "email": "buyer_365fab@example.com",
    "full_name": "Interested Buyer",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "5723416e-38e6-4426-807c-87fc7be42c89",
    "email": "devlead_d0644f@example.com",
    "full_name": "Lead Developer",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "fdf9a3da-ba78-45f9-85c6-78de942c45cc",
    "email": "buyer_b3925a@example.com",
    "full_name": "Interested Buyer",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "f34c1588-c624-4049-8e58-777c6769dd50",
    "email": "devlead_749f01@example.com",
    "full_name": "Lead Developer",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "92553388-9497-4f01-a2f5-1c1ba2b7ff5b",
    "email": "buyer_0d4a89@example.com",
    "full_name": "Interested Buyer",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "ba47ee8d-e567-42ee-90c3-2180646f1117",
    "email": "devlead_f50e59@example.com",
    "full_name": "Lead Developer",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "d8d24f7f-4833-4ca6-894e-511fee153d90",
    "email": "buyer_5b24c8@example.com",
    "full_name": "Interested Buyer",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "1e808355-1dda-43ae-a6d7-3de83e3d4a34",
    "email": "devlead_3908fd@example.com",
    "full_name": "Lead Developer",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "2346edbd-f536-425d-803f-d484217b80b8",
    "email": "buyer_a7a1a5@example.com",
    "full_name": "Interested Buyer",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "46cf8fc8-8b1e-4cbc-bf23-f5bc64f3aa9a",
    "email": "devlead_ff5617@example.com",
    "full_name": "Lead Developer",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "859e7836-f5a5-40ce-b710-ba8715553c5c",
    "email": "buyer_881eb9@example.com",
    "full_name": "Interested Buyer",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "44d638e1-b0b2-4458-a4b8-2e48544c1b75",
    "email": "devlead_9e7e94@example.com",
    "full_name": "Lead Developer",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "239fc1a1-e32b-4818-87f9-3ef34a9e9eb6",
    "email": "user@example.com",
    "full_name": "string",
    "role": "SUPER_ADMIN",
    "is_active": true
  },
  {
    "id": "2a3a2d83-0f53-44a3-abfe-ba5a270bcfd5",
    "email": "user@example2.com",
    "full_name": "string2",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "1fc11785-6e41-4bb5-8fa7-639bfaaebb91",
    "email": "dev_hook_643c0f@example.com",
    "full_name": "Hook Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "b9863195-ca88-457b-8359-0a95d3c06179",
    "email": "buyer_dff115@example.com",
    "full_name": "Buyer",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "aaea06b8-b00f-46e7-8c9b-f1980d598c13",
    "email": "dev_hook_c1f8d6@example.com",
    "full_name": "Hook Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "405ad7ef-e930-42e3-96d4-2fc55002408b",
    "email": "buyer_8abc45@example.com",
    "full_name": "Buyer",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "f0827785-9c18-4ac9-9c4e-8d3075cc8a51",
    "email": "filter_dev_141eb2@example.com",
    "full_name": "Filter Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "19b546fd-ad5a-4bad-b7ef-65d158f3a519",
    "email": "admin_portal@example.com",
    "full_name": "Admin User",
    "role": "ADMIN",
    "is_active": true
  },
  {
    "id": "57c2ea64-f228-49a1-86fc-ccfb65c7eb5f",
    "email": "dev_portal@example.com",
    "full_name": "Dev User",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "51b22157-683f-4baa-91de-452edb5b4631",
    "email": "buyer_portal@example.com",
    "full_name": "Portal Buyer Pro",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "2d8d4cd3-00cb-404c-a58e-983f4909d111",
    "email": "admin@realtech.in",
    "full_name": "Admin User",
    "role": "SUPER_ADMIN",
    "is_active": true
  },
  {
    "id": "9778a485-2194-490b-82ee-c6bcb84ed90a",
    "email": "user@exampl43e.com",
    "full_name": "string",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "62e54f1a-e6a9-42df-a7df-b03a5178c2dc",
    "email": "user@examp43le.com",
    "full_name": "string",
    "role": "SUPER_ADMIN",
    "is_active": true
  },
  {
    "id": "37098c83-83f9-49d3-bb71-29c52d1dcee4",
    "email": "pavan@example.com",
    "full_name": "Pavan",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "22349a6f-1b6b-4620-b074-82d40f5a495b",
    "email": "pavan1@example.com",
    "full_name": "Pavan",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "518bd40c-73bc-4221-a7e8-1ba2c7ece43f",
    "email": "dev_26f6b4@example.com",
    "full_name": "Test Dev",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "0f82dda4-0c92-4160-8e2e-3c7ce1566e32",
    "email": "dev_1219bf@example.com",
    "full_name": "Test Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "3334345b-e534-40e1-b7bb-1d52f3756ec4",
    "email": "dev_633439@example.com",
    "full_name": "Test Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "bf2d9c84-9ce7-41f5-ba67-f29d1d223e90",
    "email": "dev_dee307@example.com",
    "full_name": "Test Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "4f7cd3b7-e58b-41e4-bb6d-74bdacb1a99b",
    "email": "dev_213941@example.com",
    "full_name": "Test Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "7156d06a-3839-4ab4-88e8-ecc0b66c1f80",
    "email": "dev_767715@example.com",
    "full_name": "Test Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "f44ff5c5-6da5-4929-82fd-b281a1c2389b",
    "email": "dev_6497c5@example.com",
    "full_name": "Test Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "c7c32934-4ebb-47ee-96c9-d3a9cbc4155c",
    "email": "superadmin@realstart.com",
    "full_name": "Super Admin",
    "role": "SUPER_ADMIN",
    "is_active": true
  },
  {
    "id": "42e6a5f6-f6cc-433b-a06c-0c39ef4f0378",
    "email": "dev@realstart.com",
    "full_name": "Developer User",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "92c5972f-f9eb-40a6-9200-7bc02b94aca8",
    "email": "user@realstart.com",
    "full_name": "Updated Name",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "fd51e7ed-c561-49ad-9778-1d0cbf66ce84",
    "email": "user_7074@example.com",
    "full_name": "Test User",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "72c8dd92-b3e0-4140-b6c5-12e2b94b10c1",
    "email": "newuser_b0wejg@example.com",
    "full_name": "New User",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "c07fd961-303d-42f2-a9f8-bc4dd3b4149c",
    "email": "newuser_pegvjr@example.com",
    "full_name": "New User",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "8f959715-7c8c-46f8-8700-7a36b072cffa",
    "email": "newuser_gkbciu@example.com",
    "full_name": "New User",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "992cbda6-a1fc-4a85-93ac-d078fc476be1",
    "email": "newadmin_gkbciu@realstart.com",
    "full_name": "New Admin",
    "role": "ADMIN",
    "is_active": true
  },
  {
    "id": "ab0db9f4-160c-4830-a4f9-0a13c25fbe7a",
    "email": "newuser_otjwf6@example.com",
    "full_name": "New User",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "e3e640af-d32e-4ed9-b303-2a27ae66b0d3",
    "email": "newadmin_otjwf6@realstart.com",
    "full_name": "New Admin",
    "role": "ADMIN",
    "is_active": true
  },
  {
    "id": "b1ca05ff-1369-48f6-af13-f3661fedc010",
    "email": "newuser_eiuiid@example.com",
    "full_name": "New User",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "7d32d22f-5c06-46ef-943b-3872a3a1c08d",
    "email": "newadmin_eiuiid@realstart.com",
    "full_name": "New Admin",
    "role": "ADMIN",
    "is_active": true
  },
  {
    "id": "bc9eb373-bfd6-4271-a548-5920809d7254",
    "email": "dev_63vvtq@realstart.com",
    "full_name": "Fresh Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "654bfe3e-bea1-4f60-b76b-c579df7ef2cb",
    "email": "newuser_63vvtq@example.com",
    "full_name": "New User",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "1e0c0e10-45c1-498f-8c7a-ac6a05185a4d",
    "email": "newadmin_63vvtq@realstart.com",
    "full_name": "New Admin",
    "role": "ADMIN",
    "is_active": true
  },
  {
    "id": "56abf9f0-dfad-43de-9222-edde57b72547",
    "email": "dev_9xyth1@realstart.com",
    "full_name": "Fresh Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "ab400cc3-1b51-4309-8e28-e4c84cb7ded8",
    "email": "newuser_9xyth1@example.com",
    "full_name": "New User",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "b5cf1a72-8ee8-46a3-ad26-41b34c99521c",
    "email": "newadmin_9xyth1@realstart.com",
    "full_name": "New Admin",
    "role": "ADMIN",
    "is_active": true
  },
  {
    "id": "4e7ce445-0b0d-484f-a388-8ba45f7972d7",
    "email": "dev_3umvzp@debug.com",
    "full_name": "Debug Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "4990804b-e7db-4883-b04f-7cc28e8ea692",
    "email": "dev_yjapg2@realstart.com",
    "full_name": "Fresh Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "57454b2d-dee3-497b-8fef-37ab0f1163a5",
    "email": "newuser_yjapg2@example.com",
    "full_name": "New User",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "52544ad1-3d4b-4c4f-bcee-68c7e5a04c12",
    "email": "newadmin_yjapg2@realstart.com",
    "full_name": "New Admin",
    "role": "ADMIN",
    "is_active": true
  },
  {
    "id": "225462ab-80cf-48f0-bd64-bc094add8834",
    "email": "dev_d6ms4l@realstart.com",
    "full_name": "Fresh Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "64ea59e2-d894-4779-9376-869e74d8e247",
    "email": "buyer_d6ms4l@example.com",
    "full_name": "Fresh Buyer",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "55cf6234-5e91-47be-b949-c534ad9b0a1c",
    "email": "b2_d6ms4l@ex.com",
    "full_name": "Test",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "bdedbf50-fc5c-48da-b51f-47643cf78d03",
    "email": "adm2_d6ms4l@ex.com",
    "full_name": "Test Admin",
    "role": "ADMIN",
    "is_active": true
  },
  {
    "id": "44a5737d-02e1-4363-83cf-4de61ee872f8",
    "email": "dev_fmbpsp@realstart.com",
    "full_name": "Fresh Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "48e741a6-0458-40ea-9302-d4743c4e6329",
    "email": "buyer_fmbpsp@example.com",
    "full_name": "Fresh Buyer",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "2d64eaaa-63b7-4319-bf9b-a761b9617166",
    "email": "b2_fmbpsp@ex.com",
    "full_name": "Test",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "c2357c46-5fa0-4656-94c9-258df6f89b5c",
    "email": "adm2_fmbpsp@ex.com",
    "full_name": "Test Admin",
    "role": "ADMIN",
    "is_active": true
  },
  {
    "id": "fac9cac5-c35b-4146-ba78-2e3bc22dca8d",
    "email": "dev_o7oxe5@realstart.com",
    "full_name": "Fresh Dev",
    "role": "DEVELOPER",
    "is_active": true
  },
  {
    "id": "de814814-727d-482c-998d-de82f825c229",
    "email": "buyer_o7oxe5@example.com",
    "full_name": "Fresh Buyer",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "64eb85b4-b925-4a6c-aaaa-4f30ac634e49",
    "email": "b2_o7oxe5@ex.com",
    "full_name": "Test",
    "role": "BUYER",
    "is_active": true
  },
  {
    "id": "585ac933-f0a8-4f34-bcba-f5ee31a251e8",
    "email": "adm2_o7oxe5@ex.com",
    "full_name": "Test Admin",
    "role": "ADMIN",
    "is_active": true
  }
]
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/users/' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 54. Get User (Admin)
**URL**: `http://localhost:8000/api/v1/admin/users/{user_id}`

**Success Response**
Status: `422`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/users/{user_id}' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": [
        "path",
        "user_id"
      ],
      "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `u` at 2",
      "input": "{user_id}",
      "ctx": {
        "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `u` at 2"
      }
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/admin/users/{user_id}' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 55. Update User (Admin)
**URL**: `http://localhost:8000/api/v1/admin/users/{user_id}`

**Success Response**
Status: `422`
```bash
curl -X PUT 'http://localhost:8000/api/v1/admin/users/{user_id}' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE' -H 'Content-Type: application/json' -d '{"full_name": "Updated User"}'
```
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": [
        "path",
        "user_id"
      ],
      "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `u` at 2",
      "input": "{user_id}",
      "ctx": {
        "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `u` at 2"
      }
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X PUT 'http://localhost:8000/api/v1/admin/users/{user_id}' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"full_name": "Updated User"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 56. Suspend User (Admin)
**URL**: `http://localhost:8000/api/v1/admin/users/{user_id}/suspend`

**Success Response**
Status: `422`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/admin/users/{user_id}/suspend' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": [
        "path",
        "user_id"
      ],
      "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `u` at 2",
      "input": "{user_id}",
      "ctx": {
        "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `u` at 2"
      }
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/admin/users/{user_id}/suspend' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 57. Activate User (Admin)
**URL**: `http://localhost:8000/api/v1/admin/users/{user_id}/activate`

**Success Response**
Status: `422`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/admin/users/{user_id}/activate' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": [
        "path",
        "user_id"
      ],
      "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `u` at 2",
      "input": "{user_id}",
      "ctx": {
        "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `u` at 2"
      }
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/admin/users/{user_id}/activate' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 58. Delete User (Admin)
**URL**: `http://localhost:8000/api/v1/admin/users/{user_id}`

**Success Response**
Status: `422`
```bash
curl -X DELETE 'http://localhost:8000/api/v1/admin/users/{user_id}' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzAsInN1YiI6ImM3YzMyOTM0LTRlYmItNDdlZS05NmM5LWQzYTljYmM0MTU1YyJ9.TxPZwdjD2_GwgMfm2N6uu_Dqo2wJFYitnB06N7qXcOE'
```
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": [
        "path",
        "user_id"
      ],
      "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `u` at 2",
      "input": "{user_id}",
      "ctx": {
        "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `u` at 2"
      }
    }
  ]
}
```

**Failure Response**
Status: `403`
```bash
curl -X DELETE 'http://localhost:8000/api/v1/admin/users/{user_id}' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 59. Change Password
**URL**: `http://localhost:8000/api/v1/settings/change-password`

**Success Response**
Status: `200`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/settings/change-password' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w' -H 'Content-Type: application/json' -d '{"old_password": "StrongUserPass123!", "new_password": "NewStrongPass1!"}'
```
```json
{
  "id": "de814814-727d-482c-998d-de82f825c229",
  "email": "buyer_o7oxe5@example.com",
  "full_name": "Fresh Buyer",
  "role": "BUYER",
  "is_active": true
}
```

**Failure Response**
Status: `403`
```bash
curl -X PATCH 'http://localhost:8000/api/v1/settings/change-password' -H 'Authorization: Bearer invalid' -H 'Content-Type: application/json' -d '{"old_password": "StrongUserPass123!", "new_password": "NewStrongPass1!"}'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 60. Get My Profile (Settings)
**URL**: `http://localhost:8000/api/v1/settings/profile`

**Success Response**
Status: `200`
```bash
curl -X GET 'http://localhost:8000/api/v1/settings/profile' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc3NzUxMzksInN1YiI6ImRlODE0ODE0LTcyN2QtNDgyYy05OThkLWRlODJmODI1YzIyOSJ9.2Bg7IWV0ZDaSj1-6g86bTWBBpDCHFADKFnd53DuaE8w'
```
```json
{
  "id": "de814814-727d-482c-998d-de82f825c229",
  "email": "buyer_o7oxe5@example.com",
  "full_name": "Fresh Buyer",
  "role": "BUYER",
  "is_active": true
}
```

**Failure Response**
Status: `403`
```bash
curl -X GET 'http://localhost:8000/api/v1/settings/profile' -H 'Authorization: Bearer invalid'
```
```json
{
  "detail": "Could not validate credentials"
}
```

---

