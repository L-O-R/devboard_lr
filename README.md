# Manager API (Devboard Project)

A robust, role-based project management system built with **Django REST Framework (DRF)**. This system allows organizations to manage their members, projects, and sprint lifecycles with granular permissions.

---

## Folder Structure

Below is the directory layout of the application:

```text
manager/
├── .env                  # Environment configurations (DB name, passwords, DEBUG, SECRET_KEY)
├── .gitignore            # Git ignore rules
├── requirements.txt      # Python package dependencies
├── manage.py             # Django project manager entrypoint
├── devboard_project/     # Project core configuration directory
│   ├── __init__.py
│   ├── asgi.py           # ASGI configuration
│   ├── settings.py       # Global Django settings, cookie security, & REST configuration
│   ├── urls.py           # Main routing entrypoint (api/auth, api/organizations)
│   └── wsgi.py           # WSGI configuration
└── apps/                 # Application modules
    ├── accounts/         # User management, profile configuration, and authentication
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── authentication.py  # Cookie-based custom TokenAuthentication handler
    │   ├── models.py          # Custom User model with roles
    │   ├── serializers.py     # Login, registration, password validation, and user profiles
    │   ├── urls.py            # Routing for user profile and authentication endpoints
    │   └── views.py           # View handling for login, registration, logout, and profile
    ├── organizations/    # Organization structures, membership states, and invitations
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py          # Organization and OrgMembership schemas
    │   ├── permissions.py     # Permissions checking OrgMembership status
    │   ├── serializers.py     # Organization representation and membership validations
    │   ├── urls.py            # Organization/member management routes
    │   └── views.py           # CRUD views for organizations and active membership invitation/removal
    ├── projects/         # Project workspaces, project memberships, and agile sprint flows
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py          # Project, ProjectMembership, and Sprint schemas
    │   ├── permissions.py     # Permissions check for Project Membership & Organization Manager roles
    │   ├── serializers.py     # Validation structures for projects, sprints, and membership actions
    │   ├── urls.py            # Project views and sprint details nested routes
    │   └── views.py           # View endpoints for project listing, members, and sprint states
    └── tasks/            # Issue tracking, status workflows, and tag management
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── models.py          # Label and Task schemas
        ├── permissions.py     # Task-specific permissions checking Project Membership role
        ├── serializers.py     # Serializers for task lists, task details, status transitions, and labels
        ├── urls.py            # Label and task management routes
        └── views.py           # CRUD views for tasks and labels, including developer status transition logic
```

---

## Project Flow & Flowchart

The workflow logic operates around four tiers of hierarchy: **User -> Organization -> Project/Sprint -> Task**. 

Below is an ASCII representation of the project flow:

```text
                  +-----------------------------------+
                  |             User Registration /   |
                  |                   Login           |
                  +-----------------+-----------------+
                                    |
                                    v (Cookie Auth / Token Response)
                  +-----------------+-----------------+
                  |      Authenticated User           |
                  +-----------------+-----------------+
                                    |
            +-----------------------+-----------------------+
            | (Creates Organization)                        | (Joins via Invitation)
            v                                               v
+-----------+-----------+                       +-----------+-----------+
|  Organization Owner   |                       |  Organization Member  |
|  (Role: Org Admin)    |                       |  (Role: Dev, PM, etc) |
+-----------+-----------+                       +-----------+-----------+
            |                                               |
            |-- (Invites Members via Email)                 |
            |-- (Manages/Removes Members)                   |
            |                                               |
            v                                               v
+-----------+-----------------------------------------------+-----------+
|                          Project Management                           |
+-----------------------------------+-----------------------------------+
                                    |
         +--------------------------+--------------------------+
         | (Create Project)                                    | (Join Project)
         v                                                     v
+--------+---------------+                            +--------+---------------+
| Project Creator/PM     |                            | Project Member         |
| (Role: Project Manager)|                            | (Role: Developer, etc) |
+--------+---------------+                            +--------+---------------+
         |                                                     |
         |-- (Manages Sprint Lifecycle)                        |-- (Views Project/Sprint info)
         |-- (Adds Org Members to Project)                     |
         |                                                     |
         v                                                     v
+--------+-----------------------------------------------------+--------+
|                      Sprints (Planned / Active / Completed)            |
+-----------------------------------+-----------------------------------+
                                    |
                                    v (Create / Update / Assign)
+-----------------------------------+-----------------------------------+
|            Tasks (Backlog / Todo / In Progress / In Review / Done)    |
+-----------------------------------------------------------------------+
```

---

## Models

### 1. Accounts Module (`apps.accounts`)
*   **User**: Inherits from Django's `AbstractUser` and replaces `username` with `email` as the primary identifier field.
    *   `email`: `EmailField` (Unique)
    *   `role`: `CharField` (Choices: `super_admin`, `org_admin`, `project_manager`, `developer`, `viewer`; defaults to `viewer`)
    *   `profile_picture`: `ImageField` (Uploads to `profiles/`, optional)
    *   `bio`: `TextField` (Optional)
    *   *Helpers*: `@property` tags checking if `is_org_admin` or `is_project_manager`.

### 2. Organizations Module (`apps.organizations`)
*   **Organization**: Represents a company, client group, or software dev division.
    *   `name`: `CharField` (Unique)
    *   `description`: `TextField` (Optional)
    *   `logo`: `ImageField` (Uploads to `org_logos/`, optional)
    *   `created_by`: `ForeignKey` to `User` (On delete: `SET_NULL`)
    *   `created_at` / `updated_at`: `DateTimeField` metadata
*   **OrgMembership**: Links Users to Organizations with active context and role.
    *   `user`: `ForeignKey` to `User` (On delete: `CASCADE`)
    *   `organization`: `ForeignKey` to `Organization` (On delete: `CASCADE`)
    *   `role`: `CharField` (Choices: `org_admin`, `project_manager`, `developer`, `viewer`; defaults to `developer`)
    *   `joined_at`: `DateTimeField`
    *   `is_active`: `BooleanField` (Defaults to `True`)
    *   *Constraints*: `unique_together = ('user', 'organization')`

### 3. Projects Module (`apps.projects`)
*   **Project**: A workspaces folder created inside an Organization.
    *   `name`: `CharField`
    *   `description`: `TextField` (Optional)
    *   `organization`: `ForeignKey` to `Organization` (On delete: `CASCADE`)
    *   `created_by`: `ForeignKey` to `User` (On delete: `SET_NULL`)
    *   `status`: `CharField` (Choices: `active`, `on_hold`, `completed`, `archived`; defaults to `active`)
    *   `visibility`: `CharField` (Choices: `public`, `private`; defaults to `private`)
    *   `start_date` / `end_date`: `DateField` (Optional)
    *   `created_at` / `updated_at`: Timestamps
    *   *Constraints*: `unique_together = ('name', 'organization')`
*   **ProjectMembership**: Manages project memberships.
    *   `user`: `ForeignKey` to `User` (On delete: `CASCADE`)
    *   `project`: `ForeignKey` to `Project` (On delete: `CASCADE`)
    *   `role`: `CharField` (Choices: `project_manager`, `developer`, `viewer`; defaults to `developer`)
    *   `joined_at`: `DateTimeField`
    *   *Constraints*: `unique_together = ('user', 'project')`
*   **Sprint**: Time-boxed execution periods for tasks inside a project.
    *   `name`: `CharField`
    *   `goal`: `TextField` (Optional)
    *   `project`: `ForeignKey` to `Project` (On delete: `CASCADE`)
    *   `start_date` / `end_date`: `DateField` (Optional)
    *   `created_by`: `ForeignKey` to `User` (On delete: `SET_NULL`)
    *   `status`: `CharField` (Choices: `planned`, `active`, `completed`; defaults to `planned`)
    *   `created_at`: `DateTimeField`

### 4. Tasks Module (`apps.tasks`)
*   **Label**: Tags that can be added to tasks for categorization within a project workspace.
    *   `name`: `CharField`
    *   `color`: `CharField` (HEX color representation, defaults to `#f5f5f5`)
    *   `project`: `ForeignKey` to `Project` (On delete: `CASCADE`)
    *   *Constraints*: `unique_together = ['name', 'project']`
*   **Task**: Individual issues or work items tracked within a project and optionally associated with a sprint.
    *   `title`: `CharField`
    *   `description`: `TextField` (Optional)
    *   `project`: `ForeignKey` to `Project` (On delete: `CASCADE`)
    *   `sprint`: `ForeignKey` to `Sprint` (On delete: `SET_NULL`, optional)
    *   `created_by`: `ForeignKey` to `User` (On delete: `SET_NULL`, optional)
    *   `assigned_to`: `ForeignKey` to `User` (On delete: `SET_NULL`, optional)
    *   `status`: `CharField` (Choices: `backlog`, `todo`, `in_progress`, `in_review`, `done`; defaults to `backlog`)
    *   `priority`: `CharField` (Choices: `low`, `medium`, `high`, `critical`; defaults to `medium`)
    *   `due_data`: `DateField` (Optional, maps to due date)
    *   `order`: `PositiveBigIntegerField` (Defaults to `0`)
    *   `created_at` / `updated_at`: Timestamps
---

## Serializers

*   **RegisterSerializer**: Validates that passwords match (`password == password2`), extracts `password2` before database persistence, and registers users.
*   **LoginSerializer**: Accepts `email`/`password` and leverages Django's `authenticate` tool. Validates whether accounts are active (`is_active = True`).
*   **UserProfileSerializer**: Generates representation fields. The fields `id`, `email`, `role`, and `date_joined` are set to `read_only`.
*   **ChangePasswordSerializer**: Allows password modification. Verifies that the supplied `old_password` matches the requesting user's password.
*   **OrganizationSerializer**: Generates fields representing organizations. Uses a `SerializerMethodField` (`member_count`) to compute active memberships.
*   **OrgMembershipSerializer**: Links active profiles inside organizations. Employs a nested `UserProfileSerializer`.
*   **InviteMemberSerializer**: Validates membership invites. Checks if the invited email exists in the database.
*   **ProjectSerializer**: Contains read-only properties for `organization` and `created_by`. Uses method fields `member_count` and `sprint_count`.
*   **ProjectMembershipSerializer**: Represents project members with nested profile metadata.
*   **SprintSerializer**: Validates date validity (`end_date >= start_date`) and serializes sprint metrics.
*   **AddProjectMemberSerializer**: Validates project membership requests by confirming the target user exists.
*   **LabelSerializer**: Represents labels with `id`, `name`, `color`, and `project` fields (with `id` and `project` read-only).
*   **TaskSerializer**: Represents full tasks including nested creator, assignee, and labels. Uses `PrimaryKeyRelatedField`s to accept ID inputs for writes (`assigned_to_id`, `label_ids`, `sprint_id`), and scopes them to the correct project's context.
*   **TaskStatusUpdateSerializer**: Lightweight serializer used by developers for updating only the task `status`. Restricts status transitions based on a predefined workflow (e.g., `backlog` -> `todo` -> `in_progress` -> `in_review` -> `done`).

---

## URLs & Endpoints Map

Authentication and organization routes are mounted directly, whereas project and sprint configurations are logically nested (`/api/organizations/<org_id>/projects/`).

| App | Endpoint | HTTP Method | View Class | Permissions | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **accounts** | `/api/auth/register` | `POST` | `RegisterVIEW` | `AllowAny` | Registers user. Creates a token and injects it into client cookies. |
| **accounts** | `/api/auth/login` | `POST` | `LoginView` | `AllowAny` | Authenticates email/password. Injects Token into cookies. |
| **accounts** | `/api/auth/logout` | `POST` | `LogoutView` | `IsAuthenticated` | Deletes token on DB, deletes cookie. |
| **accounts** | `/api/auth/profile` | `GET` / `PATCH` | `ProfileView` | `IsAuthenticated` | View or partially update profile fields. |
| **organizations** | `/api/organizations/` | `GET` | `OrganizationListCreateView` | `IsAuthenticated` | Retrieves all organizations the requester belongs to. |
| **organizations** | `/api/organizations/` | `POST` | `OrganizationListCreateView` | `IsAuthenticated` | Creates organization. Automatically inserts creator as `Org Admin`. |
| **organizations** | `/api/organizations/<org_id>/` | `GET` | `OrganiztionDetailView` | `IsOrgMember` | Gets details of a specific organization. |
| **organizations** | `/api/organizations/<org_id>/` | `PATCH` / `DELETE` | `OrganiztionDetailView` | `isOrgAdmin` | Updates metadata or deletes/drops the organization. |
| **organizations** | `/api/organizations/<org_id>/members/` | `GET` | `OrgMembersListView` | `IsOrgMember` | Lists active memberships inside the organization. |
| **organizations** | `/api/organizations/<org_id>/invite/` | `POST` | `InviteMemberView` | `isOrgAdmin` | Invites a member to join the organization via email. |
| **organizations** | `/api/organizations/<org_id>/members/<user_id>/remove/` | `DELETE` | `RemoveMemberView` | `isOrgAdmin` | Removes a user's membership. |
| **projects** | `/api/organizations/<org_id>/projects/` | `GET` | `ProjectListCreateView` | `IsAuthenticated` | Lists project workspaces (`public` visibility OR user belongs to). |
| **projects** | `/api/organizations/<org_id>/projects/` | `POST` | `ProjectListCreateView` | `isOrgMemberForProject` | Creates project in org. User becomes `Project Manager`. |
| **projects** | `/api/organizations/<org_id>/projects/<project_id>/` | `GET` | `ProjectDetailView` | `IsProjectMember` | Gets details of a project. |
| **projects** | `/api/organizations/<org_id>/projects/<project_id>/` | `PATCH` / `DELETE` | `ProjectDetailView` | `IsProjectManager` | Partially updates metadata or deletes project. |
| **projects** | `/api/organizations/<org_id>/projects/<project_id>/members/` | `GET` | `ProjectMemberView` | `IsProjectMember` | Lists project memberships. |
| **projects** | `/api/organizations/<org_id>/projects/<project_id>/members/` | `POST` | `ProjectMemberView` | `IsProjectManager` | Adds active org member to project with specified role. |
| **projects** | `/api/organizations/<org_id>/projects/<project_id>/sprints/` | `GET` | `SprintListCreateView` | `IsProjectMember` | Lists sprints within a project. |
| **projects** | `/api/organizations/<org_id>/projects/<project_id>/sprints/` | `POST` | `SprintListCreateView` | `IsProjectManager` | Creates a new sprint. |
| **projects** | `/api/organizations/<org_id>/projects/<project_id>/sprints/<sprint_id>/` | `GET` | `SprintDetailView` | `IsProjectMember` | Retrieves details of a specific sprint. |
| **projects** | `/api/organizations/<org_id>/projects/<project_id>/sprints/<sprint_id>/` | `PATCH` / `DELETE` | `SprintDetailView` | `IsProjectManager` | Updates or deletes a sprint. |
| **tasks** | `/api/organizations/<org_id>/projects/<project_id>/labels/` | `GET` | `LabelListCreateView` | `IsAuthenticated`, `ISTaskProjectMember` | Lists all labels in the project. |
| **tasks** | `/api/organizations/<org_id>/projects/<project_id>/labels/` | `POST` | `LabelListCreateView` | `IsAuthenticated`, `ISTaskProjectMember` | Creates a new label in the project. |
| **tasks** | `/api/organizations/<org_id>/projects/<project_id>/tasks/` | `GET` | `TaskListCreateView` | `IsAuthenticated`, `ISTaskProjectMember` | Lists tasks in the project. Supports query filtering by `sprint_id` (or `backlog`), `assigned_to`, `status`, `priority`, and text `search`. |
| **tasks** | `/api/organizations/<org_id>/projects/<project_id>/tasks/` | `POST` | `TaskListCreateView` | `IsAuthenticated`, `ISTaskProjectMember` | Creates a new task in the project. Creator is automatically set to requester. |
| **tasks** | `/api/organizations/<org_id>/projects/<project_id>/tasks/<task_id>/` | `GET` | `TaskDetailView` | `IsAuthenticated`, `CanManageTask` | Retrieves details of a specific task. |
| **tasks** | `/api/organizations/<org_id>/projects/<project_id>/tasks/<task_id>/` | `PATCH` | `TaskDetailView` | `IsAuthenticated`, `CanManageTask` | Updates task details. If the user is a `developer`, only status updates are allowed (validated by `TaskStatusUpdateSerializer`). |
| **tasks** | `/api/organizations/<org_id>/projects/<project_id>/tasks/<task_id>/` | `DELETE` | `TaskDetailView` | `IsAuthenticated`, `CanManageTask` | Deletes a task. Only accessible by a Project Manager. |

---

## Views

*   **Cookie Authentication**: Inherits from DRF's `TokenAuthentication`. Attempts to read the token from `devboard_auth` cookies before delegating to the fallback headers parser.
*   **Custom Permissions**:
    *   `isOrgAdmin`: Confirms user has an active `OrgMembership` with role `org_admin` on the organization matching `org_id`.
    *   `IsOrgMember`: Confirms user has an active `OrgMembership` matching `org_id`.
    *   `isOrgMemberForProject`: Custom validation allowing organization members to start projects inside their organization structure.
    *   `IsProjectMember`: Confirms user has a `ProjectMembership` for the specified `project_id`.
    *   `IsProjectManager`: Confirms user has an `OrgMembership` role of `project_manager` or `org_admin` for the organization.
    *   `ISTaskProjectMember`: Confirms user is a member of the project matching the `project_id` parameter.
    *   `CanManageTask`: Checks project membership and enforces role-based access for tasks. Viewers are restricted to safe HTTP methods (GET/HEAD/OPTIONS).

---

## Installation Process

Follow these steps to configure and run the application locally on Windows:

### Prerequisites
*   Python 3.10+
*   PostgreSQL installed and running

### Step-by-Step Setup
1.  **Clone the project** to your local workspace directory.
2.  **Initialize Virtual Environment**:
    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    ```
3.  **Install dependencies**:
    ```powershell
    pip install -r requirements.txt
    ```
4.  **Configure environment file (`.env`)**:
    Create or edit the `.env` file in the root directory (matching your PostgreSQL setup):
    ```env
    SECRET_KEY=your-django-insecure-key-here
    DEBUG=True
    DB_NAME=devboard_db
    DB_USER=postgres
    DB_PASSWORD=your_password
    DB_HOST=localhost
    DB_PORT=5432
    ```
5.  **Create Database**:
    Ensure your PostgreSQL server is running, and create the database named `devboard_db`:
    ```sql
    CREATE DATABASE devboard_db;
    ```
6.  **Apply database migrations**:
    ```powershell
    python manage.py migrate
    ```
7.  **Create a Superuser**:
    Create an initial superuser account for administration access:
    ```powershell
    python manage.py createsuperuser
    ```
8.  **Run Development Server**:
    ```powershell
    python manage.py runserver
    ```
    The application will start at `http://127.0.0.1:8000/`.

---

## Testing Process

Tests are isolated inside the `tests.py` file within each application module directory.

### Running Tests
Execute the test suites using Django's test runner:
```powershell
python manage.py test
```

### Coverage reporting (optional)
To measure code coverage, install `coverage`:
```powershell
pip install coverage
coverage run manage.py test
coverage report
```

---



### Backlog & Features to Add

1.  **Work History / Audit Logging**:
    *   Track action histories such as "Member added to project", "Sprint status changed", or "Task assigned" to feed an activity board widget.
2.  **Secure JWT / Double Token Auth**:
    *   Migrate authentication to a robust setup using JWT tokens (e.g., SimpleJWT) stored in HTTP-only cookies with CSRF token protection headers.
3.  **Real-Time Notifications**:
    *   Integrate `django-channels` and websockets to notify users when they are assigned tasks or invited to organizations.
