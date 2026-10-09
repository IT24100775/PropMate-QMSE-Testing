# Step 2 – Database and Security Test Plan

## 1. Testing Scope

This test plan covers the database and security testing of the PropMate system.

The database testing focuses on data integrity, constraints, relationships, persistence, transactions, and database schema consistency.

The security testing focuses on authentication, authorization, role-based access control, JWT validation, object-level authorization, API security, and CORS.

---

## 2. Database Test Plan

| Test ID | What Will Be Tested                           | Testing Type                             | Expected Result                                                          | Tool / Framework                    | Responsible Member |
| ------- | --------------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------ | ----------------------------------- | ------------------ |
| DB-T01  | User email uniqueness                         | Database / Constraint Testing            | Duplicate email should not be accepted.                                  | ASP.NET Core / EF Core / PostgreSQL | Student 4          |
| DB-T02  | Required user fields                          | Database / Data Integrity Testing        | Required fields should reject invalid or missing data.                   | ASP.NET Core / EF Core              | Student 4          |
| DB-T03  | Favourite uniqueness                          | Database / Constraint Testing            | Same user should not create duplicate favourite for the same property.   | EF Core / PostgreSQL                | Student 4          |
| DB-T04  | Viewing booking and viewing slot relationship | Database / Relationship Testing          | Booking should reference a valid viewing slot.                           | EF Core / PostgreSQL                | Student 4          |
| DB-T05  | Viewing slot availability after booking       | Database / Data Integrity Testing        | Slot availability should correctly change after a successful booking.    | ASP.NET Core / EF Core              | Student 4          |
| DB-T06  | Viewing slot availability after cancellation  | Database / Data Integrity Testing        | Slot should become available again after valid cancellation.             | ASP.NET Core / EF Core              | Student 4          |
| DB-T07  | Rental application and agreement relationship | Database / Relationship Testing          | One rental application should not have multiple agreements.              | EF Core / PostgreSQL                | Student 4          |
| DB-T08  | Purchase offer and agreement relationship     | Database / Relationship Testing          | One purchase offer should not have multiple agreements.                  | EF Core / PostgreSQL                | Student 4          |
| DB-T09  | Foreign-key integrity                         | Database / Referential Integrity Testing | Invalid related records should be rejected.                              | PostgreSQL / EF Core                | Student 4          |
| DB-T10  | Monetary value precision                      | Database / Boundary Testing              | Price/rent/offer values should be stored with the configured precision.  | PostgreSQL / EF Core                | Student 4          |
| DB-T11  | Database migration consistency                | Database / Migration Testing             | Database schema should match the application's expected schema.          | EF Core Migrations / PostgreSQL     | Student 4          |
| DB-T12  | Transaction failure handling                  | Database / Transaction Testing           | Failed multi-step operations should not leave inconsistent partial data. | ASP.NET Core / EF Core / PostgreSQL | Student 4          |

---

## 3. Security Test Plan

| Test ID | What Will Be Tested                              | Testing Type                       | Expected Result                                                                                     | Tool / Framework       | Responsible Member |
| ------- | ------------------------------------------------ | ---------------------------------- | --------------------------------------------------------------------------------------------------- | ---------------------- | ------------------ |
| SEC-T01 | Access protected endpoint without authentication | Authentication Testing             | Request should be rejected with an unauthorized response.                                           | Postman                | Student 4          |
| SEC-T02 | Access endpoint using invalid JWT                | JWT Security Testing               | Invalid token should be rejected.                                                                   | Postman                | Student 4          |
| SEC-T03 | Access endpoint using expired JWT                | JWT Security Testing               | Expired token should be rejected.                                                                   | Postman                | Student 4          |
| SEC-T04 | JWT token tampering                              | JWT Security Testing               | Modified token should not be accepted.                                                              | Postman                | Student 4          |
| SEC-T05 | Buyer/Renter accessing Owner/Agent-only endpoint | Authorization Testing              | Access should be denied.                                                                            | Postman                | Student 4          |
| SEC-T06 | Owner/Agent accessing Admin-only endpoint        | Role-Based Authorization Testing   | Access should be denied.                                                                            | Postman                | Student 4          |
| SEC-T07 | Owner accessing another owner's property         | Object-Level Authorization Testing | Access or modification should be denied.                                                            | Postman                | Student 4          |
| SEC-T08 | User accessing another user's viewing booking    | Object-Level Authorization Testing | Unauthorized access should be denied.                                                               | Postman                | Student 4          |
| SEC-T09 | Password security during registration/login      | Authentication / Security Testing  | Password should not be stored as plain text and authentication should verify the password securely. | ASP.NET Core / Postman | Student 4          |
| SEC-T10 | CORS configuration                               | API Security Testing               | Cross-origin access should follow the application's intended security policy.                       | Browser / Postman      | Student 4          |
| SEC-T11 | Sensitive information exposure                   | API Security Testing               | API responses should not expose sensitive credentials or security information.                      | Postman                | Student 4          |
| SEC-T12 | General API security vulnerabilities             | Security Scanning                  | No critical security vulnerabilities should be identified.                                          | OWASP ZAP              | Student 4          |

---

## 4. Test Execution Evidence

Evidence will be collected during test execution and may include:

* Postman request and response screenshots
* API response status codes
* Database records before and after testing
* PostgreSQL query results
* Automated test output
* Application logs
* OWASP ZAP security scan results
* Screenshots of failed and passed tests
* Defect reports
* Retesting results

---

## 5. Test Result Status

Each test case will be recorded with one of the following statuses:

* **PASS** – Expected result was achieved.
* **FAIL** – Actual result did not match the expected result.
* **BLOCKED** – Test could not be executed because of an external issue or dependency.

Failed tests will be investigated, defects will be recorded, fixes will be applied where appropriate, and the affected tests will be executed again for retesting.
