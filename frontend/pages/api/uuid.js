export default async function handler(req, res) {
  // extract UUID from inputted query parameters
  const { query: { uuid } } = req;

  // fetch data from a FastAPI server endpoint using the UUID and parse response into JSON
  const response = await fetch(`http://localhost:8000/api/response/${uuid}`);
  const data = await response.json();

  // If no data for UUID is returned, send a 404 response with an error message
  if (!data) {
    return res.status(404).json({ error: 'Data not found' });
  }

  // if data is found, send a 200 response with the data
  res.status(200).json(data);
}