import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "font-awesome/css/font-awesome.min.css";
import axios from "axios";

const Compare = () => {
  const [precheckFile, setPrecheckFile] = useState(null);
  const [postcheckFile, setPostcheckFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState({
    precheck: "",
    postcheck: "",
  });
  const [loading, setLoading] = useState(false); // Add loading state

  const handleFileUpload = (event, fileType) => {
    const file = event.target.files[0];
    if (file) {
      if (file.name.endsWith(".txt")) {
        if (fileType === "precheck") {
          setPrecheckFile(file);
          setUploadStatus((prev) => ({
            ...prev,
            precheck: "File uploaded successfully!",
          }));
        } else if (fileType === "postcheck") {
          setPostcheckFile(file);
          setUploadStatus((prev) => ({
            ...prev,
            postcheck: "File uploaded successfully!",
          }));
        }
      } else {
        alert(`${file.name} is not a valid .txt file.`);
        event.target.value = "";
      }
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!precheckFile || !postcheckFile) {
      alert("Please upload both files before submitting.");
      return;
    }

    const formData = new FormData();
    formData.append("file1", precheckFile);
    formData.append("file2", postcheckFile);

    setLoading(true); // Set loading to true
    axios
      .post("http://127.0.0.1:8000/home/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then(function (response) {
        console.log("Response:", response.data);
        alert("Files submitted successfully!");
      })
      .catch(function (error) {
        console.error("Error:", error);
        alert("Error submitting files. Please try again.");
      })
      .finally(() => {
        setLoading(false); // Set loading to false once axios is done
      });

    setPrecheckFile(null);
    setPostcheckFile(null);
    setUploadStatus({ precheck: "", postcheck: "" });
  };

  const inlineStyles = {
    container: {
      fontFamily: "Arial, sans-serif",
      backgroundColor: "#f4f4f9",
      padding: "20px",
      borderRadius: "10px",
      maxWidth: "600px",
      margin: "20px auto",
      boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
      position: "relative",
    },
    heading: {
      fontSize: "1.5em",
      marginBottom: "20px",
      textAlign: "center",
      color: "#007bff",
    },
    fileInputContainer: {
      marginBottom: "15px",
    },
    label: {
      display: "block",
      marginBottom: "5px",
      fontWeight: "bold",
    },
    status: {
      fontSize: "0.9em",
      color: "#28a745",
    },
    button: {
      marginTop: "15px",
    },
    overlay: {
      position: "absolute",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(255, 255, 255, 0.7)",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      zIndex: 10,
    },
    spinner: {
      border: "4px solid #f3f3f3",
      borderTop: "4px solid #007bff",
      borderRadius: "50%",
      width: "40px",
      height: "40px",
      animation: "spin 1s linear infinite",
    },
    "@keyframes spin": {
      "0%": { transform: "rotate(0deg)" },
      "100%": { transform: "rotate(360deg)" },
    },
  };

  return (
    <div style={inlineStyles.container}>
      <h2 style={inlineStyles.heading}>Compare Files</h2>
      {loading && (
        <div style={inlineStyles.overlay}>
          <div style={inlineStyles.spinner}></div>
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div style={inlineStyles.fileInputContainer}>
          <label style={inlineStyles.label} htmlFor="precheck">
            Precheck File
          </label>
          <input
            type="file"
            id="precheck"
            onChange={(e) => handleFileUpload(e, "precheck")}
          />
          {uploadStatus.precheck && (
            <div style={inlineStyles.status}>{uploadStatus.precheck}</div>
          )}
        </div>
        <div style={inlineStyles.fileInputContainer}>
          <label style={inlineStyles.label} htmlFor="postcheck">
            Postcheck File
          </label>
          <input
            type="file"
            id="postcheck"
            onChange={(e) => handleFileUpload(e, "postcheck")}
          />
          {uploadStatus.postcheck && (
            <div style={inlineStyles.status}>{uploadStatus.postcheck}</div>
          )}
        </div>
        <button
          type="submit"
          className="btn btn-primary"
          style={inlineStyles.button}
          disabled={!precheckFile || !postcheckFile || loading}
        >
          Compare
        </button>
      </form>
    </div>
  );
};

export default Compare;
