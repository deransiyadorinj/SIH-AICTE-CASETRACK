import { useState, useEffect, useCallback } from 'react';

/**
 * Hook to fetch data from an async service function.
 * Returns { data, loading, error, refetch }.
 */
export function useAsync(asyncFn, args = [], immediate = true) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...overrideArgs) => {
    setLoading(true);
    setError(null);
    try {
      const result = await asyncFn(...(overrideArgs.length ? overrideArgs : args));
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || 'Something went wrong');
      return null;
    } finally {
      setLoading(false);
    }
  }, [asyncFn, JSON.stringify(args)]);

  useEffect(() => {
    if (immediate) execute();
  }, [execute, immediate]);

  return { data, loading, error, refetch: execute };
}
