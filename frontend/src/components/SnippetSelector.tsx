import { DIFFICULTIES, TOPICS } from "../types";

interface SnippetSelectorProps {
  topic: string;
  difficulty: string;
  onTopicChange: (t: string) => void;
  onDifficultyChange: (d: string) => void;
  onFetch: () => void;
  loading: boolean;
}

export default function SnippetSelector({
  topic,
  difficulty,
  onTopicChange,
  onDifficultyChange,
  onFetch,
  loading,
}: SnippetSelectorProps) {
  return (
    <div className="snippet-selector">
      <div className="selector-group">
        <label htmlFor="topic-select">Topic</label>
        <select
          id="topic-select"
          value={topic}
          onChange={(e) => onTopicChange(e.target.value)}
        >
          {TOPICS.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>
      <div className="selector-group">
        <label htmlFor="difficulty-select">Difficulty</label>
        <select
          id="difficulty-select"
          value={difficulty}
          onChange={(e) => onDifficultyChange(e.target.value)}
        >
          {DIFFICULTIES.map((d) => (
            <option key={d.value} value={d.value}>
              {d.label}
            </option>
          ))}
        </select>
      </div>
      <button className="btn btn-secondary" onClick={onFetch} disabled={loading}>
        {loading ? "Loading…" : "New Snippet"}
      </button>
    </div>
  );
}
