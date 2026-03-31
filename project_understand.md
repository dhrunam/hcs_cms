# HCS CMS (High Court Case Management System) - Project Overview

This document serves as a high-level technical overview of the **HCS CMS** project, providing insights into its architecture, core functionality, and technical stack.

## Architecture Overview
The system is built using a modern decoupled (headless) architecture, orchestrated via Docker. 

* **Backend Service**: A web API built with Python, Django, and Django REST Framework (DRF). It is served by Gunicorn.
* **Frontend Service**: A Single Page Application (SPA) built natively using Angular 21. 
* **Database**: Uses PostgreSQL (v16). The backend actually connects to *two* separate PostgreSQL databases:
  1. `hcs_cms_db` (The primary transactional database).
  2. `cis_old_db` / `sikkimhc_pg` (A read-only legacy 'CIS 1.0' database for backward compatibility and introspection tasks).

## Authentication & Security (SSO)
The application handles authentication externally.
* **Backend (`drf_sso_resource`)**: The backend functions as an **OAuth2 Resource Server** by using a custom local django app to intercept and validate OAuth bearer tokens against an introspection endpoint.
* **Frontend**: The Angular app behaves as a public OAuth2 Client. It relies on the robust `angular-oauth2-oidc` library to handle token negotiation and refresh cycles with the identity provider.

## Domain Modules (Django Apps)
The backend business logic is heavily domain-driven and split into the following apps:
* **`efiling`**: The digital intake system. It facilitates advocates submitting case files and Interlocutory Applications (IAs). Crucially, it tracks the status of a filing (Submitted) and coordinates notifications as a **Scrutiny Officer** reviews and eventually accepts or rejects the upload.
* **`cis`**: The Case Information System module handling the core schema for legal casework and integrating with the legacy endpoints.
* **`accounts`**: Custom user models, managing specific roles like Advocate, Scrutiny Officer, and more.
* **`judge` & `listing`**: Handles scheduling, docket lists (case cause lists), and dedicated interfaces for judges to review their assigned cases.
* **`master`**: Manage all the dynamic lookups and constants (Case types, Court branches, outcome types, etc).

## Frontend Tech Stack
The frontend is tailored for enterprise use with the following libraries:
* **UI Framework**: Angular v21 + Bootstrap 5.
* **Components**: Uses `@fortawesome` for iconography, `sweetalert2` and `ngx-toastr` for elegant user notifications.
* **Utilities**: Uses `pdfjs-dist` indicating the web app relies heavily on rendering, viewing, and validating PDF files (which maps directly to e-filing scrutiny processes).
