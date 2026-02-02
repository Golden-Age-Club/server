# Golden Age CRM Backend

This is the Node.js/Express backend for the Golden Age CRM and Casino platform.

## Prerequisites

- Node.js (v20.x recommended)
- MongoDB
- npm

## Installation

1.  Navigate to the server directory:
    ```bash
    cd server
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```

## Configuration

Create a `.env` file in the `server` directory with the following variables:

```env
PORT=8000
MONGODB_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/<dbname>
JWT_SECRET_KEY=your_super_secret_jwt_key
ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend-domain.com

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Payment Providers
CCPAYMENT_APP_ID=your_ccpayment_app_id
CCPAYMENT_APP_SECRET=your_ccpayment_app_secret
CCPAYMENT_API_URL=https://admin.ccpayment.com

# Webhooks
WEBHOOK_URL=https://your-backend-domain.com/api/webhook/unified

# Testing
TESTING_MODE=false # Set to true to bypass Telegram signature validation
```

## Running the Server

-   **Development (with nodemon):**
    ```bash
    npm run dev
    ```
-   **Production:**
    ```bash
    npm start
    ```

## API Documentation

### Authentication

**IMPORTANT: There is NO generic `/api/auth/login` endpoint.** You must use the specific endpoint for the login method.

#### 1. Telegram WebApp Login
*   **Endpoint:** `POST /api/auth/login/telegram`
*   **Description:** Authenticates a user using the Telegram WebApp `initData`.
*   **Payload:**
    ```json
    {
      "init_data": "query_id=AAH..." // Raw initData string from Telegram WebApp
    }
    ```
*   **Response:**
    ```json
    {
      "access_token": "eyJ...",
      "token_type": "bearer",
      "user": { ... }
    }
    ```

#### 2. Email Login
*   **Endpoint:** `POST /api/auth/login/email`
*   **Description:** Authenticates a user with email and password.
*   **Payload:**
    ```json
    {
      "email": "user@example.com",
      "password": "secret_password"
    }
    ```

#### 3. Register (Email)
*   **Endpoint:** `POST /api/auth/register/email`
*   **Payload:**
    ```json
    {
      "email": "user@example.com",
      "username": "newuser",
      "password": "secret_password",
      "first_name": "John",
      "last_name": "Doe"
    }
    ```

### User

*   **Get Current User:** `GET /api/users/me` (Requires Bearer Token)

### Wallet

*   **Deposit:** `POST /api/wallet/deposit`
    *   Payload: `{ "amount": 100, "currency": "USDT", "return_url": "..." }`
*   **Withdraw:** `POST /api/wallet/withdraw`
    *   Payload: `{ "amount": 50, "currency": "USDT", "wallet_address": "..." }`

### Casino (PG Soft)

*   **Get Games:** `GET /api/casino/pg/games`
    *   Query Params: `page`, `limit`, `search`
*   **Play Game:** `POST /api/casino/pg/play`
    *   Payload: `{ "game_id": "123", "exit_url": "..." }`
