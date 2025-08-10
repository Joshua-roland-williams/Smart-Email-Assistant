import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface AuthStatus {
  authenticated: boolean;
  message: string;
}

const AuthHandler: React.FC = () => {
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = 'http://localhost:8000/api'; // Your backend API base URL

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await axios.get<AuthStatus>(`${API_BASE_URL}/auth/status`);
        setAuthStatus(response.data);
      } catch (err) {
        setError('Failed to check authentication status.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();

    // Handle OAuth callback if present in URL
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const authError = urlParams.get('error');

    if (code) {
      // This part is typically handled by the backend redirecting to a specific frontend route
      // For simplicity, we'll just log and clear the URL params here.
      // In a real app, you'd likely have a dedicated callback route on the frontend
      // that then makes a call to the backend's /auth/google/callback.
      console.log('Received OAuth code:', code);
      // Clear the code from the URL to prevent re-processing on refresh
      window.history.replaceState({}, document.title, window.location.pathname);
      // After successful backend processing, you might want to re-check auth status
      checkAuthStatus(); 
    } else if (authError) {
      setError(`OAuth Error: ${authError}`);
      window.history.replaceState({}, document.title, window.location.pathname);
    }

  }, []);

  const handleLogin = async () => {
    try {
      const response = await axios.get<{ authorization_url: string }>(`${API_BASE_URL}/auth/google/login`);
      window.location.href = response.data.authorization_url;
    } catch (err) {
      setError('Failed to initiate Google login.');
      console.error(err);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API_BASE_URL}/auth/logout`);
      setAuthStatus({ authenticated: false, message: "Logged out successfully." });
    } catch (err) {
      setError('Failed to logout.');
      console.error(err);
    }
  };

  if (loading) return <div className="p-4">Checking authentication status...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {error}</div>;

  return (
    <div className="p-4 bg-gray-100 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-3">Authentication Status</h2>
      <p className="mb-4">Status: {authStatus?.message}</p>
      
      {authStatus?.authenticated ? (
        <button 
          onClick={handleLogout} 
          className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
        >
          Logout from Google
        </button>
      ) : (
        <button 
          onClick={handleLogin} 
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Login with Google
        </button>
      )}
    </div>
  );
};

export default AuthHandler;
