# Django REST API for FixIt Hub Platform

This Django REST API backend supports the FixIt Hub application — a job marketplace connecting clients with local handymen. The API includes user registration, authentication, role-based access control, handyman profiles, job requests, reviews, payments, job ads, and admin logs.

## Features

- JWT-based authentication
- Role-based views (Admin, Handyman, Client)
- User registration and login
- Handyman profile management
- Job request creation and acceptance
- Client review system
- Payment record logging
- Job advertisement posting
- Admin-only access to SMS logs and user management

## Endpoints Summary

### Authentication

- `POST /api/register/` — Register a new user
- `POST /api/token/` — Obtain JWT token (customized)

### Test & Role-Based Access

- `GET /api/test-auth/` — Test if user is authenticated
- `GET /api/admin-only/` — Admin-only test endpoint
- `GET /api/handyman-only/` — Handyman-only test endpoint
- `GET /api/client-only/` — Client-only test endpoint

### User Management

- `GET /api/user/` — Get own profile
- `GET /api/user/<user_id>/` — Admin: get any user by ID
- `PUT /api/user/<user_id>/` — Admin or user: update profile
- `DELETE /api/user/<user_id>/` — Admin: delete user
- `POST /api/user/<user_id>/ban/` — Admin: ban user

### Handyman Profile

- `GET /api/handyman-profile/` — Get own or all handyman profiles
- `POST /api/handyman-profile/` — Handyman: create profile
- `PUT /api/handyman-profile/` — Handyman: update profile

### Job Requests

- `GET /api/job-requests/` — List job requests based on role
- `POST /api/job-requests/` — Client: create job request
- `POST /api/job-requests/<job_id>/accept/` — Handyman: accept a pending job

### Reviews

- `GET /api/reviews/` — List reviews based on role
- `POST /api/reviews/` — Client: post a review after job completion

### Payments

- `GET /api/payments/` — View own (or all for admin) payment logs
- `POST /api/payments/` — Submit a new payment record

### Job Advertisements

- `GET /api/job-ads/` — View all active job ads
- `POST /api/job-ads/` — Handyman: post new job ad

### SMS Logs (Admin Only)

- `GET /api/sms-logs/` — View all SMS log entries

## Roles

- **Admin** — Full access to users, SMS logs, and platform moderation
- **Client** — Can request jobs, post reviews, and make payments
- **Handyman** — Can create profiles, post ads, and accept jobs

## Logging

All actions are logged using Django's logging framework for monitoring and debugging purposes.

## Permissions

Custom permission classes:
- `IsAdmin`
- `IsClient`
- `IsHandyman`
- `IsOwnerOrAdmin`

## Dependencies

- Django
- Django REST Framework
- Simple JWT
- Python logging module

## Notes

- Only authenticated users can access most views.
- Admins have the ability to manage other users, ban accounts, and view SMS logs.
- Clients can only perform actions relevant to their role (e.g., create jobs, post reviews).
- Handymen can manage their profile, accept jobs, and advertise services.

