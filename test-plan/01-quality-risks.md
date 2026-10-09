# Step 1 – Quality Risks Identification

## 1. Scope

This testing activity focuses on identifying important quality risks related to **Database Testing** and **Security Testing** in the PropMate system.

The testing scope covers the backend API, PostgreSQL database, authentication, authorization, role-based access control, JWT security, and data integrity.

---

## 2. Important Database Workflows

The following database-related workflows are important to the PropMate system:

1. User registration and login data persistence.
2. Property listing creation, updating, submission, approval and publishing.
3. Property image and property status data persistence.
4. Viewing slot creation, updating and deletion.
5. Viewing booking creation and cancellation.
6. Rental application and agreement data persistence.
7. Purchase offer and agreement data persistence.
8. Negotiation and related data persistence.
9. Relationships between users, properties, viewing slots, bookings, applications, offers and agreements.
10. Database migrations and schema consistency.

---

## 3. Database Quality Risks

| Risk ID | Quality Risk                                                                               | Priority |
| ------- | ------------------------------------------------------------------------------------------ | -------- |
| DB-R01  | Required fields may accept null or invalid values if validation is inconsistent.           | High     |
| DB-R02  | Duplicate user email records may be created.                                               | High     |
| DB-R03  | Invalid foreign-key relationships or orphan records may occur.                             | High     |
| DB-R04  | Duplicate favourite records may be created for the same user and property.                 | Medium   |
| DB-R05  | Viewing booking relationships may become inconsistent with viewing slots.                  | High     |
| DB-R06  | Viewing slot availability status may become incorrect after booking or cancellation.       | High     |
| DB-R07  | More than one rental agreement may be created for the same rental application.             | High     |
| DB-R08  | More than one purchase agreement may be created for the same purchase offer.               | High     |
| DB-R09  | Invalid monetary values or precision problems may affect property prices, rents or offers. | Medium   |
| DB-R10  | Database migration and application schema may become inconsistent.                         | High     |
| DB-R11  | Partial database updates may occur when a multi-step operation fails.                      | High     |
| DB-R12  | Incorrect cascade/restrict delete behaviour may cause data loss or invalid relationships.  | Medium   |

---

## 4. Important Security Workflows

The following security-related workflows are important:

1. User registration.
2. User login and authentication.
3. JWT token generation and validation.
4. Access to authenticated API endpoints.
5. Role-based authorization for Buyer/Renter, Owner/Agent and Admin users.
6. Owner-level authorization for properties and viewing slots.
7. User-level authorization for viewing bookings.
8. Protection against invalid, expired or tampered JWT tokens.
9. Protection of administrator-only operations.
10. API security and CORS configuration.
11. Protection of sensitive user information and credentials.

---

## 5. Security Quality Risks

| Risk ID | Quality Risk                                                                  | Priority |
| ------- | ----------------------------------------------------------------------------- | -------- |
| SEC-R01 | An unauthenticated user may access protected API endpoints.                   | Critical |
| SEC-R02 | A user may access functionality belonging to another user role.               | Critical |
| SEC-R03 | An owner may access or modify another owner's property or viewing slot.       | Critical |
| SEC-R04 | A user may access or cancel another user's viewing booking.                   | Critical |
| SEC-R05 | Invalid or expired JWT tokens may be accepted.                                | High     |
| SEC-R06 | A tampered JWT token or manipulated claims may be accepted.                   | Critical |
| SEC-R07 | User passwords may be stored or handled insecurely.                           | Critical |
| SEC-R08 | Non-admin users may access administrator-only operations.                     | Critical |
| SEC-R09 | Overly permissive CORS configuration may allow unwanted cross-origin access.  | High     |
| SEC-R10 | Sensitive information may be exposed through API responses or errors.         | High     |
| SEC-R11 | General API security vulnerabilities may expose system functionality or data. | High     |

---

## 6. Evidence Reviewed

The following parts of the PropMate backend were reviewed when identifying the above risks:

* `backend/PropMate.Api/Data/AppDbContext.cs`
* `backend/PropMate.Api/Program.cs`
* `backend/PropMate.Api/Services/AuthService.cs`
* `backend/PropMate.Api/Services/JwtService.cs`
* `backend/PropMate.Api/Controllers/ViewingSlotsController.cs`
* `backend/PropMate.Api/Controllers/ViewingBookingsController.cs`
* `backend/PropMate.Api/Controllers/PropertyListingsController.cs`

---

## 7. Testing Focus

### Database Testing

The identified database risks will be tested using:

* Database integration testing
* Constraint testing
* Foreign-key and relationship testing
* Data integrity testing
* CRUD persistence testing
* Database migration and schema testing
* Transaction-related testing
* Duplicate and boundary-value testing

### Security Testing

The identified security risks will be tested using:

* Authentication testing
* Authorization testing
* Role-based access-control testing
* Object-level authorization testing
* JWT validation testing
* JWT tampering and expiration testing
* Password security testing
* API security testing
* CORS testing
* OWASP security testing

---

## 8. Highest Priority Risks

The highest priority risks identified for the PropMate system are:

1. Unauthorized access to protected API endpoints.
2. Incorrect role-based authorization.
3. Unauthorized access to another user's property or booking.
4. JWT validation and token tampering vulnerabilities.
5. Database relationship and referential-integrity failures.
6. Incorrect viewing-slot availability after booking or cancellation.
7. Duplicate agreement records.
8. Partial database updates caused by transaction failures.

These risks will receive higher priority during the subsequent test-case design and execution stages.

---

## 9. Conclusion

The quality-risk analysis identifies **database integrity, relationship consistency, authentication, authorization and API security** as the main areas requiring focused testing.

The identified risks will be used as the basis for developing the test plan, test cases, test execution and defect/retesting evidence in the following steps.
