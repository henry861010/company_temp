import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx' // Make sure this points to your file
import './index.css' // You can delete this line if you deleted the file

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)