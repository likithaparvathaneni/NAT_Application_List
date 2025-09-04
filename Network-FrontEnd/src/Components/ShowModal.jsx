import React from 'react';
import '../Css/Modal.css'; // Optional: for styling

const Modal = () => {
  return (
    <div className={`modal ${show ? 'show' : ''}`}>
      <h1>Hi</h1>
    </div>
  );
};

export default Modal;
