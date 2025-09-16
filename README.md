# StockFlow B2B SaaS - Case Study Solution

This repository contains the complete solution to the StockFlow B2B SaaS take-home case study. The solution is structured as a typical Flask web application to demonstrate a clear separation of concerns.

- **Project Structure**:
  - `app/`: Contains the core application logic, including models and API routes.
  - `database/`: Contains the SQL script for database schema creation.
  - `README.md`: This file, explaining the solution and design choices.

---

## Part 1: Code Review & Debugging

### Analysis of the Original Code

The initial code snippet had several critical issues:

1.  **Non-Atomic Transaction**: Two separate `db.session.commit()` calls could lead to data inconsistency if the second one failed.
2.  **Lack of Input Validation**: Direct dictionary access (`data['key']`) without validation would cause 500 errors on missing or malformed input.
3.  **Flawed Business Logic**: Storing `warehouse_id` on the `Product` model incorrectly coupled a product to a single warehouse.
4.  **No Uniqueness Check**: The code did not check if a SKU already existed, violating a key business rule.
5.  **Improper HTTP Response**: Returned a `200 OK` instead of the more appropriate `201 Created` for resource creation.

### Corrected Implementation

The corrected, robust implementation of the product creation endpoint can be found in:
- **`app/routes.py`** (the `create_product` function)

This version addresses all the identified issues by using a single atomic transaction, validating all inputs, correcting the business logic, checking for SKU uniqueness, and returning the proper HTTP status code.

---

## Part 2: Database Design

A scalable and normalized database schema was designed to meet the requirements.

### Schema and Models

- The complete SQL DDL to create the tables is available in **`database/schema.sql`**.
- The corresponding SQLAlchemy models for use in the Flask application are defined in **`app/models.py`**.

### Design Decisions & Justifications

- **Multi-Tenancy**: The schema is designed for multi-tenancy, with `company_id` on key tables like `products` and `warehouses`. SKUs are unique *per company*.
- **Auditing**: An `inventory_logs` table provides a full audit trail of every stock change, which is critical for reporting and business intelligence.
- **Flexibility**: The `bundle_components` table provides a flexible many-to-many structure for defining product bundles.
- **Normalization**: The schema is normalized to reduce data redundancy (e.g., `product_types` table to manage low-stock thresholds centrally).

---

## Part 3: API Implementation

### Low-Stock Alerts Endpoint

The implementation for the `GET /api/companies/{company_id}/alerts/low-stock` endpoint is located in:
- **`app/routes.py`** (the `get_low_stock_alerts` function)

### Approach and Edge Cases Handled

- **Performance**: The solution uses a single, efficient SQL query with a **subquery** to calculate recent sales data. This avoids the "N+1 query problem" and is highly performant.
- **Assumptions**: The implementation assumes "recent sales" means sales within the last 30 days and that each product has one primary supplier.
- **Edge Cases**:
  - The code handles cases where a company is not found (returns 404).
  - It correctly calculates `days_until_stockout` and avoids division-by-zero errors if a product has no recent sales.
  - It handles products that may not have an assigned supplier (`OUTER JOIN`).
