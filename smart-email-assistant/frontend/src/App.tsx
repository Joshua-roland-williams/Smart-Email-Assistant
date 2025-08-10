import React, { useState, useEffect } from 'react'; // Import useState and useEffect
import Header from './components/Header';
import EmailList from './components/EmailList';
import Footer from './components/Footer';
import AuthHandler from './components/AuthHandler'; // Import AuthHandler
import './App.css';
import axios from 'axios'; // Import axios

interface AuthStatus {
  authenticated: boolean;
  message: string;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loadingAuth, setLoadingAuth] = useState<boolean>(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axios.get<AuthStatus>('http://localhost:8000/api/auth/status');
        setIsAuthenticated(response.data.authenticated);
      } catch (error) {
        console.error("Error checking authentication status:", error);
        setIsAuthenticated(false);
      } finally {
        setLoadingAuth(false);
      }
    };
    checkAuth();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <Header />
      <main className="flex-grow container mx-auto p-4">
        <AuthHandler /> {/* AuthHandler component for login/logout */}
        {loadingAuth ? (
          <div className="text-center py-8">Loading authentication status...</div>
        ) : isAuthenticated ? (
          <EmailList />
        ) : (
          <div className="text-center py-8 text-red-600">
            Please log in with Google to view and process emails.
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}

export default App;
