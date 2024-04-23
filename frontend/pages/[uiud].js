import { useRouter } from 'next/router.js';
import { useState, useEffect } from 'react';
import Index from './index.js';

export default function Home() {

    // manage the URL input value and the response from the server
    const [url, setUrl] = useState('');
    const [response, setResponse] = useState(null);
    
    // access Next.js router and extract UUID from router query
    const router = useRouter();
    const { uuid } = router.query;

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

    // render components for webpage
    // if UUID is of valid format but no corresponding data is found, return 404 error
    // if UUID is invalidly formatted, return to homepage
    return (
        <div>
            <h2>Enter Research Link:</h2>
            <form onSubmit={submit}>
            <label>
            <input
                type="text"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
            />
            </label>
            <button type="submit">Submit</button>
        </form>

        {response && !response.detail ? (
            <div>
            <h2>Response:</h2>
            <ul>
                {Object.entries(response).map(([key, value]) => (
                <li key={key}>
                    <strong>{key}:</strong> {JSON.stringify(value)}
                </li>
                ))}
            </ul>
            </div>
        ) : response && response.detail ? (
            <div>
            <h2>404 Not Found</h2>
            </div>
        ) : (
            <Index />
        )}
        </div>
    );
    }
