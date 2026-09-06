import { createContext, useContext, useEffect, useState } from "react";
import { authApi } from "../api/endpoints";

const AuthContext = createContext(null);

const STAFF_ROLES = [
  "admin",
  "general_manager",
  "manager",
  "billing_person",
  "room_servant",
  "food_servant",
  "chef",
];

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("hrm_user");
    return stored ? JSON.parse(stored) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("hrm_token");
    if (!token) {
      setLoading(false);
      return;
    }
    authApi
      .me()
      .then((res) => {
        const merged = { ...user, ...res.data };
        setUser(merged);
        localStorage.setItem("hrm_user", JSON.stringify(merged));
      })
      .catch(() => {
        localStorage.removeItem("hrm_token");
        localStorage.removeItem("hrm_user");
        setUser(null);
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function login(username, password) {
    const res = await authApi.login(username, password);
    const data = res.data;
    localStorage.setItem("hrm_token", data.access_token);
    const userData = { username: data.username, role: data.role, display_name: data.display_name };
    localStorage.setItem("hrm_user", JSON.stringify(userData));
    setUser(userData);
    return userData;
  }

  function logout() {
    localStorage.removeItem("hrm_token");
    localStorage.removeItem("hrm_user");
    setUser(null);
  }

  const isStaff = !!user && STAFF_ROLES.includes(user.role);
  const isAdmin = user?.role === "admin";
  const isCustomer = user?.role === "customer";

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isStaff, isAdmin, isCustomer }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
