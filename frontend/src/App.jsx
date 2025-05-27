import React, { useRef, useState } from "react";

export default function App() {
  const [recording, setRecording] = useState(false);
  const [hindiTranscript, setHindiTranscript] = useState("");
  const [englishTranslation, setEnglishTranslation] = useState("");
  const [reviewFeedback, setReviewFeedback] = useState("");
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks.current = [];
    mediaRecorder.current = new MediaRecorder(stream);

    mediaRecorder.current.ondataavailable = (e) => {
      audioChunks.current.push(e.data);
    };

    mediaRecorder.current.onstop = async () => {
      const blob = new Blob(audioChunks.current, { type: "audio/wav" });

      const formData = new FormData();
      formData.append("audio", blob, "recording.wav");

      try {
        const res = await fetch("https://fispitchaidraft1.onrender.com/upload", {
  method: "POST",
  body: formData,
});

        const data = await res.json();
        setHindiTranscript(data.hindi_transcript || "[No Hindi transcript returned]");
        setEnglishTranslation(data.english_translation || "[No English translation returned]");
        setReviewFeedback(data.review_feedback || "[No review feedback returned]");

      } catch (err) {
        console.error("[FRONTEND] Upload failed:", err);
        setHindiTranscript("[Error occurred while uploading or processing the file]");
        setEnglishTranslation("");
      }
    };

    mediaRecorder.current.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorder.current.stop();
    setRecording(false);
  };

  return (
    <div className="p-4 font-sans">
      <h1 className="text-2xl font-bold mb-4">🎙️ Hindi to English Translator</h1>

      <button
        onClick={recording ? stopRecording : startRecording}
        className={`px-4 py-2 rounded text-white ${
          recording ? "bg-red-600" : "bg-green-600"
        }`}
      >
        {recording ? "⏹️ Stop Recording" : "🎤 Start Recording"}
      </button>

      <div className="mt-6">
        <h2 className="text-xl font-semibold">🗣️ Hindi Transcript</h2>
        <pre className="bg-gray-100 p-2 rounded h-32 overflow-y-auto break-words whitespace-pre-wrap">
          {hindiTranscript}
        </pre>

        <h2 className="text-xl font-semibold mt-4">🌐 English Translation</h2>
        <pre className="bg-gray-100 p-2 rounded h-32 overflow-y-auto break-words whitespace-pre-wrap">
          {englishTranslation}
        </pre>
        <h2 className="text-xl font-semibold mt-4">🧠 Review Feedback</h2>
        <pre className="bg-gray-100 p-2 rounded h-48 overflow-y-auto break-words whitespace-pre-wrap">
          {reviewFeedback}
        </pre>

        
      </div>
    </div>
  );
}
