# Online Shop Bot Readme

Welcome to the Online Shop Bot repository! This bot provides an interactive interface for users to browse products, add them to their cart, and complete orders through a secure payment system. Below, you'll find an overview of the main features and functionalities of the bot, along with information on how to set it up and use it.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Contributing](#contributing)
- [Contact](#contact)

## Overview

The Online Shop Bot is built using the [Aiogram](https://docs.aiogram.dev/) library, which is an asynchronous framework for building Telegram bots using Python. It allows users to perform actions like registering an account, browsing the catalog, adding products to the cart, and completing orders with secure payment integration.

## Features

- User registration: Users can register by providing their name, telephone number, and delivery address.
- Catalog browsing: Users can view the list of available products in the catalog.
- Product details: Users can see detailed information about each product, including its name, description, and price.
- Cart management: Users can add products to their cart, view the cart contents, and proceed to checkout.
- Order processing: Users can confirm and complete their orders, receiving a summary of their purchase.
- Secure payment: The bot supports payments through a secure payment provider (e.g., ЮKassa).
- Order history: Users can view their past orders.

## Getting Started

To set up the Online Shop Bot on your system, follow these steps:

1. **Clone the repository:**

2. **Install dependencies:**

3. **Configure your bot:**
Rename the `config_example.py` file to `config.py` and fill in your Telegram bot token and other configuration details.

4. **Set up the database:**
Create an SQLite database (e.g., `online_shop.db`) to store user data and product information. You can find the database schema in the `database_schema.sql` file.

5. **Run the bot:**

## Usage

Once the bot is up and running, users can interact with it by sending commands in a Telegram chat. Here are some of the commands and their functionalities:

- `/start`: Start the bot and display the main menu.
- `/help`: Show a help message with command explanations.
- `/Доставка`: Get information about delivery options.
- `/Каталог`: Browse the catalog of available products.
- `/Регистрация`: Register a new user account.
- `/Оплата`: Learn about payment options.
- `/Корзина`: View and manage the items in your cart.
- `/Мои заказы`: View your order history.

The bot will guide users through the registration process, catalog browsing, product selection, cart management, and order confirmation. Users can complete their orders securely by following the payment process.

## Contributing

Contributions to the Online Shop Bot are welcome! If you'd like to contribute new features, bug fixes, or improvements, please follow these steps:

1. Fork the repository and create a new branch for your feature or fix.
2. Make your changes and ensure the code follows PEP 8 style guidelines.
3. Test your changes thoroughly.
4. Create a pull request with a clear description of your changes.

## Contact

If you have any questions, feedback, or suggestions, feel free to contact us at [n79633045137@gmail.com] or [Telegram]([https://t.me/AntonNaumov2022]. We're here to help and improve the Online Shop Bot together!

