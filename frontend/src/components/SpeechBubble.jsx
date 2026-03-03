/**
 * SpeechBubble — the AI orb.
 *
 * Visual states
 *   idle        – dim, slow breathe (tap to connect)
 *   connecting  – brighter pulse
 *   listening   – gentle breathe + sonar-like ripple rings
 *   speaking    – dynamic scale & glow driven by audioLevel
 */
export default function SpeechBubble({ status, audioLevel, isSpeaking, onTap }) {
  const isListening = status === 'connected' && !isSpeaking;
  const isTalking   = status === 'connected' && isSpeaking;

  // choose CSS modifier class
  let stateClass = 'orb--idle';
  if (status === 'connecting') stateClass = 'orb--connecting';
  else if (isListening)        stateClass = 'orb--listening';
  else if (isTalking)          stateClass = 'orb--speaking';

  // dynamic values only apply while AI is speaking
  const dynamicScale = isTalking ? 1 + audioLevel * 0.35 : 1;

  return (
    <div className="orb-wrapper" onClick={onTap} role="button" tabIndex={0}>
      <div
        className={`orb ${stateClass}`}
        style={{
          transform: `scale(${dynamicScale})`,
          '--glow': isTalking ? audioLevel : 0,
        }}
      >
        <div className="orb__core" />
        <div className="orb__ring orb__ring--1" />
        <div className="orb__ring orb__ring--2" />
        <div className="orb__ring orb__ring--3" />
      </div>
    </div>
  );
}
