"use client"
import SessionList from '../components/SessionList';

export default function DashboardPage() {
  const handleStartNewSession = () => {
    window.location.href = '/live';
  };

  return <SessionList onStartNewSession={handleStartNewSession} />;
}
