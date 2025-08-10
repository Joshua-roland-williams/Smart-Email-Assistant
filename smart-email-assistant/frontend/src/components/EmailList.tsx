import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

interface Email {
  id: string;
  sender: string;
  subject: string;
  date: string;
  summary: string;
  replied: boolean;
  draftReply: string;
  priority: string;
  threadId: string;
}

const EmailList: React.FC = () => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshInterval, setRefreshInterval] = useState<number>(300000); // Default to 5 minutes (300,000 ms)

  const fetchEmails = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('http://localhost:8000/api/emails/today');
      setEmails(response.data);
    } catch (err) {
      setError('Failed to process emails.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEmails(); // Initial fetch

    const intervalId = setInterval(fetchEmails, refreshInterval);

    return () => clearInterval(intervalId); // Cleanup on unmount
  }, [fetchEmails, refreshInterval]);

  const handleRefreshClick = () => {
    fetchEmails();
  };

  if (loading) return <div>Loading emails...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Email Dashboard</h1>
      <button
        onClick={handleRefreshClick}
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
      >
        Refresh Emails
      </button>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white shadow-md rounded-lg">
          <thead>
            <tr className="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
              <th className="py-3 px-6 text-left">Sender</th>
              <th className="py-3 px-6 text-left">Subject</th>
              <th className="py-3 px-6 text-left">Date</th>
              <th className="py-3 px-6 text-left">Summary</th>
              <th className="py-3 px-6 text-left">Replied</th>
              <th className="py-3 px-6 text-left">Draft Reply</th>
              <th className="py-3 px-6 text-left">Priority</th>
            </tr>
          </thead>
          <tbody className="text-gray-600 text-sm font-light">
            {emails.map((email) => (
              <tr key={email.id} className="border-b border-gray-200 hover:bg-gray-100">
                <td className="py-3 px-6 text-left whitespace-nowrap">{email.sender}</td>
                <td className="py-3 px-6 text-left">{email.subject}</td>
                <td className="py-3 px-6 text-left">{new Date(email.date).toLocaleString()}</td>
                <td className="py-3 px-6 text-left">
                  <div className="bg-blue-50 p-2 rounded-md border border-blue-200">
                    <h3 className="font-semibold text-blue-800 mb-1">Summary:</h3>
                    <p className="text-gray-800">{email.summary}</p>
                  </div>
                </td>
                <td className="py-3 px-6 text-left">{email.replied ? 'Yes' : 'No'}</td>
                <td className="py-3 px-6 text-left">
                  <div className="bg-green-50 p-2 rounded-md border border-green-200">
                    <h3 className="font-semibold text-green-800 mb-1">Suggested Reply:</h3>
                    <p className="text-gray-800">{email.draftReply}</p>
                  </div>
                </td>
                <td className="py-3 px-6 text-left">{email.priority}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EmailList;
