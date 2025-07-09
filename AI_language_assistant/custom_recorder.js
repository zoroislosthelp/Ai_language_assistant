let mediaRecorder;
let audioChunks = [];

const startRecording = () => {
  audioChunks = [];
  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    mediaRecorder.addEventListener("dataavailable", event => {
      audioChunks.push(event.data);
    });

    mediaRecorder.addEventListener("stop", () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      audioBlob.arrayBuffer().then(buffer => {
        const uint8Array = new Uint8Array(buffer);
        const base64String = btoa(String.fromCharCode.apply(null, uint8Array));
        const data = { audio: base64String };
        const json = JSON.stringify(data);
        Streamlit.setComponentValue(json);
      });
    });

    setTimeout(() => {
      mediaRecorder.stop();
    }, 4000); // 4 seconds recording
  });
};

startRecording();
