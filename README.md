# Order Management Backend

A REST API backend for a food delivery application's Order Management feature, built with Django and Django REST Framework.

The project provides APIs for:

- Food/menu item retrieval
- Order placement
- Order CRUD operations
- Order item and quantity management
- Delivery/customer details
- Automatic order total calculation
- Order status updates
- Search, filtering, ordering, and pagination
- API validation
- Automated API tests

## Project Requirements

The backend is designed according to the Full Stack Developer assessment requirements:

- REST API for menu retrieval, order placement, and order status updates
- Database storage for menu items and orders
- Input validation and edge-case handling
- Tests covering CRUD operations, validation, and status updates
- React/Vite or Next.js can be used as the frontend
- Order status progression can be simulated through the backend

## Tech Stack

- Python
- Django
- Django REST Framework
- Django Filter
- django-cors-headers
- Pillow
- SQLite (development)
- Postman (API testing)

## Project Structure

```text
food_delivery_backend/
│
├── manage.py
├── requirements.txt
├── db.sqlite3
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── orders/
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    └── migrations/
```

## Data Models

### FoodItem

| Field | Description |
|---|---|
| `id` | Unique food item ID |
| `name` | Food name |
| `description` | Food description |
| `price` | Current food price |
| `image` | Food image |
| `is_available` | Whether the item can be ordered |
| `created_at` | Creation timestamp |
| `updated_at` | Last update timestamp |

### Order

| Field | Description |
|---|---|
| `id` | Unique order ID |
| `customer_name` | Customer name |
| `address` | Delivery address |
| `phone` | Customer phone number |
| `status` | Current order status |
| `total_amount` | Calculated order total |
| `created_at` | Creation timestamp |
| `updated_at` | Last update timestamp |

### OrderItem

| Field | Description |
|---|---|
| `id` | Unique order item ID |
| `order` | Related order |
| `food_item` | Ordered food item |
| `quantity` | Ordered quantity |
| `price` | Price captured when ordered |
| `subtotal` | Price × quantity |

The order item stores the price at the time of purchase so that later menu-price changes do not alter historical orders.

## Order Statuses

```text
ORDER_RECEIVED
PREPARING
OUT_FOR_DELIVERY
DELIVERED
CANCELLED
```

Example status flow:

```text
ORDER_RECEIVED
       ↓
PREPARING
       ↓
OUT_FOR_DELIVERY
       ↓
DELIVERED
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Vismayak2000/Order-Management-Backend.git
cd Order-Management-Backend
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create an admin user

```bash
python manage.py createsuperuser
```

### 6. Start the server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## Admin Panel

Open:

```text
http://127.0.0.1:8000/admin/
```

Use the superuser credentials created with:

```bash
python manage.py createsuperuser
```

Create food items from the admin panel before testing order creation.

## API Endpoints

Base URL:

```text
http://127.0.0.1:8000/api
```

### Menu

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/menu/` | List available food items |
| GET | `/api/menu/{id}/` | Retrieve a food item |

### Orders

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/orders/` | List orders |
| POST | `/api/orders/` | Create an order |
| GET | `/api/orders/{id}/` | Retrieve an order |
| PUT | `/api/orders/{id}/` | Update an order |
| PATCH | `/api/orders/{id}/` | Partially update an order |
| DELETE | `/api/orders/{id}/` | Delete an order |
| PATCH | `/api/orders/{id}/status/` | Update order status |

## Create an Order

### Request

```http
POST /api/orders/
Content-Type: application/json
```

```json
{
    "customer_name": "John",
    "address": "12 Main Street, Kochi",
    "phone": "9876543210",
    "items": [
        {
            "food_item": 1,
            "quantity": 2
        },
        {
            "food_item": 2,
            "quantity": 1
        }
    ]
}
```

The frontend does not send the price or total amount.

The backend retrieves the current food price from the database and calculates:

```text
subtotal = price × quantity

total_amount = sum of all subtotals
```

### Example Response

```json
{
    "id": 1,
    "customer_name": "John",
    "address": "12 Main Street, Kochi",
    "phone": "9876543210",
    "status": "ORDER_RECEIVED",
    "total_amount": "500.00",
    "items": [
        {
            "id": 1,
            "food_item": 1,
            "name": "Pizza",
            "quantity": 2,
            "price": "200.00",
            "subtotal": "400.00"
        },
        {
            "id": 2,
            "food_item": 2,
            "name": "Burger",
            "quantity": 1,
            "price": "100.00",
            "subtotal": "100.00"
        }
    ]
}
```

## Update Order Status

```http
PATCH /api/orders/1/status/
Content-Type: application/json
```

```json
{
    "status": "PREPARING"
}
```

Then:

```json
{
    "status": "OUT_FOR_DELIVERY"
}
```

Then:

```json
{
    "status": "DELIVERED"
}
```

Invalid statuses are rejected by the API.

## Search, Filtering and Ordering

### Search menu

```text
GET /api/menu/?search=pizza
```

### Search orders

```text
GET /api/orders/?search=John
```

### Filter orders by status

```text
GET /api/orders/?status=PREPARING
```

### Order menu by price

```text
GET /api/menu/?ordering=price
```

Descending price:

```text
GET /api/menu/?ordering=-price
```

### Order by total amount

```text
GET /api/orders/?ordering=-total_amount
```

### Pagination

The API uses DRF page-number pagination.

Example:

```text
GET /api/menu/?page=2
```

## Validation

The backend validates:

- Customer name cannot be empty.
- Address cannot be empty.
- Phone number must contain valid digits.
- Phone number length must be between 10 and 15 characters.
- At least one order item is required.
- Quantity must be greater than zero.
- Food item must exist.
- Unavailable food items cannot be ordered.
- Duplicate food items are rejected.
- Invalid order statuses are rejected.
- Order totals are calculated by the backend.

## Testing

Run the complete test suite:

```bash
python manage.py test
```

The test suite covers:

- Menu listing
- Menu item retrieval
- Order creation
- Order listing
- Order retrieval
- Order update
- Order deletion
- Empty order validation
- Invalid quantity
- Invalid phone number
- Unavailable food items
- Order status updates
- Invalid order status

## Postman

A ready-to-import Postman collection is included with this project:

```text
postman/Order_Management_API.postman_collection.json
```

Import the collection into Postman and set:

```text
base_url = http://127.0.0.1:8000
```

The collection contains requests for:

- Menu APIs
- Order CRUD
- Order status updates
- Search
- Filtering
- Ordering
- Validation scenarios

## CORS

The backend is configured to allow the Vite development server:

```text
http://localhost:5173
```

This allows the React/Vite frontend to communicate with the Django REST API during development.

## Development Notes

SQLite is used for local development.

For production deployment, a production database such as PostgreSQL should be configured, along with production environment variables, secure CORS/host settings, static/media handling, and a production WSGI/ASGI server.

## Assessment Deliverables

The assessment requires:

1. Public GitHub repository
2. Hosted application
3. Loom walkthrough video

The backend provides the REST API required for the order-management feature and can be connected to a React/Vite or Next.js frontend.

## Future Improvements

Potential extensions include:

- User authentication
- Customer-specific order history
- Role-based access for restaurant/admin users
- WebSocket-based real-time order tracking
- PostgreSQL for production
- API documentation with Swagger/OpenAPI
- Docker support
- CI/CD pipeline
- Production deployment
