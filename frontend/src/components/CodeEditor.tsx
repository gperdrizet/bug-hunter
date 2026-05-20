import MonacoEditor from "@monaco-editor/react";

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  readOnly?: boolean;
  height?: string;
}

export default function CodeEditor({
  value,
  onChange,
  readOnly = false,
  height = "100%",
}: CodeEditorProps) {
  return (
    <MonacoEditor
      height={height}
      language="python"
      value={value}
      theme="vs-dark"
      options={{
        fontSize: 14,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        readOnly,
        lineNumbers: "on",
        wordWrap: "on",
        automaticLayout: true,
        tabSize: 4,
        insertSpaces: true,
      }}
      onChange={(val) => onChange(val ?? "")}
      // Use CDN — no self-hosted asset configuration needed for Vite
    />
  );
}
