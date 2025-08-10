import React from 'react';
import { Mail, Settings, LogOut } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-blue-600 text-white p-4 shadow-md flex justify-between items-center">
      <div className="flex items-center">
        <Mail className="mr-2" size={28} />
        <h1 className="text-xl font-semibold">Smart Email Assistant</h1>
      </div>
      <nav>
        <ul className="flex space-x-4">
          <li>
            <button className="flex items-center text-white hover:text-blue-200 transition-colors duration-200">
              <Settings size={20} className="mr-1" />
              Settings
            </button>
          </li>
          <li>
            <button className="flex items-center text-white hover:text-blue-200 transition-colors duration-200">
              <LogOut size={20} className="mr-1" />
              Logout
            </button>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
