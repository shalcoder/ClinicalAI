import { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const manualInitialState = {
  Age: 34,
  Gender: "Male",
  WBC_Count: 5300,
  "Neutrophils_%": 58,
  Hemoglobin: 14.5,
  MCV: 89,
  ALT: 35,
  AST: 29,
  Creatinine: 0.9,
  Glucose_Fasting: 110,
  CRP: 8,
  ANA_Positive: 0,
};

const fieldConfig = [
  ["Age", "number"],
  ["Gender", "select"],
  ["WBC_Count", "number"],
  ["Neutrophils_%", "number"],
  ["Hemoglobin", "number"],
  ["MCV", "number"],
  ["ALT", "number"],
  ["AST", "number"],
  ["Creatinine", "number"],
  ["Glucose_Fasting", "number"],
  ["CRP", "number"],
  ["ANA_Positive", "select"],
];

const tabItems = [
  { id: "command", label: "Command Center" },
  { id: "diagnosis", label: "Diagnosis Lab" },
  { id: "patients", label: "Patient Records" },
  { id: "care", label: "Care Network" },
];

function App() {
  const [overview, setOverview] = useState(null);
  const [doctorDisease, setDoctorDisease] = useState("");
  const [doctors, setDoctors] = useState([]);
  const [diseases, setDiseases] = useState([]);
  const [patientId, setPatientId] = useState("");
  const [patientResult, setPatientResult] = useState(null);
  const [patientError, setPatientError] = useState("");
  const [manualForm, setManualForm] = useState(manualInitialState);
  const [manualResult, setManualResult] = useState(null);
  const [loadingManual, setLoadingManual] = useState(false);
  const [loadingPatient, setLoadingPatient] = useState(false);
  const [activeTab, setActiveTab] = useState("command");

  useEffect(() => {
    loadOverview();
    loadDiseases();
    loadDoctors("");
  }, []);

  async function loadOverview() {
    const response = await fetch(`${API_BASE_URL}/api/overview`);
    const data = await response.json();
    setOverview(data);
  }

  async function loadDiseases() {
    const response = await fetch(`${API_BASE_URL}/api/diseases`);
    const data = await response.json();
    setDiseases(data.items || []);
  }

  async function loadDoctors(disease) {
    const query = disease ? `?disease=${encodeURIComponent(disease)}` : "";
    const response = await fetch(`${API_BASE_URL}/api/doctors${query}`);
    const data = await response.json();
    setDoctors(data.items || []);
  }

  async function handlePatientLookup(event) {
    event.preventDefault();
    setLoadingPatient(true);
    setPatientError("");
    setPatientResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/patients/${encodeURIComponent(patientId)}`);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Patient lookup failed");
      }
      setPatientResult(data);
      setActiveTab("patients");
    } catch (error) {
      setPatientError(error.message);
    } finally {
      setLoadingPatient(false);
    }
  }

  async function handleManualSubmit(event) {
    event.preventDefault();
    setLoadingManual(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/diagnosis/manual`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(manualForm),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Diagnosis failed");
      }
      setManualResult(data);
      setActiveTab("diagnosis");
    } catch (error) {
      setManualResult({ error: error.message });
    } finally {
      setLoadingManual(false);
    }
  }

  function updateManualField(name, value, type) {
    const nextValue = type === "number" ? Number(value) : value;
    setManualForm((current) => ({ ...current, [name]: nextValue }));
  }

  const monitoringCards = [
    { label: "High Priority Cases", value: manualResult?.diagnosis ? 1 : 0 },
    { label: "Autoimmune Alerts", value: manualResult?.autoimmune?.score > 60 ? 1 : 0 },
    { label: "Specialists Available", value: doctors.length || "--" },
    { label: "Diagnoses Tracked", value: overview?.diagnosis_distribution?.length ?? "--" },
  ];

  return (
    <div className="page-shell">
      <header className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Clinical Intelligence Platform</p>
          <h1>Professional clinical decision support, rebuilt for deployment.</h1>
          <p className="hero-text">
            A production-ready frontend for patient lookup, AI-assisted diagnosis, specialist
            discovery, and operational insight dashboards.
          </p>
          <div className="hero-actions">
            <button className="primary-link" onClick={() => setActiveTab("diagnosis")} type="button">
              Open Diagnosis Lab
            </button>
            <button className="secondary-link" onClick={() => setActiveTab("patients")} type="button">
              Open Patient Records
            </button>
          </div>
        </div>
        <div className="hero-panel">
          <div className="panel-label">System Status</div>
          <div className="metric-grid">
            <MetricCard label="Records" value={overview?.summary?.records ?? "--"} />
            <MetricCard label="Avg Age" value={overview?.summary?.avg_age ?? "--"} />
            <MetricCard label="Avg Glucose" value={overview?.summary?.avg_glucose ?? "--"} />
            <MetricCard label="Avg CRP" value={overview?.summary?.avg_crp ?? "--"} />
          </div>
        </div>
      </header>

      <section className="tabs-shell">
        <div className="tabs-row">
          {tabItems.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`tab-button${activeTab === tab.id ? " active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === "command" ? (
          <section className="tab-panel">
            <div className="section-heading">
              <div>
                <p className="section-kicker">Operations</p>
                <h2>Clinical command center</h2>
              </div>
            </div>
            <div className="status-grid">
              {monitoringCards.map((card) => (
                <div className="status-card" key={card.label}>
                  <p className="small-label">{card.label}</p>
                  <strong>{card.value}</strong>
                </div>
              ))}
            </div>
            <div className="content-grid">
              <section className="card">
                <div className="section-heading">
                  <div>
                    <p className="section-kicker">Model Overview</p>
                    <h2>Top clinical drivers</h2>
                  </div>
                </div>
                <div className="feature-list">
                  {overview?.top_features?.map((feature) => (
                    <div className="feature-row" key={feature.feature}>
                      <span>{feature.feature}</span>
                      <div className="feature-bar">
                        <div style={{ width: `${Math.min(feature.importance, 100)}%` }} />
                      </div>
                      <strong>{feature.importance}</strong>
                    </div>
                  ))}
                </div>
              </section>

              <section className="card">
                <div className="section-heading">
                  <div>
                    <p className="section-kicker">Case Mix</p>
                    <h2>Diagnosis distribution</h2>
                  </div>
                </div>
                <div className="distribution-list">
                  {overview?.diagnosis_distribution?.map((item) => (
                    <div key={item.diagnosis} className="distribution-row">
                      <span>{item.diagnosis}</span>
                      <strong>{item.count}</strong>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          </section>
        ) : null}

        {activeTab === "diagnosis" ? (
          <section className="tab-panel">
            <section className="card wide-card" id="manual-diagnosis">
              <div className="section-heading">
                <div>
                  <p className="section-kicker">AI Diagnosis</p>
                  <h2>Manual clinical assessment</h2>
                </div>
              </div>
              <form className="form-grid" onSubmit={handleManualSubmit}>
                {fieldConfig.map(([fieldName, type]) => (
                  <label key={fieldName} className="field">
                    <span>{fieldName.replaceAll("_", " ")}</span>
                    {type === "select" ? (
                      <select
                        value={manualForm[fieldName]}
                        onChange={(event) => updateManualField(fieldName, event.target.value, type)}
                      >
                        {fieldName === "Gender" ? (
                          <>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                          </>
                        ) : (
                          <>
                            <option value={0}>Negative</option>
                            <option value={1}>Positive</option>
                          </>
                        )}
                      </select>
                    ) : (
                      <input
                        type="number"
                        step="0.1"
                        value={manualForm[fieldName]}
                        onChange={(event) => updateManualField(fieldName, event.target.value, type)}
                      />
                    )}
                  </label>
                ))}
                <button className="primary-button" disabled={loadingManual} type="submit">
                  {loadingManual ? "Analyzing..." : "Generate Diagnosis"}
                </button>
              </form>
              <DiagnosisResult result={manualResult} />
            </section>
          </section>
        ) : null}

        {activeTab === "patients" ? (
          <section className="tab-panel">
            <div className="content-grid">
              <section className="card" id="patient-lookup">
                <div className="section-heading">
                  <div>
                    <p className="section-kicker">Patient Search</p>
                    <h2>Lookup by patient ID</h2>
                  </div>
                </div>
                <form className="search-row" onSubmit={handlePatientLookup}>
                  <input
                    value={patientId}
                    onChange={(event) => setPatientId(event.target.value)}
                    placeholder="Enter Patient ID"
                  />
                  <button className="secondary-button" disabled={loadingPatient} type="submit">
                    {loadingPatient ? "Searching..." : "Search"}
                  </button>
                </form>
                {patientError ? <p className="error-text">{patientError}</p> : null}
                {patientResult ? (
                  <div className="stack">
                    <div className="result-banner">
                      <div>
                        <p className="small-label">Patient</p>
                        <h3>{patientResult.patient.Patient_ID}</h3>
                      </div>
                      <div>
                        <p className="small-label">Predicted Disease</p>
                        <h3>{patientResult.prediction.diagnosis}</h3>
                      </div>
                      <div>
                        <p className="small-label">Confidence</p>
                        <h3>{patientResult.prediction.confidence}%</h3>
                      </div>
                    </div>
                    <LabTable items={patientResult.prediction.lab_analysis} />
                  </div>
                ) : null}
              </section>

              <section className="card">
                <div className="section-heading">
                  <div>
                    <p className="section-kicker">Patient Summary</p>
                    <h2>Clinical profile snapshot</h2>
                  </div>
                </div>
                {patientResult ? (
                  <div className="profile-grid">
                    <ProfileItem label="Age" value={patientResult.patient.Age} />
                    <ProfileItem label="Gender" value={patientResult.patient.Gender} />
                    <ProfileItem label="Glucose" value={patientResult.patient.Glucose_Fasting} />
                    <ProfileItem label="CRP" value={patientResult.patient.CRP} />
                    <ProfileItem label="Hemoglobin" value={patientResult.patient.Hemoglobin} />
                    <ProfileItem label="WBC Count" value={patientResult.patient.WBC_Count} />
                  </div>
                ) : (
                  <p className="muted">Search a patient ID to load the clinical summary and lab trend data.</p>
                )}
              </section>
            </div>
          </section>
        ) : null}

        {activeTab === "care" ? (
          <section className="tab-panel">
            <div className="content-grid">
              <section className="card">
                <div className="section-heading">
                  <div>
                    <p className="section-kicker">Specialist Network</p>
                    <h2>Doctor recommendations</h2>
                  </div>
                  <select
                    value={doctorDisease}
                    onChange={(event) => {
                      const value = event.target.value;
                      setDoctorDisease(value);
                      loadDoctors(value);
                    }}
                  >
                    <option value="">All diseases</option>
                    {diseases.map((disease) => (
                      <option key={disease} value={disease}>
                        {disease}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="doctor-grid">
                  {doctors.map((doctor) => (
                    <article className="doctor-card" key={`${doctor.disease}-${doctor.doctor}`}>
                      <p className="chip">{doctor.disease}</p>
                      <h3>{doctor.doctor}</h3>
                      <p>{doctor.clinic}</p>
                      <p className="muted">{doctor.experience}</p>
                      <p className="coordinates">
                        {doctor.lat}, {doctor.lon}
                      </p>
                    </article>
                  ))}
                </div>
              </section>

              <section className="card">
                <div className="section-heading">
                  <div>
                    <p className="section-kicker">Care Workflow</p>
                    <h2>Recommended next actions</h2>
                  </div>
                </div>
                <div className="timeline">
                  <TimelineItem
                    title="Triage case"
                    description="Run manual diagnosis or search an existing patient record to establish urgency."
                  />
                  <TimelineItem
                    title="Assign specialist"
                    description="Filter the doctor network by disease and route the case to the right clinic."
                  />
                  <TimelineItem
                    title="Review inflammatory markers"
                    description="Use CRP, WBC, hemoglobin, and ANA status to assess autoimmune escalation."
                  />
                  <TimelineItem
                    title="Document treatment plan"
                    description="Capture medication guidance and clinician review before patient handoff."
                  />
                </div>
              </section>
            </div>
          </section>
        ) : null}
      </section>
    </div>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="metric-card">
      <p>{label}</p>
      <strong>{value}</strong>
    </div>
  );
}

function ProfileItem({ label, value }) {
  return (
    <div className="profile-item">
      <p className="small-label">{label}</p>
      <strong>{value}</strong>
    </div>
  );
}

function TimelineItem({ title, description }) {
  return (
    <div className="timeline-item">
      <div className="timeline-dot" />
      <div>
        <strong>{title}</strong>
        <p>{description}</p>
      </div>
    </div>
  );
}

function DiagnosisResult({ result }) {
  if (!result) {
    return null;
  }
  if (result.error) {
    return <p className="error-text">{result.error}</p>;
  }
  return (
    <div className="stack diagnosis-result">
      <div className="result-banner">
        <div>
          <p className="small-label">Diagnosis</p>
          <h3>{result.diagnosis}</h3>
        </div>
        <div>
          <p className="small-label">Confidence</p>
          <h3>{result.confidence}%</h3>
        </div>
        <div>
          <p className="small-label">Stage</p>
          <h3>{result.stage || "N/A"}</h3>
        </div>
      </div>
      <div className="detail-grid">
        <div className="detail-card">
          <p className="small-label">Medication</p>
          <strong>{result.recommended_medication}</strong>
        </div>
        <div className="detail-card">
          <p className="small-label">Autoimmune Risk</p>
          <strong>{result.autoimmune.risk_level}</strong>
          <span>{result.autoimmune.condition}</span>
        </div>
        <div className="detail-card">
          <p className="small-label">Autoimmune Score</p>
          <strong>{result.autoimmune.score}%</strong>
          <span>Risk score from inflammatory markers</span>
        </div>
      </div>
      <LabTable items={result.lab_analysis} />
    </div>
  );
}

function LabTable({ items }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Lab Test</th>
            <th>Value</th>
            <th>Normal Range</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.lab_test}>
              <td>{item.lab_test}</td>
              <td>{item.value}</td>
              <td>{item.normal_range}</td>
              <td>{item.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
