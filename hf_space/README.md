---
title: Distributed Order Management System
emoji: 🕸️
colorFrom: gray
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Distributed Order Management System

Every order runs a 4-step saga: Inventory → Payment → Fulfillment → Notification. Failures compensate completed steps in reverse order.

The landing page is an interactive API console — click any endpoint to call the live API.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health + saga stats |
| GET | `/products` | Catalog (20 products) |
| POST | `/orders` | Place order (202, saga runs async; ?fail_at=payment to force compensation) |
| GET | `/orders/{id}` | Order + full saga step log |
| GET | `/orders` | List orders, paginated |

## Stack

Python 3.11 · FastAPI · SQLite · Pydantic v2 · Next.js 14 (static export) · Tailwind CSS · Docker
