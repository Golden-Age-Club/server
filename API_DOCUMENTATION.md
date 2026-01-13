# Golden Age API Documentation

This document describes all the endpoints available in the Golden Age USDT Wallet API.

## 🔑 Authentication

The API uses JWT (JSON Web Token) for authentication. Most endpoints require the `Authorization: Bearer <token>` header.

### 1. Telegram Login
*   **Endpoint:** `POST /api/auth/login/telegram`
*   **Description:** Authenticates a user via Telegram WebApp data.
*   **Body:**
    ```json
    {
        "init_data": "QUERY_STRING_FROM_TELEGRAM"
    }
    ```
*   **Response:** Returns JWT `access_token` and `user` profile.

### 2. Email Registration
*   **Endpoint:** `POST /api/auth/register/email`
*   **Description:** Creates a new account using email and password.
*   **Body:**
    ```json
    {
        "email": "user@example.com",
        "password": "strongpassword",
        "first_name": "John",
        "last_name": "Doe"
    }
    ```

### 3. Email Login
*   **Endpoint:** `POST /api/auth/login/email`
*   **Description:** Authenticates using email credentials.
*   **Body:**
    ```json
    {
        "email": "user@example.com",
        "password": "strongpassword"
    }
    ```

### 4. Get Profile
*   **Endpoint:** `GET /api/auth/me`
*   **Auth Required:** Yes
*   **Description:** Returns the current user's full profile.

---

## 💰 Wallet Operations

All financial operations use USDT (Tether).

### 1. Create Deposit
*   **Endpoint:** `POST /api/wallet/deposit`
*   **Auth Required:** Yes
*   **Body:**
    ```json
    {
        "amount": 50.0,
        "currency": "USDT",
        "return_url": "https://yourfrontend.com/success"
    }
    ```
*   **Response:** Includes `payment_url` and `payment_address`.

### 2. Create Withdrawal
*   **Endpoint:** `POST /api/wallet/withdraw`
*   **Auth Required:** Yes
*   **Body:**
    ```json
    {
        "amount": 25.0,
        "wallet_address": "TRC20_WALLET_ADDRESS",
        "currency": "USDT"
    }
    ```

### 3. Get Balance
*   **Endpoint:** `GET /api/wallet/balance`
*   **Auth Required:** Yes
*   **Response:** `{"user_id": "...", "balance": 150.0}`

### 4. Transaction History
*   **Endpoint:** `GET /api/wallet/transactions`
*   **Auth Required:** Yes
*   **Response:** List of transaction objects.

### 5. Transaction Status
*   **Endpoint:** `GET /api/wallet/transaction/{id}`
*   **Auth Required:** Yes

---

## ⚓ Webhooks (CCPayment)

*   **Endpoint:** `POST /api/webhook/ccpayment`
*   **Description:** Receives payment status updates from CCPayment.
*   **Security:** Requires `timestamp` and `sign` headers for signature verification.

---

## 🛡️ Admin Panel

*   **URL:** `http://<domain>:8002/admin/`
*   **Custom Views:**
    - Dashboard: `/panel/dashboard/`
    - Player Management: `/panel/users/`
    - Transaction History: `/panel/transactions/`
    - Financial Reports: `/panel/reports/`

---

## 🏥 System Health
*   **Root:** `GET /` (Version & Metadata)
*   **Health:** `GET /health` (DB & Provider Status)
