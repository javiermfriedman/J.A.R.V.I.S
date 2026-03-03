import { useEffect, useRef, useState, useCallback } from 'react';

const SPEAK_ON = 0.08;  // level must exceed this to enter "speaking"
const SPEAK_OFF = 0.03; // level must drop below this to leave "speaking"
const SMOOTH = 0.25;    // exponential-smoothing factor (0 = sluggish, 1 = raw)

/**
 * Analyses a remote MediaStream and returns a smoothed audio level (0–1)
 * plus a debounced boolean indicating whether the far end is speaking.
 *
 * Call `resumeAudio()` inside a click handler so Chromium unlocks the
 * AudioContext (Safari does this automatically).
 */
export default function useAudioAnalyser(mediaStream) {
  const [audioLevel, setAudioLevel] = useState(0);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const ctxRef = useRef(null);
  const rafRef = useRef(null);
  const smoothedRef = useRef(0);
  const speakingRef = useRef(false);

  /* ── Call this from a click handler to unlock the AudioContext ── */
  const resumeAudio = useCallback(() => {
    if (!ctxRef.current) ctxRef.current = new AudioContext();
    ctxRef.current.resume();
  }, []);

  useEffect(() => {
    if (!mediaStream) {
      smoothedRef.current = 0;
      speakingRef.current = false;
      setAudioLevel(0);
      setIsSpeaking(false);
      return;
    }

    // Reuse the context that was unlocked by the click, or create one
    const ctx = ctxRef.current ?? new AudioContext();
    ctxRef.current = ctx;
    ctx.resume();

    const source = ctx.createMediaStreamSource(mediaStream);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 256;
    source.connect(analyser);

    const buf = new Uint8Array(analyser.fftSize);

    const tick = () => {
      analyser.getByteTimeDomainData(buf);

      // RMS volume
      let sum = 0;
      for (let i = 0; i < buf.length; i++) {
        const s = (buf[i] - 128) / 128;
        sum += s * s;
      }
      const rms = Math.sqrt(sum / buf.length);
      const raw = Math.min(rms / 0.2, 1);

      // exponential smoothing
      smoothedRef.current += (raw - smoothedRef.current) * SMOOTH;
      const level = smoothedRef.current;

      setAudioLevel(level);

      // hysteresis so the orb doesn't flicker
      if (level > SPEAK_ON && !speakingRef.current) {
        speakingRef.current = true;
        setIsSpeaking(true);
      } else if (level < SPEAK_OFF && speakingRef.current) {
        speakingRef.current = false;
        setIsSpeaking(false);
      }

      rafRef.current = requestAnimationFrame(tick);
    };

    tick();

    return () => {
      cancelAnimationFrame(rafRef.current);
      source.disconnect();
      analyser.disconnect();
      // Don't close ctx — it's reused across reconnects
    };
  }, [mediaStream]);

  return { audioLevel, isSpeaking, resumeAudio };
}
