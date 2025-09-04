import React, { useState } from 'react';
import Modal from './Modal';
import axios from "axios";
import "../Css/button.css"
const Main = () => {
  const [showModal, setShowModal] = useState(false);
  const [inputValue, setInputValue] = useState('');

  const handleOpenModal = () => setShowModal(true);
  const handleCloseModal = () => setShowModal(false);
  const handleInputChange = (e) => setInputValue(e.target.value);
  const [formData, setFormData] = useState({
    Host: "",
    Username: "",
    Password:""
  });

  const [errors, setErrors] = useState({});
  const [submissionError, setSubmissionError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [Response,setResponse]=useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const error = "";

    setFormData({ ...formData, [name]: value });
    setErrors({ ...errors, [name]: error });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmissionError("");
    setIsSubmitting(true);

    const formValid =
      Object.values(formData).every((field) => field.trim() !== "");

    if (formValid) {
      try {
        await  axios({
          method: 'post',
          responseType: 'json',
          url: `http://127.0.0.1:8000/firewall_fetch/`,
          data: formData,
          headers:{

            "Content-Type": "multipart/form-data",
          }
        })
        .then((response) => {
          setResponse(response.data)
          console.log(response)
        })
        .catch((error) => {
          //error.data.error.message
          console.log(error)
        });
      } catch (error) {
        setSubmissionError("Failed to submit. Please try again.");
        console.error("Submission error:", error);
      } finally {
        setIsSubmitting(false);
      }
    } else {
      setSubmissionError("Please fix errors before submitting.");
      setIsSubmitting(false);
    }
  };
  return (
    <div>
      <button onClick={handleOpenModal} className="glass-button" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>Update firewall</button>
      <Modal show={showModal} handleClose={handleCloseModal}>
        <div className="upload-container">
      <h2>Firewall Updation</h2>
      <p>Please enter the required information:</p>
      <form onSubmit={handleSubmit}>
        {[
          { label: "Host", name: "Host" },
          { label: "Username", name: "Username" },
          {label:"Password",name: "Password"}
        ].map((field, idx) => (
          <div className="form-group row" key={idx}>
            <label className="col-sm-4 col-form-label form-label">
              {field.label}
            </label>
            <div className="col-sm-8">
              <input
                type="text"
                name={field.name}
                value={formData[field.name]}
                onChange={handleChange}
                className="form-control"
              />
              {errors[field.name] && (
                <span className="error-message">{errors[field.name]}</span>
              )}
            </div>
          </div>
        ))}

        <button
          type="submit"
          className="btn btn-primary"
          disabled={
            isSubmitting ||
            !Object.values(errors).every((err) => !err) ||
            !Object.values(formData).every((field) => field.trim() !== "")
          }
          style={{marginTop: "20px",
          padding: "15px 30px",
          fontSize: "18px",
          backgroundColor:  isSubmitting ||
          !Object.values(errors).every((err) => !err) ||
          !Object.values(formData).every((field) => field.trim() !== "") ? "rgba(0, 123, 255, 0.3)" : "rgba(0, 123, 255, 0.5)",
          color: "white",
          border: "none",
          borderRadius: "8px",
          cursor:  isSubmitting ||
          !Object.values(errors).every((err) => !err) ||
          !Object.values(formData).every((field) => field.trim() !== "")? "not-allowed" : "pointer",
          transition: "all 0.3s ease",
          backdropFilter: "blur(5px)",
          display: "block",
          width: "200px",
          marginLeft: "auto",
          marginRight: "auto",
          textAlign: "center",}}
        >
          {isSubmitting ? "Submitting..." : "Submit"}
        </button>
        {submissionError && (
          <p className="error-message" style={{ color: "red" }}>
            {submissionError}
          </p>
        )}
      </form>
      {Response && Response.data ? (
 <div>
 <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
   <path d="M9 16.2L4.8 12L3.4 13.4L9 19L21 7L19.6 5.6L9 16.2Z" fill="currentColor"/>
 </svg> Updation Sucessful
</div>
) : (
  <div> Error</div>
)}

    </div>
      </Modal>
    </div>
  );
};

export default Main;
