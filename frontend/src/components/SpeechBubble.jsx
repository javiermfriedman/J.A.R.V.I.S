/**
 * SpeechBubble — the AI orb.
 *
 * Visual states (driven entirely by useAudioAnalyser's bubbleState):
 *   idle        – dim, slow breathe (tap to connect)
 *   connecting  – brighter pulse
 *   listening   – gentle breathe + sonar-like ripple rings
 *   speaking    – dynamic scale & glow driven by audioLevel
 */
export default function SpeechBubble({ bubbleState, audioLevel, onTap }) {
  const isTalking = bubbleState === 'speaking';

  const stateClass = `orb--${bubbleState}`;
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
