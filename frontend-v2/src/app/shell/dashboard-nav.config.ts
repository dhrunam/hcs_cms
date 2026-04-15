/** Route prefix (first URL segment) → shell metadata and primary nav. */
export type DashboardAreaKey =
  | 'superadmin'
  | 'advocate'
  | 'party'
  | 'judges'
  | 'reader'
  | 'listing-officers'
  | 'scrutiny-officers'
  | 'steno';

export type NavIcon = 'home' | 'user' | 'management';

export interface ShellNavChild {
  label: string;
  /** Path segments from app root, e.g. ['admin','users'] */
  link: string[];
}

export interface ShellNavItem {
  label: string;
  /** Top-level route (omit when using `children` only). */
  link?: string[];
  icon?: NavIcon;
  /** Collapsible sub-menu (e.g. Super Admin Management). */
  children?: ShellNavChild[];
}

export interface ShellAreaConfig {
  areaKey: DashboardAreaKey;
  /** Shown in shell header */
  title: string;
  nav: ShellNavItem[];
}

function areaNav(prefix: DashboardAreaKey): ShellNavItem[] {
  return [
    { label: 'Dashboard', link: [prefix, 'dashboard', 'home'], icon: 'home' },
    { label: 'Profile', link: [prefix, 'dashboard', 'profile'], icon: 'user' },
  ];
}

function superadminNav(): ShellNavItem[] {
  return [
    { label: 'Dashboard', link: ['superadmin', 'dashboard', 'home'], icon: 'home' },
    {
      label: 'Management',
      icon: 'management',
      children: [
        { label: 'Users', link: ['admin', 'users'] },
        { label: 'Roles', link: ['admin', 'roles'] },
        { label: 'Permissions', link: ['admin', 'permissions'] },
      ],
    },
    { label: 'Profile', link: ['superadmin', 'dashboard', 'profile'], icon: 'user' },
  ];
}

export const DASHBOARD_AREA_CONFIG: Record<DashboardAreaKey, ShellAreaConfig> = {
  superadmin: {
    areaKey: 'superadmin',
    title: 'Super Admin',
    nav: superadminNav(),
  },
  advocate: {
    areaKey: 'advocate',
    title: 'Advocate',
    nav: areaNav('advocate'),
  },
  party: {
    areaKey: 'party',
    title: 'Party in person',
    nav: areaNav('party'),
  },
  judges: {
    areaKey: 'judges',
    title: 'Judge',
    nav: areaNav('judges'),
  },
  reader: {
    areaKey: 'reader',
    title: 'Reader',
    nav: areaNav('reader'),
  },
  'listing-officers': {
    areaKey: 'listing-officers',
    title: 'Listing officer',
    nav: areaNav('listing-officers'),
  },
  'scrutiny-officers': {
    areaKey: 'scrutiny-officers',
    title: 'Scrutiny officer',
    nav: areaNav('scrutiny-officers'),
  },
  steno: {
    areaKey: 'steno',
    title: 'Steno',
    nav: areaNav('steno'),
  },
};
