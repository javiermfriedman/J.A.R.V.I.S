import useWebRTC from './hooks/useWebRTC';
import useAudioAnalyser from './hooks/useAudioAnalyser';
import SpeechBubble from './components/SpeechBubble';
import './App.css';

export default function App() {
  const { status, remoteStream, botAudioRef, toggle } = useWebRTC();
  const { audioLevel, isSpeaking, resumeAudio } = useAudioAnalyser(remoteStream);

  const handleTap = () => {
    resumeAudio();   // unlock AudioContext on first tap (enables orb animation)
    toggle();
  };

  return (
    <div className="app">
      <SpeechBubble
        status={status}
        audioLevel={audioLevel}
        isSpeaking={isSpeaking}
        onTap={handleTap}
      />

      {/* hidden element — plays the bot's voice */}
      <audio ref={botAudioRef} autoPlay playsInline style={{ display: 'none' }} />
    </div>
  );
}
