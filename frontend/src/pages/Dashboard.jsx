
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Brain,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  ClipboardCheck,
  Clock3,
  FileText,
  Layers,
  LoaderCircle,
  Plus,
  Sparkles,
  Target,
  UploadCloud,
} from "lucide-react";
import {
  BarChart,
  Bar,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import api from "../services/api";

const quickActions = [
  {
    title: "Create a summary",
    description: "Turn a chapter into revision notes.",
    icon: FileText,
    href: "/summaries",
    tone: "violet",
  },
  {
    title: "Review flashcards",
    description: "Remember important concepts.",
    icon: Layers,
    href: "/flashcards",
    tone: "orange",
  },
  {
    title: "Practice a quiz",
    description: "Test your understanding.",
    icon: ClipboardCheck,
    href: "/quizzes",
    tone: "blue",
  },
];

const numberFormat = new Intl.NumberFormat();

function formatDate(value) {
  if (!value) return "Recently added";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "Recently added";

  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function MetricCard({ title, value, caption, icon: Icon, tone }) {
  return (
    <article className="card dash-metric">
      <div className="dash-metric-top">
        <span className="dash-muted">{title}</span>
        <span className={`dash-icon dash-icon-${tone}`}>
          <Icon size={19} />
        </span>
      </div>

      <div className="dash-metric-value">
        {typeof value === "number" ? numberFormat.format(value) : value}
      </div>

      <p className="dash-metric-caption">{caption}</p>
    </article>
  );
}

function SectionHeading({ eyebrow, title, action, to }) {
  return (
    <div className="dash-section-heading">
      <div>
        {eyebrow && <p className="dash-eyebrow">{eyebrow}</p>}
        <h2>{title}</h2>
      </div>

      {action && to && (
        <Link className="dash-text-link" to={to}>
          {action}
          <ArrowRight size={15} />
        </Link>
      )}
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statsError, setStatsError] = useState("");
  const [progressError, setProgressError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      setLoading(true);

      const [statsResult, progressResult] = await Promise.allSettled([
        api.get("/api/dashboard/stats"),
        api.get("/api/progress"),
      ]);

      if (!active) return;

      if (statsResult.status === "fulfilled") {
        setStats(statsResult.value.data);
        setStatsError("");
      } else {
        setStatsError(
          statsResult.reason?.userMessage ||
            "Could not load your dashboard statistics."
        );
      }

      if (progressResult.status === "fulfilled") {
        setProgress(progressResult.value.data);
        setProgressError("");
      } else {
        setProgressError(
          progressResult.reason?.userMessage ||
            "Could not load your quiz performance."
        );
      }

      setLoading(false);
    }

    loadDashboard();

    return () => {
      active = false;
    };
  }, []);

  const documents = stats?.recent_documents || [];
  const totals = progress?.totals || {};

  const metrics = [
    {
      title: "Documents",
      value: stats?.documents ?? 0,
      caption: "Study materials saved",
      icon: BookOpen,
      tone: "violet",
    },
    {
      title: "AI summaries",
      value: stats?.summaries ?? 0,
      caption: "Revision notes created",
      icon: FileText,
      tone: "green",
    },
    {
      title: "Flashcards",
      value: stats?.flashcards ?? 0,
      caption: "Cards in your collection",
      icon: Layers,
      tone: "orange",
    },
    {
      title: "Quiz attempts",
      value: stats?.quiz_attempts ?? 0,
      caption: "Practice sessions completed",
      icon: ClipboardCheck,
      tone: "blue",
    },
  ];

  const quizScores = (progress?.quiz_scores || []).slice(-7).map(
    (attempt, index) => ({
      attempt: `Quiz ${index + 1}`,
      score: Number(attempt.percentage) || 0,
    })
  );

  const averageScore = Number(stats?.average_score) || 0;
  const recentActivity = stats?.recent_activity || [];

  return (
    <main className="page dash-page">
      <header className="dash-header">
        <div>
          <div className="dash-eyebrow">
            <Sparkles size={14} />
            YOUR LEARNING WORKSPACE
          </div>

          <h1 className="dash-title">Make learning feel easier.</h1>

          <p className="dash-subtitle">
            Your study materials, AI tools, and learning progress — all in
            one place.
          </p>
        </div>

        <Link to="/upload" className="btn btn-primary dash-upload-button">
          <Plus size={18} />
          Upload material
        </Link>
      </header>

      {statsError && (
        <div className="dash-alert" role="alert">
          <Activity size={18} />
          <div>
            <strong>Statistics could not be loaded.</strong>
            <p>{statsError} Make sure the FastAPI backend is running.</p>
          </div>
        </div>
      )}

      {loading && (
        <div className="dash-loading" role="status">
          <LoaderCircle size={19} className="dash-spin" />
          Loading your study workspace...
        </div>
      )}

      <section className="dash-hero">
        <div className="dash-hero-content">
          <div className="dash-hero-label">
            <span className="dash-hero-sparkle">
              <Sparkles size={15} />
            </span>
            YOUR PERSONAL AI STUDY ASSISTANT
          </div>

          <h2>One document. Many ways to learn.</h2>

          <p>
            Upload your lecture notes or a chapter. Create summaries, generate
            flashcards, and prepare for quizzes from your own study material.
          </p>

          <Link to="/upload" className="dash-hero-button">
            <UploadCloud size={18} />
            Upload your first document
            <ArrowUpRight size={17} />
          </Link>
        </div>

        <div className="dash-hero-art" aria-hidden="true">
          <div className="dash-art-orbit dash-art-orbit-one" />
          <div className="dash-art-orbit dash-art-orbit-two" />

          <div className="dash-art-card dash-art-card-back">
            <Layers size={23} />
            <span>Flashcards</span>
          </div>

          <div className="dash-art-card dash-art-card-front">
            <div className="dash-art-document-icon">
              <FileText size={28} />
            </div>
            <div className="dash-art-lines">
              <span />
              <span />
              <span />
            </div>
            <div className="dash-art-ai">
              <Sparkles size={15} />
              AI ready
            </div>
          </div>

          <div className="dash-art-bubble">
            <CheckCircle2 size={17} />
            Study smarter
          </div>
        </div>
      </section>

      <section className="dash-metrics-grid" aria-label="Study statistics">
        {metrics.map((metric) => (
          <MetricCard key={metric.title} {...metric} />
        ))}
      </section>

      <section className="dash-main-grid">
        <div className="dash-panel dash-quick-panel">
          <SectionHeading
            eyebrow="MAKE PROGRESS"
            title="What would you like to study?"
          />

          <div className="dash-action-list">
            {quickActions.map(({ title, description, icon: Icon, href, tone }) => (
              <Link
                key={href}
                to={href}
                className="dash-action-item"
              >
                <span className={`dash-action-icon dash-icon-${tone}`}>
                  <Icon size={20} />
                </span>

                <span className="dash-action-copy">
                  <strong>{title}</strong>
                  <span>{description}</span>
                </span>

                <ChevronRight className="dash-action-chevron" size={19} />
              </Link>
            ))}
          </div>

          <Link to="/upload" className="dash-upload-strip">
            <span className="dash-upload-strip-icon">
              <UploadCloud size={20} />
            </span>
            <span>
              <strong>Have new lecture notes?</strong>
              <small>Upload a PDF, DOCX, or TXT file.</small>
            </span>
            <ArrowRight size={18} />
          </Link>
        </div>

        <div className="dash-panel dash-chart-panel">
          <SectionHeading
            eyebrow="YOUR PERFORMANCE"
            title="Quiz progress"
            action="Full report"
            to="/progress"
          />

          <div className="dash-score-summary">
            <div>
              <span className="dash-muted">Average quiz score</span>
              <div className="dash-average-score">
                {averageScore}
                <span>%</span>
              </div>
            </div>

            <span className="dash-score-icon">
              <Target size={23} />
            </span>
          </div>

          {progressError && (
            <p className="dash-inline-error">{progressError}</p>
          )}

          {quizScores.length > 0 ? (
            <div className="dash-chart">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={quizScores}
                  margin={{ top: 8, right: 4, left: -24, bottom: 0 }}
                >
                  <CartesianGrid
                    stroke="#edf0f6"
                    strokeDasharray="4 4"
                    vertical={false}
                  />
                  <XAxis
                    dataKey="attempt"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "#8790a4", fontSize: 11 }}
                  />
                  <YAxis
                    domain={[0, 100]}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "#8790a4", fontSize: 11 }}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <Tooltip
                    cursor={{ fill: "#f4f3ff" }}
                    formatter={(value) => [`${value}%`, "Score"]}
                    contentStyle={{
                      border: "1px solid #e9eaf3",
                      borderRadius: 12,
                      boxShadow: "0 8px 24px rgba(25, 32, 55, .08)",
                    }}
                  />
                  <Bar
                    dataKey="score"
                    fill="#7065e8"
                    radius={[6, 6, 0, 0]}
                    maxBarSize={34}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="dash-empty-chart">
              <span>
                <ClipboardCheck size={25} />
              </span>
              <strong>Your quiz journey starts here</strong>
              <p>
                Complete a practice quiz to see your actual scores displayed
                here.
              </p>
              <Link to="/quizzes" className="dash-text-link">
                Practice a quiz <ArrowRight size={15} />
              </Link>
            </div>
          )}

          <div className="dash-chart-footer">
            <span>
              <span className="dash-chart-dot" />
              Submitted quiz scores
            </span>
            <Link to="/progress" aria-label="View full study progress">
              <ArrowUpRight size={17} />
            </Link>
          </div>
        </div>
      </section>

      <section className="dash-bottom-grid">
        <div className="dash-panel">
          <SectionHeading
            eyebrow="YOUR MATERIALS"
            title="Recently added"
            action="View library"
            to="/library"
          />

          {documents.length > 0 ? (
            <div className="dash-document-list">
              {documents.slice(0, 5).map((document) => (
                <article className="dash-document-item" key={document.id}>
                  <span className="dash-document-icon">
                    <FileText size={20} />
                  </span>

                  <div className="dash-document-info">
                    <strong title={document.title}>
                      {document.title}
                    </strong>
                    <span>
                      {document.subject || "General"} ·{" "}
                      {formatDate(document.created_at)}
                    </span>
                  </div>

                  <Link
                    to={`/summaries?document=${document.id}`}
                    className="dash-document-open"
                    aria-label={`Create summary for ${document.title}`}
                    title="Create a summary"
                  >
                    <ArrowUpRight size={18} />
                  </Link>
                </article>
              ))}
            </div>
          ) : (
            <div className="dash-empty-documents">
              <span>
                <BookOpen size={25} />
              </span>
              <strong>Your library is ready for its first document.</strong>
              <p>
                Start with a lecture, chapter, or set of notes you want to
                understand better.
              </p>
              <Link to="/upload" className="btn btn-primary">
                <Plus size={17} />
                Add study material
              </Link>
            </div>
          )}
        </div>

        <div className="dash-panel dash-snapshot-panel">
          <SectionHeading
            eyebrow="YOUR STUDY SNAPSHOT"
            title="Keep the momentum"
          />

          <div className="dash-snapshot-row">
            <span className="dash-snapshot-icon dash-icon-green">
              <CheckCircle2 size={19} />
            </span>
            <span className="dash-snapshot-copy">
              <strong>Cards marked as known</strong>
              <small>Cards you feel confident about</small>
            </span>
            <b>{numberFormat.format(totals.cards_known ?? 0)}</b>
          </div>

          <div className="dash-snapshot-row">
            <span className="dash-snapshot-icon dash-icon-orange">
              <Layers size={19} />
            </span>
            <span className="dash-snapshot-copy">
              <strong>Cards to practice</strong>
              <small>Concepts to review again</small>
            </span>
            <b>{numberFormat.format(stats?.cards_to_practice ?? 0)}</b>
          </div>

          <div className="dash-snapshot-row">
            <span className="dash-snapshot-icon dash-icon-blue">
              <Clock3 size={19} />
            </span>
            <span className="dash-snapshot-copy">
              <strong>Recent study activity</strong>
              <small>
                {recentActivity.length} recent{" "}
                {recentActivity.length === 1 ? "event" : "events"} recorded
              </small>
            </span>
            <Link
              to="/progress"
              className="dash-snapshot-link"
              aria-label="View recent study activity"
            >
              <ArrowUpRight size={17} />
            </Link>
          </div>

          <div className="dash-snapshot-note">
            <CalendarDays size={17} />
            <span>
              Your progress updates as you upload materials, review cards,
              and complete quizzes.
            </span>
          </div>

          <Link to="/progress" className="dash-progress-button">
            Explore study progress
            <ArrowRight size={17} />
          </Link>
        </div>
      </section>

      <footer className="dash-footer">
        <span>
          <Brain size={16} />
          AI Study Buddy
        </span>
        <span>Built to help you learn one topic at a time.</span>
      </footer>
    </main>
  );
}
