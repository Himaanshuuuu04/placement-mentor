# Realtime Architecture

## 1. Overview
The Realtime Platform (PLANE E) handles all low-latency, bidirectional communication between the student and the AI Mentor. It supports both text-based streaming and real-time audio (voice) interview sessions. 

The architecture strictly separates responsibilities between **WebSockets** (for control, text, and events) and **WebRTC** (for low-latency audio media).

## 2. WebSocket Architecture (Text & Events)

WebSockets are used for persistent data connections, session presence, text streaming, and signaling.

**Flow:**
Client ↔ Realtime Gateway (WebSocket) ↔ Interview Service ↔ LangGraph Agent ↔ Services

### 2.1 Responsibilities
- **Token Streaming:** Streaming LLM text generation back to the client token-by-token for a responsive UI.
- **Event Streaming:** Pushing system events (e.g., `ExecutionCompleted`, `MasteryUpdated`) to the client.
- **Session Presence:** Tracking active users and interview connectivity state.
- **WebRTC Signaling:** Exchanging SDP offers/answers and ICE candidates to establish peer-to-peer or client-to-server audio connections.

### 2.2 Redis Integration
Redis Pub/Sub is utilized behind the Realtime Gateway to route messages to the correct WebSocket server instance where the user is connected, supporting horizontal scaling of the Realtime Gateway.

## 3. WebRTC Architecture (Audio Interviews)

WebRTC is used specifically for real-time audio communication during voice-based mock interviews. It is not used for text or standard API calls.

**Flow:**
Client ↔ WebRTC Media/Signaling Layer ↔ Speech-to-Text / Text-to-Speech Pipeline ↔ Interview Service ↔ LangGraph Agent

### 3.1 Responsibilities
- **Audio Streaming:** Low-latency transmission of student voice to the server and AI voice back to the student.
- **Media Processing:** Audio tracks are piped into a Speech-to-Text (STT) model for transcription.
- **Generation:** Transcribed text is sent to the LangGraph Interview Conductor. The resulting text is converted back via Text-to-Speech (TTS) and streamed over the WebRTC track.

### 3.2 Component Boundaries
- **Signaling:** Happens over the established WebSocket connection.
- **Media Server (SFU/MCU or Direct):** Handles WebRTC audio tracks, passing buffers to STT/TTS services.

## 4. Failure Handling
- **Connection Drops:** Clients implement automatic reconnection with exponential backoff. State is re-synchronized using the persistent Agent Checkpoints stored in PostgreSQL.
- **Latency/Degradation:** If WebRTC audio quality drops, the system falls back gracefully to WebSocket-based text chat.
