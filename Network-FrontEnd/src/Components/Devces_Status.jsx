import React, { useRef,useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "font-awesome/css/font-awesome.min.css";
import axios from "axios";

const Modal = ({ message }) => (
  <div
    style={{
      position: "fixed",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
      backgroundColor: "rgba(0, 0, 0, 0.5)",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      zIndex: 1000,
    }}
  >
    <div
      style={{
        backgroundColor: "white",
        padding: "20px",
        borderRadius: "10px",
        textAlign: "center",
        boxShadow: "0 0 10px rgba(0, 0, 0, 0.25)",
      }}
    >
      <h3>{message}</h3>
      <div className="spinner" style={{ margin: "20px 0" }}>
        <i className="fa fa-spinner fa-spin" style={{ fontSize: "2em", color: "#007bff" }}></i>
      </div>
    </div>
  </div>
);

const Device_Status = ({ 
   file1, file2, url,message
}) => {
  const [hostFile, setHostFile] = useState(null);
  const [commandsFile, setCommandsFile] = useState(null);
  const [hostStatus, setHostStatus] = useState("Drag and drop the file or click");
  const [commandsStatus, setCommandsStatus] = useState("Drag and drop the file or click");
  const [loading, setLoading] = useState(false);
  const inputRef1 = useRef(null);
  const inputRef2 = useRef(null);

  const handleFileUpload = (file, setFile, setStatus) => {
    if (!file) return;
    const ext = file.name.slice(-4);

    if (ext !== ".txt") {
      alert(`${file.name} file is not in .txt format.`);
      return;
    }

    setFile(file);
    setStatus(
      <>
        <i className="fa fa-check-circle"></i> {file.name} uploaded successfully!
      </>
    );
  };

  const handleDragOver = (e) => e.preventDefault();

  const handleDrop = (e, setFile, setStatus) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    handleFileUpload(file, setFile, setStatus);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!hostFile || !commandsFile) {
      alert("Please upload both files before submitting.");
      return;
    }

    const formData = new FormData();
    formData.append("file1", hostFile);
    formData.append("file2", commandsFile);

    setLoading(true);

    axios
      .post("http://127.0.0.1:8000/" + url, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        responseType: "blob", // Handle binary response for file download
      })
      .then((response) => {
        if(url=="home_check/"){
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "reports.zip");
        document.body.appendChild(link);
        link.click();
        link.remove();
        }
        
        // Hide loading spinner
        setLoading(false); 

        // Reset files and statuses after processing
        setHostFile(null);
        setCommandsFile(null);
        setHostStatus("Drag and drop the file or click");
        setCommandsStatus("Drag and drop the file or click");

        // Reset file input values manually
        inputRef1.current.value = "";
        inputRef2.current.value = "";

        // Optionally alert the user after processing is done
        alert("Processing is complete!");
      })
      .catch((error) => {
        console.error("Error:", error);
        setLoading(false); // Ensure loading is hidden even on error
        alert("Error processing files. Please try again.");
        
        // Optionally reset the states in case of error
        setHostFile(null);
        setCommandsFile(null);
        setHostStatus("Drag and drop the file or click");
        setCommandsStatus("Drag and drop the file or click");

        // Reset file inputs on error
        inputRef1.current.value = "";
        inputRef2.current.value = "";
      });
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        {/* Host File Upload */}
        <div
          onClick={() => inputRef1.current.click()}
          onDragOver={handleDragOver}
          onDrop={(e) => handleDrop(e, setHostFile, setHostStatus)}
          style={{
            border: "2px dashed #ccc",
            borderRadius: "10px",
            padding: "20px",
            marginTop: "10px",
            textAlign: "center",
            cursor: "pointer",
          }}
        >
          <div style={{ fontSize: "2.5em", color: "#007bff" }}>
            <i className="fa fa-file-alt"></i>
          </div>
          <div>{file1}</div>
          <div>{hostStatus}</div>
          <input
            type="file"
            ref={inputRef1}
            style={{ display: "none" }}
            onChange={(e) => handleFileUpload(e.target.files[0], setHostFile, setHostStatus)}
          />
        </div>

        {/* Commands File Upload */}
        <div
          onClick={() => inputRef2.current.click()}
          onDragOver={handleDragOver}
          onDrop={(e) => handleDrop(e, setCommandsFile, setCommandsStatus)}
          style={{
            border: "2px dashed #ccc",
            borderRadius: "10px",
            padding: "20px",
            marginTop: "10px",
            textAlign: "center",
            cursor: "pointer",
          }}
        >
          <div style={{ fontSize: "2.5em", color: "#007bff" }}>
            <i className="fa fa-file-alt"></i>
          </div>
          <div>{file2}</div>
          <div>{commandsStatus}</div>
          <input
            type="file"
            ref={inputRef2}
            style={{ display: "none" }}
            onChange={(e) => handleFileUpload(e.target.files[0], setCommandsFile, setCommandsStatus)}
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !(hostFile && commandsFile)}
          style={{
            marginTop: "20px",
            padding: "15px 30px",
            fontSize: "18px",
            backgroundColor: loading || !(hostFile && commandsFile) ? "rgba(0, 123, 255, 0.3)" : "rgba(0, 123, 255, 0.5)",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: loading || !(hostFile && commandsFile) ? "not-allowed" : "pointer",
            transition: "all 0.3s ease",
            backdropFilter: "blur(5px)",
            display: "block",
            width: "200px",
            marginLeft: "auto",
            marginRight: "auto",
            textAlign: "center",
          }}
        >
          {loading ? "Submitting..." : message}
        </button>
      </form>

      {/* Display Modal */}
      {loading && <Modal message="Processing files, please wait..." />}
    </div>
  );
};

export default Device_Status;
