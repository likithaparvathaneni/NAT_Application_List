import React, { useState, useRef } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
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

const Device_Status_Generation = ({ file2, url, message }) => {
  const [ips, setIps] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [commandsFile, setCommandsFile] = useState(null);
  const [commandsStatus, setCommandsStatus] = useState("Drag and drop the file or click");
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const inputRef2 = useRef(null);

  const validateInput = (name, value) => {
    let error = "";
    if (!value) {
      return "This field is required.";
    }

    if (name === "ips") {
      const ipPattern =
        /^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$/;
      const ipsArray = value.split(",");
      if (!ipsArray.every(ip => ipPattern.test(ip.trim()))) {
        error = "Invalid IP address format.";
      }
    }

    return error;
  };

  const handleFileUpload = (file) => {
    if (!file) return;
    const ext = file.name.slice(-4);

    if (ext !== ".txt") {
      setErrors(prevErrors => ({
        ...prevErrors,
        commandsFile: "File is not in .txt format."
      }));
      return;
    }

    setCommandsFile(file);
    setCommandsStatus(
      <>
        <i className="fa fa-check-circle"></i> {file.name} uploaded successfully!
      </>
    );
    setErrors(prevErrors => ({ ...prevErrors, commandsFile: "" }));
  };

  const handleDragOver = (e) => e.preventDefault();

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    handleFileUpload(file);
  };

  const handleChange = (name, value) => {
    const error = validateInput(name, value);
    setErrors(prevErrors => ({
      ...prevErrors,
      [name]: error,
    }));

    if (name === "ips") {
      setIps(value);
    } else if (name === "username") {
      setUsername(value);
    } else if (name === "password") {
      setPassword(value);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (Object.values(errors).some(err => err)) {
      alert("Please fix errors before submitting.");
      return;
    }

    if (!ips || !username || !password || !commandsFile) {
      alert("Please fill all inputs and upload the commands file before submitting.");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("ips", ips);
    formData.append("username", username);
    formData.append("password", password);
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
        // Handle response here
        if(url=="home_check/"){
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", "reports.zip");
          document.body.appendChild(link);
          link.click();
          link.remove();
          }
          setLoading(false);
          setCommandsFile(null);
          setIps("")
          setUsername("")
          setPassword("")
          inputRef2.current.value = "";
          alert("Processing is complete!");
          setCommandsStatus("Drag and drop the file or click");
      })
      .catch((error) => {
        console.error("Error:", error);
        setLoading(false);
        alert("Error processing files. Please try again.");
        setIps("");
        setUsername("");
        setPassword("");
        setCommandsStatus("Drag and drop the file or click")
      });
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div style={{
            border: "2px dashed #ccc",
            borderRadius: "10px",
            padding: "20px",
            marginTop: "10px",
            textAlign: "center",
            cursor: "pointer",
          }}>
        <div style={{ display: "flex", justifyContent: "center", gap: "10px", marginTop: "10px" }}>
          <div style={{ display: "flex",justifyContent:"center", flexDirection: "column", width: "200px" }}>
            <label htmlFor=""> Enter Host Details:</label>
          </div>
          <div style={{ display: "flex", flexDirection: "column", width: "200px" }}>
          <label htmlFor="">
              ips <span style={{ color: "red" }}>*</span>
            </label>
            <input
              type="text"
              placeholder="Comma separated IPs"
              value={ips}
              onChange={(e) => handleChange("ips", e.target.value)}
              style={{ padding: "10px", borderRadius: "5px" }}
            />
            {errors.ips && (
              <div style={{ color: "red", marginTop: "5px" }}>{errors.ips}</div>
            )}
          </div>
          <div style={{ display: "flex", flexDirection: "column", width: "200px" }}>
            <label htmlFor="">
              Username <span style={{ color: "red" }}>*</span>
            </label>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => handleChange("username", e.target.value)}
              style={{ padding: "10px", borderRadius: "5px" }}
            />
            {errors.username && (
              <div style={{ color: "red", marginTop: "5px" }}>{errors.username}</div>
            )}
          </div>
          <div style={{ display: "flex", flexDirection: "column", width: "200px" }}>
          <label htmlFor="">
              Password <span style={{ color: "red" }}>*</span>
            </label>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => handleChange("password", e.target.value)}
              style={{ padding: "10px", borderRadius: "5px" }}
            />
            {errors.password && (
              <div style={{ color: "red", marginTop: "5px" }}>{errors.password}</div>
            )}
          </div>
        </div>
        </div>

        {/* Commands File Upload */}
        <div
          onClick={() => inputRef2.current.click()}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
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
          {errors.commandsFile && (
            <div style={{ color: "red", marginTop: "5px" }}>{errors.commandsFile}</div>
          )}
          <input
            type="file"
            ref={inputRef2}
            style={{ display: "none" }}
            onChange={(e) => handleFileUpload(e.target.files[0])}
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || Object.values(errors).some(err => err) || !ips || !username || !password || !commandsFile}
          style={{
            marginTop: "20px",
            padding: "15px 30px",
            fontSize: "18px",
            backgroundColor:
              loading || !ips || !username || !password || !commandsFile || Object.values(errors).some(err => err)
                ? "rgba(0, 123, 255, 0.3)"
                : "rgba(0, 123, 255, 0.5)",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor:
              loading || !ips || !username || !password || !commandsFile || Object.values(errors).some(err => err)
                ? "not-allowed"
                : "pointer",
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

      {loading && <Modal message="Processing files, please wait..." />}
    </div>
  );
};

export default Device_Status_Generation;