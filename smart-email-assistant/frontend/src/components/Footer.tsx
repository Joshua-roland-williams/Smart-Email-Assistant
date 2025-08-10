import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-blue-600 text-white p-4 text-center mt-8">
      <p>&copy; {new Date().getFullYear()} Smart Email Assistant. All rights reserved.</p>
    </footer>
  );
};

export default Footer;
