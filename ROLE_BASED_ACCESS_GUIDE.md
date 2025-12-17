# Role-Based Access Control Guide for CrimeLens

## Available Roles

The system supports the following roles (in order of permissions):

1. **ADMIN** - Full system access, can view all reports and manage everything
2. **DEPARTMENT_HEAD** / **DEPARTMENT** - Can manage their department's reports and assign staff
3. **DEPARTMENT_STAFF** - Can view and update only assigned reports
4. **USER** - Can submit reports and track their own reports
5. **MODERATOR** - (Available but not commonly used)

---

## 1. Checking User Roles in Components

### Using NextAuth Session Hook

```typescript
'use client';

import { useSession } from 'next-auth/react';

export default function MyComponent() {
  const { data: session, status } = useSession();
  const role = (session?.user as any)?.role;

  if (status === 'loading') {
    return <div>Loading...</div>;
  }

  if (status === 'unauthenticated') {
    return <div>Please sign in</div>;
  }

  // Check specific role
  if (role === 'ADMIN') {
    return <div>Admin content</div>;
  }

  // Check multiple roles
  if (['DEPARTMENT_HEAD', 'DEPARTMENT'].includes(role)) {
    return <div>Department content</div>;
  }

  return <div>Regular user content</div>;
}
```

### Using useMemo for Permission Checks

```typescript
import { useMemo } from 'react';
import { useSession } from 'next-auth/react';

export default function ReportPage() {
  const { data: session } = useSession();
  const role = (session?.user as any)?.role;

  const canUpdateStatus = useMemo(() => {
    if (!role) return false;
    return ['ADMIN', 'DEPARTMENT_HEAD', 'DEPARTMENT_STAFF'].includes(role);
  }, [role]);

  const canAssignStaff = useMemo(() => {
    if (!role) return false;
    return ['ADMIN', 'DEPARTMENT_HEAD', 'DEPARTMENT'].includes(role);
  }, [role]);

  return (
    <div>
      {canUpdateStatus && <button>Update Status</button>}
      {canAssignStaff && <button>Assign Staff</button>}
    </div>
  );
}
```

---

## 2. Protecting Routes/Pages

### Client-Side Route Protection

```typescript
'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function AdminPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    } else if (status === 'authenticated' && session?.user?.role !== 'ADMIN') {
      router.push('/dashboard'); // Redirect non-admins
    }
  }, [status, session, router]);

  if (status === 'loading' || (status === 'authenticated' && session?.user?.role !== 'ADMIN')) {
    return <div>Loading...</div>;
  }

  return <div>Admin Dashboard</div>;
}
```

### Multiple Roles Protection

```typescript
'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

const allowedRoles = new Set(['DEPARTMENT_HEAD', 'DEPARTMENT']);

export default function DepartmentPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    } else if (status === 'authenticated' && !allowedRoles.has(session?.user?.role as any)) {
      router.push('/dashboard');
    }
  }, [status, session, router]);

  if (status === 'loading' || (status === 'authenticated' && !allowedRoles.has(session?.user?.role as any))) {
    return <div>Loading...</div>;
  }

  return <div>Department Dashboard</div>;
}
```

### Server-Side Route Protection (API Routes)

```typescript
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const session = await getServerSession(authOptions);

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const role = (session.user as any)?.role;

  if (role !== 'ADMIN') {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }

  // Admin-only logic here
  return NextResponse.json({ data: 'Admin data' });
}
```

---

## 3. Creating Users with Different Roles

### Method 1: Using the Signup API (for USER role)

The regular signup endpoint creates users with `USER` role by default:

```typescript
// POST /api/auth/signup
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

### Method 2: Direct Database Insert (for Admin/Department roles)

You can create users directly in the database or via a script:

```typescript
import sql from '@/lib/db';
import bcrypt from 'bcryptjs';

async function createAdminUser() {
  const hashedPassword = await bcrypt.hash('admin123', 10);
  
  const admin = sql.createUser({
    email: 'admin@example.com',
    name: 'Admin User',
    password: hashedPassword,
    role: 'ADMIN'
  });
  
  return admin;
}

async function createDepartmentHead() {
  const hashedPassword = await bcrypt.hash('dept123', 10);
  
  // First, get or create department
  const department = sql.getDepartmentByName('Police');
  
  const head = sql.createUser({
    email: 'police.head@example.com',
    name: 'Police Department Head',
    password: hashedPassword,
    role: 'DEPARTMENT_HEAD',
    departmentId: department?.id
  });
  
  return head;
}
```

### Method 3: Using the Seed Script

Run the seed script to create test users with all roles:

```bash
cd crime_lens
npm run seed
```

This creates:
- **Admin**: `admin@gmail.com` / `adminadmin`
- **Regular User**: `user@gmail.com` / `useruser`
- **Department accounts**: Various department emails (see seed.ts)
- **Department Heads**: `{department-slug}.head@crimelens.local`
- **Department Staff**: `{department-slug}.staff{1-3}@crimelens.local`

---

## 4. Role-Based Dashboard Routing

The main dashboard automatically routes users based on their role:

```typescript
// crime_lens/src/app/dashboard/page.tsx
useEffect(() => {
  if (status === 'authenticated') {
    const role = (session?.user as any)?.role;

    if (role === 'ADMIN') {
      router.push('/dashboard/admin');
    } else if (role === 'DEPARTMENT_HEAD' || role === 'DEPARTMENT') {
      router.push('/dashboard/department');
    } else if (role === 'DEPARTMENT_STAFF') {
      router.push('/dashboard/staff');
    } else {
      router.push('/dashboard/user');
    }
  }
}, [status, session, router]);
```

---

## 5. Role-Based Data Filtering

### Filter Reports by Role

```typescript
// Admin sees all reports
if (role === 'ADMIN') {
  const reports = await fetch('/api/reports?all=true');
}

// Department sees only their department's reports
if (role === 'DEPARTMENT_HEAD' || role === 'DEPARTMENT') {
  const reports = await fetch(`/api/reports?departmentName=${department}`);
}

// Staff sees only assigned reports
if (role === 'DEPARTMENT_STAFF') {
  const reports = await fetch(`/api/reports?reporterUserId=${userId}`);
}

// User sees only their own reports
if (role === 'USER') {
  const reports = await fetch(`/api/reports?reporterUserId=${userId}`);
}
```

---

## 6. Common Role-Based Patterns

### Pattern 1: Conditional Rendering

```typescript
{role === 'ADMIN' && (
  <button onClick={deleteReport}>Delete Report</button>
)}

{['DEPARTMENT_HEAD', 'DEPARTMENT'].includes(role) && (
  <button onClick={assignStaff}>Assign Staff</button>
)}

{role === 'DEPARTMENT_STAFF' && (
  <button onClick={updateStatus}>Update Status</button>
)}
```

### Pattern 2: Permission Hooks

```typescript
function usePermissions() {
  const { data: session } = useSession();
  const role = (session?.user as any)?.role;

  return {
    isAdmin: role === 'ADMIN',
    isDepartmentHead: ['DEPARTMENT_HEAD', 'DEPARTMENT'].includes(role),
    isStaff: role === 'DEPARTMENT_STAFF',
    isUser: role === 'USER',
    canManageReports: ['ADMIN', 'DEPARTMENT_HEAD', 'DEPARTMENT'].includes(role),
    canAssignStaff: ['ADMIN', 'DEPARTMENT_HEAD', 'DEPARTMENT'].includes(role),
    canUpdateStatus: ['ADMIN', 'DEPARTMENT_HEAD', 'DEPARTMENT', 'DEPARTMENT_STAFF'].includes(role),
  };
}

// Usage
const { canAssignStaff, isAdmin } = usePermissions();
```

### Pattern 3: Role-Based Component Wrapper

```typescript
function RoleGuard({ 
  allowedRoles, 
  children, 
  fallback = null 
}: { 
  allowedRoles: string[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}) {
  const { data: session } = useSession();
  const role = (session?.user as any)?.role;

  if (!role || !allowedRoles.includes(role)) {
    return fallback;
  }

  return <>{children}</>;
}

// Usage
<RoleGuard allowedRoles={['ADMIN', 'DEPARTMENT_HEAD']}>
  <AdminPanel />
</RoleGuard>
```

---

## 7. Accessing Role Information

### In Client Components

```typescript
const { data: session } = useSession();
const role = (session?.user as any)?.role;
const departmentId = (session?.user as any)?.departmentId;
const department = (session?.user as any)?.department;
```

### In Server Components/API Routes

```typescript
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

const session = await getServerSession(authOptions);
const role = (session?.user as any)?.role;
const userId = (session?.user as any)?.id;
```

---

## 8. Example: Complete Protected Page

```typescript
'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect, useMemo } from 'react';

const allowedRoles = ['ADMIN', 'DEPARTMENT_HEAD', 'DEPARTMENT'];

export default function ProtectedReportPage({ reportId }: { reportId: string }) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const role = (session?.user as any)?.role;

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    } else if (status === 'authenticated' && !allowedRoles.includes(role)) {
      router.push('/dashboard');
    }
  }, [status, session, router, role]);

  const canUpdateStatus = useMemo(() => {
    return allowedRoles.includes(role);
  }, [role]);

  const canAssignStaff = useMemo(() => {
    return ['ADMIN', 'DEPARTMENT_HEAD', 'DEPARTMENT'].includes(role);
  }, [role]);

  if (status === 'loading' || !allowedRoles.includes(role)) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Report Details</h1>
      {canUpdateStatus && <button>Update Status</button>}
      {canAssignStaff && <button>Assign Staff</button>}
    </div>
  );
}
```

---

## 9. Testing Different Roles

### Quick Test Users (from seed script)

1. **Admin Access**:
   - Email: `admin@gmail.com`
   - Password: `adminadmin`
   - Access: All dashboards and reports

2. **Department Head**:
   - Email: `roads-public-works-pwd.head@crimelens.local`
   - Password: `roadspublicworkspwdHead@123`
   - Access: Department dashboard, can assign staff

3. **Department Staff**:
   - Email: `roads-public-works-pwd.staff1@crimelens.local`
   - Password: `roadspublicworkspwdStaff1@123`
   - Access: Staff dashboard, assigned reports only

4. **Regular User**:
   - Email: `user@gmail.com`
   - Password: `useruser`
   - Access: User dashboard, own reports only

---

## 10. Best Practices

1. **Always check authentication first**, then role
2. **Use consistent role checking patterns** across the app
3. **Protect both client and server side** when needed
4. **Use TypeScript types** for role safety
5. **Create reusable permission hooks** for common checks
6. **Log unauthorized access attempts** for security
7. **Test with different roles** before deploying

---

## Summary

Role-based access in CrimeLens works through:
- **NextAuth session** containing user role information
- **Client-side checks** using `useSession()` hook
- **Server-side checks** using `getServerSession()`
- **Automatic routing** based on role in dashboard
- **Database-level role storage** in User table

The role is stored in the session token and available throughout the application for access control decisions.

