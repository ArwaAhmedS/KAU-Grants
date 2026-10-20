# Donor Relations Management System

A system for managing grants and relationships between donor organizations and beneficiary entities at King Abdulaziz University, developed for the Donor Relations Department.

The system was built as a proof of concept and consists of four parts:

1. **Public website** — an informational site with a grant-acceptance journey, donor tier information, and contact/suggestion forms.
2. **Donor portal** — lets each donor view their grants, beneficiaries, impact reports, and donation history.
3. **Beneficiary portal** — lets each beneficiary manage received grants: beneficiary counts, in-kind items, and impact report uploads.
4. **Admin panel** — an internal dashboard for staff to manage donors, beneficiaries, and grants.

## Tech Stack

- Python 3.12 or newer (developed on 3.13)
- Django 6 (backend framework)
- MySQL (database)
- Tailwind CSS (via CDN)
- Alpine.js (frontend interactivity, via CDN)

## Setup

Prerequisites: Python 3.12+ and a running MySQL server with an empty database named `drms_db`.

Clone the repository and enter the project folder:

```
git clone https://github.com/ArwaAhmedS/KAU-Grants.git
cd KAU-Grants
```

Create a virtual environment and activate it:

```
python -m venv venv

source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

Install dependencies:

```
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your database and email credentials:

```
cp .env.example .env
```

`.env` must also contain a `SECRET_KEY`. Generate one with:

```
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

Build the database tables:

```
python manage.py migrate
```

Create a superuser account (for internal use via Django Admin only — see **Access & Roles** below):

```
python manage.py createsuperuser
```

Run the server:

```
python manage.py runserver
```

The system will be available at `http://127.0.0.1:8000`.

## Access & Roles

The system has three user roles — donor, beneficiary, and admin (manager) — each with an isolated login flow:

- **Role gateway:** `http://127.0.0.1:8000/accounts/portal-login/` — presents three cards, one per role, each leading to its own dedicated login page.
- **Donor and beneficiary accounts** log in through the gateway and are taken to their respective portal.
- **Admin (manager) accounts** log in through the gateway and are taken to the internal admin panel at `/admin-panel/`.
- **Django Admin** (`/admin/`) is a separate, technical-only entry point used for direct database management (via the superuser account created above). It is independent of the three-role login system and is not linked from anywhere in the user-facing site.

## Project Structure

```
config/              Project settings and the root URL table
static/              Assets shared by the whole site (university logos)
scripts/             One-off scripts that create accounts and sample data
media/               Uploaded files (not committed)

accounts/            Users, roles, login/logout, and the access decorators
entities/            The organisations: Donor (with contacts) and Beneficiary models
grants/              Grant models and the logic shared by the portals and the admin panel
audit/               The change log: who changed what and when
public_site/         Public website
portal/              Donor and beneficiary portals
admin_panel/         Internal admin dashboard
```

Every app follows the same internal shape, so once you know one you know them all:

```
<app>/
  models.py                  Database tables (only in apps that own data)
  urls.py                    Which address opens which page
  views.py  or  views/       The pages — one file per area when there are many
  templates/<app>/           HTML pages
  templates/<app>/partials/  Pieces reused across pages (file names start with _)
  static/<app>/              This app's own CSS, JavaScript, images and downloads
```

Page behaviour (filters, pop-up cards, pickers) is written in Alpine.js and lives in `static/<app>/js/`, not inside the HTML. In the admin panel each page has one small file in `js/pages/`, built from shared pieces:

```
admin_panel/static/admin_panel/js/
  helpers.js            Helpers every page uses, and how pieces are combined
  grant_cards.js        The grant detail, items and impact-report cards (shared by three pages)
  date_range_picker.js  The from–to date filter
  date_picker.js        The single-date picker on the add-grant form
  logo_cropper.js       The donor logo cropper
  pages/<page>.js       What is specific to one page — same name as its HTML template
```

The files worth knowing by name:

```
grants/models.py                    Grant, GrantItem, BeneficiaryCount, Visit, ImpactReport, GrantUpdate
grants/donor_categories.py          The eight donor tiers and how a donor's tier is calculated
grants/saving.py                    Saving items and beneficiary counts (used by both portals)
grants/page_data.py                 Turning a grant's items into JSON for the pages
public_site/content.py              All static content (news, partners, goals, contact details, form fields)
public_site/form_delivery.py        Sending emails and writing the grant-requests Excel file
portal/views/donor.py               Donor portal (read-only)
portal/views/beneficiary.py         Beneficiary portal (counts, items, impact reports)
admin_panel/views/dashboard.py      Main dashboard
admin_panel/views/donors.py         Donor list (donor_list), add donor, one donor's page (donor_detail)
admin_panel/views/beneficiaries.py  Beneficiary list (beneficiary_list), one beneficiary's page (beneficiary_detail)
admin_panel/views/grants.py         Add grant (add_grant), upload official impact report
admin_panel/views/grant_actions.py  Saving edits from the shared grant cards
admin_panel/views/page_data.py      Turning grant data into JSON for the pages
```

### Where to look when something goes wrong

| Problem with… | Start in… |
|---|---|
| Logging in, or "not allowed" errors | `accounts/views.py`, `accounts/decorators.py` |
| A donor's tier | `grants/donor_categories.py` |
| Saving in-kind items or beneficiary counts | `grants/saving.py` |
| A page in the admin panel | the matching file in `admin_panel/views/` |
| Saving from a grant card in the admin panel | `admin_panel/views/grant_actions.py` |
| A button, filter or pop-up card not responding in the admin panel | the browser console, then `admin_panel/static/admin_panel/js/` |
| The beneficiary or donor portal | `portal/views/` |
| Public site text, news or partner logos | `public_site/content.py` (images in `public_site/static/public_site/images/`) |
| Public forms not sending | `public_site/form_delivery.py`, and the email settings in `.env` |

## Sample Data

The `scripts/` folder contains scripts for creating test accounts and sample grants. Run them from the project root through the Django shell:

```
python manage.py shell < scripts/create_accounts.py
python manage.py shell < scripts/create_sample_grants.py
python manage.py shell < scripts/create_more_sample_grants.py
python manage.py shell < scripts/create_manager_account.py
```

`create_sample_grants.py` depends on the entities created by `create_accounts.py`, so run that one first.

The scripts read their passwords from `.env` (`SAMPLE_ACCOUNTS_PASSWORD` for the three test accounts, `MANAGER_PASSWORD` for the manager account) and stop with a message if the value is missing.

There is also a management command that gives every donor a tier by adding a grant where needed (try it first with `--dry-run`):

```
python manage.py ensure_donor_categories --dry-run
```

## Notes

- The `.env` file is not committed to the repository; it holds the database and email credentials.
- Some content (donor tier definitions and their benefits, contact information, news) is defined as constants in the code rather than stored in the database.
- Grant submission and suggestion forms on the public site are sent by email and are not stored in the database. Grant submissions are additionally appended to `media/exports/grant_requests.xlsx`.
- Uploaded files (donor logos, impact reports, item attachments) are stored under the local `media/` directory during development.

## Security

- Secrets (the Django secret key, database and email passwords, script passwords) live only in `.env`, never in the code.
- Uploaded files are checked for type, size and real content (`grants/uploads.py`): impact reports accept PDF and Word up to 10 MB, item attachments PDF, Word, Excel and images up to 10 MB, donor logos PNG, JPG or WEBP up to 2 MB.
- Logging out is a button (POST with a CSRF token), not a plain link.
- Values taken from the page address (such as `?open=12`) are accepted only as plain numbers before they reach the page's JavaScript.
- Alpine.js is loaded at a fixed version with an integrity hash, so the browser refuses a modified copy.
- Uploaded files are never served as open links. Every `/media/...` request goes through `accounts/file_access.py`, which checks who is asking: staff can open everything; a beneficiary only the reports and attachments of their own grants; a donor only the official reports of their own grants; donor logos are public; everything else (such as the grant-requests Excel file) is staff-only. A logged-out visitor with a link is sent to the login page.
- After 5 wrong passwords for the same account, or from the same device, logging in is blocked for 15 minutes (`accounts/login_protection.py`).
- Users are logged out after 30 minutes without activity.
- Public forms accept at most 5 submissions per hour from one device, and carry a hidden trap field that only automated bots fill in (`public_site/spam_protection.py`).
- Every change to grants, items, beneficiary counts, impact reports, donors and beneficiaries is recorded with who, when and what changed (`audit/`). The record is read-only and visible to the superuser in Django Admin under "سجل التعديلات".
- The limits above are set in `config/settings.py` (`LOGIN_LOCKOUT_ATTEMPTS`, `LOGIN_LOCKOUT_MINUTES`, `SESSION_COOKIE_AGE`, `PUBLIC_FORM_LIMIT_PER_HOUR`).

### Before going live

- Turn off `DEBUG`, set `ALLOWED_HOSTS`, and serve the site over HTTPS.
- Do not let the web server (nginx, Apache) serve the `media/` folder directly; send `/media/` requests to Django so the access check runs.
- If the site sits behind a proxy or load balancer, make sure Django sees the visitor's real IP address, otherwise the login lockout and form limits treat all visitors as one device.
