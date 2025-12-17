Crime Lens (Awaz Uthao)

Crime Lens (Awaz Uthao) is a secure, citizen-centric crime and civic issue reporting platform designed to improve transparency, accountability, and public safety. It allows citizens to anonymously report incidents, track case progress, and view nearby crime hotspots, while enabling authorities to manage, audit, and resolve cases efficiently.

🚨 Problem Statement

Local issue reporting is often unstructured and inefficient. Reports get lost across informal channels, updates are unclear, and accountability is weak. Crime Lens centralizes reporting, ensures proper routing, and provides real-time tracking with auditable workflows.

✅ Key Features

Anonymous and verified incident reporting

Role-Based Access Control (Admin, Department Head, Staff, Citizen)

Secure authentication and authorization

Smart report routing to relevant departments

Case status tracking (Pending → In Progress → Resolved → Dismissed)

Crime hotspot map with location-based visualization

Feedback system with sentiment analysis

Detailed audit logs for accountability

Admin dashboards for monitoring and analytics

🛡️ Security & Compliance Focus

Role-Based Access Control (RBAC)

Audit logs for all sensitive actions

Rate limiting and verified user roles

Data privacy protection

Secure backend APIs

Compliance-aligned design (ISO 27001, SOC 2 concepts)

🧱 Tech Stack

Frontend

Next.js (React + TypeScript)

CSS

Leaflet (Maps)

Backend

FastAPI (Python)

REST APIs

AI integration (Gemini)

Database

SQLite (ACID compliant)

External Services

Nominatim (Geocoding)

Qdrant (Vector search – optional)

🧩 System Roles

Citizen – Submit and track reports

Department Staff – Handle assigned cases

Department Head – Manage department workload

Admin – Verify users, control routing, audit system activity

🔄 Workflow Overview

Citizen submits a report (anonymous or logged-in)

System detects duplicates and routes to the correct department

Staff updates case progress with evidence

Admin monitors actions via audit logs

Citizen tracks status and provides feedback

🧪 Testing Strategy

Unit testing (backend, sentiment analysis)

Integration testing (frontend ↔ backend)

Manual UI testing for citizen and admin workflows

🚀 Future Enhancements

Offline report submission

AI-based crime hotspot prediction

Live case tracking with officer interaction

Multi-language support

Voice-based reporting assistant

📸 Screenshots

Screenshots of Home Page, Report Submission, Crime Map, Admin Dashboard, and Feedback pages are included in the project report.

📚 Academic Context

This project was developed as part of Security Audit and Compliance (TCS-595)
Graphic Era Hill University, Bhimtal Campus (2025–2026)

👨‍💻 Contributors

Mayank Kandpal

Vijay Kumar

Deepak Karki

Saurav Chuphal

📄 License

This project is intended for academic and educational purposes.
