import useWebRTC from './hooks/useWebRTC';
import useAudioAnalyser from './hooks/useAudioAnalyser';
import SpeechBubble from './components/SpeechBubble';
import './App.css';

export default function App() {
  const { status, remoteStream, botAudioRef, toggle } = useWebRTC();
  const { bubbleState, audioLevel } = useAudioAnalyser(remoteStream, status);

  return (
    <div className="app">
      <SpeechBubble
        bubbleState={bubbleState}
        audioLevel={audioLevel}
        onTap={toggle}
      />

      {/* hidden element — plays the bot's voice */}
      <audio ref={botAudioRef} autoPlay playsInline style={{ display: 'none' }} />
    </div>
  );
}
