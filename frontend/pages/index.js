import { useState } from 'react';

export default function Home() {

  // manage the URL input value and the response from the server
  const [url, setUrl] = useState('');
  const [response, setResponse] = useState(null);

  // handle form submission
  const submit = async (event) => {

    // prevent the default form submission behavior that causes webpage to reload
    event.preventDefault();

    // send a POST request to the FastAPI server with the entered URL
    const response = await fetch('http://localhost:8000/api/generate_hypothesis/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }), // convert the URL to JSON to send it in the request body
    });

    // parse response from the server as JSON
    const data = await response.json();

    // update response variable state with server output
    setResponse(data.llm_response);

    // redirect to page with new UUID to allow for shareable links
    if (data && data.new_uuid) {
      window.location.href = `/${data.new_uuid}`;
    }
  };

  // render components for webpage
  return (
    <div className="container">
      <h2>Input Research Link</h2>
      <form className="form-container" onSubmit={submit}>
        <label>
          <input
            type="text"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="Enter URL"
          />
        </label>
        <button className="submit-btn" type="submit">Submit</button>
      </form>
      {response && (
        <div className="response-container">
          <h2>Response</h2>
          <ul className="response-list">
            {Object.entries(response).map(([key, value]) => (
              <li className="response-item" key={key}>
                <strong>{key}:</strong> {JSON.stringify(value)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
