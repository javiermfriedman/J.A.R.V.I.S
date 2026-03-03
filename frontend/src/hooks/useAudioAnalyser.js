import { useEffect, useRef, useState } from 'react';

const SPEAKING_THRESHOLD = 8;   // old model: low threshold, relies on default smoothing
const SILENCE_TIMEOUT_MS = 800; // hold "speaking" for 800 ms after last loud frame
const FFT_SIZE = 64;

/**
 * Analyses the bot's audio stream and manages the orb state machine.
 *
 * Uses the original detection model:
 *   – default smoothingTimeConstant (0.8) for stable readings
 *   – SPEAKING_THRESHOLD = 8  (lower, but smoothing prevents noise triggers)
 *   – silence timer resets on every quiet frame (800 ms after LAST loud frame)
 *
 * States: idle → connecting → listening ↔ speaking
 *
 * @param {MediaStream|null} botStream  – remote stream from useWebRTC
 * @param {string}           status     – 'idle' | 'connecting' | 'connected'
 * @returns {{ bubbleState: string, audioLevel: number }}
 */
export default function useAudioAnalyser(botStream, status) {
  const [bubbleState, setBubbleState] = useState('idle');
  const [audioLevel, setAudioLevel] = useState(0);

  const rafRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const speakingRef = useRef(false);

  /* ── Sync non-connected states directly from status ──────────── */
  useEffect(() => {
    if (status === 'idle') {
      setBubbleState('idle');
      setAudioLevel(0);
      speakingRef.current = false;
      clearTimeout(silenceTimerRef.current);
    } else if (status === 'connecting') {
      setBubbleState('connecting');
      setAudioLevel(0);
      speakingRef.current = false;
      clearTimeout(silenceTimerRef.current);
    }
  }, [status]);

  /* ── Frequency-domain analysis on a cloned stream ────────────── */
  useEffect(() => {
    if (!botStream || status !== 'connected') return;

    const clonedStream = botStream.clone();

    const ctx = new AudioContext();
    ctx.resume();
    const source = ctx.createMediaStreamSource(clonedStream);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = FFT_SIZE;
    // No explicit smoothingTimeConstant — default 0.8 smooths out noise spikes
    source.connect(analyser);

    const bins = analyser.frequencyBinCount;
    const freqData = new Uint8Array(bins);

    setBubbleState('listening');

    const tick = () => {
      analyser.getByteFrequencyData(freqData);

      // RMS across all frequency bins
      let sum = 0;
      for (let i = 0; i < bins; i++) {
        sum += freqData[i] * freqData[i];
      }
      const rms = Math.sqrt(sum / bins);

      // Normalise to 0–1 for the orb glow / scale
      const level = Math.min(rms / 80, 1);
      setAudioLevel(level);

      if (rms > SPEAKING_THRESHOLD) {
        /* ── audio detected ─────────────────────────────────────── */
        speakingRef.current = true;
        clearTimeout(silenceTimerRef.current);
        setBubbleState('speaking');
      } else if (speakingRef.current) {
        /* ── silence frame while still in "speaking" ────────────── */
        // Reset timer on every silent frame so the 800 ms countdown
        // always starts from the LAST loud frame (more forgiving for
        // natural speech gaps)
        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = setTimeout(() => {
          speakingRef.current = false;
          setBubbleState('listening');
          setAudioLevel(0);
        }, SILENCE_TIMEOUT_MS);
      }

      rafRef.current = requestAnimationFrame(tick);
    };

    tick();

    return () => {
      cancelAnimationFrame(rafRef.current);
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
      clonedStream.getTracks().forEach((t) => t.stop());
      ctx.close();
    };
  }, [botStream, status]);

  return { bubbleState, audioLevel };
}
