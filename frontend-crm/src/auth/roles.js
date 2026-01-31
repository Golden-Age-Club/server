export const ROLES = {
  SUPER_ADMIN: "super_admin",
  OPERATOR: "operator",
  FINANCE: "finance",
  RISK: "risk",
  SUPPORT: "support",
};

// Frontend mapping for what each role can access (can later come from backend).
export const ROLE_PERMISSIONS = {
  [ROLES.SUPER_ADMIN]: [
    "dashboard",
    "users",
    "finance",
    "bets",
    "games",
    "vip",
    "risk",
    "promotions",
    "reports",
    "system",
  ],
  [ROLES.OPERATOR]: ["dashboard", "users", "bets", "games", "vip", "promotions", "reports"],
  [ROLES.FINANCE]: ["dashboard", "finance", "reports"],
  [ROLES.RISK]: ["dashboard", "users", "risk", "reports"],
  [ROLES.SUPPORT]: ["dashboard", "users"],
};

export const DEFAULT_ROLE = ROLES.SUPER_ADMIN;

