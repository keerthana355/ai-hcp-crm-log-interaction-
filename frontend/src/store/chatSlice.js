import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import client from '../api/client'
import { setInteraction } from './interactionSlice'

function makeConversationId() {
  return 'conv_' + Math.random().toString(36).slice(2) + Date.now()
}

const initialState = {
  conversationId: makeConversationId(),
  messages: [
    {
      role: 'assistant',
      content:
        'Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure") or ask for help.',
    },
  ],
  sending: false,
  error: null,
}

export const sendChatMessage = createAsyncThunk(
  'chat/sendMessage',
  async (message, { getState, dispatch, rejectWithValue }) => {
    const { chat } = getState()
    try {
      const res = await client.post('/api/agent/chat', {
        conversation_id: chat.conversationId,
        message,
      })
      if (res.data.interaction) {
        dispatch(setInteraction(res.data.interaction))
      }
      return res.data.reply
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Something went wrong talking to the assistant.')
    }
  }
)

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state, action) => {
        state.sending = true
        state.error = null
        state.messages.push({ role: 'user', content: action.meta.arg })
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.sending = false
        state.messages.push({ role: 'assistant', content: action.payload })
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.sending = false
        state.error = action.payload
        state.messages.push({ role: 'error', content: action.payload })
      })
  },
})

export default chatSlice.reducer
