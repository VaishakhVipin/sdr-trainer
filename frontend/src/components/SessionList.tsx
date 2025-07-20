"use client"
import React, { useEffect, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Select } from './ui/select';
import { Skeleton } from './ui/skeleton';

const SORT_OPTIONS = [
  { value: 'score-desc', label: 'Highest Score' },
  { value: 'score-asc', label: 'Lowest Score' },
  { value: 'date-desc', label: 'Most Recent' },
  { value: 'date-asc', label: 'Oldest' },
];

function sortSessions(sessions, sort) {
  if (!sessions) return [];
  switch (sort) {
    case 'score-desc':
      return [...sessions].sort((a, b) => (b.score ?? 0) - (a.score ?? 0));
    case 'score-asc':
      return [...sessions].sort((a, b) => (a.score ?? 0) - (b.score ?? 0));
    case 'date-asc':
      return [...sessions].sort((a, b) => (a.created_at ?? 0) - (b.created_at ?? 0));
    case 'date-desc':
    default:
      return [...sessions].sort((a, b) => (b.created_at ?? 0) - (a.created_at ?? 0));
  }
}

export default function SessionList({ onStartNewSession }) {
  const [sessions, setSessions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sort, setSort] = useState('date-desc');

  useEffect(() => {
    setLoading(true);
    fetch('http://localhost:8000/sessions')
      .then(res => res.json())
      .then(data => {
        setSessions(data);
        setLoading(false);
      });
  }, []);

  const sortedSessions = sortSessions(sessions, sort);

  return (
    <div className="w-full max-w-3xl mx-auto py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Your Sales Call Sessions</h1>
        <Button onClick={onStartNewSession}>Start New Session</Button>
      </div>
      <div className="flex items-center gap-4 mb-4">
        <label htmlFor="sort" className="font-medium">Sort by:</label>
        <Select id="sort" value={sort} onValueChange={setSort}>
          {SORT_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </Select>
      </div>
      {loading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-24 w-full rounded-lg" />)}
        </div>
      ) : (
        <div className="space-y-4">
          {sortedSessions.length === 0 && (
            <div className="text-center text-gray-500">No sessions yet. Start your first call!</div>
          )}
          {sortedSessions.map(session => (
            <Card key={session.session_id} className="flex items-center justify-between p-4">
              <div>
                <div className="text-lg font-semibold">{session.title}</div>
                <div className="text-sm text-gray-500">{new Date(session.created_at * 1000).toLocaleString()}</div>
              </div>
              <div className="flex items-center gap-4">
                <Badge>{session.score ?? 'N/A'}</Badge>
                <Button variant="outline" onClick={() => window.location.href = `/session/${session.session_id}`}>View</Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
} 