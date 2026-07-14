import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { clearHighlights } from '../store/interactionSlice'

function Field({ label, children, name, highlighted }) {
  return (
    <div className="field-group">
      <label>{label}</label>
      {children}
    </div>
  )
}

function ReadonlyText({ value, placeholder, highlighted, multiline }) {
  const className = `readonly-field ${!value ? 'empty' : ''} ${highlighted ? 'highlighted' : ''}`
  if (multiline) {
    return <textarea className={className} value={value || ''} placeholder={placeholder} readOnly />
  }
  return <div className={className}>{value || placeholder}</div>
}

export default function LogInteractionForm() {
  const dispatch = useDispatch()
  const { interaction, updatedFields } = useSelector((s) => s.interaction)

  // Fade the highlight after a couple seconds
  useEffect(() => {
    if (updatedFields.length === 0) return
    const t = setTimeout(() => dispatch(clearHighlights()), 2200)
    return () => clearTimeout(t)
  }, [updatedFields, dispatch])

  const is = (field) => updatedFields.includes(field)

  return (
    <div className="panel form-panel">
      <div className="panel-title">Log HCP Interaction</div>

      <div className="field-row">
        <Field label="HCP Name">
          <ReadonlyText
            value={interaction?.hcp?.name}
            placeholder="Search or select HCP..."
            highlighted={is('hcp')}
          />
        </Field>
        <Field label="Interaction Type">
          <ReadonlyText
            value={interaction?.interaction_type}
            placeholder="Meeting"
            highlighted={is('interaction_type')}
          />
        </Field>
      </div>

      <div className="field-row">
        <Field label="Date">
          <ReadonlyText
            value={interaction?.interaction_date ? new Date(interaction.interaction_date).toLocaleDateString() : null}
            placeholder="—"
            highlighted={is('interaction_date')}
          />
        </Field>
        <Field label="Time">
          <ReadonlyText
            value={interaction?.interaction_date ? new Date(interaction.interaction_date).toLocaleTimeString() : null}
            placeholder="—"
            highlighted={is('interaction_date')}
          />
        </Field>
      </div>

      <Field label="Attendees">
        <ReadonlyText
          value={interaction?.attendees}
          placeholder="Enter names or search..."
          highlighted={is('attendees')}
        />
      </Field>

      <Field label="Topics Discussed">
        <ReadonlyText
          value={interaction?.topics_discussed}
          placeholder="Enter key discussion points..."
          highlighted={is('topics_discussed')}
          multiline
        />
      </Field>

      <Field label="Materials Shared / Samples Distributed">
        <div className="chip-list">
          {(interaction?.materials_shared || []).map((m, i) => (
            <span className="chip" key={`m-${i}`}>{m}</span>
          ))}
          {(interaction?.samples_distributed || []).map((s, i) => (
            <span className="chip" key={`s-${i}`}>{s}</span>
          ))}
          {!interaction?.materials_shared?.length && !interaction?.samples_distributed?.length && (
            <span className="readonly-field empty" style={{ border: 'none', padding: 0 }}>
              No materials added.
            </span>
          )}
        </div>
      </Field>

      <Field label="Observed / Inferred HCP Sentiment">
        {interaction?.sentiment ? (
          <span className={`sentiment-badge ${interaction.sentiment} ${is('sentiment') ? 'highlighted' : ''}`}>
            {interaction.sentiment}
          </span>
        ) : (
          <span className="readonly-field empty" style={{ border: 'none', padding: 0 }}>
            Not yet determined
          </span>
        )}
      </Field>

      <Field label="Outcomes">
        <ReadonlyText
          value={interaction?.outcomes}
          placeholder="Key outcomes or agreements..."
          highlighted={is('outcomes')}
          multiline
        />
      </Field>

      <Field label="Follow-up Actions">
        {interaction?.follow_up_actions?.length ? (
          <ul className={`followup-list ${is('follow_up_actions') ? 'highlighted' : ''}`}>
            {interaction.follow_up_actions.map((f, i) => (
              <li key={i}>• {f.action}</li>
            ))}
          </ul>
        ) : (
          <div className="readonly-field empty">No follow-ups suggested yet</div>
        )}
      </Field>

      {interaction?.compliance_note && interaction.compliance_note !== 'No compliance concerns detected.' && (
        <Field label="Compliance Note">
          <div className={`compliance-note ${is('compliance_note') ? 'highlighted' : ''}`}>
            {interaction.compliance_note}
          </div>
        </Field>
      )}
    </div>
  )
}
