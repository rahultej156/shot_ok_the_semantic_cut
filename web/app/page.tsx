"use client";

import { useState } from "react";

interface SearchResult {
  clip_id: string;
  video_id: string;
  start: number;
  end: number;
  text: string;
  score: number;
  confidence: string;
  metadata: any;
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [explanation, setExplanation] = useState("");
  const [explaining, setExplaining] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResults([]);
    setExplanation("");
    try {
      const res = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, limit: 10 }),
      });
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error(err);
      alert("Search failed");
    } finally {
      setLoading(false);
    }
  };

  const handleExplain = async () => {
    if (!query || results.length === 0) return;

    setExplaining(true);
    try {
      const res = await fetch("/api/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, limit: 5 }), // Explain top 5
      });
      const data = await res.json();
      setExplanation(data.explanation);
    } catch (err) {
      console.error(err);
      alert("Explanation failed");
    } finally {
      setExplaining(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-900 text-neutral-100 p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <header className="text-center space-y-4">
          <h1 className="text-4xl font-bold tracking-tight text-blue-500">The Semantic Cut</h1>
          <p className="text-neutral-400">Team Shot Ok • Semantic Search for Video Footage</p>
        </header>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Describe the scene (e.g., 'tense dinner conversation')..."
            className="w-full bg-neutral-800 border border-neutral-700 rounded-xl px-6 py-4 text-lg focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-xl placeholder-neutral-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="absolute right-3 top-3 bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </form>

        {/* AI Explanation Section */}
        {results.length > 0 && (
          <div className="bg-neutral-800/50 border border-neutral-700 rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                ✨ AI Summary
              </h2>
              <button
                onClick={handleExplain}
                disabled={explaining || explanation.length > 0}
                className="text-sm bg-purple-600 hover:bg-purple-500 px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
              >
                {explaining ? "Thinking..." : explanation ? "Regenerate" : "Explain Results"}
              </button>
            </div>
            {explanation && (
              <div className="prose prose-invert max-w-none text-neutral-300 animate-in fade-in slide-in-from-top-2">
                <p>{explanation}</p>
              </div>
            )}
          </div>
        )}

        {/* Results Grid */}
        <div className="space-y-6">
          {results.map((clip) => (
            <div
              key={clip.clip_id}
              className="bg-neutral-800 border border-neutral-700 rounded-xl overflow-hidden hover:border-neutral-600 transition-colors"
            >
              {/* Header: Scene Info */}
              <div className="bg-neutral-900/50 px-6 py-3 border-b border-neutral-700 flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm text-yellow-500">
                    {clip.metadata?.scene_id || clip.video_id}
                  </span>
                  <span className="text-neutral-500">/</span>
                  <span className="font-medium text-blue-400">
                    {clip.metadata?.location || "Unknown Location"}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-neutral-700 text-neutral-400">
                    {clip.metadata?.int_ext} • {clip.metadata?.time_of_day}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <div className={`text-xs font-bold px-2 py-1 rounded uppercase ${clip.confidence === "High" ? "bg-green-900 text-green-300" :
                    clip.confidence === "Medium" ? "bg-yellow-900 text-yellow-300" :
                      "bg-red-900 text-red-300"
                    }`}>
                    {clip.confidence} Match
                  </div>
                  <span className="text-xs text-neutral-600 font-mono">
                    {clip.score.toFixed(2)}
                  </span>
                </div>
              </div>

              <div className="p-6 grid md:grid-cols-3 gap-6">
                {/* Left: Metadata & Actors */}
                <div className="md:col-span-1 space-y-4 text-sm">
                  <div>
                    <h4 className="text-neutral-500 font-medium mb-1 uppercase text-xs tracking-wider">Clip ID</h4>
                    <p className="font-mono text-neutral-300">{clip.clip_id}</p>
                  </div>
                  <div>
                    <h4 className="text-neutral-500 font-medium mb-1 uppercase text-xs tracking-wider">Actors</h4>
                    <div className="flex flex-wrap gap-2">
                      {clip.metadata?.actors?.map((actor: string) => (
                        <span key={actor} className="bg-neutral-700 px-2 py-1 rounded text-neutral-300">
                          {actor}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-neutral-500 font-medium mb-1 uppercase text-xs tracking-wider">Time</h4>
                    <p className="font-mono text-neutral-300">
                      {clip.metadata?.start}s - {clip.metadata?.end}s
                    </p>
                  </div>
                </div>

                {/* Right: Description & Dialogue */}
                <div className="md:col-span-2 space-y-4">
                  <div>
                    <h4 className="text-neutral-500 font-medium mb-1 uppercase text-xs tracking-wider">Visual Action</h4>
                    <p className="text-neutral-300 leading-relaxed">
                      {clip.metadata?.clip_description?.join(" ") || "No description available."}
                    </p>
                  </div>

                  {clip.metadata?.dialogue && clip.metadata.dialogue.length > 0 && (
                    <div>
                      <h4 className="text-neutral-500 font-medium mb-1 uppercase text-xs tracking-wider">Dialogue</h4>
                      <div className="bg-neutral-900 rounded-lg p-3 space-y-2 max-h-40 overflow-y-auto custom-scrollbar">
                        {clip.metadata.dialogue.map((line: any, idx: number) => (
                          <div key={idx} className="text-sm">
                            <span className="text-blue-400 font-bold mr-2">{line.actor}:</span>
                            <span className="text-neutral-400">{line.text}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {results.length === 0 && !loading && query && (
            <div className="text-center py-12 text-neutral-500">
              No footage found. Try a different query.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
