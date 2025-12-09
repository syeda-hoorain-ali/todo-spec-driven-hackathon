# Data Model: Authentication System

## User Entity
**Description**: Represents a registered user in the system

**Fields**:
- `id` (UUID, Primary Key): Unique identifier for the user
- `email` (String, Unique, Indexed): User's email address, validated for proper format
- `hashed_password` (String): bcrypt-hashed password
- `is_active` (Boolean, Default: true): Account status flag
- `is_verified` (Boolean, Default: false): Email verification status
- `created_at` (DateTime, Indexed): Account creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `last_login_at` (DateTime, Nullable): Timestamp of last successful login
- `failed_login_attempts` (Integer, Default: 0): Count of consecutive failed login attempts
- `locked_until` (DateTime, Nullable): Timestamp until which account is locked (for rate limiting)

**Relationships**:
- One-to-Many: User has many Sessions
- One-to-Many: User has many PasswordResetTokens

**Validation Rules**:
- Email must follow standard email format
- Email must be unique across all users
- Password must meet moderate policy (8+ chars, mixed case or number)
- Email length must be between 5 and 255 characters

## Session Entity
**Description**: Represents an active user session with JWT token information

**Fields**:
- `id` (UUID, Primary Key): Unique identifier for the session
- `user_id` (UUID, Foreign Key): Reference to the associated user
- `session_token` (String, Indexed): JWT session token identifier
- `refresh_token` (String, Indexed): Refresh token for session renewal
- `expires_at` (DateTime, Indexed): Session expiration timestamp
- `created_at` (DateTime): Session creation timestamp
- `last_accessed_at` (DateTime): Last access timestamp
- `ip_address` (String, Nullable): IP address of the session origin
- `user_agent` (String, Nullable): User agent string of the client

**Relationships**:
- Many-to-One: Session belongs to one User
- Index: Composite index on (user_id, expires_at) for efficient queries

**Validation Rules**:
- Session must be associated with a valid user
- Session tokens must be unique
- Expiration time must be in the future
- Cannot have more than 10 concurrent active sessions per user (configurable)

## PasswordResetToken Entity
**Description**: Represents a temporary token for password reset functionality

**Fields**:
- `id` (UUID, Primary Key): Unique identifier for the token
- `user_id` (UUID, Foreign Key): Reference to the associated user
- `token` (String, Unique, Indexed): The reset token value (randomly generated)
- `expires_at` (DateTime, Indexed): Token expiration timestamp (typically 1 hour)
- `used_at` (DateTime, Nullable): Timestamp when token was used (null if unused)
- `created_at` (DateTime): Token creation timestamp

**Relationships**:
- Many-to-One: PasswordResetToken belongs to one User

**Validation Rules**:
- Token must be associated with a valid user
- Token must be unique
- Token must not be expired when used
- Token can only be used once
- Only one active token per user at a time

## State Transitions

### User Account States:
1. **Pending** → **Active**: After successful registration and optional email verification
2. **Active** → **Locked**: After exceeding failed login attempts (5 attempts in 15 minutes)
3. **Locked** → **Active**: After lockout period expires or admin intervention
4. **Active** → **Inactive**: When user requests account deletion (soft delete)
5. **Inactive** → **Deleted**: After 30-day retention period (hard delete)

### Session States:
1. **Active** → **Expired**: When expiration time is reached
2. **Active** → **Revoked**: When user signs out or refresh token is invalidated

## Indexing Strategy
- User email: B-tree index for fast lookups during authentication
- User created_at: B-tree index for temporal queries
- Session user_id and expires_at: Composite index for active session queries
- Session_token: B-tree index for token validation
- PasswordResetToken token: B-tree index for reset token lookup
- PasswordResetToken expires_at: B-tree index for cleanup queries

## Constraints
- Email uniqueness is enforced at the database level
- Password policies are enforced at the application level
- Concurrent session limits are enforced at the application level
- Soft deletion preserves data for 30 days before permanent removal
- All timestamps are stored in UTC
