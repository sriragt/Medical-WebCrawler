import { useRouter } from 'next/router.js';
import { useState, useEffect } from 'react';

export default function Home() {

    // manage the URL input value and the response from the server
    const [url, setUrl] = useState('');
    const [response, setResponse] = useState(null);
    const [loading, setLoading] = useState(false);
    const [loadingText, setLoadingText] = useState('Loading');
    const [error, setError] = useState(null);
    
    // access Next.js router and extract UUID from router query
    const router = useRouter();
    const { uuid } = router.query;

    // handle form submission
    const submit = async (event) => {

        // prevent the default form submission behavior that causes webpage to reload
        event.preventDefault();
        setLoading(true);
        setError(null);

        // send a POST request to the FastAPI server with the entered URL
        const response = await fetch('http://localhost:8000/api/generate_hypothesis/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }), // convert the URL to JSON to send it in the request body
        });

        // check if response is successful
        if (!response.ok) {
            // if response is not ok, parse error response as JSON
            const errorData = await response.json();
            setError(errorData.detail);
            setLoading(false);
            return; // return early to stop further execution
        }

        // parse response from the server as JSON
        const data = await response.json();

        // update response variable state with server output
        setResponse(data.llm_response);

        // redirect to page with new UUID to allow for shareable links
        if (data && data.new_uuid) {
            window.location.href = `/${data.new_uuid}`;
        }

        setLoading(false);
        setError(null);
    };

    // extract UUID from URL pathname
    const getUuidFromUrl = (pathname) => {
        const parts = pathname.split('/');
        const lastPart = parts[parts.length - 1];

        // check validity of UUID
        if (lastPart.length === 36 && lastPart.match(/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/)) {
            return lastPart;
        }
        else {router.push('/')}; // return to homepage if UUID is invalid

        return null;
    };

    // on loading of webpage, use hook to fetch data based on UUID from URL
    useEffect(() => {
        const fetchData = async () => {
        const pathname = window.location.pathname;
        const extractedUuid = getUuidFromUrl(pathname);
        if (extractedUuid) {
            const response = await fetch(`/api/uuid?uuid=${extractedUuid}`);
            const data = await response.json();
            setResponse(data);
        }
        };

        fetchData();
    }, []);

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
    // if UUID is of valid format but no corresponding data is found, return 404 error
    // if UUID is invalidly formatted, return to homepage
    return (
        <div className="container">
            <h2>Input Research Link</h2>
            {error && <p>Error: {error}</p>}
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

            {!loading && response && !response.detail ? (
                <div className="response-container">
                    <h2>Response</h2>
                    <ul className="response-list">
                        {Object.keys(response).map((drug, index) => (
                            <li className="response-item" key={index}>
                                <p><strong>{drug}:</strong></p>
                                <div className="list-container">
                                <ul>
                                    {Object.entries(JSON.parse(response[drug])).map(([key, value]) => (
                                        <li key={key}><strong>{key}: </strong> 
                                            {Array.isArray(value) ? (
                                                <ul>
                                                    {value.map((item, idx) => (
                                                        <li key={idx}>{item}</li>
                                                    ))}
                                                </ul>
                                            ) : (
                                                value
                                            )}
                                        </li>
                                    ))}
                                </ul>
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            ) : !loading && response && response.detail ? (
                <div>
                    <h2>404 Not Found</h2>
                </div>
            ) : (
                <p>{loadingText}</p>
            )}
        </div>
    );
    }
