import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

const App = () => {
  const [text, setText] = useState("");
  const [images, setImages] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    setImages((prevImages) => [...prevImages, ...files]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData();
    formData.append("text", text);
    images.forEach((image) => formData.append("images", image));

    const userMessage = {
      role: "user",
      content: text || "Uploaded images",
      images: images.map((image) => URL.createObjectURL(image)), // Add image previews
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const res = await fetch("http://127.0.0.1:5000/api/openai", {
        method: "POST",
        body: formData,
      });
      const result = await res.json();

      if (res.ok) {
        const aiMessage = { role: "ai", content: result.result };
        setMessages((prev) => [...prev, aiMessage]);
      } else {
        const errorMessage = {
          role: "ai",
          content: `Error: ${result.error}`,
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        role: "ai",
        content: `Error: ${error.message}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setText(""); // Clear text input
      setImages([]); // Clear attachments
    }
  };

  return (
    <div className="container mt-5">
      <div className="card shadow p-4">
        <div className="card-body">
          <h3 className="card-title text-center mb-4">
            AI Chat and Image Uploader
          </h3>
          <div className="mb-3">
            <textarea
              className="form-control"
              placeholder="Type your message..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows="3"
            />
          </div>
          <div className="mb-3">
            <input
              type="file"
              className="form-control"
              multiple
              onChange={handleImageUpload}
            />
          </div>
          {images.length > 0 && (
            <div className="mb-3">
              <h5>Attachments:</h5>
              <div className="d-flex flex-wrap gap-2">
                {images.map((image, index) => (
                  <div
                    key={index}
                    className="border rounded"
                    style={{
                      width: "60px",
                      height: "60px",
                      overflow: "hidden",
                    }}
                  >
                    <img
                      src={URL.createObjectURL(image)}
                      alt={`upload-${index}`}
                      style={{
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
          <button
            className="btn btn-primary w-100"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? (
              <span
                className="spinner-border spinner-border-sm"
                role="status"
                aria-hidden="true"
              ></span>
            ) : (
              "Send"
            )}
          </button>
        </div>
        <div className="mt-4">
          <h5>Messages:</h5>
          <div
            className="border rounded p-3"
            style={{ height: "300px", overflowY: "auto" }}
          >
            {messages.map((message, index) => (
              <div
                key={index}
                className={`d-flex ${
                  message.role === "user"
                    ? "justify-content-end"
                    : "justify-content-start"
                }`}
              >
                <div
                  className={`p-2 mb-2 rounded ${
                    message.role === "user"
                      ? "bg-primary text-white"
                      : "bg-light text-dark"
                  }`}
                  style={{ maxWidth: "70%" }}
                >
                  <div>{message.content}</div>
                  {message.images && message.images.length > 0 && (
                    <div className="mt-2">
                      <span role="img" aria-label="camera">
                        📷
                      </span>{" "}
                      <small>{message.images.length} image(s) attached</small>
                      <div className="d-flex flex-wrap gap-2 mt-2">
                        {message.images.map((imgSrc, imgIndex) => (
                          <div
                            key={imgIndex}
                            className="border rounded"
                            style={{
                              width: "50px",
                              height: "50px",
                              overflow: "hidden",
                            }}
                          >
                            <img
                              src={imgSrc}
                              alt={`attachment-${imgIndex}`}
                              style={{
                                width: "100%",
                                height: "100%",
                                objectFit: "cover",
                              }}
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
