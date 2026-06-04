import { useEffect, useState } from "react";
import { getHealth } from "./api";

export function useVersion(): string | null {
  const [version, setVersion] = useState<string | null>(null);
  useEffect(() => {
    getHealth()
      .then(({ version }) => setVersion(version))
      .catch(() => {});
  }, []);
  return version;
}
