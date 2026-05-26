# Devboard Manager API Documentation

Welcome to the Devboard Manager API documentation. This API is designed to support a robust, role-based project management system enabling organizations to manage their members, projects, sprint lifecycles, and tasks with granular permissions.

---

## 1. Authentication & Security

The API uses **Django REST Framework (DRF) Token Authentication**. Authenticated requests can be performed in two ways:

### A. HTTP Authorization Header
Specify the token in the `Authorization` header:
```http
Authorization: Token <your_auth_token>
```

### B. Cookie Authentication (Custom)
During successful **Registration** or **Login**, a session cookie is returned.
- **Cookie Name**: `devboard_auth`
- **Security flags**: `HttpOnly = True`, `SameSite = Lax`
- **Expiry**: 7 days (`Max-Age = 604800` seconds)

---

## 2. Roles & Permissions

The application implements dual layers of role-based access control (RBAC) at the **Organization** and **Project** levels.

### Organization Roles
- **Org Admin**: Full control over organization metadata, memberships (invite/remove), and project creations.
- **Project Manager / Developer / Viewer**: Standard organization members.

### Project Roles
- **Project Manager**: Full control over project settings, project memberships, and sprint lifecycles. Can perform tasks CRUD.
- **Developer**: Can view project details and tasks. Can only modify the `status` of tasks assigned to them (constrained by allowed status transitions).
- **Viewer**: Read-only access to projects, sprints, and tasks.

---

## 3. API Endpoints Reference

### 3.1. Authentication App (`/api/auth/`)

#### Register User
* **Endpoint**: `POST /api/auth/register`
* **Permission**: `AllowAny`
* **Description**: Register a new user. On success, sets `devboard_auth` cookie and returns user details.
* **Request Body** (JSON):
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `email` | String (Email) | **Yes** | Must be unique. Used as primary identifier. |
  | `username` | String | **Yes** | Chosen display name. |
  | `password` | String | **Yes** | Min length 8 characters. |
  | `password2` | String | **Yes** | Min length 8 characters. Must match `password`. |
  | `role` | String | No | Default: `'viewer'`. Choice of `org_admin`, `project_manager`, `developer`, `viewer`. |
* **Success Response (`201 Created`)**:
  ```json
  {
    "message": "Registration Successful!",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "user123",
      "role": "developer",
      "bio": null,
      "profile_picture": null,
      "date_joined": "2026-05-26T12:00:00Z"
    }
  }
  ```

#### Login User
* **Endpoint**: `POST /api/auth/login`
* **Permission**: `AllowAny`
* **Description**: Authenticates user credentials. Sets session cookie on success.
* **Request Body** (JSON):
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `email` | String (Email) | **Yes** | Registered email. |
  | `password` | String | **Yes** | User password. |
* **Success Response (`200 OK`)**:
  ```json
  {
    "message": "Login Successfully",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "user123",
      "role": "developer",
      "bio": null,
      "profile_picture": null,
      "date_joined": "2026-05-26T12:00:00Z"
    }
  }
  ```

#### Logout User
* **Endpoint**: `POST /api/auth/logout`
* **Permission**: `IsAuthenticated`
* **Description**: Deletes current auth token and removes `devboard_auth` cookie.
* **Success Response (`200 OK`)**:
  ```json
  {
    "message": "Logout was successful"
  }
  ```

#### Get User Profile
* **Endpoint**: `GET /api/auth/profile`
* **Permission**: `IsAuthenticated`
* **Description**: Retrieve authenticated user details.
* **Success Response (`200 OK`)**:
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "username": "user123",
    "role": "developer",
    "bio": "Software developer bio.",
    "profile_picture": null,
    "date_joined": "2026-05-26T12:00:00Z"
  }
  ```

#### Update User Profile
* **Endpoint**: `PATCH /api/auth/profile`
* **Permission**: `IsAuthenticated`
* **Description**: Partially update display metadata.
* **Request Body** (JSON / Multipart):
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `username` | String | No | Update display name. |
  | `bio` | String | No | Update description. |
  | `profile_picture` | File (Image) | No | Upload new avatar. |
* **Success Response (`200 OK`)**:
  *(Returns updated user profile JSON)*

---

### 3.2. Organizations App (`/api/organizations/`)

#### List Organizations
* **Endpoint**: `GET /api/organizations/`
* **Permission**: `IsAuthenticated`
* **Description**: Returns all organizations the current user belongs to where membership is active.
* **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 4,
      "name": "Acme Corp",
      "description": "Enterprise Solutions",
      "logo": null,
      "created_by": {
        "id": 1,
        "email": "admin@acme.com",
        "username": "admin"
      },
      "member_count": 5,
      "created_at": "2026-05-26T12:00:00Z"
    }
  ]
  ```

#### Create Organization
* **Endpoint**: `POST /api/organizations/`
* **Permission**: `IsAuthenticated`
* **Description**: Creates a new organization. The creator is automatically added as `Org Admin`.
* **Request Body** (JSON):
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `name` | String | **Yes** | Unique organization name. |
  | `description` | String | No | Optional summary. |
  | `logo` | File | No | Optional logo image. |
* **Success Response (`201 Created`)**:
  *(Returns created organization object JSON)*

#### Get Organization Detail
* **Endpoint**: `GET /api/organizations/<org_id>/`
* **Permission**: `IsOrgMember` (Must have active membership in the organization)
* **Success Response (`200 OK`)**:
  *(Returns organization object JSON)*

#### Partial Update Organization
* **Endpoint**: `PATCH /api/organizations/<org_id>/`
* **Permission**: `isOrgAdmin` (Must be an administrator of the organization)
* **Request Body** (JSON):
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `name` | String | No | New name. |
  | `description` | String | No | New description. |
* **Success Response (`200 OK`)**:
  *(Returns updated organization object JSON)*

#### Delete Organization
* **Endpoint**: `DELETE /api/organizations/<org_id>/`
* **Permission**: `isOrgAdmin`
* **Success Response (`204 No Content`)**:
  ```json
  {
    "message": "deleted successfully"
  }
  ```

#### List Organization Members
* **Endpoint**: `GET /api/organizations/<org_id>/members/`
* **Permission**: `IsOrgMember`
* **Description**: Returns all active members in the organization.
* **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 12,
      "user": {
        "id": 2,
        "email": "dev@acme.com",
        "username": "developer1"
      },
      "role": "developer",
      "joined_at": "2026-05-26T12:05:00Z",
      "is_active": true
    }
  ]
  ```

#### Invite Organization Member
* **Endpoint**: `POST /api/organizations/<org_id>/invite/`
* **Permission**: `isOrgAdmin`
* **Description**: Invites an existing system user to join the organization.
* **Request Body** (JSON):
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `email` | String (Email) | **Yes** | Email of the existing system user. |
  | `role` | String | No | Default: `'developer'`. Choice of `org_admin`, `project_manager`, `developer`, `viewer`. |
* **Success Response (`201 Created`)**:
  ```json
  {
    "message": "dev@acme.com added as developer."
  }
  ```

#### Remove Organization Member
* **Endpoint**: `DELETE /api/organizations/<org_id>/members/<user_id>/remove/`
* **Permission**: `isOrgAdmin`
* **Description**: Removes membership from the organization. Admins cannot remove themselves.
* **Success Response (`204 No Content`)**:
  ```json
  {
    "message": "Member removed successfully."
  }
  ```

---

### 3.3. Projects & Sprints App (`/api/organizations/<org_id>/projects/`)

#### List Projects
* **Endpoint**: `GET /api/organizations/<org_id>/projects/`
* **Permission**: `IsAuthenticated` (Limits results to `public` visibility projects OR projects where the user holds an active membership)
* **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 2,
      "name": "Devboard Rewrite",
      "description": "Porting codebase to NextJS",
      "status": "active",
      "visibility": "private",
      "start_date": "2026-06-01",
      "end_date": "2026-08-01",
      "created_by": {
        "id": 1,
        "email": "pm@acme.com",
        "username": "pm1"
      },
      "member_count": 3,
      "sprint_count": 1,
      "created_at": "2026-05-26T12:10:00Z",
      "updated_at": "2026-05-26T12:10:00Z"
    }
  ]
  ```

#### Create Project
* **Endpoint**: `POST /api/organizations/<org_id>/projects/`
* **Permission**: `isOrgMemberForProject` (Must be an active member of the hosting organization)
* **Description**: Create a project workspace. The creator is added as the `Project Manager` in project memberships.
* **Request Body** (JSON):
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `name` | String | **Yes** | Project name (must be unique inside this organization). |
  | `description` | String | No | Summary. |
  | `status` | String | No | Default: `'active'`. Choices: `active`, `on_hold`, `completed`, `archived`. |
  | `visibility` | String | No | Default: `'private'`. Choices: `public`, `private`. |
  | `start_date` | Date (YYYY-MM-DD) | No | Start date. |
  | `end_date` | Date (YYYY-MM-DD) | No | Projected end date. |
* **Success Response (`201 Created`)**:
  *(Returns created project object JSON)*

#### Get Project Detail
* **Endpoint**: `GET /api/organizations/<org_id>/projects/<project_id>/`
* **Permission**: `IsProjectMember`
* **Success Response (`200 OK`)**:
  *(Returns project object JSON)*

#### Partial Update Project
* **Endpoint**: `PATCH /api/organizations/<org_id>/projects/<project_id>/`
* **Permission**: `IsProjectManager` (Project manager membership role or organization admin)
* **Request Body** (JSON):
  *(Accepts any patchable project parameters)*
* **Success Response (`200 OK`)**:
  *(Returns updated project object JSON)*

#### Delete Project
* **Endpoint**: `DELETE /api/organizations/<org_id>/projects/<project_id>/`
* **Permission**: `IsProjectManager`
* **Success Response (`204 No Content`)**:
  ```json
  {
    "message": "Project deleted!"
  }
  ```

#### List Project Members
* **Endpoint**: `GET /api/organizations/<org_id>/projects/<project_id>/members/`
* **Permission**: `IsProjectMember`
* **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 4,
      "user": {
        "id": 3,
        "email": "dev2@acme.com",
        "username": "developer2"
      },
      "role": "developer",
      "joined_at": "2026-05-26T12:12:00Z"
    }
  ]
  ```

#### Add Project Member
* **Endpoint**: `POST /api/organizations/<org_id>/projects/<project_id>/members/`
* **Permission**: `IsProjectManager`
* **Description**: Adds an active organization member into this project workspace.
* **Request Body** (JSON):
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `email` | String (Email) | **Yes** | Member email. The user must be a member of the organization first. |
  | `role` | String | No | Default: `'developer'`. Choices: `project_manager`, `developer`, `viewer`. |
* **Success Response (`201 Created`)**:
  ```json
  {
    "message": "dev2@acme.com added as developer!"
  }
  ```

#### List Sprints
* **Endpoint**: `GET /api/organizations/<org_id>/projects/<project_id>/sprints/`
* **Permission**: `IsProjectMember`
* **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 1,
      "name": "Sprint 1 - Foundations",
      "goal": "Setup authentication routes and CI/CD pipelines.",
      "project": 2,
      "status": "active",
      "start_date": "2026-05-27",
      "end_date": "2026-06-10",
      "created_by": {
        "id": 1,
        "email": "pm@acme.com",
        "username": "pm1"
      },
      "task_count": 4,
      "created_at": "2026-05-26T12:15:00Z"
    }
  ]
  ```

#### Create Sprint
* **Endpoint**: `POST /api/organizations/<org_id>/projects/<project_id>/sprints/`
* **Permission**: `IsProjectManager`
* **Request Body** (JSON):
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `name` | String | **Yes** | Sprint name. |
  | `goal` | String | No | Sprint objective context. |
  | `status` | String | No | Default: `'planned'`. Choices: `planned`, `active`, `completed`. |
  | `start_date` | Date (YYYY-MM-DD) | No | Start date. |
  | `end_date` | Date (YYYY-MM-DD) | No | End date (must be after or equal to `start_date`). |
* **Success Response (`201 Created`)**:
  *(Returns created sprint object JSON)*

#### Get Sprint Detail
* **Endpoint**: `GET /api/organizations/<org_id>/projects/<project_id>/sprints/<sprint_id>/`
* **Permission**: `IsProjectMember`
* **Success Response (`200 OK`)**:
  *(Returns sprint object JSON)*

#### Update Sprint
* **Endpoint**: `PATCH /api/organizations/<org_id>/projects/<project_id>/sprints/<sprint_id>/`
* **Permission**: `IsProjectManager`
* **Success Response (`200 OK`)**:
  *(Returns updated sprint object JSON)*

#### Delete Sprint
* **Endpoint**: `DELETE /api/organizations/<org_id>/projects/<project_id>/sprints/<sprint_id>/`
* **Permission**: `IsProjectManager`
* **Success Response (`204 No Content`)**:
  ```json
  {
    "message": "Sprint deleted!"
  }
  ```

---

### 3.4. Tasks & Labels App (`/api/organizations/<org_id>/projects/<project_id>/`)

#### List Project Labels
* **Endpoint**: `GET /api/organizations/<org_id>/projects/<project_id>/labels/`
* **Permission**: `IsTaskProjectMember` (Must be member of the parent project)
* **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 1,
      "name": "Bug",
      "color": "#ff0000",
      "project": 2
    }
  ]
  ```

#### Create Project Label
* **Endpoint**: `POST /api/organizations/<org_id>/projects/<project_id>/labels/`
* **Permission**: `IsTaskProjectMember`
* **Request Body** (JSON):
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `name` | String | **Yes** | Tag name (must be unique inside the project workspace). |
  | `color` | String (Hex) | No | Default: `'#f5f5f5'`. Valid hex color representation (e.g. `#3b82f6`). |
* **Success Response (`201 Created`)**:
  *(Returns created label object JSON)*

#### List Project Tasks
* **Endpoint**: `GET /api/organizations/<org_id>/projects/<project_id>/tasks/`
* **Permission**: `IsTaskProjectMember`
* **Query Parameters** (Filters):
  - `sprint_id` (Integer / String): Filter tasks associated with a specific sprint ID. Pass the string `backlog` to retrieve tasks that are *not* assigned to any sprint.
  - `assigned_to` (Integer): Filter tasks assigned to a specific user ID.
  - `status` (String): Filter by task status (`backlog`, `todo`, `in_progress`, `in_review`, `done`).
  - `priority` (String): Filter by task priority (`low`, `medium`, `high`, `critical`).
  - `search` (String): Free text search matching against task `title` and `description` (case-insensitive).
* **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 42,
      "title": "Fix permission validation",
      "description": "Remove is_active validation from project membership query.",
      "project": 2,
      "sprint": 1,
      "assigned_to": {
        "id": 3,
        "email": "dev2@acme.com",
        "username": "developer2"
      },
      "created_by": {
        "id": 1,
        "email": "pm@acme.com",
        "username": "pm1"
      },
      "status": "done",
      "priority": "critical",
      "labels": [
        {
          "id": 1,
          "name": "Bug",
          "color": "#ff0000",
          "project": 2
        }
      ],
      "due_data": "2026-06-05",
      "order": 0,
      "created_at": "2026-05-26T12:20:00Z",
      "updated_at": "2026-05-26T12:35:00Z"
    }
  ]
  ```

#### Create Project Task
* **Endpoint**: `POST /api/organizations/<org_id>/projects/<project_id>/tasks/`
* **Permission**: `IsTaskProjectMember`
* **Request Body** (JSON):
  | Field | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `title` | String | **Yes** | Task summary. |
  | `description` | String | No | Detailed task context. |
  | `sprint_id` | Integer | No | Sprint ID connection (must belong to the same project). |
  | `assigned_to_id` | Integer | No | User ID of assignee (must hold membership in this project). |
  | `status` | String | No | Default: `'backlog'`. Choices: `backlog`, `todo`, `in_progress`, `in_review`, `done`. |
  | `priority` | String | No | Default: `'medium'`. Choices: `low`, `medium`, `high`, `critical`. |
  | `label_ids` | Array of Ints | No | IDs of project labels to associate with this task. |
  | `due_data` | Date (YYYY-MM-DD) | No | Due date of the task. |
  | `order` | Integer | No | Board task layout sequence order. |
* **Success Response (`201 Created`)**:
  *(Returns created task object JSON)*

#### Get Task Detail
* **Endpoint**: `GET /api/organizations/<org_id>/projects/<project_id>/tasks/<task_id>/`
* **Permission**: `CanManageTask` (Must be project member)
* **Success Response (`200 OK`)**:
  *(Returns task object JSON)*

#### Update Task
* **Endpoint**: `PATCH /api/organizations/<org_id>/projects/<project_id>/tasks/<task_id>/`
* **Permission**: `CanManageTask`
* **Description**: Partially updates a task. Enforces role-based rules:
  1. **Project Managers** (or Org Admins) can update any field.
  2. **Developers** can *only* update the task `status`. If a developer tries to change other fields, they are ignored or rejected. The status update must conform to the allowed workflow transitions:
     - `backlog` &rarr; `todo`
     - `todo` &rarr; `in_progress`
     - `in_progress` &rarr; `in_review` or `todo`
     - `in_review` &rarr; `done` or `in_progress`
     - `done` &rarr; `in_review`
  3. **Viewers** are rejected with a permission error.
* **Request Body** (JSON):
  *(Accepts any patchable task parameters. If developer, only `status` is evaluated)*
* **Success Response (`200 OK`)**:
  *(Returns updated task object JSON)*

#### Delete Task
* **Endpoint**: `DELETE /api/organizations/<org_id>/projects/<project_id>/tasks/<task_id>/`
* **Permission**: `CanManageTask` (Only Project Managers can delete tasks)
* **Success Response (`204 No Content`)**:
  ```json
  {
    "message": "Task deleted!"
  }
  ```
