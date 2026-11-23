import { FormEvent, useEffect, useState } from "react";
import { api } from "./api";
import type { Dashboard, Dataset, QualityCheck, QualityRun } from "./types";

const emptyDashboard: Dashboard = {
  dataset_count: 0,
  check_count: 0,
  passed: 0,
  failed: 0,
  average_score: 0,
};

export default function App() {
  const [dashboard, setDashboard] = useState(emptyDashboard);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [checks, setChecks] = useState<QualityCheck[]>([]);
  const [runs, setRuns] = useState<QualityRun[]>([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function refresh() {
    try {
      const [metrics, data, qualityChecks, qualityRuns] = await Promise.all([
        api.dashboard(),
        api.datasets(),
        api.checks(),
        api.runs(),
      ]);
      setDashboard(metrics);
      setDatasets(data);
      setChecks(qualityChecks);
      setRuns(qualityRuns);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load dashboard");
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function createDataset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await api.createDataset({
        name: String(form.get("name")),
        source_type: String(form.get("source_type")),
        owner: String(form.get("owner")),
        description: String(form.get("description")),
      });
      event.currentTarget.reset();
      setNotice("Dataset connected");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to connect dataset");
    }
  }

  async function createCheck(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await api.createCheck({
        dataset_id: Number(form.get("dataset_id")),
        name: String(form.get("name")),
        check_type: String(form.get("check_type")),
        column_name: String(form.get("column_name")),
        threshold: Number(form.get("threshold")),
      });
      event.currentTarget.reset();
      setNotice("Quality check created");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create check");
    }
  }

  async function runCheck(id: number) {
    try {
      await api.runCheck(id);
      setNotice("Check run completed");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to run check");
    }
  }

  async function sync(provider: string) {
    try {
      const result = await api.sync(provider);
      setNotice(`${provider} sync: ${result.status}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sync integration");
    }
  }

  return (
    <main>
      <header>
        <div>
          <p className="eyebrow">GOVERNANCE WORKSPACE</p>
          <h1>Data Quality Hub</h1>
        </div>
        <button className="profile">Alex Chen</button>
      </header>

      {error && <div className="alert error">{error}</div>}
      {notice && <div className="alert success">{notice}</div>}

      <section className="metrics">
        <article><span>Datasets</span><strong>{dashboard.dataset_count}</strong></article>
        <article><span>Quality checks</span><strong>{dashboard.check_count}</strong></article>
        <article><span>Passed runs</span><strong>{dashboard.passed}</strong></article>
        <article><span>Average score</span><strong>{dashboard.average_score}%</strong></article>
      </section>

      <section className="grid">
        <div className="panel">
          <h2>Connect a dataset</h2>
          <form onSubmit={createDataset}>
            <input name="name" placeholder="Dataset name" required />
            <select name="source_type" defaultValue="PostgreSQL">
              <option>PostgreSQL</option><option>Snowflake</option><option>SQL Server</option><option>MySQL</option>
            </select>
            <input name="owner" placeholder="Data owner" required />
            <input name="description" placeholder="Description" />
            <button type="submit">Connect dataset</button>
          </form>
        </div>

        <div className="panel">
          <h2>Create a quality check</h2>
          <form onSubmit={createCheck}>
            <select name="dataset_id" required>
              <option value="">Select dataset</option>
              {datasets.map((dataset) => <option key={dataset.id} value={dataset.id}>{dataset.name}</option>)}
            </select>
            <input name="name" placeholder="Check name" required />
            <select name="check_type">
              <option value="completeness">Completeness</option>
              <option value="uniqueness">Uniqueness</option>
              <option value="validity">Validity</option>
              <option value="freshness">Freshness</option>
            </select>
            <input name="column_name" placeholder="Column name" />
            <input name="threshold" type="number" min="0" max="100" defaultValue="95" />
            <button type="submit" disabled={!datasets.length}>Create check</button>
          </form>
        </div>
      </section>

      <section className="panel">
        <h2>Quality checks</h2>
        {checks.length ? (
          <table>
            <thead><tr><th>Name</th><th>Type</th><th>Threshold</th><th>Status</th><th></th></tr></thead>
            <tbody>{checks.map((check) =>
              <tr key={check.id}>
                <td>{check.name}</td><td>{check.check_type}</td><td>{check.threshold}%</td>
                <td><span className={`status ${check.status}`}>{check.status}</span></td>
                <td><button className="secondary" onClick={() => void runCheck(check.id)}>Run</button></td>
              </tr>
            )}</tbody>
          </table>
        ) : <p className="empty">No quality checks yet.</p>}
      </section>

      <section className="grid">
        <div className="panel">
          <h2>Recent runs</h2>
          {runs.length ? runs.slice(0, 6).map((run) =>
            <div className="run" key={run.id}>
              <div><strong>{run.check_name}</strong><small>{run.dataset_name}</small></div>
              <span className={`status ${run.status}`}>{run.score}%</span>
            </div>
          ) : <p className="empty">No runs yet.</p>}
        </div>
        <div className="panel">
          <h2>Integrations</h2>
          {["collibra", "soda", "snowflake"].map((provider) =>
            <div className="integration" key={provider}>
              <strong>{provider}</strong>
              <button className="secondary" onClick={() => void sync(provider)}>Sync</button>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
