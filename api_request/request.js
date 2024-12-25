const fetchConfluencePage = async (baseUrl, pageId, username, password) => {
  // Construct the API URL with the required os_authType=basic parameter
  const url = `${baseUrl}/rest/api/content/${pageId}?expand=body.storage&os_authType=basic`;

  // Encode the username and password in Base64 for Basic Authentication
  const credentials = btoa(`${username}:${password}`);

  try {
    // Send the GET request with the Authorization header
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json',
      },
    });

    // Check if the request was successful
    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    // Parse and return the response JSON
    const data = await response.json();
    console.log('Confluence Page Data:', data);
    return data;
  } catch (error) {
    console.error('Error fetching Confluence page:', error);
  }
};
  
  // Example usage
/*
  1. how to get the page id? https://confluence.atlassian.com/confkb/how-to-get-confluence-page-id-648380445.html
  2. token: https://community.atlassian.com/t5/Confluence-questions/How-to-create-API-Tokens-in-Confluence-6-10-Data-Center/qaq-p/901350
 */
const confluenceBaseUrl = 'http://localhost:8090'; // Replace with your Confluence server URL
const confluencePageId = '98380'; // Replace with the page ID
const confluenceUsername = 'henry'; // Replace with your username
const confluenceApiToken = '1225'; // Replace with your API token or password
//OTMzOTMxNTgwNzM5OlY0mxTuYqmkeMZW5zMqfG1VbFuf
fetchConfluencePage(confluenceBaseUrl, confluencePageId, confluenceUsername, confluenceApiToken);
