import { useEffect, useState } from "react";
import { FaSyncAlt, FaClock, FaFire, FaLightbulb } from "react-icons/fa";
import Sidebar from "../components/Sidebar";
import { getDailyMentorBriefing } from "../api";

const URGENCY_STYLES = {
  high: { bg: "#FEE2E2", color: "#B91C1C" },
  medium: { bg: "#FEF3C7", color: "#92400E" },
  low: { bg: "#DCFCE7", color: "#15803D" },
};

function Mentor() {
  const [briefing, setBriefing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const res = await getDailyMentorBriefing();
      setBriefing(res.data);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || "Couldn't load your mentor briefing."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="app-shell flex">
      <Sidebar />

      <div className="main">
        <div className="page-head">
          <div>
            <h1>Mentor</h1>
            <p>Your AI mentor's take on today.</p>
          </div>
          <button className="btn btn-outline" onClick={load} disabled={loading}>
            {loading ? (
              <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                <span className="spinner" /> Refreshing…
              </span>
            ) : (
              <>
                <FaSyncAlt style={{ marginRight: 6 }} /> Refresh
              </>
            )}
          </button>
        </div>

        {error && <p className="error-text" style={{ marginBottom: 20 }}>{error}</p>}

        {loading && !briefing ? (
          <p style={{ color: "var(--ink-faint)" }}>Loading…</p>
        ) : briefing ? (
          <>
            {/* Greeting + motivation */}
            <div className="card" style={{ marginBottom: 24 }}>
              <h2 style={{ marginBottom: 8 }}>{briefing.greeting}</h2>
              <p style={{ color: "var(--ink-soft)" }}>{briefing.motivation}</p>
            </div>

            <div className="grid" style={{ marginBottom: 24 }}>
              {/* Priorities */}
              <div className="card">
                <div className="feature-icon icon-pink">
                  <FaFire />
                </div>
                <h3 style={{ marginBottom: 12 }}>Today's Priorities</h3>
                {briefing.priorities.length === 0 ? (
                  <p style={{ fontSize: 14, color: "var(--ink-faint)" }}>
                    Nothing urgent on your plate — nice.
                  </p>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    {briefing.priorities.map((p, i) => {
                      const style = URGENCY_STYLES[p.urgency] || URGENCY_STYLES.medium;
                      return (
                        <div
                          key={i}
                          style={{
                            padding: "10px 12px",
                            borderRadius: 10,
                            background: "var(--surface-alt)",
                          }}
                        >
                          <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                            <strong style={{ fontSize: 14 }}>{p.title}</strong>
                            <span
                              style={{
                                fontSize: 11,
                                fontWeight: 700,
                                textTransform: "uppercase",
                                padding: "2px 8px",
                                borderRadius: 999,
                                background: style.bg,
                                color: style.color,
                                whiteSpace: "nowrap",
                                height: "fit-content",
                              }}
                            >
                              {p.urgency}
                            </span>
                          </div>
                          {p.why && (
                            <p style={{ fontSize: 13, color: "var(--ink-soft)", marginTop: 4 }}>
                              {p.why}
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Schedule */}
              <div className="card">
                <div className="feature-icon icon-sky">
                  <FaClock />
                </div>
                <h3 style={{ marginBottom: 12 }}>Suggested Schedule</h3>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {briefing.schedule.map((block, i) => (
                    <div
                      key={i}
                      style={{
                        display: "flex",
                        gap: 10,
                        fontSize: 13.5,
                        padding: "8px 0",
                        borderBottom:
                          i < briefing.schedule.length - 1
                            ? "1px solid var(--border)"
                            : "none",
                      }}
                    >
                      <span style={{ fontWeight: 600, color: "var(--ink)", whiteSpace: "nowrap" }}>
                        {block.time}
                      </span>
                      <span style={{ color: "var(--ink-soft)" }}>{block.activity}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Tips */}
              <div className="card">
                <div className="feature-icon icon-mint">
                  <FaLightbulb />
                </div>
                <h3 style={{ marginBottom: 12 }}>Mentor Tips</h3>
                <ul style={{ paddingLeft: 18, display: "flex", flexDirection: "column", gap: 8 }}>
                  {briefing.tips.map((tip, i) => (
                    <li key={i} style={{ fontSize: 13.5, color: "var(--ink-soft)" }}>
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Raw snapshot of what the mentor is basing this on */}
            <div className="card">
              <h3 style={{ marginBottom: 10 }}>What I'm looking at</h3>
              <p style={{ fontSize: 13, color: "var(--ink-faint)" }}>
                {briefing.context.tasks.length} task(s) planned today ·{" "}
                {briefing.context.assignments.length} assignment(s) due soon ·{" "}
                {briefing.context.deadlines.length} deadline(s) coming up ·{" "}
                {briefing.context.minutes_studied_today} minute(s) studied today
              </p>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

export default Mentor;
