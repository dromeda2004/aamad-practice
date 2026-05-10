import { useMemo, useState } from "react";
import type { EmploymentType, RequisitionInput } from "../api/types";

const EMPTY: RequisitionInput = {
  role_title: "",
  must_have_skills: [],
  preferred_skills: [],
  experience_min_years: 2,
  experience_max_years: 8,
  location: "",
  employment_type: "full_time",
  free_text_brief: "",
};

function parseList(raw: string): string[] {
  return raw
    .split(/[,;\n]/)
    .map((s) => s.trim())
    .filter(Boolean);
}

interface Props {
  onSubmit: (data: RequisitionInput) => void;
  disabled?: boolean;
}

export function RoleIntakeForm({ onSubmit, disabled }: Props) {
  const [form, setForm] = useState<RequisitionInput>(EMPTY);
  const [mustRaw, setMustRaw] = useState("");
  const [prefRaw, setPrefRaw] = useState("");
  const [blocked, setBlocked] = useState<string | null>(null);
  const [warnJunior, setWarnJunior] = useState(false);

  const titleId = "field-role-title";
  const mustId = "field-must-skills";

  const skillsForWarning = useMemo(
    () => parseList(mustRaw),
    [mustRaw],
  );

  const checkJuniorConflict = (minY: number, maxY: number, title: string) => {
    const t = title.toLowerCase();
    const junior = /\b(junior|entry|graduate|intern)\b/.test(t);
    if (junior && (minY >= 4 || maxY >= 8)) {
      setWarnJunior(true);
    } else {
      setWarnJunior(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const must = parseList(mustRaw);
    const preferred = parseList(prefRaw);

    if (!form.role_title.trim()) {
      setBlocked("Role title is required.");
      document.getElementById(titleId)?.focus();
      return;
    }
    if (must.length === 0) {
      setBlocked("Enter at least one must-have skill.");
      document.getElementById(mustId)?.focus();
      return;
    }
    if (form.experience_min_years > form.experience_max_years) {
      setBlocked("Minimum experience cannot exceed maximum.");
      return;
    }

    setBlocked(null);
    onSubmit({
      ...form,
      must_have_skills: must,
      preferred_skills: preferred,
      role_title: form.role_title.trim(),
      location: form.location.trim(),
    });
  };

  return (
    <form className="panel" onSubmit={handleSubmit} noValidate>
      <h2 className="panel__title">Role intake</h2>
      <p className="muted">
        Guided form per PRD: block if title or must-have skills are missing.
      </p>

      <div className="field">
        <label htmlFor={titleId}>Role title</label>
        <input
          id={titleId}
          name="role_title"
          type="text"
          autoComplete="organization-title"
          value={form.role_title}
          disabled={disabled}
          onChange={(e) => {
            setForm((f) => ({ ...f, role_title: e.target.value }));
            checkJuniorConflict(
              form.experience_min_years,
              form.experience_max_years,
              e.target.value,
            );
          }}
          required
          aria-required="true"
        />
      </div>

      <div className="field">
        <label htmlFor={mustId}>Must-have skills (comma-separated)</label>
        <textarea
          id={mustId}
          name="must_have_skills"
          rows={3}
          value={mustRaw}
          disabled={disabled}
          placeholder="e.g. Full-cycle recruiting, ATS, Boolean search"
          onChange={(e) => setMustRaw(e.target.value)}
          aria-required="true"
        />
      </div>

      <div className="field">
        <label htmlFor="field-pref-skills">Preferred skills</label>
        <textarea
          id="field-pref-skills"
          name="preferred_skills"
          rows={2}
          value={prefRaw}
          disabled={disabled}
          placeholder="e.g. Engineering hiring, Employer branding"
          onChange={(e) => setPrefRaw(e.target.value)}
        />
      </div>

      <div className="field-row">
        <div className="field">
          <label htmlFor="field-exp-min">Min years experience</label>
          <input
            id="field-exp-min"
            type="number"
            min={0}
            max={40}
            value={form.experience_min_years}
            disabled={disabled}
            onChange={(e) => {
              const v = Number(e.target.value);
              setForm((f) => ({ ...f, experience_min_years: v }));
              checkJuniorConflict(v, form.experience_max_years, form.role_title);
            }}
          />
        </div>
        <div className="field">
          <label htmlFor="field-exp-max">Max years experience</label>
          <input
            id="field-exp-max"
            type="number"
            min={0}
            max={40}
            value={form.experience_max_years}
            disabled={disabled}
            onChange={(e) => {
              const v = Number(e.target.value);
              setForm((f) => ({ ...f, experience_max_years: v }));
              checkJuniorConflict(form.experience_min_years, v, form.role_title);
            }}
          />
        </div>
      </div>

      <div className="field-row">
        <div className="field">
          <label htmlFor="field-location">Location / work model</label>
          <input
            id="field-location"
            type="text"
            value={form.location}
            disabled={disabled}
            placeholder="e.g. Remote US, Hybrid NYC"
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                location: e.target.value,
              }))
            }
          />
        </div>
        <div className="field">
          <label htmlFor="field-employment">Employment type</label>
          <select
            id="field-employment"
            value={form.employment_type || "full_time"}
            disabled={disabled}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                employment_type: e.target.value as EmploymentType,
              }))
            }
          >
            <option value="full_time">Full time</option>
            <option value="part_time">Part time</option>
            <option value="contract">Contract</option>
            <option value="intern">Intern</option>
          </select>
        </div>
      </div>

      <div className="field">
        <label htmlFor="field-brief">Optional role brief (free text)</label>
        <textarea
          id="field-brief"
          rows={3}
          value={form.free_text_brief}
          disabled={disabled}
          placeholder="Paste a hiring manager brief — backend may parse into structured fields."
          onChange={(e) =>
            setForm((f) => ({
              ...f,
              free_text_brief: e.target.value,
            }))
          }
        />
      </div>

      {blocked && (
        <div className="banner banner--error" role="alert">
          {blocked}
        </div>
      )}

      {warnJunior && (
        <div className="banner banner--warn" role="status">
          Role title suggests junior level but experience range is high. Consider
          adjusting years or title wording.
        </div>
      )}

      <div className="actions-row">
        <button type="submit" className="btn btn--primary" disabled={disabled}>
          Start recruitment run
        </button>
      </div>

      {skillsForWarning.length > 0 && (
        <p className="muted tiny" aria-live="polite">
          Parsed must-have skills:{" "}
          <strong>{skillsForWarning.join(", ")}</strong>
        </p>
      )}
    </form>
  );
}
