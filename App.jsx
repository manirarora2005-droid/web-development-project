import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function App() {
  const [summary, setSummary] = useState([]);
  const [records, setRecords] = useState([]);
  const [insight, setInsight] = useState("");
  const [loadingInsight, setLoadingInsight] = useState(false);

  useEffect(() => {
    fetch("/api/summary")
      .then((r) => r.json())
      .then(setSummary);
    fetch("/api/data")
      .then((r) => r.json())
      .then(setRecords);
  }, []);

  const fetchInsight = () => {
    setLoadingInsight(true);
    fetch("/api/insights", { method: "POST" })
      .then((r) => r.json())
      .then((data) => setInsight(data.insight))
      .finally(() => setLoadingInsight(false));
  };

  return (
    <div style={{ fontFamily: "sans-serif", maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <h1>Attendance dashboard</h1>

      <section style={{ marginBottom: 32 }}>
        <h2>Daily attendance rate</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={summary}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis domain={[0, 100]} unit="%" />
            <Tooltip />
            <Line type="monotone" dataKey="rate" stroke="#3378DD" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </section>

      <section style={{ marginBottom: 32 }}>
        <h2>AI insight</h2>
        <button onClick={fetchInsight} disabled={loadingInsight}>
          {loadingInsight ? "Thinking..." : "Generate insight"}
        </button>
        {insight && (
          <p style={{ marginTop: 12, padding: 12, background: "#f4f4f4", borderRadius: 8 }}>
            {insight}
          </p>
        )}
      </section>

      <section>
        <h2>Raw records ({records.length})</h2>
        <table width="100%" cellPadding="6" style={{ borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid #ccc" }}>
              <th>Name</th>
              <th>Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {records.slice(0, 20).map((r) => (
              <tr key={r.id} style={{ borderBottom: "1px solid #eee" }}>
                <td>{r.name}</td>
                <td>{r.date}</td>
                <td>{r.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
