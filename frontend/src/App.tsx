import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import ErrorBoundary from "./components/ErrorBoundary";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import RobotsPage from "./pages/RobotsPage";
import SensorsPage from "./pages/SensorsPage";
import FaultsPage from "./pages/FaultsPage";
import CommandsPage from "./pages/CommandsPage";
import TicketsPage from "./pages/TicketsPage";
import ConfigsPage from "./pages/ConfigsPage";
import AuditsPage from "./pages/AuditsPage";
import AdminPage from "./pages/AdminPage";
import MainLayout from "./layouts/MainLayout";

function hasToken(): boolean {
  return Boolean(localStorage.getItem("access_token"));
}

function Protected({ children }: { children: React.ReactNode }) {
  if (!hasToken()) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <Protected>
                <MainLayout />
              </Protected>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="robots" element={<RobotsPage />} />
            <Route path="sensors" element={<SensorsPage />} />
            <Route path="faults" element={<FaultsPage />} />
            <Route path="commands" element={<CommandsPage />} />
            <Route path="tickets" element={<TicketsPage />} />
            <Route path="configs" element={<ConfigsPage />} />
            <Route path="audits" element={<AuditsPage />} />
            <Route path="admin" element={<AdminPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
