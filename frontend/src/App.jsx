
import React, { useEffect, useState } from "react";
import {
  Routes,
  Route,
  Navigate,
  NavLink,
  useLocation,
} from "react-router-dom";

import {
  BookOpen,
  LayoutDashboard,
  Files,
  FileText,
  Layers,
  ClipboardCheck,
  Brain,
  ChartNoAxesCombined,
  LibraryBig,
  Sun,
  Moon,
  GraduationCap,
} from "lucide-react";

import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Summaries from "./pages/Summaries";
import Flashcards from "./pages/Flashcards";
import Quizzes from "./pages/Quizzes";
import Tutor from "./pages/Tutor";
import Library from "./pages/Library";
import Progress from "./pages/Progress";

const nav = [
  ["/", "Dashboard", LayoutDashboard],
  ["/upload", "Upload material", Files],
  ["/summaries", "Summaries", FileText],
  ["/flashcards", "Flashcards", Layers],
  ["/quizzes", "Practice quizzes", ClipboardCheck],
  ["/tutor", "AI tutor", Brain],
  ["/library", "Study library", LibraryBig],
  ["/progress", "Study progress", ChartNoAxesCombined],
];

function Navigation() {
  return (
    <>
      {nav.map(([to, label, Icon]) => (
        <NavLink
          key={to}
          to={to}
          end={to === "/"}
          className={({ isActive }) =>
            "nav-link " + (isActive ? "active" : "")
          }
        >
          <Icon size={18} />
          <span className="nav-label">{label}</span>
        </NavLink>
      ))}
    </>
  );
}

export function useNotify() {
  const [toast, setToast] = useState("");

  const notify = (message) => {
    setToast(message);
    setTimeout(() => setToast(""), 3800);
  };

  return { toast, notify };
}

export default function App() {
  const [dark, setDark] = useState(false);
  const location = useLocation();

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
  }, [dark]);

  return (
    <div className="app-shell">
      {/* Main sidebar */}
      <aside className="sidebar">
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "0 10px 28px",
          }}
        >
          <div
            style={{
              background: "#5b5bd6",
              color: "white",
              borderRadius: 12,
              padding: 9,
            }}
          >
            <GraduationCap size={22} />
          </div>

          <div className="brand-name">
            <b style={{ fontSize: 16 }}>Study Buddy</b>
            <div className="muted" style={{ fontSize: 11 }}>
              Your AI learning space
            </div>
          </div>
        </div>

        <div
          className="eyebrow"
          style={{ padding: "0 13px 10px" }}
        >
          Workspace
        </div>

        <Navigation />

        <div
          className="side-footer"
          style={{
            marginTop: "auto",
            padding: 12,
            background: "#f7f7ff",
            borderRadius: 14,
          }}
        >
          <div
            style={{
              display: "flex",
              gap: 8,
              alignItems: "center",
            }}
          >
            <Brain size={18} color="#5b5bd6" />
            <b style={{ fontSize: 13 }}>Learn smarter</b>
          </div>

          <p
            className="muted"
            style={{ fontSize: 12, lineHeight: 1.5 }}
          >
            Turn your notes into a study plan with AI.
          </p>
        </div>
      </aside>

      {/* Main content */}
      <div className="main-area">
        {/* Mobile header only — no duplicate navigation */}
        <header className="mobile-top">
          <b>
            <BookOpen
              size={17}
              style={{
                display: "inline",
                verticalAlign: "middle",
                marginRight: 7,
              }}
            />
            Study Buddy
          </b>

          <button
            className="btn btn-secondary"
            onClick={() => setDark((previous) => !previous)}
            aria-label="Toggle theme"
          >
            {dark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </header>

        {/* Desktop theme toggle */}
        <div
          className="desktop-theme"
          style={{
            display: "flex",
            justifyContent: "flex-end",
            padding: "14px 34px 0",
          }}
        >
          <button
            className="btn btn-secondary"
            onClick={() => setDark((previous) => !previous)}
          >
            {dark ? <Sun size={16} /> : <Moon size={16} />}
            {dark ? " Light mode" : " Dark mode"}
          </button>
        </div>

        {/* Page routes */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/summaries" element={<Summaries />} />
          <Route path="/flashcards" element={<Flashcards />} />
          <Route path="/quizzes" element={<Quizzes />} />
          <Route path="/tutor" element={<Tutor />} />
          <Route path="/library" element={<Library />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
}
