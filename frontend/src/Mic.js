import React, { useEffect, useState } from "react"
import {
  FiMic
} from "react-icons/fi";

const MIC = ({ useMic, handleMIC, handleText, forceEnd }) => {
  const [_, setListening] = useState(false);
  const [text, setText] = useState("");
  const [finished, setFinished] = useState(false)
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = SpeechRecognition ? new SpeechRecognition() : null;

  useEffect(() => {
    if (!recognition) return;
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "vi-VN";
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join("");
      setText(_ => transcript);
      handleText(transcript);
    };
    recognition.onend = () => {
      console.log("Recognition ended");
      setListening(false);
      setFinished(true);
    };
  }, [recognition, text]);


  useEffect(() => {
    if (finished) {
      forceEnd(text);
      setFinished(false);
    }
  }, [text, finished])

  const startListening = () => {
    if (!recognition) return alert("Speech Recognition not supported!");
    recognition.start();
    setText("");
    setListening(true);
    setFinished(false);
  };

  const stopListening = () => {
    if (!recognition) return;
    recognition.stop();
    setListening(false);
  };

  useEffect(() => {
    if (useMic) {
      startListening()
    } else {
      stopListening()
    }
  }, [useMic])

  const handleMICEvent = () => {
    handleMIC();
  }


  return <div onClick={handleMICEvent} className={useMic ? 'MIC active' : 'MIC'} >
    <FiMic></FiMic>
  </div>
}

export default MIC;