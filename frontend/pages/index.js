import { useState } from 'react';

export default function Home() {

  // manage the URL input value and the response from the server
  const [url, setUrl] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('Loading');

  // handle form submission
  const submit = async (event) => {

    // prevent the default form submission behavior that causes webpage to reload
    event.preventDefault();
    setLoading(true);

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

    // set loading state to false after response is received
    setLoading(false);
  };

  // create dynamic loading page
  useEffect(() => {
      const intervalId = setInterval(() => {
          setLoadingText(prevText => {
              switch (prevText) {
                  case 'Loading':
                      return 'Loading.';
                  case 'Loading.':
                      return 'Loading..';
                  case 'Loading..':
                      return 'Loading...';
                  default:
                      return 'Loading';
              }
          });
      }, 750);

      return () => clearInterval(intervalId);
  }, []);

  // render components for webpage
  return (
    <div className="container">
      <h2>Input Research Link</h2>
      <div className='form-continer'>
          <form className="form" onSubmit={submit}>
              <label>
                  <input
                      type="text"
                      value={url}
                      onChange={(event) => setUrl(event.target.value)}
                      placeholder="Enter URL"
                  />
              </label>
              <button type="submit" className="submit-btn">Submit</button>
          </form>
      </div>
      {loading && <p>{loadingText}</p>}
    </div>
  );
}
