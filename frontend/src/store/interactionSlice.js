import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  interaction: null,       // the current interaction object from the backend
  updatedFields: [],       // field names changed by the most recent agent response (for highlight animation)
}

function diffFields(prev, next) {
  if (!next) return []
  if (!prev) return Object.keys(next).filter((k) => next[k] !== null && next[k] !== undefined)

  const changed = []
  const keys = ['hcp', 'interaction_type', 'interaction_date', 'attendees', 'topics_discussed',
    'sentiment', 'outcomes', 'materials_shared', 'samples_distributed', 'follow_up_actions', 'compliance_note']

  for (const key of keys) {
    const a = JSON.stringify(prev[key] ?? null)
    const b = JSON.stringify(next[key] ?? null)
    if (a !== b) changed.push(key)
  }
  return changed
}

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    setInteraction(state, action) {
      const next = action.payload
      state.updatedFields = diffFields(state.interaction, next)
      state.interaction = next
    },
    clearHighlights(state) {
      state.updatedFields = []
    },
  },
})

export const { setInteraction, clearHighlights } = interactionSlice.actions
export default interactionSlice.reducer
