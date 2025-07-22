# E-Commerce API

A complete e-commerce backend system built with FastAPI featuring session-based authentication, role-based access control, and full product/cart/order management.


## Features

### Core Functionality
- **Session-based authentication** 
- **Role-based access control** (Admin/User)
- **Password reset** via email
- **Product management** (CRUD operations)
- **Shopping cart system**
- **Order processing**

### API Endpoints
| Category        | Endpoints                                                                 |
|-----------------|--------------------------------------------------------------------------|
| Authentication  | `POST /auth/signup`, `POST /auth/signin`, `POST /auth/signout`          |
| Password Reset  | `POST /auth/forgot-password`, `POST /auth/reset-password`               |
| Admin Products  | `POST/GET/PUT/DELETE /admin/products`                                   |
| Public Products | `GET /products`, `GET /products/search`, `GET /products/{id}`           |
| Shopping Cart   | `POST/GET/PUT/DELETE /cart`                                             |
| Orders          | `POST /checkout`, `GET /orders`, `GET /orders/{id}`                     |

## Tech Stack

### Backend
- **Python 3.9+**
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Uvicorn** - ASGI server

### Database
- **SQLite** (Development)
- **PostgreSQL** (Production-ready)

### Security
- **Bcrypt** - Password hashing
- **Session tokens** - Database-backed authentication

