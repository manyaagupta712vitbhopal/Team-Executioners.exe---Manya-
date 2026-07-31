import { useEffect, useState } from "react";
import {
  FaSyncAlt,
  FaClock,
  FaFire,
  FaLightbulb,
  FaPlus,
  FaTrash,
  FaCheckCircle,
  FaRegCircle,
} from "react-icons/fa";
import Sidebar from "../components/Sidebar";
import {
  getDailyMentorBriefing,
  getTodayTasks,
  createTask,
  toggleTask,
  deleteTask,
  getAssignments,
  createAssignment,
  completeAssignment,
  deleteAssignment,
  getDeadlines,
  createDeadline,
  deleteDeadline,
} from "../api";

const URGENCY_STYLES = {
  high: { bg: "#FEE2E2", color: "#B91C1C" },
  medium: { bg: "#FEF3C7", color: "#92400E" },
  low: { bg: "#DCFCE7", color: "#15803D" },
};

const KINDS = [
  { key: "task", label: "Task (today)" },
  { key: "assignment", label: "Assignment" },
  { key: "deadline", label: "Deadline" },
];

/* -------------------------------------------------------------------------- */
/*  Tell Mentor panel — where the user assigns work to the mentor             */
/* -------------------------------------------------------------------------- */

function TellMentorPanel({ onChange }) {
  const [kind, setKind] = useState("task");
  const [title, setTitle] = useState("");
  const [when, setWhen] = useState("");
  const [priority, setPriority] = useState("medium");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const [tasks, setTasks] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [deadlines, setDeadlines] = useState([]);
  const [loadingLists, setLoadingLists] = useState(true);

  async function loadLists() {
    setLoadingLists(true);
    try {
      const [taskRes, assignRes, deadlineRes] = await Promise.all([
        getTodayTasks(),
        getAssignments(),
        getDeadlines(),
      ]);
      setTasks(taskRes.data);
      setAssignments(assignRes.data);
      setDeadlines(deadlineRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingLists(false);
    }
  }

  useEffect(() => {
    loadLists();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!title.trim()) return;

    setSubmitting(true);
    setError("");
    try {
      if (kind === "task") {
        await createTask(title.trim());
      } else if (kind === "assignment") {
        await createAssignment({
          title: title.trim(),
          due_date: when || null,
          priority,
        });
      } else {
        await createDeadline({
          title: title.trim(),
          deadline: when || null,
          type: "deadline",
        });
      }
      setTitle("");
      setWhen("");
      await loadLists();
      onChange?.();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Couldn't save that. Try again.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleToggleTask(id) {
    await toggleTask(id);
    await loadLists();
    onChange?.();
  }

  async function handleDeleteTask(id) {
    await deleteTask(id);
    await loadLists();
    onChange?.();
  }

  async function handleCompleteAssignment(id) {
    await completeAssignment(id);
    await loadLists();
    onChange?.();
  }

  async function handleDeleteAssignment(id) {
    await deleteAssignment(id);
    await loadLists();
    onChange?.();
  }

  async function handleDeleteDeadline(id) {
    await deleteDeadline(id);
    await loadLists();
    onChange?.();
  }

  return (
    <div className="card" style={{ marginBottom: 24 }}>
      <h3 style={{ marginBottom: 4 }}>Tell your mentor what's on your plate</h3>
      <p style={{ fontSize: 13.5, color: "var(--ink-soft)", marginBottom: 16 }}>
        Add tasks, assignments, and deadlines here — the mentor above builds
        your priorities and schedule from exactly this list.
      </p>

      {/* Kind selector */}
      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        {KINDS.map((k) => (
          <button
            key={k.key}
            type="button"
            className={`btn btn-sm ${kind === k.key ? "" : "btn-outline"}`}
            onClick={() => setKind(k.key)}
          >
            {k.label}
          </button>
        ))}
      </div>

      {/* Add form */}
      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}
      >
        <input
          type="text"
          placeholder={
            kind === "task"
              ? "e.g. Finish OS assignment draft"
              : kind === "assignment"
              ? "e.g. Data Structures homework 3"
              : "e.g. Scholarship application"
          }
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          style={{ flex: "1 1 240px" }}
          required
        />

        {kind !== "task" && (
          <input
            type="date"
            value={when}
            onChange={(e) => setWhen(e.target.value)}
            style={{ flex: "0 1 160px" }}
          />
        )}

        {kind === "assignment" && (
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            style={{ flex: "0 1 130px" }}
          >
            <option value="high">High priority</option>
            <option value="medium">Medium priority</option>
            <option value="low">Low priority</option>
          </select>
        )}

        <button className="btn btn-sm" type="submit" disabled={submitting}>
          {submitting ? (
            <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
              <span className="spinner" /> Adding…
            </span>
          ) : (
            <>
              <FaPlus style={{ marginRight: 6 }} /> Add
            </>
          )}
        </button>
      </form>

      {error && <p className="error-text" style={{ marginBottom: 12 }}>{error}</p>}

      {/* Current lists */}
      {!loadingLists && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 16,
          }}
        >
          {/* Tasks */}
          <div>
            <p style={{ fontSize: 12.5, fontWeight: 700, color: "var(--ink-faint)", marginBottom: 8, textTransform: "uppercase" }}>
              Today's tasks
            </p>
            {tasks.length === 0 ? (
              <p style={{ fontSize: 13, color: "var(--ink-faint)" }}>None yet.</p>
            ) : (
              tasks.map((t) => (
                <div
                  key={t.id}
                  style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}
                >
                  <button
                    type="button"
                    onClick={() => handleToggleTask(t.id)}
                    style={{ background: "none", border: "none", cursor: "pointer", padding: 0, color: t.completed ? "#15803D" : "var(--ink-faint)" }}
                    title="Toggle complete"
                  >
                    {t.completed ? <FaCheckCircle /> : <FaRegCircle />}
                  </button>
                  <span
                    style={{
                      fontSize: 13.5,
                      flex: 1,
                      textDecoration: t.completed ? "line-through" : "none",
                      color: t.completed ? "var(--ink-faint)" : "var(--ink)",
                    }}
                  >
                    {t.title}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleDeleteTask(t.id)}
                    style={{ background: "none", border: "none", cursor: "pointer", color: "var(--ink-faint)" }}
                    title="Delete"
                  >
                    <FaTrash size={12} />
                  </button>
                </div>
              ))
            )}
          </div>

          {/* Assignments */}
          <div>
            <p style={{ fontSize: 12.5, fontWeight: 700, color: "var(--ink-faint)", marginBottom: 8, textTransform: "uppercase" }}>
              Assignments
            </p>
            {assignments.length === 0 ? (
              <p style={{ fontSize: 13, color: "var(--ink-faint)" }}>None yet.</p>
            ) : (
              assignments.map((a) => (
                <div
                  key={a.id}
                  style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}
                >
                  <button
                    type="button"
                    onClick={() => handleCompleteAssignment(a.id)}
                    style={{ background: "none", border: "none", cursor: "pointer", padding: 0, color: "var(--ink-faint)" }}
                    title="Mark complete"
                  >
                    <FaRegCircle />
                  </button>
                  <span style={{ fontSize: 13.5, flex: 1 }}>
                    {a.title}
                    {a.due_date && (
                      <span style={{ color: "var(--ink-faint)" }}> · due {a.due_date}</span>
                    )}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleDeleteAssignment(a.id)}
                    style={{ background: "none", border: "none", cursor: "pointer", color: "var(--ink-faint)" }}
                    title="Delete"
                  >
                    <FaTrash size={12} />
                  </button>
                </div>
              ))
            )}
          </div>

          {/* Deadlines */}
          <div>
            <p style={{ fontSize: 12.5, fontWeight: 700, color: "var(--ink-faint)", marginBottom: 8, textTransform: "uppercase" }}>
              Deadlines
            </p>
            {deadlines.length === 0 ? (
              <p style={{ fontSize: 13, color: "var(--ink-faint)" }}>None yet.</p>
            ) : (
              deadlines.map((d) => (
                <div
                  key={d.id}
                  style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}
                >
                  <span style={{ fontSize: 13.5, flex: 1 }}>
                    {d.title}
                    {d.deadline && (
                      <span style={{ color: "var(--ink-faint)" }}> · {d.deadline}</span>
                    )}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleDeleteDeadline(d.id)}
                    style={{ background: "none", border: "none", cursor: "pointer", color: "var(--ink-faint)" }}
                    title="Delete"
                  >
                    <FaTrash size={12} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

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

        <TellMentorPanel onChange={load} />

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
