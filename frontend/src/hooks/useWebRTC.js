import { useState, useRef, useCallback } from 'react';

const SERVER = 'http://localhost:8000';

export default function useWebRTC() {
  const [status, setStatus] = useState('idle'); // idle | connecting | connected
  const [remoteStream, setRemoteStream] = useState(null);

  const pcRef = useRef(null);
  const localStreamRef = useRef(null);
  const botAudioRef = useRef(null);

  /* ── Tear everything down ─────────────────────────────────────── */
  const disconnect = useCallback(() => {
    pcRef.current?.close();
    pcRef.current = null;

    localStreamRef.current?.getTracks().forEach((t) => t.stop());
    localStreamRef.current = null;

    if (botAudioRef.current) botAudioRef.current.srcObject = null;

    setRemoteStream(null);
    setStatus('idle');
  }, []);

  /* ── Full WebRTC handshake (mirrors main.html) ────────────────── */
  const connect = useCallback(async () => {
    if (pcRef.current) return; // already active
    setStatus('connecting');

    try {
      // 1 · Microphone — aggressive constraints help suppress external audio
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation:  { ideal: true },
          noiseSuppression:  { ideal: true },
          autoGainControl:   { ideal: true },
          channelCount:      1,
          sampleRate:        { ideal: 16000 },
        },
      });
      localStreamRef.current = stream;

      // 2 · Peer connection
      const pc = new RTCPeerConnection({
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
      });
      pcRef.current = pc;

      stream.getTracks().forEach((t) => pc.addTrack(t, stream));

      const iceCandidates = [];
      pc.onicecandidate = (e) => {
        if (e.candidate) iceCandidates.push(e.candidate);
      };

      pc.ontrack = (e) => {
        const remote = e.streams[0];
        setRemoteStream(remote);
        if (botAudioRef.current) {
          botAudioRef.current.srcObject = remote;
          botAudioRef.current.play().catch(() => {});
        }
      };

      // 3 · SDP offer → POST /api/offer → SDP answer
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const res = await fetch(`${SERVER}/api/offer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sdp: offer.sdp, type: offer.type }),
      });
      if (!res.ok) throw new Error(`Server ${res.status}`);

      const answer = await res.json();
      await pc.setRemoteDescription({ type: answer.type, sdp: answer.sdp });

      // 4 · ICE candidates → PATCH /api/offer
      await new Promise((r) => setTimeout(r, 1000));

      if (iceCandidates.length) {
        await fetch(`${SERVER}/api/offer`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            pc_id: answer.pc_id,
            candidates: iceCandidates.map((c) => ({
              candidate: c.candidate,
              sdp_mid: c.sdpMid,
              sdp_mline_index: c.sdpMLineIndex,
            })),
          }),
        });
      }

      // 5 · Done — audio flows peer-to-peer
      setStatus('connected');
    } catch (err) {
      console.error('WebRTC error:', err);
      disconnect();
    }
  }, [disconnect]);

  /* ── Single tap toggles connection ─────────────────────────────── */
  const toggle = useCallback(() => {
    if (pcRef.current) disconnect();
    else connect();
  }, [connect, disconnect]);

  return { status, remoteStream, botAudioRef, toggle };
}
