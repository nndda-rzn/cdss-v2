# Admin Dashboard & Role-Specific Sidebar Plan

## Problem
Admin users see both Clinical and Admin sections in the sidebar. Admin should only see admin pages, not clinical pages.

## Goal
- Admin sidebar: Admin section only (Users, Facilities)
- Clinical sidebar: Clinical section only (Dashboard, Patients)
- Admin gets own dashboard page at `/admin`
- Login redirects admin to `/admin`, others to `/dashboard`

## Changes

### 1. SidebarNav.tsx
- Admin → `[ADMIN_SECTION]`
- Others → `BASE_SECTIONS`

### 2. AdminDashboardPage (NEW)
- Route: `/admin`
- Stats: total users, total facilities (from API)
- Quick links to Users & Facilities

### 3. App.tsx
- Add `/admin` route with AdminDashboardRoute
- Default redirect: admin → `/admin`, others → `/dashboard`

### 4. Login redirect
- After successful login, check role from JWT
- Admin → navigate to `/admin`
- Others → navigate to `/dashboard`
