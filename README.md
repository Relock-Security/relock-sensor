# Relock - Session Protection Demo

Relock Sensor is a lightweight demo application that demonstrates
**infrastructure-level session protection** using Relock Security.

This project shows how session token authenticity can be verified
**outside of application logic**, using Load Balancer rules and 
Relock Cloud --- without requiring backend API integration.

The only integration inside the application is the inclusion of the
JavaScript agent (`relock.js`).

------------------------------------------------------------------------

# What This Demo Proves

This demo demonstrates that:

-   Session protection can be enforced at the **infrastructure layer**
-   Token verification can be performed outside the application
-   Backend services do not need to validate token signatures
-   Request-level authentication can be applied consistently
-   Security logic can be fully decoupled from business logic

The Flask application remains unaware of verification mechanics.
All validation is handled by NGINX and Relock Cloud.

------------------------------------------------------------------------

# Architecture Overview

The deployment emulates a typical cloud setup similar to:

    User Browser
         ↓
    Reverse Proxy + auth_request
         ↓
    Web Application

Relock Cloud acts as the external trust authority.

------------------------------------------------------------------------

## Components

### Flask Application

The Flask app:

-   Emulates a microservice
-   Serves a basic UI
-   Initializes user sessions
-   Manages session cookies
-   Loads the Relock JavaScript agent (`relock.js`) from Relock Cloud

The application **does not validate token authenticity**.

------------------------------------------------------------------------

### NGINX Reverse Proxy (Security Sidecar)

NGINX runs in front of the Flask application and is responsible for:

-   Routing traffic
-   Forwarding verification requests to Relock Cloud
-   Enforcing request authentication using the `auth_request` module
-   Blocking unauthenticated or invalid requests

Request authentication is enabled by default for all requests except the
initial session-establishing request.

This ensures security enforcement is infrastructure-driven rather than
application-driven.

------------------------------------------------------------------------

# Prerequisites

Before starting, ensure you have:

-   Docker
-   Make
-   Administrative privileges (to modify `/etc/hosts` and install
    certificates)
-   Internet access
-   A valid SSL certificate (self-signed is acceptable for local
    development)

> TLS is mandatory. Browser-based cryptographic operations require a
> secure context (`https`).

------------------------------------------------------------------------

# Detailed Setup

## 1. Clone the Repository

``` bash
git clone https://github.com/Relock-Security/relock-sensor.git
cd relock-sensor
```

------------------------------------------------------------------------

## 2. Verify Environment Configuration

Open the `.env` file and confirm the following values:

``` env
RELOCK_HOST=test.relock.id
HOST=relock.app
```

-   `RELOCK_HOST` should point to your Relock Gatekeeper instance.
-   `HOST` defines the local hostname used for the demo.

------------------------------------------------------------------------

## 3. Build the Demo Image

``` bash
make image
```

------------------------------------------------------------------------

## 4. Generate TLS Certificate

``` bash
make certificate
```

This generates a self-signed certificate (`cert.pem`) for `relock.app`.

------------------------------------------------------------------------

## 5. Run the Demo Container

``` bash
make run
```

After startup, identify the container IP address:

``` bash
docker inspect sensor | grep IPAddress
```

------------------------------------------------------------------------

## 6. Configure Local Hostname Resolution

Edit your `/etc/hosts` file:

``` bash
sudo nano /etc/hosts
```

Add:

    172.17.0.X relock.app
    172.17.0.X www.relock.app

Replace the IP address with your container's actual IP.

------------------------------------------------------------------------

## 7. Install the Certificate

### macOS

1.  Open `cert.pem`
2.  Add it to **Keychain Access**
3.  Set the certificate to **Always Trust**

### Linux

``` bash
sudo cp cert.pem /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

------------------------------------------------------------------------

## 8. Configure Relock Cloud

1.  Log in or create an account at:

    https://relock.id

2.  Add a new **Protected Origin**:

        relock.app

3.  In **Origin Configuration → Wildcard ID**:

    -   Create a new wildcard

    -   Use:

            test

    You should see:

        test.relock.id

4.  In **Origin Configuration → Session Binding**:

    -   Session Cookie Name: `session`
    -   Implicit Trust: `True`
    -   Interim Session Time: `30m`

Save configuration changes.

------------------------------------------------------------------------

## 9. Access the Application

Open your browser:

    https://relock.app

If the certificate is trusted correctly, the application should load
without warnings.

------------------------------------------------------------------------

# Security Design Notes

This demo intentionally models a zero-trust architecture:

-   The backend does not communicate directly with Relock Cloud.
-   Trust signals pass through the browser.
-   `relock.js` mediates cryptographic validation.
-   NGINX enforces per-request authentication.

If trust conditions change, Relock Cloud signals the browser, which
triggers session termination.

------------------------------------------------------------------------

# Session Termination Model

In this demo:

-   Relock Cloud cannot directly terminate backend sessions.
-   Security events are delivered to the frontend.
-   The browser triggers the logout flow.

------------------------------------------------------------------------

# Troubleshooting

### HTTPS Warning

Ensure: - The certificate is installed and trusted - `/etc/hosts` is
configured correctly - You are accessing `https://relock.app`

------------------------------------------------------------------------

### Requests Blocked by NGINX

Check: - `RELOCK_HOST` configuration - Relock origin settings - Session
Cookie Name matches `session`

------------------------------------------------------------------------

### Wildcard Not Visible

Ensure: - The origin is correctly added - The wildcard ID is created
under the correct origin - Configuration changes are saved

------------------------------------------------------------------------

# Summary

Relock Sensor demonstrates an infrastructure-enforced approach to 
session protection aligned with modern Zero Trust architecture and 
enterprise compliance frameworks such as SOC 2 and ISO 27001.

Security & Compliance Alignment

Zero Trust Enforcement
Every request is explicitly validated before reaching the application. 
Trust is continuously evaluated — not assumed after authentication.

Independent Security Control Layer
Session verification is enforced at the proxy layer using NGINX 
(auth_request), establishing a clear separation between business logic 
and security controls. This supports defense-in-depth and strong 
control boundaries.

Reduced Application Risk Surface
The backend does not parse or validate tokens, minimizing exposure to 
JWT parsing errors, signature misconfigurations, and inconsistent 
enforcement across services.

Centralized Policy Enforcement
Authentication and session validation policies are applied 
consistently at the infrastructure layer, supporting uniform access 
control and improved auditability.

Secure Cryptographic Context
Browser-based cryptographic operations require HTTPS, reinforcing 
secure session handling in accordance with modern security standards.

Relock shifts session protection from an application responsibility 
to a verifiable infrastructure control aligned with Zero Trust 
architecture principles.
